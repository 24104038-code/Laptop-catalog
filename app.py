import os
import re
import math
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.getenv("SECRET_KEY", "laptop_catalog_secret_key_1234567890")

# Standard Categories and Default Photo
DEFAULT_CATEGORIES = ["Electronics"]
DEFAULT_LAPTOP_IMAGE = "/static/images/hero_laptop.jpg"

# Initial Default Laptops (Each stored as an individual MongoDB document)
DEFAULT_LAPTOPS = [
    {
        "product_name": "Laptop",
        "brand_name": "HP",
        "model": "HP 15",
        "category": "Electronics",
        "price": 55000.0,
        "stock": 10,
        "specification": "Intel Core i5 12th Gen, 16GB RAM, 512GB SSD, 15.6-inch FHD Anti-Glare",
        "image_url": "/static/images/hp_laptop.jpg",
        "details": {
            "processor": "Intel Core i5 12th Gen",
            "ram": "16GB RAM",
            "storage": "512GB SSD",
            "display": "15.6-inch FHD Anti-Glare"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "Dell",
        "model": "Dell Inspiron 3520",
        "category": "Electronics",
        "price": 60000.0,
        "stock": 8,
        "specification": "Intel Core i5 12th Gen, 16GB RAM, 512GB SSD, 120Hz 15.6-inch Display",
        "image_url": "/static/images/dell_laptop.jpg",
        "details": {
            "processor": "Intel Core i5 12th Gen",
            "ram": "16GB RAM",
            "storage": "512GB SSD",
            "display": "120Hz 15.6-inch Display"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "Lenovo",
        "model": "Lenovo IdeaPad Slim 3",
        "category": "Electronics",
        "price": 52000.0,
        "stock": 15,
        "specification": "AMD Ryzen 5 5500U, 16GB RAM, 512GB SSD, 15.6-inch FHD IPS Dolby Audio",
        "image_url": "/static/images/lenovo_laptop.jpg",
        "details": {
            "processor": "AMD Ryzen 5 5500U",
            "ram": "16GB RAM",
            "storage": "512GB SSD",
            "display": "15.6-inch FHD IPS Dolby Audio"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "ASUS",
        "model": "ASUS VivoBook 15",
        "category": "Electronics",
        "price": 58000.0,
        "stock": 12,
        "specification": "Intel Core i5 1235U, 16GB RAM, 512GB SSD, OLED 15.6-inch Display",
        "image_url": "/static/images/asus_laptop.jpg",
        "details": {
            "processor": "Intel Core i5 1235U",
            "ram": "16GB RAM",
            "storage": "512GB SSD",
            "display": "OLED 15.6-inch Display"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "Acer",
        "model": "Acer Aspire 5",
        "category": "Electronics",
        "price": 49000.0,
        "stock": 6,
        "specification": "Intel Core i5 11th Gen, 8GB RAM, 512GB SSD, Backlit Keyboard FHD",
        "image_url": "/static/images/acer_laptop.jpg",
        "details": {
            "processor": "Intel Core i5 11th Gen",
            "ram": "8GB RAM",
            "storage": "512GB SSD",
            "display": "15.6-inch FHD Backlit"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "MSI",
        "model": "MSI Modern 14",
        "category": "Electronics",
        "price": 54000.0,
        "stock": 4,
        "specification": "Intel Core i5 12th Gen, 16GB RAM, 512GB SSD, Ultra Thin & Light 1.4kg",
        "image_url": "/static/images/msi_laptop.jpg",
        "details": {
            "processor": "Intel Core i5 12th Gen",
            "ram": "16GB RAM",
            "storage": "512GB SSD",
            "display": "14-inch FHD IPS"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "Apple",
        "model": "MacBook Air M2",
        "category": "Electronics",
        "price": 99900.0,
        "stock": 7,
        "specification": "Apple M2 8-Core CPU, 8GB Unified Memory, 256GB SSD, 13.6 Liquid Retina",
        "image_url": "/static/images/apple_laptop.jpg",
        "details": {
            "processor": "Apple M2 8-Core CPU",
            "ram": "8GB Unified Memory",
            "storage": "256GB SSD",
            "display": "13.6-inch Liquid Retina"
        }
    },
    {
        "product_name": "Laptop",
        "brand_name": "SAMSUNG",
        "model": "Galaxy Book 4 Pro",
        "category": "Electronics",
        "price": 100000.0,
        "stock": 5,
        "specification": "Intel Core Ultra 7 155H, 16GB LPDDR5X, 512GB NVMe SSD, 15.6 AMOLED Anti-Reflective",
        "image_url": "/static/images/samsung_laptop.jpg",
        "details": {
            "processor": "Intel Core Ultra 7 155H",
            "ram": "16GB LPDDR5X",
            "storage": "512GB NVMe SSD",
            "display": "15.6-inch AMOLED Anti-Reflective"
        }
    }
]

# MongoDB Database & Collection Setup
MONGO_URI = os.getenv("MONGO_URI")
LOCAL_MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = os.getenv("DB_NAME", "laptop_catalog_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "laptops")

mongo_client = None
db = None
laptops_collection = None
mongo_connected = False
active_mongo_source = None


def ensure_seeded_collection(col):
    """Ensures collection has documents; seeds initial laptops if empty."""
    try:
        if col.count_documents({}) == 0:
            col.insert_many([dict(d) for d in DEFAULT_LAPTOPS])
            print(f"[MongoDB] Seeded {len(DEFAULT_LAPTOPS)} laptops into collection.")
    except Exception as e:
        print(f"[MongoDB] Seed check error: {e}")


def init_mongo_connection():
    """
    Connects to MongoDB Atlas first. If Atlas times out or is offline,
    automatically falls back to Local MongoDB (localhost:27017).
    """
    global mongo_client, db, laptops_collection, mongo_connected, active_mongo_source

    # 1. Try Configured MONGO_URI (Atlas)
    if MONGO_URI:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
            client.admin.command("ping")
            mongo_client = client
            db = mongo_client[DB_NAME]
            laptops_collection = db[COLLECTION_NAME]
            ensure_seeded_collection(laptops_collection)
            mongo_connected = True
            active_mongo_source = "MongoDB Atlas"
            print(f"[MongoDB] Connected successfully to {active_mongo_source} ({DB_NAME}.{COLLECTION_NAME})!")
            return laptops_collection
        except Exception as e:
            print(f"[MongoDB] Atlas connection timeout/error: {e}")

    # 2. Try Local MongoDB (localhost:27017) only when in local environment (not Vercel)
    if not os.getenv("VERCEL"):
        try:
            client = MongoClient(LOCAL_MONGO_URI, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            mongo_client = client
            db = mongo_client[DB_NAME]
            laptops_collection = db[COLLECTION_NAME]
            ensure_seeded_collection(laptops_collection)
            mongo_connected = True
            active_mongo_source = "Local MongoDB (localhost:27017)"
            print(f"[MongoDB] Connected successfully to {active_mongo_source} ({DB_NAME}.{COLLECTION_NAME})!")
            return laptops_collection
        except Exception as e:
            print(f"[MongoDB] Local MongoDB connection error: {e}")

    mongo_connected = False
    return None


# Initialize on startup
init_mongo_connection()


def get_collection():
    """Returns active laptops collection, reconnecting if disconnected."""
    global laptops_collection, mongo_connected
    if laptops_collection is not None and mongo_connected:
        return laptops_collection
    return init_mongo_connection()


def sync_db_write(action_fn):
    """
    Executes a write operation on the active MongoDB collection,
    and synchronizes the same write to the secondary database (Local / Atlas).
    """
    global mongo_client
    col = get_collection()
    if col is None or mongo_client is None:
        return None

    # Execute on primary
    res = action_fn(col)

    # Sync to secondary if available (skip local MongoDB on Vercel)
    if not os.getenv("VERCEL"):
        try:
            if active_mongo_source == "MongoDB Atlas":
                c_loc = MongoClient(LOCAL_MONGO_URI, serverSelectionTimeoutMS=1000)
                sec_col = c_loc[DB_NAME][COLLECTION_NAME]
                action_fn(sec_col)
            else:
                if MONGO_URI:
                    c_atl = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
                    sec_col = c_atl[DB_NAME][COLLECTION_NAME]
                    action_fn(sec_col)
        except Exception:
            pass

    return res


def resolve_brand_image(brand_name, user_image_url):
    """Assigns appropriate branded product photography if default or empty."""
    if user_image_url and user_image_url.strip() and user_image_url != DEFAULT_LAPTOP_IMAGE:
        return user_image_url.strip()

    b_lower = (brand_name or "").lower().strip()
    brand_map = {
        "samsung": "/static/images/samsung_laptop.jpg",
        "hp": "/static/images/hp_laptop.jpg",
        "dell": "/static/images/dell_laptop.jpg",
        "lenovo": "/static/images/lenovo_laptop.jpg",
        "asus": "/static/images/asus_laptop.jpg",
        "acer": "/static/images/acer_laptop.jpg",
        "msi": "/static/images/msi_laptop.jpg",
        "apple": "/static/images/apple_laptop.jpg",
    }
    for k, v in brand_map.items():
        if k in b_lower:
            return v
    return DEFAULT_LAPTOP_IMAGE


def sync_to_legacy_catalog(action, laptop_data):
    """
    Synchronizes brand additions/deletions with product_catalog_db.products
    so that both databases in MongoDB Atlas stay 100% updated and in sync.
    """
    global mongo_client
    if mongo_client is None:
        return
    try:
        all_dbs = mongo_client.list_database_names()
        if "product_catalog_db" in all_dbs:
            prod_col = mongo_client["product_catalog_db"]["products"]
            parent_doc = prod_col.find_one({"product_name": "Laptop"})
            if parent_doc:
                brand_name = laptop_data.get("brand_name")
                if action == "add":
                    new_brand = {
                        "brand_name": brand_name,
                        "model": laptop_data.get("model"),
                        "price": laptop_data.get("price"),
                        "stock": laptop_data.get("stock"),
                        "specification": laptop_data.get("specification"),
                        "image_url": laptop_data.get("image_url")
                    }
                    prod_col.update_one(
                        {"_id": parent_doc["_id"]},
                        {"$push": {"brands": new_brand}}
                    )
                elif action == "delete":
                    prod_col.update_one(
                        {"_id": parent_doc["_id"]},
                        {"$pull": {"brands": {"brand_name": brand_name}}}
                    )
    except Exception as e:
        print(f"[Legacy DB Sync Warning] {e}")



@app.template_filter("currency")
def currency_filter(value):
    """Formats numeric values into Indian Rupee (₹) currency format with commas."""
    try:
        val = float(value)
        if val.is_integer():
            return f"₹{int(val):,}"
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹{value}"


def calculate_catalog_metrics(col):
    """Calculates total laptops, total stock inventory, and price range from MongoDB documents."""
    all_laptops = list(col.find({}, {"price": 1, "stock": 1, "brand_name": 1}))
    if not all_laptops:
        return {
            "total_laptops": 0,
            "total_stock": 0,
            "min_price": 0.0,
            "max_price": 0.0,
            "is_in_stock": False
        }

    prices = [float(l["price"]) for l in all_laptops if "price" in l and l["price"] is not None]
    stocks = [int(l["stock"]) for l in all_laptops if "stock" in l and l["stock"] is not None]

    total_stock = sum(stocks) if stocks else 0
    return {
        "total_laptops": len(all_laptops),
        "total_stock": total_stock,
        "min_price": min(prices) if prices else 0.0,
        "max_price": max(prices) if prices else 0.0,
        "is_in_stock": total_stock > 0
    }


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def index():
    """
    Laptop Catalog Dashboard:
    - Queries MongoDB for the list of individual laptop documents.
    - Demonstrates MongoDB queries: col.find(), col.distinct(), sort, skip, limit.
    - Displays master hero presentation, aggregated catalog stats, and laptop cards with photos.
    - Server-side pagination (6 laptops per page) strictly preserving search and filters.
    """
    col = get_collection()
    if col is None:
        flash("Database connection unavailable. Please verify your MongoDB configuration in .env.", "error")
        return render_template(
            "index.html",
            laptops=[],
            all_brands=[],
            metrics={"total_laptops": 0, "total_stock": 0, "min_price": 0, "max_price": 0, "is_in_stock": False},
            current_page=1,
            total_pages=1,
            total_count=0,
            search="",
            selected_brand="",
            selected_sort=""
        )

    # MongoDB Query: Distinct brands for filter dropdown
    try:
        all_brands = sorted([b for b in col.distinct("brand_name") if b])
    except errors.PyMongoError:
        all_brands = ["HP", "Dell", "Lenovo", "ASUS", "Acer", "MSI", "Apple"]

    # Request parameters
    search = request.args.get("search", "").strip()
    brand_filter = request.args.get("brand", "").strip()
    sort_by = request.args.get("sort", "").strip()
    page_arg = request.args.get("page", "1").strip()
    per_page_arg = request.args.get("per_page", "12").strip()

    try:
        page = int(page_arg)
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    if per_page_arg.lower() in ("all", "0"):
        per_page = 1000
    else:
        try:
            per_page = int(per_page_arg)
            if per_page < 1:
                per_page = 12
        except ValueError:
            per_page = 12

    # Build MongoDB Query Filter
    query = {}
    if brand_filter and brand_filter != "All Brands":
        query["brand_name"] = brand_filter

    if search:
        query["$or"] = [
            {"brand_name": {"$regex": re.escape(search), "$options": "i"}},
            {"model": {"$regex": re.escape(search), "$options": "i"}},
            {"specification": {"$regex": re.escape(search), "$options": "i"}}
        ]

    # Build MongoDB Sort Criteria
    sort_criteria = [("_id", -1)]  # Default newest first
    if sort_by == "price_low":
        sort_criteria = [("price", 1)]
    elif sort_by == "price_high":
        sort_criteria = [("price", -1)]
    elif sort_by == "name_asc":
        sort_criteria = [("brand_name", 1), ("model", 1)]
    elif sort_by == "name_desc":
        sort_criteria = [("brand_name", -1), ("model", -1)]
    elif sort_by == "stock_high":
        sort_criteria = [("stock", -1)]

    # MongoDB Queries: count_documents, sort, skip, limit
    total_count = col.count_documents(query)
    total_pages = max(1, math.ceil(total_count / per_page))
    if page > total_pages:
        page = total_pages

    skip_count = (page - 1) * per_page
    cursor = col.find(query).sort(sort_criteria).skip(skip_count).limit(per_page)
    paged_laptops = list(cursor)

    start_index = (page - 1) * per_page + 1 if total_count > 0 else 0
    end_index = min(page * per_page, total_count)
    metrics = calculate_catalog_metrics(col)

    return render_template(
        "index.html",
        laptops=paged_laptops,
        all_brands=all_brands,
        metrics=metrics,
        total_count=total_count,
        current_page=page,
        total_pages=total_pages,
        start_index=start_index,
        end_index=end_index,
        per_page=per_page,
        search=search,
        selected_brand=brand_filter,
        selected_sort=sort_by
    )


@app.route("/product/<product_id>")
@app.route("/laptop/<product_id>")
def product_details(product_id):
    """
    Laptop Details View:
    - MongoDB Query: col.find_one({'_id': ObjectId(product_id)})
    - Displays high-resolution laptop photo, hardware specs, stock status, and actions.
    """
    col = get_collection()
    if col is None:
        flash("Database unavailable. Please check MongoDB connection.", "error")
        return redirect(url_for("index"))

    try:
        obj_id = ObjectId(product_id)
        laptop = col.find_one({"_id": obj_id})
    except (InvalidId, TypeError):
        flash("Invalid laptop ID.", "error")
        return redirect(url_for("index"))

    if not laptop:
        flash("Laptop not found.", "error")
        return redirect(url_for("index"))

    # Also fetch all laptops for quick comparison table
    all_laptops = list(col.find().sort("price", 1))

    return render_template(
        "product_details.html",
        laptop=laptop,
        all_laptops=all_laptops
    )


@app.route("/add-product", methods=["GET", "POST"])
@app.route("/add-laptop", methods=["GET", "POST"])
@app.route("/add-brand", methods=["GET", "POST"])
def add_product():
    """
    Add Laptop to MongoDB:
    - Collects brand name, model, price, stock, specifications, and photo URL.
    - MongoDB Query: col.insert_one(laptop_doc) -> Creates a new document in MongoDB!
    """
    col = get_collection()
    if col is None:
        flash("Database unavailable. Please check MongoDB connection.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        brand_name = request.form.get("brand_name", "").strip()
        model = request.form.get("model", "").strip()
        category = request.form.get("category", "Electronics").strip() or "Electronics"
        price_raw = request.form.get("price", "").strip()
        stock_raw = request.form.get("stock", "").strip()
        specification = request.form.get("specification", "").strip()
        image_url = request.form.get("image_url", "").strip() or DEFAULT_LAPTOP_IMAGE

        errors_list = []
        if not brand_name:
            errors_list.append("Brand name is required.")
        if not model:
            errors_list.append("Laptop model is required.")

        price_val = 0.0
        try:
            price_val = float(price_raw)
            if price_val < 0:
                errors_list.append("Price must be 0 or greater.")
        except (ValueError, TypeError):
            errors_list.append("Valid price number is required.")

        stock_val = 0
        try:
            stock_val = int(stock_raw)
            if stock_val < 0:
                errors_list.append("Stock must be 0 or greater.")
        except (ValueError, TypeError):
            errors_list.append("Valid stock integer is required.")

        if errors_list:
            for err in errors_list:
                flash(err, "error")
            return render_template("add_product.html", form_data=request.form)

        resolved_image = resolve_brand_image(brand_name, image_url)

        # Build Laptop document with embedded details
        new_laptop = {
            "product_name": "Laptop",
            "brand_name": brand_name,
            "model": model,
            "category": category,
            "price": price_val,
            "stock": stock_val,
            "specification": specification or f"{brand_name} {model} Standard Configuration",
            "image_url": resolved_image,
            "details": {
                "processor": specification or "Standard Processor",
                "brand": brand_name,
                "model": model
            }
        }

        try:
            # MongoDB Query: insert_one to create new laptop document
            sync_db_write(lambda c: c.insert_one(new_laptop))
            sync_to_legacy_catalog("add", new_laptop)
            flash(f"Successfully added brand '{brand_name}' ({model}) to Laptop Catalog & MongoDB! Now visible in the catalog below.", "success")
            return redirect(url_for("index", page=1))
        except errors.PyMongoError as e:
            flash(f"MongoDB query error: {e}", "error")
            return render_template("add_product.html", form_data=request.form)

    return render_template("add_product.html", form_data={})


@app.route("/edit-product/<product_id>", methods=["GET", "POST"])
@app.route("/edit-laptop/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    """
    Edit Laptop in MongoDB:
    - Pre-fills current laptop details.
    - MongoDB Query: col.update_one({'_id': ObjectId(product_id)}, {'$set': updated_fields}).
    """
    col = get_collection()
    if col is None:
        flash("Database unavailable. Please check MongoDB connection.", "error")
        return redirect(url_for("index"))

    try:
        obj_id = ObjectId(product_id)
        laptop = col.find_one({"_id": obj_id})
    except (InvalidId, TypeError):
        flash("Invalid laptop ID.", "error")
        return redirect(url_for("index"))

    if not laptop:
        flash("Laptop not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        brand_name = request.form.get("brand_name", "").strip() or laptop.get("brand_name", "")
        model = request.form.get("model", "").strip() or laptop.get("model", "")
        category = request.form.get("category", "Electronics").strip() or "Electronics"
        price_raw = request.form.get("price", "").strip()
        stock_raw = request.form.get("stock", "").strip()
        specification = request.form.get("specification", "").strip()
        image_url = request.form.get("image_url", "").strip() or laptop.get("image_url", DEFAULT_LAPTOP_IMAGE)

        errors_list = []
        if not brand_name:
            errors_list.append("Brand name is required.")
        if not model:
            errors_list.append("Laptop model is required.")

        price_val = laptop.get("price", 0.0)
        try:
            price_val = float(price_raw)
            if price_val < 0:
                errors_list.append("Price must be 0 or greater.")
        except (ValueError, TypeError):
            errors_list.append("Valid price number is required.")

        stock_val = laptop.get("stock", 0)
        try:
            stock_val = int(stock_raw)
            if stock_val < 0:
                errors_list.append("Stock must be 0 or greater.")
        except (ValueError, TypeError):
            errors_list.append("Valid stock integer is required.")

        if errors_list:
            for err in errors_list:
                flash(err, "error")
            return render_template("edit_product.html", laptop=laptop)

        resolved_image = resolve_brand_image(brand_name, image_url)
        updated_data = {
            "brand_name": brand_name,
            "model": model,
            "category": category,
            "price": price_val,
            "stock": stock_val,
            "specification": specification,
            "image_url": resolved_image,
            "details": {
                "processor": specification or "Standard Processor",
                "brand": brand_name,
                "model": model
            }
        }

        try:
            # MongoDB Query: update_one with $set operator
            sync_db_write(lambda c: c.update_one({"_id": obj_id}, {"$set": updated_data}))
            flash(f"Laptop {brand_name} ({model}) updated successfully in MongoDB and Laptop Catalog!", "success")
            return redirect(url_for("product_details", product_id=str(obj_id)))
        except errors.PyMongoError as e:
            flash(f"MongoDB query error: {e}", "error")
            return render_template("edit_product.html", laptop=laptop)

    return render_template("edit_product.html", laptop=laptop)


@app.route("/delete-product/<product_id>", methods=["POST"])
@app.route("/delete-laptop/<product_id>", methods=["POST"])
def delete_product(product_id):
    """
    Delete Laptop from MongoDB:
    - MongoDB Query: col.delete_one({'_id': ObjectId(product_id)})
    - Decrements the laptop document count in MongoDB Atlas!
    """
    col = get_collection()
    if col is None:
        flash("Database unavailable. Please check MongoDB connection.", "error")
        return redirect(url_for("index"))

    try:
        obj_id = ObjectId(product_id)
        laptop = col.find_one({"_id": obj_id})
        laptop_name = f"{laptop.get('brand_name', '')} {laptop.get('model', '')}" if laptop else "Laptop"
    except (InvalidId, TypeError):
        flash("Invalid laptop ID.", "error")
        return redirect(url_for("index"))

    try:
        # MongoDB Query: delete_one
        sync_db_write(lambda c: c.delete_one({"_id": obj_id}))
        if laptop:
            sync_to_legacy_catalog("delete", laptop)
        flash(f"Laptop '{laptop_name}' deleted successfully from MongoDB and Laptop Catalog!", "success")
    except errors.PyMongoError as e:
        flash(f"MongoDB query error: {e}", "error")

    return redirect(url_for("index"))


@app.route("/seed-sample-data", methods=["POST"])
def seed_sample_data():
    """
    Resets & seeds MongoDB with the 7 standard laptop documents.
    MongoDB Queries: delete_many({}) and insert_many(DEFAULT_LAPTOPS).
    """
    col = get_collection()
    if col is None:
        flash("Database unavailable. Please check MongoDB connection.", "error")
        return redirect(url_for("index"))

    try:
        sync_db_write(lambda c: (c.delete_many({}), c.insert_many([dict(d) for d in DEFAULT_LAPTOPS])))
        flash(f"Successfully seeded {len(DEFAULT_LAPTOPS)} laptops into MongoDB!", "success")
    except errors.PyMongoError as e:
        flash(f"MongoDB query error: {e}", "error")

    return redirect(url_for("index"))


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found_page(e):
    return render_template("base.html", custom_error="404 - The requested page was not found."), 404


@app.errorhandler(500)
def server_error_page(e):
    return render_template("base.html", custom_error="500 - An unexpected internal server error occurred."), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)