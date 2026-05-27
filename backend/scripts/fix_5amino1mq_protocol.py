"""
Migration: fix 5-Amino-1MQ to correct subcutaneous dose 200 mcg/day (5 on / 2 off).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_5amino1mq_protocol.py
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

NEW_TITLE = "Subcutaneous Protocol (vial 10 mg, 2 mL bac water = 5 mg/mL)"
NEW_STANDARD = {
    "route": "Subcutaneous",
    "frequency": "Once daily, morning on empty stomach",
}
NEW_DOSAGES = [
    {
        "indication": "Standard research dose",
        "schedule": "1x daily, morning fasted (5 days on / 2 off)",
        "dose": "200 mcg/day",
    }
]
NEW_PHASES = [
    {"number": 1, "phase": "Standard cycle (Weeks 1-6)", "dose": "200 mcg/day SC — 5 on / 2 off"},
    {"number": 2, "phase": "Off cycle (Weeks 7-8)", "dose": "Washout — 2 weeks rest"},
]
NEW_RECONSTITUTION = (
    "Reconstitute the 10 mg vial with 2 mL of bacteriostatic water "
    "(final concentration 5 mg/mL = 5000 mcg/mL). At 5 mg/mL, a 200 mcg dose "
    "= 0.04 mL (about 4 units on a 100-unit insulin syringe). "
    "Store at 2-8°C after reconstitution."
)


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    if not mongo_url:
        print("ERROR: MONGO_URL not set in backend/.env")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    doc = await db.peptide_library.find_one({"slug": "5-amino-1mq"}, {"_id": 0, "slug": 1})
    if not doc:
        print("ERROR: 5-Amino-1MQ peptide not found.")
        sys.exit(1)

    result = await db.peptide_library.update_one(
        {"slug": "5-amino-1mq"},
        {
            "$set": {
                "protocols.title": NEW_TITLE,
                "protocols.standard": NEW_STANDARD,
                "protocols.dosages": NEW_DOSAGES,
                "protocols.phases": NEW_PHASES,
                "protocols.reconstitution": NEW_RECONSTITUTION,
            }
        },
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

    updated = await db.peptide_library.find_one(
        {"slug": "5-amino-1mq"},
        {"_id": 0, "protocols.phases": 1, "protocols.dosages": 1, "protocols.title": 1},
    )
    print(f"\nTitle: {updated['protocols']['title']}")
    print("\nDosages:")
    for d in updated["protocols"]["dosages"]:
        print(f"  • {d['indication']}: {d['dose']} ({d['schedule']})")
    print("\nPhases:")
    for p in updated["protocols"]["phases"]:
        print(f"  {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\nDone. 5-Amino-1MQ corrected to 200 mcg/day SC.")


if __name__ == "__main__":
    asyncio.run(main())
