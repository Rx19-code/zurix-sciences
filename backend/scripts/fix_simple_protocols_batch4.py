"""
Batch 4: Update DSIP (Delta Sleep-Inducing Peptide) protocol.
Vial 10 mg + 3 mL bac water = 3.33 mg/mL.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch4.py
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
    # ═══════════ DSIP (Delta Sleep-Inducing Peptide) ═══════════
    "dsip": {
        "overview": {
            "function": "Sleep quality, deep restorative sleep, stress relief",
            "mechanism_of_action": (
                "DSIP is a neuropeptide that modulates the sleep-wake cycle by interacting "
                "with the hypothalamus and other CNS structures. It promotes delta wave "
                "(slow-wave) sleep — the deepest, most restorative phase — and balances "
                "stress-related neurotransmitters. Also exhibits adaptogenic effects, "
                "reducing cortisol and stabilizing circadian rhythm."
            ),
            "considerations": "Best results require consistent use (several weeks). Administer in the evening — not earlier in the day to avoid daytime drowsiness.",
        },
        "benefits": [
            "Improves sleep quality and duration",
            "Promotes deep restorative sleep (delta wave / slow-wave)",
            "Reduces symptoms of insomnia and sleep disorders",
            "Enhances overall recovery and well-being",
            "Reduces stress and anxiety levels",
            "Supports circadian rhythm regulation",
        ],
        "side_effects": {
            "common": [
                "Mild headaches",
                "Drowsiness (intended effect when taken at bedtime)",
                "Injection site reactions",
            ],
            "less_common": [
                "Nausea",
                "Dizziness",
                "Vivid dreams",
            ],
            "rare": [
                "Allergic reactions",
                "Daytime grogginess if dosed too late or too high",
            ],
        },
        "timing_goals": [
            {"goal": "Sleep improvement", "timing": "Administer 30-60 minutes before bedtime"},
            {"goal": "Stress reduction", "timing": "Evening dose; can be used as needed for acute stress"},
            {"goal": "Recovery enhancement", "timing": "Before sleep to maximize overnight tissue repair"},
            {"goal": "Jet lag / circadian reset", "timing": "Dose at the new bedtime for 3-5 consecutive nights"},
        ],
        "administration": {
            "route": "Subcutaneous or Intramuscular",
            "notes": "SC is preferred for ease of self-administration. Inject 30-60 minutes before sleep. Rotate injection sites.",
        },
        "legal_status": {
            "us": "Research substance — not FDA-approved for human use. Legal for research purposes only.",
            "uk": "Controlled substance — legal only for scientific research without proper authorization.",
            "canada": "Restricted to research use; not approved for human use.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "standard": {
                "route": "Subcutaneous",
                "frequency": "Once daily, 30-60 minutes before bedtime",
            },
            "dosages": [
                {
                    "indication": "Light dose / first-time users",
                    "schedule": "1x daily before bed, SC",
                    "dose": "100 mcg (≈3 units / 0.03 mL)",
                },
                {
                    "indication": "Standard sleep support",
                    "schedule": "1x daily before bed, SC",
                    "dose": "200 mcg (≈6 units / 0.06 mL)",
                },
                {
                    "indication": "Stronger sleep / chronic insomnia",
                    "schedule": "1x daily before bed, SC",
                    "dose": "300 mcg (≈9 units / 0.09 mL)",
                },
                {
                    "indication": "Peak research dose",
                    "schedule": "1x daily before bed, SC",
                    "dose": "500 mcg (≈15 units / 0.15 mL)",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "100 mcg/night SC"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "200-300 mcg/night SC"},
                {"number": 3, "phase": "Peak / chronic insomnia (Weeks 5-8)", "dose": "300-500 mcg/night SC"},
                {"number": 4, "phase": "Off cycle (Weeks 9-10)", "dose": "Washout — 1 to 2 weeks rest"},
            ],
            "reconstitution": (
                "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 3.33 mg/mL ≈ 3333 mcg/mL). "
                "200 mcg = 0.06 mL (6 units on a 100-unit insulin syringe). "
                "For 5 mg vial with 3 mL: 1.67 mg/mL — double the volume "
                "(200 mcg = 12 units). Store at 2-8°C and protect from light."
            ),
        },
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
    print(f"BATCH 4 UPDATE — {len(UPDATES)} peptide")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found")
            continue

        update_doc = {
            "overview": payload["overview"],
            "benefits": payload["benefits"],
            "side_effects": payload["side_effects"],
            "timing_goals": payload["timing_goals"],
            "administration": payload["administration"],
            "legal_status": payload["legal_status"],
            "protocols.title": payload["protocols"]["title"],
            "protocols.standard": payload["protocols"]["standard"],
            "protocols.dosages": payload["protocols"]["dosages"],
            "protocols.phases": payload["protocols"]["phases"],
            "protocols.reconstitution": payload["protocols"]["reconstitution"],
        }

        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": update_doc},
        )
        print(f"\n[OK] {doc['name']} ({slug})")
        print(f"     Matched: {result.matched_count} | Modified: {result.modified_count}")
        print(f"     • {payload['overview']['function']}")
        print(f"     • {len(payload['benefits'])} benefits | Route: {payload['administration']['route']}")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. DSIP fully updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
