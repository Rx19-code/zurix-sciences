"""
Batch 14: Adjust HGH 191AA to 2-3 IU/day target (more conservative protocol).
Conversion: 1 IU ≈ 333 mcg (somatropin 191AA standard).
Vial 10 IU = 3.33 mg, reconstitute with 3 mL → 1.11 mg/mL.
At this concentration: 1 unit ≈ 11.1 mcg → 2 IU (666 mcg) = 60 units; 3 IU (1000 mcg) = 90 units.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch14.py
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


UPDATES = {
    "hgh": {
        "considerations": (
            "Target research dose: 2-3 IU/day (≈666-1000 mcg/day). "
            "Conservative gradual titration from 1 IU → 2 IU → 3 IU over 4 weeks "
            "minimizes side effects (water retention, joint discomfort, glucose changes). "
            "5 on / 2 off (Mon-Fri) is the most common community schedule. "
            "Bedtime dose mimics physiological GH pulse during sleep. "
            "Conversion: 1 IU ≈ 333 mcg of 191aa somatropin."
        ),
        "timing_goals": [
            {"goal": "Standard research dose", "timing": "2-3 IU/day SC at bedtime — 5 on / 2 off"},
            {"goal": "Physiological GH mimicry", "timing": "Inject at bedtime to mimic natural GH peak during sleep"},
            {"goal": "Fat loss focus", "timing": "Morning fasted SC, 5 on / 2 off cycling"},
            {"goal": "Recovery / lean mass", "timing": "Daily bedtime for 8-12 weeks, then 4+ weeks off"},
            {"goal": "Gradual titration", "timing": "Week 1: 1 IU/day → Week 2: 1.5 IU → Week 3: 2 IU → Week 4+: 2-3 IU"},
        ],
        "protocols.title": "HGH 191AA Research Protocol (vial 10 IU = 3.33 mg, 3 mL bac water = 1.11 mg/mL)",
        "protocols.standard": {
            "route": "Subcutaneous",
            "frequency": "Once daily at bedtime — 5 on / 2 off",
        },
        "protocols.dosages": [
            {
                "indication": "Tolerance / initiation",
                "schedule": "1x daily SC at bedtime — 5 on / 2 off",
                "dose": "1 IU/day ≈ 333 mcg (30 units / 0.30 mL)",
            },
            {
                "indication": "Standard research dose (recovery, anti-aging)",
                "schedule": "1x daily SC at bedtime — 5 on / 2 off",
                "dose": "2 IU/day ≈ 666 mcg (60 units / 0.60 mL)",
            },
            {
                "indication": "Enhanced research dose (body composition)",
                "schedule": "1x daily SC at bedtime — 5 on / 2 off",
                "dose": "3 IU/day ≈ 1000 mcg (90 units / 0.90 mL)",
            },
            {
                "indication": "Split dose (steadier IGF-1 levels)",
                "schedule": "AM + PM SC, 5 on / 2 off",
                "dose": "1 IU morning + 1 IU bedtime (2 IU/day total = 60 units total)",
            },
        ],
        "protocols.phases": [
            {"number": 1, "phase": "Initiation (Week 1)", "dose": "1 IU/day SC bedtime (≈30 units / 333 mcg)"},
            {"number": 2, "phase": "Build-up (Week 2)", "dose": "1.5 IU/day SC bedtime (≈45 units / 500 mcg)"},
            {"number": 3, "phase": "Standard (Weeks 3-4)", "dose": "2 IU/day SC bedtime (≈60 units / 666 mcg)"},
            {"number": 4, "phase": "Peak (Weeks 5-12)", "dose": "2-3 IU/day SC bedtime — 5 on / 2 off (60-90 units)"},
            {"number": 5, "phase": "Off cycle (4+ weeks)", "dose": "Washout — restore receptor sensitivity"},
        ],
        "protocols.reconstitution": (
            "Reconstitute the 10 IU (3.33 mg) vial with 3.0 mL of bacteriostatic water "
            "(final concentration ~1.11 mg/mL ≈ 1111 mcg/mL). "
            "At this concentration on a U-100 insulin syringe: "
            "1 unit = 0.01 mL ≈ 11.1 mcg. "
            "Conversion: 1 IU ≈ 333 mcg of 191aa somatropin. "
            "Doses for the 2-3 IU/day research target: "
            "1 IU = 30 units (0.30 mL); 1.5 IU = 45 units; 2 IU = 60 units (0.60 mL); "
            "2.5 IU = 75 units; 3 IU = 90 units (0.90 mL). "
            "Lyophilized vial: store at −20°C. Reconstituted: refrigerate at 2-8°C; "
            "AVOID freeze-thaw cycles (denatures protein). Protect from light. Do NOT shake."
        ),
        "protocols.reconstitution_steps": [
            "Draw 3.0 mL of bacteriostatic water with a sterile syringe",
            "Inject slowly down the side of the vial wall — avoid foaming",
            "Gently swirl or roll until dissolved — do NOT shake (preserves protein structure)",
            "Label with reconstitution date and refrigerate at 2-8°C, protected from light",
            "Standard daily dose: 2 IU = 60 units (0.60 mL); 3 IU = 90 units (0.90 mL)",
            "Inject SC at bedtime to mimic physiological GH peak — 5 on / 2 off (Mon-Fri)",
            "Allow vial to reach room temperature before opening to minimize condensation",
        ],
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
    print(f"BATCH 14 UPDATE — HGH 191AA adjusted to 2-3 IU/day target")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1, "overview": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found")
            continue

        # Build $set carefully — keep the existing overview but update considerations field inside it
        overview = doc.get("overview", {})
        overview["considerations"] = payload["considerations"]

        update_doc = {
            "overview": overview,
            "timing_goals": payload["timing_goals"],
            "protocols.title": payload["protocols.title"],
            "protocols.standard": payload["protocols.standard"],
            "protocols.dosages": payload["protocols.dosages"],
            "protocols.phases": payload["protocols.phases"],
            "protocols.reconstitution": payload["protocols.reconstitution"],
            "protocols.reconstitution_steps": payload["protocols.reconstitution_steps"],
        }

        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": update_doc},
        )
        print(f"\n[OK] {doc['name']} ({slug})")
        print(f"     Matched: {result.matched_count} | Modified: {result.modified_count}")
        print(f"     Target range: 2-3 IU/day (≈666-1000 mcg)")
        print(f"     Conversion: 1 IU ≈ 333 mcg | 2 IU = 60 units | 3 IU = 90 units")
        print(f"     • Phases:")
        for p in payload["protocols.phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. HGH 191AA adjusted to conservative 2-3 IU/day target.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
