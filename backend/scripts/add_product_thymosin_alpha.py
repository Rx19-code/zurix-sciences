"""
Add new "Coming Soon" product: Thymosin Alpha 5mg (with image).
"""
import asyncio
import os
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


PRODUCT = {
    "id": str(uuid.uuid4()),
    "name": "Thymosin Alpha 5mg",
    "category": "Research Peptides",
    "product_type": "Thymosin Alpha",
    "purity": "99% HPLC",
    "dosage": "5mg",
    "description": "Thymosin Alpha 5mg - Immune-modulating peptide research compound for laboratory research purposes only. Coming soon.",
    "price": 0.0,
    "verification_code": "ZX-THYMA5",
    "storage_info": "Store at -20\u00b0C for long-term storage. Stable at 2-8\u00b0C for up to 30 days after reconstitution.",
    "batch_number": "ZX-THYMA-PREORDER",
    "manufacturing_date": "2026-03-01",
    "expiry_date": "2028-03-01",
    "coa_url": "/coa/thymosin-alpha-5mg.pdf",
    "featured": False,
    "image_url": "/api/images/products/thymosin-alpha-5mg.png",
    "coming_soon": True,
}


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    existing = await db.products.find_one({"name": PRODUCT["name"]}, {"_id": 0})
    if existing:
        await db.products.update_one(
            {"name": PRODUCT["name"]},
            {"$set": {k: v for k, v in PRODUCT.items() if k != "id"}},
        )
        print(f"UPDATED existing: {PRODUCT['name']}")
    else:
        await db.products.insert_one(PRODUCT.copy())
        print(f"INSERTED: {PRODUCT['name']} (id={PRODUCT['id']})")

    total = await db.products.count_documents({})
    coming = await db.products.count_documents({"coming_soon": True})
    print(f"Total: {total}  |  Coming soon: {coming}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
