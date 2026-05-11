"""
Add 4 new "Coming Soon" products:
- GSH Glutathione 1500mg
- Sermorelin 10mg
- BPC-157 + TB-500 Blend 10mg+10mg
- DSIP 5mg
"""
import asyncio
import os
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "GSH Glutathione 1500mg",
        "category": "Research Peptides",
        "product_type": "Glutathione",
        "purity": "99% HPLC",
        "dosage": "1500mg",
        "description": "GSH Glutathione 1500mg - Master antioxidant tripeptide for laboratory research purposes only. Coming soon.",
        "price": 0.0,
        "verification_code": "ZX-GSH1500",
        "storage_info": "Store at -20\u00b0C for long-term storage. Stable at 2-8\u00b0C for up to 30 days after reconstitution.",
        "batch_number": "ZX-GSH-PREORDER",
        "manufacturing_date": "2026-03-01",
        "expiry_date": "2028-03-01",
        "coa_url": "/coa/gsh-glutathione-1500mg.pdf",
        "featured": False,
        "image_url": None,
        "coming_soon": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Sermorelin 10mg",
        "category": "Research Peptides",
        "product_type": "Sermorelin",
        "purity": "99% HPLC",
        "dosage": "10mg",
        "description": "Sermorelin 10mg - GHRH analog research compound for laboratory research purposes only. Coming soon.",
        "price": 0.0,
        "verification_code": "ZX-SERMO10",
        "storage_info": "Store at -20\u00b0C for long-term storage. Stable at 2-8\u00b0C for up to 30 days after reconstitution.",
        "batch_number": "ZX-SERMO-PREORDER",
        "manufacturing_date": "2026-03-01",
        "expiry_date": "2028-03-01",
        "coa_url": "/coa/sermorelin-10mg.pdf",
        "featured": False,
        "image_url": None,
        "coming_soon": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "BPC-157 + TB-500 Blend 10mg+10mg",
        "category": "Research Peptides",
        "product_type": "BPC-157/TB-500 Blend",
        "purity": "99% HPLC",
        "dosage": "10mg + 10mg",
        "description": "BPC-157 + TB-500 Blend 10mg+10mg - Premium healing and recovery peptide blend for laboratory research purposes only. Coming soon.",
        "price": 0.0,
        "verification_code": "ZX-BPCTB10",
        "storage_info": "Store at -20\u00b0C for long-term storage. Stable at 2-8\u00b0C for up to 30 days after reconstitution.",
        "batch_number": "ZX-BPCTB-PREORDER",
        "manufacturing_date": "2026-03-01",
        "expiry_date": "2028-03-01",
        "coa_url": "/coa/bpc-tb500-blend.pdf",
        "featured": False,
        "image_url": None,
        "coming_soon": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "DSIP 5mg",
        "category": "Research Peptides",
        "product_type": "DSIP",
        "purity": "99% HPLC",
        "dosage": "5mg",
        "description": "DSIP 5mg - Delta Sleep-Inducing Peptide research compound for laboratory research purposes only. Coming soon.",
        "price": 0.0,
        "verification_code": "ZX-DSIP5",
        "storage_info": "Store at -20\u00b0C for long-term storage. Stable at 2-8\u00b0C for up to 30 days after reconstitution.",
        "batch_number": "ZX-DSIP-PREORDER",
        "manufacturing_date": "2026-03-01",
        "expiry_date": "2028-03-01",
        "coa_url": "/coa/dsip-5mg.pdf",
        "featured": False,
        "image_url": None,
        "coming_soon": True,
    },
]


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    for product in PRODUCTS:
        existing = await db.products.find_one({"name": product["name"]}, {"_id": 0})
        if existing:
            await db.products.update_one(
                {"name": product["name"]},
                {"$set": {k: v for k, v in product.items() if k != "id"}},
            )
            print(f"UPDATED: {product['name']}")
        else:
            await db.products.insert_one(product.copy())
            print(f"INSERTED: {product['name']} (id={product['id']})")

    total = await db.products.count_documents({})
    coming_soon = await db.products.count_documents({"coming_soon": True})
    print(f"\nTotal products: {total}  |  Coming soon: {coming_soon}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
