"""
Batch 3: Update GHK-Cu protocol (SC injection only, no topical).
Vial 50 mg + 3 mL bac water = 16.67 mg/mL.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch3.py
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
    # ═══════════ GHK-Cu (Subcutaneous only — no topical) ═══════════
    "ghk-cu": {
        "overview": {
            "function": "Wound healing, anti-aging, anti-inflammatory, hair growth",
            "mechanism_of_action": (
                "GHK-Cu is a copper-binding tripeptide (Gly-His-Lys + copper ion) naturally "
                "present in human plasma. It stimulates collagen and elastin synthesis, "
                "activates wound healing pathways, modulates copper-dependent enzymes "
                "involved in tissue repair, and exhibits potent antioxidant and "
                "anti-inflammatory effects. Research shows benefits for skin regeneration, "
                "hair follicle stimulation, and systemic anti-aging markers."
            ),
            "considerations": "Subcutaneous injection only in this protocol (topical formulations are excluded). Light blue color due to copper content is normal.",
        },
        "benefits": [
            "Accelerates wound healing and tissue repair",
            "Promotes collagen and elastin synthesis (anti-aging)",
            "Reduces inflammation and oxidative stress",
            "Stimulates hair follicle growth and health",
            "Improves skin firmness, texture, and elasticity",
            "Supports systemic anti-aging via tissue regeneration pathways",
        ],
        "side_effects": {
            "common": [
                "Minimal — generally considered very safe",
                "Mild injection site reactions (redness, irritation)",
            ],
            "less_common": [
                "Transient flushing",
                "Mild headache",
            ],
            "rare": [
                "Allergic reactions in peptide-sensitive individuals",
                "Copper sensitivity (extremely rare)",
            ],
        },
        "timing_goals": [
            {"goal": "Wound healing & skin regeneration", "timing": "Administer 1-2x weekly until target tissue is healed"},
            {"goal": "Anti-aging / skin quality", "timing": "1-2x weekly continuously for ongoing benefits"},
            {"goal": "Hair growth support", "timing": "1-2x weekly; combine with consistent scalp/hair care routine"},
            {"goal": "Systemic anti-inflammatory", "timing": "1x weekly maintenance dose"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": "Inject subcutaneously using sterile technique. Rotate injection sites (abdomen, thigh). The solution will appear light blue due to copper — this is normal.",
        },
        "legal_status": {
            "us": "Available for research and cosmetic use. Not FDA-approved for therapeutic use.",
            "uk": "Research compound; allowed in cosmetic formulations under regulation.",
            "canada": "Permitted in cosmetic products; restricted to research for therapeutic use.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 50 mg, 3 mL bac water = 16.67 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "1-2 times per week"},
            "dosages": [
                {
                    "indication": "Low dose / maintenance",
                    "schedule": "1x per week, SC",
                    "dose": "1 mg (≈6 units / 0.06 mL on 50mg vial)",
                },
                {
                    "indication": "Standard research dose",
                    "schedule": "1-2x per week, SC",
                    "dose": "1.5 mg (≈9 units / 0.09 mL on 50mg vial)",
                },
                {
                    "indication": "High dose / accelerated healing",
                    "schedule": "2x per week, SC",
                    "dose": "2 mg (≈12 units / 0.12 mL on 50mg vial)",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "1 mg × 1x per week SC"},
                {"number": 2, "phase": "Standard (Weeks 3-8)", "dose": "1.5 mg × 1-2x per week SC"},
                {"number": 3, "phase": "Peak (Weeks 9-12)", "dose": "2 mg × 2x per week SC"},
                {"number": 4, "phase": "Maintenance (ongoing)", "dose": "1-1.5 mg × 1x per week SC (continuous)"},
            ],
            "reconstitution": (
                "Reconstitute the 50 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 16.67 mg/mL ≈ 16,667 mcg/mL). "
                "1 mg dose = 0.06 mL (6 units on a 100-unit insulin syringe). "
                "For 100 mg vial with 3 mL: 33.33 mg/mL — halve the volume "
                "(1 mg = 3 units). Solution appears light blue (copper) — normal. "
                "Store at 2-8°C and protect from light."
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
    print(f"BATCH 3 UPDATE — {len(UPDATES)} peptide (SC only)")
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
    print("Done. GHK-Cu fully updated (SC only, no topical).")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
