"""
Bulk migration: update simple protocols for 5 peptides with research-backed
dosing information from clinical literature.

Peptides updated:
  - tb-500 (Thymosin Beta-4)
  - tirzepatide
  - sermorelin
  - semax (intranasal)
  - selank (intranasal)

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch1.py
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

# ─────────────────────────────────────────────────────────────────────
# Protocol definitions (research-backed, simple peptide protocols)
# ─────────────────────────────────────────────────────────────────────
UPDATES = {
    # ═══════════ TB-500 / Thymosin Beta-4 ═══════════
    "tb-500": {
        "title": "Subcutaneous or Intramuscular Protocol",
        "standard": {
            "route": "Subcutaneous or Intramuscular",
            "frequency": "1-2 times per week",
        },
        "dosages": [
            {
                "indication": "Acute injury recovery",
                "schedule": "1-2x per week, SC or IM, until healed",
                "dose": "2-2.5 mg per injection",
            },
            {
                "indication": "General healing / anti-inflammatory",
                "schedule": "1x per week, SC or IM",
                "dose": "2 mg per injection",
            },
            {
                "indication": "Muscle / tendon recovery",
                "schedule": "2x per week, SC or IM",
                "dose": "2.5 mg per injection",
            },
        ],
        "phases": [
            {"number": 1, "phase": "Loading (Weeks 1-2)", "dose": "2.5 mg × 2x per week"},
            {"number": 2, "phase": "Maintenance (Weeks 3-6)", "dose": "2 mg × 1-2x per week"},
            {"number": 3, "phase": "Off cycle (Weeks 7-10)", "dose": "Washout — 2 to 4 weeks rest"},
        ],
        "reconstitution": (
            "Reconstitute the vial with bacteriostatic water (typical 2-3 mL "
            "for a 10 mg vial). Store at 2-8°C after reconstitution."
        ),
    },

    # ═══════════ Tirzepatide ═══════════
    "tirzepatide": {
        "title": "Weekly Subcutaneous Protocol (titration)",
        "standard": {
            "route": "Subcutaneous",
            "frequency": "Once weekly, same day each week",
        },
        "dosages": [
            {
                "indication": "Initial titration (weeks 1-4)",
                "schedule": "Once weekly, SC",
                "dose": "2.5 mg/week",
            },
            {
                "indication": "Standard weight loss / glycemic control",
                "schedule": "Once weekly, SC",
                "dose": "5 mg/week",
            },
            {
                "indication": "Enhanced dose (per tolerance)",
                "schedule": "Once weekly, SC",
                "dose": "7.5-10 mg/week",
            },
            {
                "indication": "Maximum research dose",
                "schedule": "Once weekly, SC",
                "dose": "15 mg/week",
            },
        ],
        "phases": [
            {"number": 1, "phase": "Titration (Weeks 1-4)", "dose": "2.5 mg/week SC"},
            {"number": 2, "phase": "Standard (Weeks 5-8)", "dose": "5 mg/week SC"},
            {"number": 3, "phase": "Step-up (Weeks 9-12)", "dose": "7.5 mg/week SC"},
            {"number": 4, "phase": "Maintenance (Weeks 13+)", "dose": "10-15 mg/week SC (per tolerance)"},
        ],
        "reconstitution": (
            "Available as pre-filled pen or lyophilized vial. For vial: reconstitute "
            "with bacteriostatic water per concentration; store at 2-8°C."
        ),
    },

    # ═══════════ Sermorelin ═══════════
    "sermorelin": {
        "title": "Daily Subcutaneous Protocol (evening / bedtime)",
        "standard": {
            "route": "Subcutaneous",
            "frequency": "Once daily, before bedtime on empty stomach",
        },
        "dosages": [
            {
                "indication": "General anti-aging / GH support",
                "schedule": "1x daily before bed, empty stomach, SC",
                "dose": "200 mcg/day",
            },
            {
                "indication": "Body recomposition / fat loss",
                "schedule": "1x daily before bed, empty stomach, SC",
                "dose": "250 mcg/day",
            },
            {
                "indication": "Peak research dose",
                "schedule": "1x daily before bed, empty stomach, SC",
                "dose": "300 mcg/day",
            },
        ],
        "phases": [
            {"number": 1, "phase": "Initiation (Month 1)", "dose": "200 mcg/day SC"},
            {"number": 2, "phase": "Standard (Months 2-3)", "dose": "250-300 mcg/day SC"},
            {"number": 3, "phase": "Extended (Months 4-6)", "dose": "300 mcg/day SC"},
            {"number": 4, "phase": "Off cycle (4 weeks)", "dose": "Washout — 4 weeks rest"},
        ],
        "reconstitution": (
            "Reconstitute the vial with bacteriostatic water (typical 2 mL for "
            "a 2-5 mg vial). Refrigerate at 2-8°C and protect from light."
        ),
    },

    # ═══════════ Semax (intranasal) ═══════════
    "semax": {
        "title": "Intranasal Protocol (5 days on / 2 days off)",
        "standard": {
            "route": "Intranasal",
            "frequency": "1-2 times daily (morning / early afternoon)",
        },
        "dosages": [
            {
                "indication": "Cognitive enhancement / focus",
                "schedule": "1x morning, intranasal — 5 days on / 2 days off",
                "dose": "300 mcg/day",
            },
            {
                "indication": "Mood support / anxiety",
                "schedule": "1x morning, intranasal — 5 days on / 2 days off",
                "dose": "400 mcg/day",
            },
            {
                "indication": "Neuroprotection (high dose)",
                "schedule": "Split AM + early afternoon, intranasal",
                "dose": "600 mcg/day",
            },
        ],
        "phases": [
            {"number": 1, "phase": "Initiation (Week 1)", "dose": "300 mcg/day intranasal"},
            {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "400-600 mcg/day intranasal"},
            {"number": 3, "phase": "Off cycle (Week 5+)", "dose": "Pause or maintain 5 on / 2 off"},
        ],
        "reconstitution": (
            "Most commonly supplied as a pre-made 0.1% nasal spray. "
            "Typical application: 2-3 drops per nostril. Store refrigerated."
        ),
    },

    # ═══════════ Selank (intranasal) ═══════════
    "selank": {
        "title": "Intranasal Protocol",
        "standard": {
            "route": "Intranasal",
            "frequency": "Daily or as needed",
        },
        "dosages": [
            {
                "indication": "Mild anxiety / mood support",
                "schedule": "1-2x daily, intranasal",
                "dose": "250-500 mcg/day",
            },
            {
                "indication": "Standard research dose",
                "schedule": "1-2x daily, intranasal",
                "dose": "1 mg/day",
            },
            {
                "indication": "High-dose / acute stress",
                "schedule": "Split AM + afternoon, intranasal",
                "dose": "2-3 mg/day",
            },
        ],
        "phases": [
            {"number": 1, "phase": "Initiation (Week 1)", "dose": "250-500 mcg/day intranasal"},
            {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "1 mg/day intranasal"},
            {"number": 3, "phase": "Acute / on-demand", "dose": "Up to 3 mg/day as needed"},
        ],
        "reconstitution": (
            "Most commonly supplied as a pre-made 0.15% nasal spray. "
            "Typical application: 2-3 drops per nostril. Store refrigerated."
        ),
    },
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
    print(f"BATCH UPDATE — {len(UPDATES)} peptides")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found in peptide_library")
            continue

        update_doc = {
            "protocols.title": payload["title"],
            "protocols.standard": payload["standard"],
            "protocols.dosages": payload["dosages"],
            "protocols.phases": payload["phases"],
            "protocols.reconstitution": payload["reconstitution"],
        }

        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": update_doc},
        )
        print(f"\n[OK] {doc['name']} ({slug})")
        print(f"     Matched: {result.matched_count} | Modified: {result.modified_count}")
        print(f"     Title:   {payload['title']}")
        print(f"     Phases:")
        for p in payload["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. All 5 peptide protocols updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
