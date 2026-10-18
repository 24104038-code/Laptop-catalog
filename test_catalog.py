import os
import sys
import re
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

from app import app, get_collection, calculate_catalog_metrics
from bson.objectid import ObjectId


def run_tests():
    print("=" * 60)
    print("RUNNING LAPTOP CATALOG FULL VERIFICATION TEST SUITE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. MongoDB Connection & Multi-Document Verification
    # ---------------------------------------------------------
    col = get_collection()
    if col is None:
        print("[FAIL] Cannot connect to MongoDB (Atlas or Local).")
        sys.exit(1)

    initial_count = col.count_documents({})
    print(f"\n[1] MONGODB MULTI-DOCUMENT VERIFICATION")
    print(f"[PASS] Connected to MongoDB!")
    print(f"[PASS] Total Laptop Documents Found: {initial_count}")
    assert initial_count >= 7, f"Expected at least 7 laptop documents, found {initial_count}"

    sample_doc = col.find_one({"brand_name": "HP"})
    assert sample_doc is not None, "HP laptop document not found in MongoDB."
    print(f"[PASS] Verified HP Laptop Document: ID={sample_doc['_id']}")
    print(f"       Brand: {sample_doc.get('brand_name')}")
    print(f"       Model: {sample_doc.get('model')}")
    print(f"       Price: Rs. {sample_doc.get('price'):,}")
    print(f"       Stock: {sample_doc.get('stock')} units")
    print(f"       Image URL: {sample_doc.get('image_url')}")
    assert "details" in sample_doc, "Embedded 'details' subdocument missing!"
    print(f"[PASS] Verified Embedded Hardware Details: {sample_doc['details']}")

    # ---------------------------------------------------------
    # 2. Flask Test Client: GET / (Homepage)
    # ---------------------------------------------------------
    print(f"\n[2] FLASK ROUTE VERIFICATION")
    client = app.test_client()

    res_home = client.get("/")
    assert res_home.status_code == 200, f"Expected 200, got {res_home.status_code}"
    html_home = res_home.data.decode("utf-8")
    assert "Laptop Catalog" in html_home, "Catalog title missing in homepage"
    assert "brand-photo-img" in html_home, "Laptop photo missing in card grid"
    assert "master-hero-img" in html_home, "Master hero image missing"
    print("[PASS] GET / -> 200 OK (Homepage loaded with laptop cards, photos, metrics)")

    # ---------------------------------------------------------
    # 3. Search & Filter Tests
    # ---------------------------------------------------------
    res_search = client.get("/?search=Dell")
    assert res_search.status_code == 200
    html_search = res_search.data.decode("utf-8")
    assert "Inspiron" in html_search, "Dell Inspiron not found in search results"
    print("[PASS] GET /?search=Dell -> 200 OK (Search query works)")

    res_brand = client.get("/?brand=Lenovo")
    assert res_brand.status_code == 200
    html_brand = res_brand.data.decode("utf-8")
    assert "IdeaPad" in html_brand, "Lenovo IdeaPad not found in brand filter"
    print("[PASS] GET /?brand=Lenovo -> 200 OK (Brand filter works)")

    res_sort = client.get("/?sort=price_low")
    assert res_sort.status_code == 200
    print("[PASS] GET /?sort=price_low -> 200 OK (Sort query works)")

    # ---------------------------------------------------------
    # 4. Laptop Details View
    # ---------------------------------------------------------
    hp_id = str(sample_doc["_id"])
    res_details = client.get(f"/product/{hp_id}")
    assert res_details.status_code == 200, f"Expected 200, got {res_details.status_code}"
    html_details = res_details.data.decode("utf-8")
    assert "hero-laptop-img" in html_details, "Hero photo missing in details page"
    assert "HP 15" in html_details, "HP 15 missing in details page"
    assert "Quick Comparison" in html_details, "Comparison table missing in details page"
    print(f"[PASS] GET /product/{hp_id} -> 200 OK (Details page with photo & spec table)")

    # ---------------------------------------------------------
    # 5. CRUD: Add, Edit, Delete Test Laptop Document in MongoDB
    # ---------------------------------------------------------
    print(f"\n[3] MONGODB CRUD DOCUMENT CYCLES (Add -> Edit -> Delete)")

    # ADD
    test_laptop_data = {
        "brand_name": "Razer",
        "model": "Blade 16 Gaming",
        "category": "Electronics",
        "price": "249999",
        "stock": "5",
        "specification": "Intel Core i9 14900HX, RTX 4090 16GB, 32GB RAM, 2TB SSD, Mini-LED Dual-Mode",
        "image_url": "/static/images/hero_laptop.jpg"
    }

    res_add = client.post("/add-product", data=test_laptop_data, follow_redirects=False)
    assert res_add.status_code == 302, f"Expected 302 redirect, got {res_add.status_code}"
    print("[PASS] POST /add-product -> 302 Redirect (Document created in MongoDB)")

    added_doc = col.find_one({"brand_name": "Razer", "model": "Blade 16 Gaming"})
    assert added_doc is not None, "Added laptop was not found in MongoDB!"
    added_id = str(added_doc["_id"])
    print(f"[PASS] Verified New Document in MongoDB: ID={added_id} (Razer Blade 16 Gaming)")
    assert col.count_documents({}) == initial_count + 1, "Document count did not increment in MongoDB!"
    print(f"[PASS] MongoDB Document Count incremented: {initial_count} -> {initial_count + 1}")

    # EDIT
    edit_data = {
        "brand_name": "Razer",
        "model": "Blade 16 OLED Special Edition",
        "category": "Electronics",
        "price": "269999",
        "stock": "3",
        "specification": "Intel Core i9 14900HX, RTX 4090 16GB, 64GB RAM, 4TB SSD, OLED 240Hz",
        "image_url": "/static/images/hero_laptop.jpg"
    }

    res_edit = client.post(f"/edit-product/{added_id}", data=edit_data, follow_redirects=False)
    assert res_edit.status_code == 302, f"Expected 302 redirect, got {res_edit.status_code}"
    print(f"[PASS] POST /edit-product/{added_id} -> 302 Redirect (Document updated in MongoDB)")

    updated_doc = col.find_one({"_id": ObjectId(added_id)})
    assert updated_doc["model"] == "Blade 16 OLED Special Edition", "Model was not updated in MongoDB!"
    assert updated_doc["price"] == 269999.0, "Price was not updated in MongoDB!"
    print(f"[PASS] Verified Updated Document in MongoDB: {updated_doc['model']} | Price: Rs. {updated_doc['price']:,}")

    # DELETE
    res_del = client.post(f"/delete-product/{added_id}", follow_redirects=False)
    assert res_del.status_code == 302, f"Expected 302 redirect, got {res_del.status_code}"
    print(f"[PASS] POST /delete-product/{added_id} -> 302 Redirect (Document deleted from MongoDB)")

    deleted_doc = col.find_one({"_id": ObjectId(added_id)})
    assert deleted_doc is None, "Document still exists in MongoDB after deletion!"
    assert col.count_documents({}) == initial_count, "Document count did not decrement back in MongoDB!"
    print(f"[PASS] MongoDB Document Count decremented: {initial_count + 1} -> {initial_count}")

    # ---------------------------------------------------------
    # 6. Strict ZERO JAVASCRIPT Verification
    # ---------------------------------------------------------
    print(f"\n[4] STRICT ZERO JAVASCRIPT COMPLIANCE AUDIT")
    js_files = []
    for root, dirs, files in os.walk("."):
        if any(skip in root for skip in ["venv", ".git", "__pycache__", ".system_generated"]):
            continue
        for f in files:
            if f.endswith(".js"):
                js_files.append(os.path.join(root, f))
    
    assert len(js_files) == 0, f"JavaScript files found: {js_files}"
    print("[PASS] 0 .js files found across the entire repository!")

    # Check templates for script tags and inline js attributes
    templates_dir = "templates"
    for f in os.listdir(templates_dir):
        if f.endswith(".html"):
            path = os.path.join(templates_dir, f)
            with open(path, "r", encoding="utf-8") as tf:
                content = tf.read()
                assert "<script" not in content.lower(), f"<script> tag detected in {f}"
                for attr in ["onclick", "onload", "onsubmit", "onchange", "javascript:"]:
                    assert attr not in content.lower(), f"Inline JS attribute '{attr}' detected in {f}"
    print("[PASS] 0 <script> tags and 0 inline JS event handlers across all HTML templates!")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! 100% OPERATIONAL.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
