"""
Add two new products to catalog: Epitalon 10mg and Adamax 10mg.
Both created as ACTIVE (not coming_soon), ready for verification codes to be imported.

Run:
  cd /var/www/zurix/backend && python3 scripts/add_epitalon_adamax.py
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient


PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Epitalon 10mg",
        "category": "Research Peptides",
        "product_type": "Epitalon",
        "purity": "≥99% HPLC",
        "dosage": "10mg",
        "description": (
            "Epitalon (Epithalon) 10mg — tetrapeptide (Ala-Glu-Asp-Gly) researched for "
            "telomerase activation, circadian rhythm modulation, and longevity applications. "
            "For laboratory research use only."
        ),
        "price": 45.00,
        "verification_code": "ZX-EPIT10",
        "storage_info": "Store lyophilized at -20°C. Stable 2-8°C for 30 days after reconstitution.",
        "batch_number": "ZX-EPIT-B01",
        "manufacturing_date": "2026-01-15",
        "expiry_date": "2028-01-15",
        "coa_url": "/coa/epitalon-10mg.pdf",
        "featured": False,
        "image_url": "/api/images/products/epitalon-10mg.png",
        "coming_soon": False,
        "out_of_stock": False,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Adamax 10mg",
        "category": "Research Peptides",
        "product_type": "Adamax",
        "purity": "≥99% HPLC",
        "dosage": "10mg",
        "description": (
            "Adamax 10mg — research peptide for laboratory investigation. "
            "For laboratory research use only."
        ),
        "price": 45.00,
        "verification_code": "ZX-ADAM10",
        "storage_info": "Store lyophilized at -20°C. Stable 2-8°C for 30 days after reconstitution.",
        "batch_number": "ZX-ADAM-B01",
        "manufacturing_date": "2026-01-15",
        "expiry_date": "2028-01-15",
        "coa_url": "/coa/adamax-10mg.pdf",
        "featured": False,
        "image_url": "/api/images/products/adamax-10mg.png",
        "coming_soon": False,
        "out_of_stock": False,
    },
]


async def main():
    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print("=" * 60)
    print(f"Adding {len(PRODUCTS)} new products")
    print("=" * 60)

    for p in PRODUCTS:
        existing = await db.products.find_one({"name": p["name"]}, {"_id": 0, "id": 1, "name": 1})
        if existing:
            update = {k: v for k, v in p.items() if k != "id"}
            await db.products.update_one({"name": p["name"]}, {"$set": update})
            print(f"[UPDATED] {p['name']} (id={existing['id']})")
        else:
            await db.products.insert_one(p.copy())
            print(f"[INSERTED] {p['name']} (id={p['id']})  price=${p['price']:.2f}")

    total = await db.products.count_documents({})
    active = await db.products.count_documents({"coming_soon": {"$ne": True}, "out_of_stock": {"$ne": True}})
    print("-" * 60)
    print(f"Total products: {total}  |  Active: {active}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
