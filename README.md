# Laptop Catalog Management System

A complete, production-grade **Laptop Catalog Management System** built with **Python Flask**, **MongoDB Atlas**, **Jinja2**, **HTML5**, and **CSS3**.

> **Crucial Architectural Rule:** This project is built around **ONE PRODUCT (Laptop) containing MULTIPLE BRANDS (HP, Dell, Lenovo, ASUS, Acer, MSI, Apple)** with **100% ZERO JavaScript** (no `.js` files, no `<script>` tags, no client-side frameworks). All CRUD operations, validation, search, brand filtering, sorting, and pagination are executed entirely through server-side Flask routes, HTML forms, and Jinja2 rendering.

---

## Table of Contents
1. [Project Concept (One Product $\rightarrow$ Multiple Brands)](#1-project-concept)
2. [Technology Stack](#2-technology-used)
3. [MongoDB Database Structure & Embedded Documents](#3-mongodb-database-structure--embedded-documents)
4. [MongoDB Queries Implemented](#4-mongodb-queries-implemented)
5. [Integrated Photos & Media](#5-integrated-photos--media)
6. [Project Structure](#6-project-structure)
7. [How to Run the Application](#7-how-to-run-the-application)
8. [Features & Capabilities](#8-features--capabilities)
9. [CRUD Operations](#9-crud-operations)
10. [Zero JavaScript Audit](#10-zero-javascript-audit)

---

## 1. Project Concept

In this system, the single product entity is **Laptop**. Instead of creating separate product documents for every laptop manufacturer, the system models **Laptop** as a **single parent document** in MongoDB that embeds multiple brand manufacturers inside an array:

$$\text{ONE PRODUCT: Laptop} \longrightarrow \text{MULTIPLE BRANDS (HP, Dell, Lenovo, ASUS, Acer, MSI, Apple)}$$

```
Laptop (Parent Document)
│
├── HP       ├── Model: HP 15               ├── Price: ₹55,000  ├── Stock: 10  └── Photo: High-Res URL
├── Dell     ├── Model: Dell Inspiron 3520  ├── Price: ₹60,000  ├── Stock: 8   └── Photo: High-Res URL
├── Lenovo   ├── Model: IdeaPad Slim 3      ├── Price: ₹52,000  ├── Stock: 15  └── Photo: High-Res URL
├── ASUS     ├── Model: ASUS VivoBook 15    ├── Price: ₹58,000  ├── Stock: 12  └── Photo: High-Res URL
├── Acer     ├── Model: Acer Aspire 5       ├── Price: ₹49,000  ├── Stock: 6   └── Photo: High-Res URL
├── MSI      ├── Model: MSI Modern 14       ├── Price: ₹54,000  ├── Stock: 4   └── Photo: High-Res URL
└── Apple    ├── Model: MacBook Air M2      ├── Price: ₹99,900  ├── Stock: 7   └── Photo: High-Res URL
```

---

## 2. Technology Used

- **Backend**: Python 3.10+ & Flask 3.x
- **Database**: MongoDB / MongoDB Atlas (using `pymongo`)
- **Templating**: Jinja2 (server-side rendering with custom currency formatting `₹`)
- **Frontend**: HTML5 & Pure CSS3 (CSS Grid, Flexbox, media queries, CSS variables)
- **Environment**: `python-dotenv` for secure environment variable isolation
- **Zero JavaScript**: 100% free of JavaScript, Node.js, npm, jQuery, React, Vue, Angular, AJAX, or `.js` files.

---

## 3. MongoDB Database Structure & Embedded Documents

- **Database**: `product_catalog_db`
- **Collection**: `products`

```json
{
  "_id": ObjectId("6ac5eb67e08d314886ebe223"),
  "product_name": "Laptop",
  "category": "Electronics",
  "description": "Portable computer catalog featuring top laptop manufacturers with models, specifications, pricing, stock inventory, and high-resolution photos.",
  "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80",
  "brands": [
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
}
```

---

## 4. MongoDB Queries Implemented

All operations utilize explicit MongoDB queries executed via PyMongo:

1. **Find Document**:
   ```python
   laptop = col.find_one({"product_name": "Laptop"})
   ```
2. **Distinct Embedded Brand Names**:
   ```python
   all_brands = col.distinct("brands.brand_name", {"_id": laptop["_id"]})
   ```
3. **Embedded Array Search ($elemMatch with $regex)**:
   ```python
   col.find_one({
       "_id": laptop["_id"],
       "brands": {"$elemMatch": {"brand_name": {"$regex": "^Dell$", "$options": "i"}}}
   })
   ```
4. **Append New Embedded Brand ($push & $each)**:
   ```python
   col.update_one(
       {"_id": laptop["_id"]},
       {"$push": {"brands": {"$each": valid_brands}}}
   )
   ```
5. **Delete Brand by Name ($pull)**:
   ```python
   col.update_one(
       {"product_name": "Laptop"},
       {"$pull": {"brands": {"brand_name": brand_name}}}
   )
   ```
6. **Update Entire Brand Catalog & Photos ($set)**:
   ```python
   col.update_one({"_id": laptop["_id"]}, {"$set": updated_data})
   ```

---

## 5. Integrated Photos & Media

- **Master Cover Photo**: Displayed prominently on the catalog dashboard and the full product details page.
- **Brand Cards**: Every brand card includes a crisp photo representing that laptop model with an in-stock / out-of-stock overlay badge.
- **Comparison Table**: Dedicated thumbnail photo column (`table-brand-thumb`) next to brand specifications.
- **Add / Edit Forms**: Input fields for custom image URLs with instant thumbnail preview.
- **Local Fallback Graphic**: `/static/images/default_laptop.svg` vector graphic automatically used if any image URL is left empty.

---

## 6. Project Structure

```
product_catalog/
│
├── app.py                  # Main Flask application and MongoDB route handlers
├── check_db.py             # Diagnostic script to test MongoDB Atlas connection & count
├── test_catalog.py         # Automated test suite (Routes, MongoDB queries, Zero-JS audit)
├── requirements.txt        # Python package dependencies (Flask, pymongo, python-dotenv)
├── .env                    # Private environment variables (Excluded from git)
├── .env.example            # Environment configuration template
├── .gitignore              # Git ignore rules
├── README.md               # Complete documentation
│
├── templates/              # Jinja2 HTML templates (Zero JavaScript)
│   ├── base.html           # Main layout, navbar, flash alerts, and footer
│   ├── index.html          # Laptop catalog dashboard, brand cards with photos, search, filter
│   ├── add_product.html    # Add brand(s) to Laptop with 10 fixed slots & photo URLs
│   ├── edit_product.html   # Pre-filled 10 slots to modify, add, or remove brands with photo preview
│   └── product_details.html# Master laptop photo & brand comparison table with thumbnail photos
│
└── static/
    ├── css/
    │   └── style.css       # Pure CSS3 stylesheet (Responsive, modern design, image styling)
    └── images/
        └── default_laptop.svg # Local vector laptop placeholder illustration
```

---

## 7. How to Run the Application

### 1. Activate Virtual Environment
In Windows PowerShell:
```powershell
venv\Scripts\activate
```

### 2. Verify MongoDB Atlas Connection
```powershell
python check_db.py
```

### 3. Run Automated Tests
```powershell
python test_catalog.py
```

### 4. Start Flask Server
```powershell
python app.py
```

### 5. Open in Web Browser
Navigate to: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 8. CRUD Operations

| Operation | HTTP Route | Method | MongoDB Query Operator | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Catalog Dashboard** | `/` | `GET` | `col.find_one()`, `col.distinct()` | Displays Laptop master card, aggregated metrics, brand cards with photos, search, brand filter, and pagination. |
| **Brand Comparison** | `/product/<id>` | `GET` | `col.find_one({"_id": id})` | Full comparison table of all brands under Laptop with thumbnail photos, specifications, and stock status. |
| **Add Brand(s)** | `/add-product` | `GET`, `POST` | `col.update_one(..., {"$push": ...})` | 10 fixed slots to add new brand models and photo URLs to the Laptop document. |
| **Manage / Edit** | `/edit-product/<id>`| `GET`, `POST` | `col.update_one(..., {"$set": ...})` | Pre-fills all 10 slots with current brands and photo URLs for editing or adding new ones. |
| **Delete Brand** | `/delete-brand/<name>` | `POST` | `col.update_one(..., {"$pull": ...})` | Removes an individual brand from the Laptop's `brands` array. |
| **Delete Catalog** | `/delete-product/<id>` | `POST` | `col.delete_one({"_id": id})` | Deletes the Laptop product document. |
| **Reset / Seed** | `/seed-sample-data` | `POST` | `col.replace_one()` | Resets to the 1 product: Laptop with 7 standard top brands and photo URLs. |

---

## 9. Zero JavaScript Audit

This project has been strictly verified to contain **NO JavaScript**:
- Total `.js` files in project: **0**
- Total `<script>` tags across templates: **0**
- All user interactions, search, filter, pagination, and form handling operate purely via HTML5 + CSS3 + Python Flask.
