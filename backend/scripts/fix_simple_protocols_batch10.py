"""
Batch 10: Enrich IGF-1 LR3 with additional info from the user's IGF-1 reference
(cycle 6-12 weeks, post-workout/bedtime timing, expanded side effects).
Merges with existing microdosing protocol from batch 8.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch10.py
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
    "igf-1-lr3": {
        "overview": {
            "function": "Muscle growth, recovery, strength, bone density, longevity",
            "mechanism_of_action": (
                "IGF-1 LR3 (Long R3 Insulin-like Growth Factor 1) is a modified analogue of "
                "the endogenous IGF-1 hormone, which is produced by the liver in response to "
                "growth hormone (GH) stimulation. IGF-1 mediates many of the growth-promoting "
                "effects of GH, influencing cell growth, repair and protein synthesis. "
                "The LR3 variant has an Arg-3 substitution (reducing IGFBP binding) and a "
                "13-residue N-terminal extension, extending half-life from ~10 minutes (native "
                "IGF-1) to 20-30 hours. It strongly activates the IGF-1 receptor, stimulating "
                "protein synthesis, satellite cell proliferation (muscle hyperplasia) and "
                "lean tissue growth."
            ),
            "considerations": (
                "Two main protocols: (1) Microdosing post-workout for power/lean mass "
                "(4-week cycles), or (2) Daily systemic protocol for general muscle building "
                "and recovery (6-12 week cycles). Monitor blood glucose due to insulin-like "
                "effects. Banned by WADA for competitive athletes."
            ),
        },
        "benefits": [
            "Stimulates muscle growth and repair",
            "Enhances recovery and tissue regeneration",
            "Boosts strength and power output without bloating",
            "Promotes lean mass via satellite cell proliferation (hyperplasia)",
            "Potentially improves bone density",
            "May support cognitive function and longevity research",
            "Improves nutrient partitioning and protein synthesis",
            "Long half-life (20-30h) — more potent than native IGF-1",
            "Site-specific growth possible when injected IM into target muscle",
        ],
        "side_effects": {
            "common": [
                "Mild hypoglycemia (have carbs available)",
                "Injection site reactions",
                "Mild fatigue immediately post-injection",
            ],
            "less_common": [
                "Joint pain (with high doses or extended cycles)",
                "Transient lower back pump",
                "Numbness or tingling (carpal tunnel-like, dose-dependent)",
            ],
            "rare": [
                "Hypoglycemia with high doses — always have a carb source nearby",
                "Theoretical risk of accelerated cell proliferation in pre-existing conditions",
                "Organ enlargement with very prolonged high-dose use",
                "Potential increased cancer risk via cell proliferation (long-term, theoretical)",
            ],
        },
        "timing_goals": [
            {"goal": "Muscle building (systemic)", "timing": "Administer post-workout OR before bedtime daily"},
            {"goal": "Recovery support", "timing": "Use consistently on training days to support healing and muscle repair"},
            {"goal": "Microdosing power builder", "timing": "20-30 mcg IM post-workout, alternate training days, 4-week cycles"},
            {"goal": "Site-specific growth", "timing": "Inject IM directly into target muscle bilaterally post-workout"},
            {"goal": "Long cycle (mass focus)", "timing": "Daily SC, 6-12 weeks on, then 4+ weeks off to restore receptor sensitivity"},
        ],
        "administration": {
            "route": "Intramuscular (preferred for site-specific) or Subcutaneous (systemic)",
            "notes": (
                "IM post-workout into trained muscle = best for site-specific growth/power. "
                "SC = best for systemic effects and longer cycles. Use an insulin syringe (1 mL). "
                "Rotate injection sites bilaterally. Have a carb source nearby in case of "
                "hypoglycemia. Store reconstituted vial refrigerated at 2-8°C. "
                "Sterile technique mandatory to prevent infection."
            ),
        },
        "legal_status": {
            "us": "IGF-1 LR3 is a controlled research substance — not FDA-approved for human use or performance enhancement. Legal for research purposes only.",
            "uk": "Classified as research chemical; not approved for medical or athletic use.",
            "canada": "Restricted to research use only.",
            "wada": "BANNED by World Anti-Doping Agency (WADA) — prohibited in competitive sports.",
        },
        "protocols": {
            "title": "Subcutaneous / Intramuscular Protocol (vial 1 mg, 1 mL bac water = 1000 mcg/mL)",
            "standard": {
                "route": "Intramuscular (post-workout) or Subcutaneous (systemic)",
                "frequency": "Daily on training days OR alternate training days (microdosing)",
            },
            "dosages": [
                {
                    "indication": "Microdose / first-time users",
                    "schedule": "Post-workout IM, alternate training days",
                    "dose": "20 mcg per injection (2 units / 0.02 mL)",
                },
                {
                    "indication": "Standard muscle building (systemic)",
                    "schedule": "Daily, SC post-workout or before bedtime",
                    "dose": "20-30 mcg/day (2-3 units / 0.02-0.03 mL)",
                },
                {
                    "indication": "Advanced lean mass focus",
                    "schedule": "Post-workout IM, on training days only",
                    "dose": "40-50 mcg per dose (4-5 units / 0.04-0.05 mL)",
                },
                {
                    "indication": "Bilateral site-specific growth",
                    "schedule": "Split between two trained muscles post-workout",
                    "dose": "20 mcg per side (2 units per site)",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "20 mcg/day SC (or IM post-workout on alternate days)"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "20-30 mcg/day SC or IM post-workout"},
                {"number": 3, "phase": "Peak (Weeks 5-8, optional)", "dose": "30-50 mcg/day SC or IM"},
                {"number": 4, "phase": "Long cycle option (Weeks 9-12)", "dose": "20-30 mcg/day to extend mass-building phase"},
                {"number": 5, "phase": "Off cycle (4+ weeks)", "dose": "Washout — 4+ weeks to restore receptor sensitivity"},
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
    print(f"BATCH 10 UPDATE — IGF-1 LR3 enriched")
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
        print(f"     • {len(payload['benefits'])} benefits | {len(payload['timing_goals'])} timing goals")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. IGF-1 LR3 enriched with full IGF-1 context.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
