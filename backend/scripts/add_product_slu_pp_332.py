"""
Add new product: SLU-PP-332 500mcg 25 tablets (Coming Soon).
"""
import asyncio
import os
import uuid
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


PRODUCT = {
    "id": str(uuid.uuid4()),
    "name": "SLU-PP-332 500mcg",
    "category": "Research Peptides",
    "product_type": "SLU-PP-332",
    "purity": "99% HPLC",
    "dosage": "500mcg x 25 tablets",
    "description": "SLU-PP-332 500mcg - 25 tablets. ERR\u03b1 agonist research compound for laboratory research purposes only. Coming soon.",
    "price": 0.0,
    "verification_code": "ZX-SLUPP332",
    "storage_info": "Store in a cool, dry place. Keep tablets in original packaging until use.",
    "batch_number": "ZX-SLUPP-PREORDER",
    "manufacturing_date": "2026-03-01",
    "expiry_date": "2028-03-01",
    "coa_url": "/coa/slu-pp-332-500mcg.pdf",
    "featured": False,
    "image_url": None,
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
        print(f"UPDATED existing product: {PRODUCT['name']}")
    else:
        await db.products.insert_one(PRODUCT.copy())
        print(f"INSERTED new product: {PRODUCT['name']} (id={PRODUCT['id']})")

    total = await db.products.count_documents({})
    coming_soon = await db.products.count_documents({"coming_soon": True})
    print(f"Total products: {total}  |  Coming soon: {coming_soon}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
