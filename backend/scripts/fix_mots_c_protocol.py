"""
One-off migration: fix MOTS-c protocol doses to align with clinical dose
(5–10 mg/week, split into 2-3 injections, cycle 4-6 weeks + 2-4 weeks off).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_mots_c_protocol.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Make backend importable
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient

NEW_DOSAGES = [
    {
        "indication": "Initial titration (low dose)",
        "schedule": "Subcutaneous, 2x per week (e.g. Mon/Thu)",
        "dose": "2.5 mg per injection (5 mg/week)",
    },
    {
        "indication": "Standard research dose",
        "schedule": "Subcutaneous, 3x per week (e.g. Mon/Wed/Fri)",
        "dose": "2.5 mg per injection (7.5 mg/week)",
    },
    {
        "indication": "Peak research dose",
        "schedule": "Subcutaneous, 3x per week",
        "dose": "3.3 mg per injection (10 mg/week)",
    },
    {
        "indication": "Maintenance after cycle",
        "schedule": "Subcutaneous, 2x per week",
        "dose": "2.5 mg per injection (5 mg/week)",
    },
]

NEW_PHASES = [
    {"number": 1, "phase": "Initial titration (Weeks 1-2)", "dose": "5 mg/week (split 2 injections)"},
    {"number": 2, "phase": "Standard dose (Weeks 3-4)", "dose": "7.5 mg/week (split 3 injections)"},
    {"number": 3, "phase": "Peak research dose (Weeks 5-6)", "dose": "10 mg/week (split 3 injections)"},
    {"number": 4, "phase": "Off cycle (Weeks 7-10)", "dose": "Washout — 2 to 4 weeks rest"},
]


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    if not mongo_url:
        print("ERROR: MONGO_URL not set in backend/.env")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    doc = await db.peptide_library.find_one({"slug": "mots-c"}, {"_id": 0, "slug": 1})
    if not doc:
        print("ERROR: MOTS-c peptide not found in peptide_library collection.")
        sys.exit(1)

    result = await db.peptide_library.update_one(
        {"slug": "mots-c"},
        {
            "$set": {
                "protocols.dosages": NEW_DOSAGES,
                "protocols.phases": NEW_PHASES,
            }
        },
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    # Verify
    updated = await db.peptide_library.find_one(
        {"slug": "mots-c"},
        {"_id": 0, "protocols.phases": 1, "protocols.dosages": 1},
    )
    print("\nUpdated phases:")
    for p in updated["protocols"]["phases"]:
        print(f"  {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\nDone. MOTS-c protocol fixed.")


if __name__ == "__main__":
    asyncio.run(main())
