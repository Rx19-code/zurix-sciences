"""
Batch 8: IGF-1 LR3 protocol (microdosing power builder approach).
Vial 1 mg + 1 mL bac water = 1000 mcg/mL (standard microdose concentration).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch8.py
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
    # ═══════════ IGF-1 LR3 ═══════════
    "igf-1-lr3": {
        "overview": {
            "function": "Lean muscle growth, recovery, strength enhancement",
            "mechanism_of_action": (
                "IGF-1 LR3 (Long R3 Insulin-like Growth Factor 1) is a modified version of "
                "endogenous IGF-1 with two key alterations: an Arg-3 substitution (reducing "
                "binding to IGFBPs) and a 13-residue extension at the N-terminus. These "
                "modifications extend its half-life from ~10 minutes (native IGF-1) to "
                "20-30 hours. IGF-1 LR3 activates the IGF-1 receptor, stimulating protein "
                "synthesis, satellite cell proliferation (muscle hyperplasia), and lean tissue "
                "growth without significant water retention."
            ),
            "considerations": (
                "Best used in short cycles (4 weeks) to avoid receptor desensitization. "
                "Microdosing post-workout (intramuscular into trained muscle) is the most "
                "popular protocol for power athletes. Monitor blood glucose — IGF-1 has "
                "insulin-like effects."
            ),
        },
        "benefits": [
            "Supports lean muscle growth without bloating or water retention",
            "Enhances post-workout recovery",
            "Boosts strength and power output",
            "Stimulates satellite cell proliferation (muscle hyperplasia)",
            "Improves nutrient partitioning and protein synthesis",
            "Long half-life (20-30h) — more potent than native IGF-1",
            "Site-specific growth when injected IM into target muscle",
        ],
        "side_effects": {
            "common": [
                "Mild hypoglycemia (rare with proper dosing)",
                "Injection site reactions",
                "Mild fatigue immediately post-injection",
            ],
            "less_common": [
                "Joint pain (with high doses or long cycles)",
                "Transient lower back pump",
                "Numbness or tingling (carpal tunnel-like, dose-dependent)",
            ],
            "rare": [
                "Hypoglycemia with high doses (have carbs available)",
                "Theoretical risk of cell growth promotion in pre-existing conditions",
                "Organ enlargement with very prolonged high-dose use",
            ],
        },
        "timing_goals": [
            {"goal": "Lean muscle growth / power", "timing": "Post-workout IM injection into trained muscle"},
            {"goal": "Microdosing protocol", "timing": "20 mcg post-workout on alternate training days for 4 weeks"},
            {"goal": "Site-specific growth", "timing": "Inject directly into the target muscle bilaterally post-workout"},
            {"goal": "Recovery from cycle", "timing": "4 weeks off after each 4-week cycle to reset receptor sensitivity"},
        ],
        "administration": {
            "route": "Intramuscular (preferred) or Subcutaneous",
            "notes": (
                "IM injection POST-WORKOUT directly into the trained muscle is the most "
                "effective protocol. Use an insulin syringe (1 mL). Rotate injection sites "
                "bilaterally. Have a carb source nearby in case of hypoglycemia. "
                "Store reconstituted vial refrigerated at 2-8°C."
            ),
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for human use. Legal for research purposes only.",
            "uk": "Classified as research chemical; not approved for medical or athletic use.",
            "canada": "Restricted to research use; banned in competitive athletics (WADA prohibited).",
        },
        "protocols": {
            "title": "Microdosing Power Builder Protocol (vial 1 mg, 1 mL bac water = 1000 mcg/mL)",
            "standard": {
                "route": "Intramuscular (post-workout)",
                "frequency": "Alternate training days, 4-week cycles",
            },
            "dosages": [
                {
                    "indication": "Microdose / first-time users",
                    "schedule": "Post-workout IM, alternate training days",
                    "dose": "20 mcg per injection (2 units on a 100-unit insulin syringe)",
                },
                {
                    "indication": "Standard power builder microdose",
                    "schedule": "Post-workout IM, alternate training days",
                    "dose": "30 mcg per injection (3 units)",
                },
                {
                    "indication": "Advanced lean mass focus",
                    "schedule": "Post-workout IM, on training days only",
                    "dose": "40-50 mcg per injection (4-5 units)",
                },
                {
                    "indication": "Bilateral site-specific growth",
                    "schedule": "Split between two trained muscles post-workout",
                    "dose": "20 mcg per side (2 units per site)",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "20 mcg post-workout IM on alternate training days"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "20-30 mcg post-workout IM on training days"},
                {"number": 3, "phase": "Off cycle (Weeks 5-8)", "dose": "Washout — 4 weeks rest to restore receptor sensitivity"},
                {"number": 4, "phase": "Repeat cycle (optional)", "dose": "Restart 20-30 mcg microdosing protocol"},
            ],
            "reconstitution": (
                "Reconstitute the 1 mg vial with 1 mL of bacteriostatic water "
                "(final concentration 1000 mcg/mL — ideal for microdosing). "
                "20 mcg = 0.02 mL = 2 units on a 100-unit insulin syringe. "
                "30 mcg = 3 units. 50 mcg = 5 units. "
                "Store at 2-8°C and protect from light. "
                "PROTOCOL EXAMPLE (Microdosing Power Builder): "
                "1) Reconstitute 1 mg with 1 mL bac water. "
                "2) Draw 20 mcg (2 units) and inject IM post-workout. "
                "3) Use on alternate training days for 4 weeks. "
                "4) Take 4 weeks off, then optionally repeat."
            ),
            "reconstitution_steps": [
                "Wipe both vials with alcohol swabs",
                "Aspirate exactly 1.0 mL of bacteriostatic water using a sterile syringe",
                "Inject slowly down the side of the IGF-1 LR3 vial — do NOT spray on powder",
                "Swirl gently until fully dissolved (do NOT shake — peptide is delicate)",
                "Label with date and refrigerate at 2-8°C",
                "Standard microdose: 20 mcg = 2 units (0.02 mL) on a 100u insulin syringe",
                "Inject IM post-workout into the trained muscle for site-specific growth",
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
    print(f"BATCH 8 UPDATE — {len(UPDATES)} peptide (IGF-1 LR3 microdosing)")
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
        print(f"     • Route: {payload['administration']['route']}")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. IGF-1 LR3 fully updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
