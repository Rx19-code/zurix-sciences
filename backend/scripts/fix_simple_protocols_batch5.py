"""
Batch 5: Update Glow Blend (multi-peptide skin/recovery blend).
Composition: GHK-Cu 50mg + BPC-157 10mg + TB-500 10mg = 70mg total
Vial 70 mg + 3 mL bac water = 23.33 mg/mL total blend.

Also flips has_product=True so it shows on /library page.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch5.py
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


# Composition (70 mg total per vial):
#   GHK-Cu       50 mg  (71.4% of vial)
#   BPC-157      10 mg  (14.3% of vial)
#   TB-500       10 mg  (14.3% of vial)
#
# Reconstituted with 3 mL bac water:
#   Total: 23.33 mg/mL blend
#   Per injection (0.10 mL = 10 units):
#     GHK-Cu  ≈ 1.67 mg
#     BPC-157 ≈ 333 mcg
#     TB-500  ≈ 333 mcg

UPDATES = {
    "glow-blend": {
        "description": "Multi-peptide aesthetic and recovery blend combining GHK-Cu, BPC-157 and TB-500 in a single vial for skin rejuvenation, tissue repair and anti-aging research.",
        "composition": [
            {"peptide": "GHK-Cu", "dose": "50 mg", "role": "Collagen & elastin synthesis, copper-mediated skin regeneration"},
            {"peptide": "BPC-157", "dose": "10 mg", "role": "Angiogenesis, wound healing, anti-inflammatory"},
            {"peptide": "TB-500", "dose": "10 mg", "role": "Tissue repair, actin modulation, accelerated recovery"},
        ],
        "overview": {
            "function": "Skin rejuvenation, anti-aging, tissue repair (multi-peptide blend)",
            "mechanism_of_action": (
                "Glow Blend combines three complementary peptides in a single injection: "
                "GHK-Cu (copper-binding tripeptide) stimulates collagen and elastin synthesis "
                "and activates skin regeneration pathways. BPC-157 promotes angiogenesis and "
                "modulates inflammatory cytokines. TB-500 (Thymosin Beta-4) accelerates cell "
                "migration and tissue repair via actin sequestration. Together, the three "
                "create a synergistic effect on skin quality, wound healing and overall recovery."
            ),
            "considerations": (
                "Single-vial blend — simplifies multi-peptide protocols. Solution will appear "
                "light blue due to the copper content in GHK-Cu — this is normal. "
                "Composition: GHK-Cu 50mg + BPC-157 10mg + TB-500 10mg = 70mg total."
            ),
        },
        "benefits": [
            "Comprehensive skin rejuvenation in a single injection",
            "Stimulates collagen and elastin synthesis (GHK-Cu)",
            "Promotes wound healing and tissue repair (BPC-157 + TB-500)",
            "Reduces inflammation and oxidative stress",
            "Improves skin firmness, texture, and elasticity",
            "Supports hair follicle health",
            "Accelerated recovery from injuries and aesthetic procedures",
            "Convenient — replaces 3 separate injections",
        ],
        "side_effects": {
            "common": [
                "Mild injection site reactions (redness, irritation)",
                "Light blue color of solution (from copper) — normal, not contamination",
            ],
            "less_common": [
                "Transient flushing",
                "Mild headache",
                "Mild nausea (typically transient)",
            ],
            "rare": [
                "Allergic reactions in peptide-sensitive individuals",
                "Copper sensitivity (extremely rare)",
            ],
        },
        "timing_goals": [
            {"goal": "Skin rejuvenation / anti-aging", "timing": "1-2x per week continuously for ongoing benefits"},
            {"goal": "Post-procedure recovery (laser, microneedling, surgery)", "timing": "Start 24-48h post-procedure, 2-3x per week for 2-4 weeks"},
            {"goal": "Active injury / wound healing", "timing": "2-3x per week until healed, then taper to 1x per week"},
            {"goal": "Hair growth support", "timing": "1-2x per week consistently for 8-12 weeks"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": (
                "Inject subcutaneously using sterile technique. Rotate injection sites "
                "(abdomen, thigh, upper arm). Solution appears light blue (copper) — normal. "
                "Pinch skin and insert at 45-90° angle."
            ),
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for therapeutic use. Legal for research and cosmetic research purposes.",
            "uk": "Classified as research chemical. Not approved for medical treatment.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 70 mg blend, 3 mL bac water = 23.33 mg/mL)",
            "standard": {
                "route": "Subcutaneous",
                "frequency": "1-3 times per week",
            },
            "dosages": [
                {
                    "indication": "Maintenance / mild anti-aging",
                    "schedule": "1x per week, SC",
                    "dose": "5 units (0.05 mL) — ≈ 0.83 mg GHK-Cu + 167 mcg BPC-157 + 167 mcg TB-500",
                },
                {
                    "indication": "Standard skin rejuvenation",
                    "schedule": "2x per week, SC",
                    "dose": "10 units (0.10 mL) — ≈ 1.67 mg GHK-Cu + 333 mcg BPC-157 + 333 mcg TB-500",
                },
                {
                    "indication": "Aggressive / post-procedure recovery",
                    "schedule": "3x per week, SC",
                    "dose": "15 units (0.15 mL) — ≈ 2.5 mg GHK-Cu + 500 mcg BPC-157 + 500 mcg TB-500",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "5 units × 1x per week SC"},
                {"number": 2, "phase": "Build-up (Weeks 3-4)", "dose": "10 units × 2x per week SC"},
                {"number": 3, "phase": "Peak (Weeks 5-8)", "dose": "10-15 units × 2-3x per week SC"},
                {"number": 4, "phase": "Maintenance (Weeks 9+)", "dose": "5-10 units × 1-2x per week SC (continuous)"},
            ],
            "reconstitution": (
                "Reconstitute the 70 mg blend vial with 3 mL of bacteriostatic water "
                "(final concentration 23.33 mg/mL total blend). "
                "Standard dose 10 units (0.10 mL) delivers: "
                "1.67 mg GHK-Cu + 333 mcg BPC-157 + 333 mcg TB-500. "
                "Solution will appear light blue (copper from GHK-Cu) — this is normal. "
                "Store at 2-8°C and protect from light. Stable for 30 days after reconstitution."
            ),
            "reconstitution_steps": [
                "Prepare a sterile work area; wipe both vials with alcohol swabs",
                "Aspirate 3.0 mL of bacteriostatic water with a sterile syringe",
                "Inject slowly down the side of the Glow Blend vial — do NOT spray directly on powder",
                "Gently swirl until fully dissolved (do not shake) — solution becomes light blue",
                "Label with reconstitution date and refrigerate at 2-8°C, protect from light",
            ],
        },
        "has_product": True,
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
    print(f"BATCH 5 UPDATE — {len(UPDATES)} blend (Glow)")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found")
            continue

        update_doc = {
            "description": payload["description"],
            "composition": payload["composition"],
            "overview": payload["overview"],
            "benefits": payload["benefits"],
            "side_effects": payload["side_effects"],
            "timing_goals": payload["timing_goals"],
            "administration": payload["administration"],
            "legal_status": payload["legal_status"],
            "has_product": payload["has_product"],
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
        print(f"     • has_product → True (now visible in /library)")
        print(f"     • Composition:")
        for c in payload["composition"]:
            print(f"        - {c['peptide']:10} {c['dose']:8}  ({c['role']})")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. Glow Blend fully updated and now visible in /library.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
