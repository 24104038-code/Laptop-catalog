import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
db = client["product_catalog_db"]
col = db["products"]

master_image = "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80"

updated_brands = [
    {
        "brand_name": "HP",
        "model": "HP 15",
        "price": 55000.0,
        "stock": 10,
        "specification": "Intel Core i5 12th Gen, 8GB RAM, 512GB SSD, 15.6 FHD Anti-Glare",
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80"
    },
    {
        "brand_name": "Dell",
        "model": "Dell Inspiron 3520",
        "price": 60000.0,
        "stock": 8,
        "specification": "Intel Core i5 12th Gen, 16GB RAM, 512GB SSD, 120Hz 15.6 Display",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80"
    },
    {
        "brand_name": "Lenovo",
        "model": "Lenovo IdeaPad Slim 3",
        "price": 52000.0,
        "stock": 15,
        "specification": "AMD Ryzen 5 5500U, 16GB RAM, 512GB SSD, 15.6 FHD IPS",
        "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?auto=format&fit=crop&w=800&q=80"
    },
    {
        "brand_name": "ASUS",
        "model": "ASUS VivoBook 15",
        "price": 58000.0,
        "stock": 12,
        "specification": "Intel Core i5 1235U, 16GB RAM, 512GB SSD, OLED 15.6 Display",
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80"
    },
    {
        "brand_name": "Acer",
        "model": "Acer Aspire 5",
        "price": 49000.0,
        "stock": 6,
        "specification": "Intel Core i5 11th Gen, 8GB RAM, 512GB SSD, Backlit Keyboard",
        "image_url": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?auto=format&fit=crop&w=800&q=80"
    },
    {
        "brand_name": "MSI",
        "model": "MSI Modern 14",
        "price": 54000.0,
        "stock": 4,
        "specification": "Intel Core i5 12th Gen, 16GB RAM, 512GB SSD, Ultra Thin & Light 1.4kg",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80"
    },
    {
        "brand_name": "Apple",
        "model": "MacBook Air M2",
        "price": 99900.0,
        "stock": 7,
        "specification": "Apple M2 8-Core CPU, 8GB Unified Memory, 256GB SSD, 13.6 Liquid Retina",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80"
    }
]

res = col.update_one(
    {"product_name": "Laptop"},
    {
        "$set": {
            "image_url": master_image,
            "description": "Portable computer catalog featuring top laptop manufacturers with models, specifications, pricing, stock inventory, and high-resolution photos.",
            "brands": updated_brands
        }
    }
)

print(f"MongoDB Update Result: matched={res.matched_count}, modified={res.modified_count}")
doc = col.find_one({"product_name": "Laptop"})
print("Updated Document ID:", doc["_id"])
print("Master photo:", doc.get("image_url"))
print("Brands count:", len(doc.get("brands", [])))
for b in doc["brands"]:
    print(f"  - {b['brand_name']}: {b['image_url'][:50]}...")
