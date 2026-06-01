"""
Batch 13: CJC-1295 DAC (5 mg vial).
- Half-life: 6-8 days (DAC = Drug Affinity Complex, binds to albumin)
- Standard dose: 600 mcg once weekly, OR split 300 mcg × 2/week
- Empty stomach, 2-3h after last meal
- Vial 5 mg + 3 mL bac water = 1.67 mg/mL

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch13.py
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
    "cjc-1295-dac": {
        "overview": {
            "function": "Sustained GH/IGF-1 elevation, anti-aging, recovery, body composition",
            "mechanism_of_action": (
                "CJC-1295 with DAC (Drug Affinity Complex) is a long-acting synthetic GHRH "
                "(Growth Hormone-Releasing Hormone) analog. The DAC modification binds the "
                "peptide to serum albumin, dramatically extending its half-life from minutes "
                "(native GHRH) to 6-8 days. It stimulates the anterior pituitary to release "
                "endogenous GH in a sustained manner, producing prolonged elevation of GH and "
                "IGF-1 levels. Unlike native CJC-1295 (no DAC), which is dosed daily, the DAC "
                "version requires only weekly (or twice-weekly) administration."
            ),
            "considerations": (
                "Always administer on EMPTY STOMACH — at least 2-3 hours after the last meal "
                "to avoid blunting GH response (carbs/sugars suppress GH release). Often stacked "
                "with Ipamorelin or another GHRP for synergistic GH pulse. Long half-life means "
                "side effects (water retention, tingling) can also persist longer."
            ),
        },
        "benefits": [
            "Sustained elevation of GH and IGF-1 for days after single injection",
            "Convenient weekly dosing schedule (vs daily for non-DAC version)",
            "Supports lean muscle growth and body recomposition",
            "Enhanced recovery from training and tissue repair",
            "Improved sleep quality (deeper REM and slow-wave sleep)",
            "Anti-aging effects via natural GH/IGF-1 elevation",
            "Increased protein synthesis and nitrogen retention",
            "Skin elasticity and connective tissue support",
            "Stacks synergistically with Ipamorelin (combined daily GHRP + weekly GHRH)",
        ],
        "side_effects": {
            "common": [
                "Water retention / mild edema (especially first weeks)",
                "Tingling or numbness (hands/feet) — usually transient",
                "Flushing or warmth sensation post-injection",
                "Injection site reactions",
            ],
            "less_common": [
                "Mild headache",
                "Fatigue / lethargy",
                "Vivid dreams (related to deeper sleep)",
                "Mild blood pressure changes",
            ],
            "rare": [
                "Glucose metabolism effects (monitor in extended protocols)",
                "Allergic reactions",
                "Persistent edema requiring dose reduction",
            ],
        },
        "timing_goals": [
            {"goal": "Sustained GH/IGF-1 elevation", "timing": "Once weekly, same day each week — empty stomach, ≥2-3h after last meal"},
            {"goal": "Split-dose for steadier levels", "timing": "300 mcg × 2x weekly (e.g. Mon/Thu) — empty stomach"},
            {"goal": "Stack with Ipamorelin", "timing": "Combine in same syringe weekly OR keep CJC-DAC weekly + Ipamorelin daily before bed"},
            {"goal": "Minimize water retention", "timing": "Start at 300 mcg/week and titrate upward over 4 weeks"},
            {"goal": "Sleep quality", "timing": "Inject at bedtime on empty stomach for amplified deep sleep effect"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": (
                "Inject SC into abdomen, thigh, or upper arm. CRITICAL: must be on empty "
                "stomach (≥2-3h after last meal, ideally before bed). Avoid carbs/sugars for "
                "2h after dose. Rotate sites. Use insulin syringe. Store reconstituted vial "
                "refrigerated at 2-8°C."
            ),
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for human use. Legal for research purposes.",
            "uk": "Classified as research chemical; not approved for medical use.",
            "canada": "Restricted to research use; not approved for medical treatments.",
            "wada": "BANNED by WADA — prohibited in competitive sports.",
        },
        "protocols": {
            "title": "Weekly Subcutaneous Protocol (vial 5 mg, 3 mL bac water = 1.67 mg/mL)",
            "standard": {
                "route": "Subcutaneous",
                "frequency": "Once weekly (or split 2x/week) — empty stomach",
            },
            "dosages": [
                {
                    "indication": "Initiation / sensitive users",
                    "schedule": "Once weekly, SC, empty stomach",
                    "dose": "300 mcg/week (≈18 units / 0.18 mL)",
                },
                {
                    "indication": "Standard research dose",
                    "schedule": "Once weekly, SC, empty stomach",
                    "dose": "600 mcg/week (≈36 units / 0.36 mL)",
                },
                {
                    "indication": "Split-dose for steadier levels",
                    "schedule": "2x per week (e.g. Mon/Thu), SC, empty stomach",
                    "dose": "300 mcg per dose (≈18 units per injection)",
                },
                {
                    "indication": "Advanced research dose",
                    "schedule": "Once or twice weekly, SC, empty stomach",
                    "dose": "1-2 mg/week (≈60-120 units total per week)",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "300 mcg/week SC (single weekly dose)"},
                {"number": 2, "phase": "Build-up (Weeks 3-4)", "dose": "600 mcg/week SC (single dose OR split 300×2)"},
                {"number": 3, "phase": "Standard cycle (Weeks 5-12)", "dose": "600 mcg/week SC (or 1-2 mg/week advanced)"},
                {"number": 4, "phase": "Off cycle (4+ weeks)", "dose": "Washout — restore pituitary sensitivity"},
            ],
            "reconstitution": (
                "Reconstitute the 5 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 1.67 mg/mL ≈ 1667 mcg/mL). "
                "300 mcg = 0.18 mL (18 units on a 100-unit insulin syringe). "
                "600 mcg = 0.36 mL (36 units). "
                "1 mg = 0.60 mL (60 units). "
                "Long-acting — entire vial covers approximately 8 weeks at 600 mcg/week. "
                "Store at 2-8°C and protect from light. Do not shake."
            ),
            "reconstitution_steps": [
                "Wipe both vials with alcohol swabs",
                "Aspirate 3.0 mL of bacteriostatic water with a sterile syringe",
                "Inject slowly down the side of the CJC-1295 DAC vial",
                "Gently swirl until fully dissolved — do NOT shake (peptide is delicate)",
                "Label with reconstitution date and refrigerate at 2-8°C, protected from light",
                "Standard weekly dose: 600 mcg = 36 units (0.36 mL) on a 100u insulin syringe",
                "Inject on empty stomach, ≥2-3h after last meal (ideally before bed)",
            ],
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
    print(f"BATCH 13 UPDATE — CJC-1295 DAC")
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
            "protocols.reconstitution_steps": payload["protocols"]["reconstitution_steps"],
        }

        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": update_doc},
        )
        print(f"\n[OK] {doc['name']} ({slug})")
        print(f"     Matched: {result.matched_count} | Modified: {result.modified_count}")
        print(f"     • {payload['overview']['function']}")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. CJC-1295 DAC fully updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
