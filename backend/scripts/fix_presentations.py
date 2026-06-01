"""
Batch 16: Align peptide_library.presentations with actually sold products.
Removes vial sizes that don't exist in the store.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_presentations.py
"""
import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient


# slug → list of actually sold vial sizes (preserve original order/case)
UPDATES = {
    "5-amino-1mq": ["10mg"],
    "mots-c": ["10mg"],
    "dsip": ["5mg"],
    "tb-500": ["10mg"],
    "bpc-157": ["10mg"],
    "bpc-157-for-neuroprotection": ["10mg"],
    "sermorelin": ["10mg"],
    "kpv": ["10mg"],
    "retatrutide": ["10mg", "40mg"],
    "glutathione": ["1500mg"],
    "slu-pp-332": ["500mcg"],
    "bacteriostatic-water": ["3ml"],
    "tesamorelin": ["10mg"],
    "ipamorelin": ["10mg"],
    "hgh-fragment-176-191": ["5mg"],
    "hgh": ["10iu"],
    "ahk-cu": ["100mg"],
    "ghk-cu": ["50mg", "100mg"],
    "cartalax": ["20mg"],
    "ghk-cu-kpv-blend": ["50mg+20mg"],
    "klow-blend": ["80mg"],
    "glow-blend": ["70mg"],
    "thymosin-alpha-1": ["5mg"],
    "selank": ["10mg"],
    "semax": ["10mg"],
    "kisspeptin": ["10mg"],
    "pt-141": ["10mg"],
    "oxytocin": ["10mg"],
    "nad-plus-": ["500mg"],
    "aod-9604": ["5mg"],
    "igf-1-lr3": ["1mg"],
    "cjc-1295-dac": ["5mg"],
    "tirzepatide": ["10mg", "15mg", "20mg", "60mg"],
}


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    if not mongo_url:
        print("ERROR: MONGO_URL not set in backend/.env")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print("=" * 60)
    print(f"BATCH 16 — Align presentations with actual sold products")
    print("=" * 60)

    changed = 0
    skipped = 0
    not_found = 0

    for slug, presentations in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1, "presentations": 1})
        if not doc:
            print(f"  ❌ {slug:35} NOT FOUND")
            not_found += 1
            continue
        current = doc.get("presentations") or []
        if current == presentations:
            print(f"  ✓  {doc['name']:30} already correct: {presentations}")
            skipped += 1
            continue
        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": {"presentations": presentations}},
        )
        print(f"  ⚙  {doc['name']:30} {current} → {presentations} (matched={result.matched_count})")
        changed += 1

    client.close()
    print("\n" + "=" * 60)
    print(f"Done. Changed: {changed} | Already OK: {skipped} | Not found: {not_found}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
