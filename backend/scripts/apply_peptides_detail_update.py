"""
PRODUCTION SEED APPLIER
Run this on the production server after git pull.

Usage on production:
    cd /path/to/app/backend
    python3 scripts/apply_peptides_detail_update.py

This script updates ONLY the 9 peptides present in seed_peptides_detail_update.json
(Ipamorelin, TB-500, Semax, Selank, KPV, CJC-1295 DAC, Tesamorelin, BPC-157, GHK-Cu).
It does NOT touch any other peptide or collection.
"""
import asyncio
import json
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

FIELDS_TO_UPDATE = [
    "background",
    "clinical_applications",
    "side_effects",
    "contraindications",
    "interactions",
]


async def main():
    seed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seed_peptides_detail_update.json")
    if not os.path.exists(seed_path):
        print(f"ERROR: seed file not found at {seed_path}")
        sys.exit(1)

    with open(seed_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    print(f"Target DB: {os.environ['DB_NAME']}")
    print(f"Loaded {len(docs)} peptides from seed file.\n")

    updated = 0
    missing = 0
    for d in docs:
        slug = d["slug"]
        existing = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "name": 1})
        if not existing:
            print(f"  SKIP (not found): {slug}")
            missing += 1
            continue
        update_fields = {k: d[k] for k in FIELDS_TO_UPDATE if k in d}
        await db.peptide_library.update_one({"slug": slug}, {"$set": update_fields})
        print(f"  UPDATED: {existing['name']} ({slug})")
        updated += 1

    print(f"\nDone. Updated: {updated}  |  Missing: {missing}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
