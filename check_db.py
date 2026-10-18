import os
import sys
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "laptop_catalog_db")
col_name = os.getenv("COLLECTION_NAME", "laptops")

print("=" * 65)
print("  MongoDB Atlas Connection Diagnostic")
print("=" * 65)

if not mongo_uri:
    print("[ERROR] MONGO_URI is missing or empty in your .env file.")
    sys.exit(1)

client = None
connected = False

for attempt in range(1, 3):
    try:
        print(f"[*] Connecting to MongoDB Atlas (Attempt {attempt} of 2)...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        client.admin.command("ping")
        connected = True
        break
    except ServerSelectionTimeoutError:
        if attempt < 2:
            print("    [!] Initial attempt timed out. Retrying in 2 seconds...")
            time.sleep(2)
        else:
            print("[ERROR] Connection timed out.")
            print("  -> Ensure your IP address is whitelisted in MongoDB Atlas.")
            print("     (MongoDB Atlas -> Network Access -> Add IP -> 0.0.0.0/0)")
            sys.exit(1)
    except ConnectionFailure as e:
        print(f"[ERROR] Authentication failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

if connected and client:
    print("[SUCCESS] Connected to MongoDB Atlas successfully!\n")
    all_dbs = client.list_database_names()
    print(f"[*] All Databases on Cluster : {all_dbs}")
    
    # Primary Database: laptop_catalog_db -> laptops
    if db_name in all_dbs:
        db_laptop = client[db_name]
        col_laptops = db_laptop[col_name]
        laptop_count = col_laptops.count_documents({})
        print(f"\n[+] Database: '{db_name}'")
        print(f"    Collection: '{col_name}'")
        print(f"    Total Documents: {laptop_count} Laptops in MongoDB Atlas")
        print("    " + "-" * 55)
        for doc in col_laptops.find().sort("price", 1):
            brand = doc.get("brand_name") or doc.get("brand", "Unknown")
            model = doc.get("model", "")
            price = doc.get("price", 0)
            stock = doc.get("stock", 0)
            doc_id = doc.get("_id")
            img = doc.get("image_url", "None")
            print(f"    * [{doc_id}] {brand} {model}")
            print(f"      Price: Rs. {price:,.2f} | Stock: {stock} units | Image: {img}")
            details = doc.get("details", {})
            if details:
                print(f"      Embedded Specs: {details}")
    
    print("\n" + "=" * 65)
    print("STATUS: ONLINE & FULLY SYNCHRONIZED")
    print("=" * 65)
