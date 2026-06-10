"""
Batch 17: Add 5 upcoming products as "Coming Soon".
- ACE-031 1mg ($90)
- FOXO4 10mg ($130)
- Semax + Selank Blend 10mg+10mg ($135)
- PTD-DBM 5mg ($100)
- GHK Basic 50mg ($75)

Products page only — NO library entries created (per user request).

Image upload note: vial images attached by user need to be moved to
/var/www/zurix/backend/product_images/ on production manually with names:
- ace-031-1mg.png
- foxo4-10mg.png
- semax-selank-blend-10mg-10mg.png
- ptd-dbm-5mg.png
- ghk-basic-50mg.png

(If images not present, generic vial placeholder will be used.)

Run on production:
  cd /var/www/zurix/backend && python3 scripts/add_upcoming_products.py
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


NEW_PRODUCTS = [
    {
        "name": "ACE-031 1mg",
        "category": "Research Peptides",
        "product_type": "ACE-031",
        "purity": "99% HPLC",
        "dosage": "1mg",
        "description": (
            "ACE-031 1mg — Soluble activin receptor type IIB (ActRIIB) decoy peptide that "
            "neutralizes myostatin and related ligands, promoting muscle hypertrophy in "
            "preclinical research. High-purity lyophilized powder for research use only."
        ),
        "price": 90.00,
        "verification_code": "ZX-ACE031",
        "storage_info": "Store at -20°C for long-term storage. Stable at 2-8°C for up to 30 days after reconstitution.",
        "batch_number": "ZX-ACE-001",
        "manufacturing_date": "2026-02-01",
        "expiry_date": "2028-02-01",
        "coa_url": "/coa/ace-031-1mg.pdf",
        "featured": False,
        "coming_soon": True,
        "image_url": "/api/images/products/ace-031-1mg.png",
    },
    {
        "name": "FOXO4 10mg",
        "category": "Research Peptides",
        "product_type": "FOXO4",
        "purity": "99% HPLC",
        "dosage": "10mg",
        "description": (
            "FOXO4-DRI 10mg — Senolytic peptide that disrupts FOXO4-p53 interaction, "
            "selectively inducing apoptosis in senescent cells. Used in longevity and "
            "anti-aging research. High-purity lyophilized powder for research use only."
        ),
        "price": 130.00,
        "verification_code": "ZX-FOXO4",
        "storage_info": "Store at -20°C for long-term storage. Stable at 2-8°C for up to 30 days after reconstitution.",
        "batch_number": "ZX-FOX-001",
        "manufacturing_date": "2026-02-01",
        "expiry_date": "2028-02-01",
        "coa_url": "/coa/foxo4-10mg.pdf",
        "featured": False,
        "coming_soon": True,
        "image_url": "/api/images/products/foxo4-10mg.png",
    },
    {
        "name": "Semax + Selank Blend 10mg+10mg",
        "category": "Research Peptides",
        "product_type": "Semax + Selank Blend",
        "purity": "99% HPLC",
        "dosage": "10mg+10mg",
        "description": (
            "Semax + Selank Blend (10mg + 10mg) — Dual nootropic peptide blend combining "
            "Semax (cognitive enhancement, focus, neuroprotection) with Selank (anxiolytic, "
            "stress modulation, mood support). Formulated for intranasal research. "
            "High-purity lyophilized powder for research use only."
        ),
        "price": 135.00,
        "verification_code": "ZX-SEMSEL",
        "storage_info": "Store at -20°C for long-term storage. Stable at 2-8°C for up to 30 days after reconstitution.",
        "batch_number": "ZX-SEMSEL-001",
        "manufacturing_date": "2026-02-01",
        "expiry_date": "2028-02-01",
        "coa_url": "/coa/semax-selank-blend.pdf",
        "featured": False,
        "coming_soon": True,
        "image_url": "/api/images/products/semax-selank-blend-10mg-10mg.png",
    },
    {
        "name": "PTD-DBM 5mg",
        "category": "Research Peptides",
        "product_type": "PTD-DBM",
        "purity": "99% HPLC",
        "dosage": "5mg",
        "description": (
            "PTD-DBM 5mg — Wnt pathway activator peptide derived from Dishevelled-binding "
            "motif. Studied for hair follicle regeneration, anti-androgenetic alopecia "
            "applications and tissue repair. High-purity lyophilized powder for research use only."
        ),
        "price": 100.00,
        "verification_code": "ZX-PTDDBM",
        "storage_info": "Store at -20°C for long-term storage. Stable at 2-8°C for up to 30 days after reconstitution.",
        "batch_number": "ZX-PTD-001",
        "manufacturing_date": "2026-02-01",
        "expiry_date": "2028-02-01",
        "coa_url": "/coa/ptd-dbm-5mg.pdf",
        "featured": False,
        "coming_soon": True,
        "image_url": "/api/images/products/ptd-dbm-5mg.png",
    },
    {
        "name": "GHK Basic 50mg",
        "category": "Research Peptides",
        "product_type": "GHK Basic",
        "purity": "99% HPLC",
        "dosage": "50mg",
        "description": (
            "GHK Basic 50mg — Glycyl-Histidyl-Lysine tripeptide without the copper carrier "
            "(non-cuprous version of GHK). Studied for tissue regeneration, gene-expression "
            "modulation, and anti-aging research without copper-related considerations. "
            "High-purity lyophilized powder for research use only."
        ),
        "price": 75.00,
        "verification_code": "ZX-GHKB",
        "storage_info": "Store at -20°C for long-term storage. Stable at 2-8°C for up to 30 days after reconstitution.",
        "batch_number": "ZX-GHKB-001",
        "manufacturing_date": "2026-02-01",
        "expiry_date": "2028-02-01",
        "coa_url": "/coa/ghk-basic-50mg.pdf",
        "featured": False,
        "coming_soon": True,
        "image_url": "/api/images/products/ghk-basic-50mg.png",
    },
]


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    if not mongo_url:
        print("ERROR: MONGO_URL not set in backend/.env")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print("=" * 60)
    print(f"Adding {len(NEW_PRODUCTS)} upcoming products (Coming Soon)")
    print("=" * 60)

    added = 0
    skipped = 0

    for prod in NEW_PRODUCTS:
        existing = await db.products.find_one({"name": prod["name"]}, {"_id": 0, "id": 1})
        if existing:
            print(f"  ⚠  {prod['name']:40} already exists (skipped)")
            skipped += 1
            continue
        prod["id"] = str(uuid.uuid4())
        await db.products.insert_one(prod.copy())
        # The insert mutates the dict (adds _id), but we already saved a clean copy in NEW_PRODUCTS
        print(f"  ✓  {prod['name']:40} added — ${prod['price']:.2f} — Coming Soon")
        added += 1

    print("\n" + "=" * 60)
    print(f"Done. Added: {added} | Skipped (already exist): {skipped}")
    print("=" * 60)
    print()
    print("⚠️  IMAGE UPLOAD NOTE:")
    print("   The product images shown on screenshots need to be uploaded manually to:")
    print("   /var/www/zurix/backend/product_images/")
    print("   With these exact filenames:")
    for prod in NEW_PRODUCTS:
        fname = prod["image_url"].split("/")[-1]
        print(f"     • {fname}")
    print("   (Until then, the cards will show a placeholder icon.)")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
