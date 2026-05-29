"""
Batch 6: Update Klow Blend (anti-inflammatory + skin + healing multi-peptide blend).
Composition: KPV 30mg + GHK-Cu 30mg + BPC-157 10mg + TB-500 10mg = 80mg total
Vial 80 mg + 3 mL bac water = 26.67 mg/mL total blend.

Also flips has_product=True so it shows on /library page.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch6.py
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


# Composition (80 mg total per vial):
#   GHK-Cu       50 mg  (62.5%)  — collagen synthesis, skin regen
#   KPV          10 mg  (12.5%)  — anti-inflammatory, antimicrobial
#   BPC-157      10 mg  (12.5%)  — angiogenesis, gut/joint healing
#   TB-500       10 mg  (12.5%)  — tissue repair, actin modulation
#
# Reconstituted with 3 mL bac water → 26.67 mg/mL blend
# Per injection (0.10 mL = 10 units):
#   GHK-Cu  ≈ 1.67 mg
#   KPV     ≈ 333 mcg
#   BPC-157 ≈ 333 mcg
#   TB-500  ≈ 333 mcg

UPDATES = {
    "klow-blend": {
        "description": (
            "Advanced 4-peptide blend combining GHK-Cu, KPV, BPC-157 and TB-500 in a single "
            "vial. Designed for skin regeneration, anti-inflammatory support and accelerated "
            "tissue healing research."
        ),
        "composition": [
            {"peptide": "GHK-Cu", "dose": "50 mg", "role": "Collagen & elastin synthesis, copper-mediated skin regeneration"},
            {"peptide": "KPV", "dose": "10 mg", "role": "Anti-inflammatory, antimicrobial, autoimmune modulation"},
            {"peptide": "BPC-157", "dose": "10 mg", "role": "Angiogenesis, gut/joint healing, anti-inflammatory"},
            {"peptide": "TB-500", "dose": "10 mg", "role": "Tissue repair, actin modulation, accelerated recovery"},
        ],
        "overview": {
            "function": "Skin regeneration, anti-inflammatory, deep tissue healing (4-peptide blend)",
            "mechanism_of_action": (
                "Klow Blend stacks four complementary peptides into a single injection. "
                "GHK-Cu (50mg, the dominant component) is the copper-binding tripeptide that "
                "drives collagen/elastin synthesis and antioxidant defense. KPV (Lys-Pro-Val), "
                "the C-terminal tripeptide of α-MSH, suppresses NF-κB and pro-inflammatory "
                "cytokines with antimicrobial properties. BPC-157 promotes angiogenesis, "
                "gut barrier repair and joint healing. TB-500 (Thymosin Beta-4) accelerates "
                "cell migration and actin-dependent tissue repair. Together, the four create "
                "synergy for skin disorders, inflammatory conditions and recovery from injury."
            ),
            "considerations": (
                "Single-vial 4-peptide blend — replaces 4 separate injections. Light blue "
                "color after reconstitution is normal (copper from GHK-Cu). "
                "Composition: GHK-Cu 50mg + KPV 10mg + BPC-157 10mg + TB-500 10mg = 80mg total."
            ),
        },
        "benefits": [
            "Comprehensive anti-inflammatory and healing effects in one injection",
            "Strong support for autoimmune and inflammatory skin conditions (psoriasis, eczema, IBD research)",
            "Stimulates collagen and elastin synthesis (GHK-Cu)",
            "Promotes wound healing and accelerated tissue repair (BPC-157 + TB-500)",
            "Antimicrobial properties (KPV)",
            "Improves skin firmness, texture and elasticity",
            "Supports gut barrier and joint health",
            "Convenient — replaces 4 separate injections",
        ],
        "side_effects": {
            "common": [
                "Mild injection site reactions (redness, irritation)",
                "Light blue color of solution (from copper) — normal, not contamination",
            ],
            "less_common": [
                "Transient flushing",
                "Mild headache",
                "Mild nausea (usually transient)",
            ],
            "rare": [
                "Allergic reactions in peptide-sensitive individuals",
                "Copper sensitivity (extremely rare)",
            ],
        },
        "timing_goals": [
            {"goal": "Chronic inflammation / autoimmune support", "timing": "2-3x per week for 6-8 weeks, then taper to 1-2x per week"},
            {"goal": "Skin conditions (psoriasis, eczema, acne research)", "timing": "2-3x per week for 8-12 weeks"},
            {"goal": "Post-procedure / acute injury recovery", "timing": "Start 24-48h post-event, 3x per week for 2-4 weeks"},
            {"goal": "General anti-aging maintenance", "timing": "1-2x per week continuously"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": (
                "Inject subcutaneously using sterile technique. Rotate injection sites "
                "(abdomen, thigh, upper arm). Solution appears light blue (copper) — normal. "
                "For active skin condition areas, prefer SC injection near (not into) the "
                "affected zone."
            ),
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for therapeutic use. Legal for research purposes.",
            "uk": "Classified as research chemical. Not approved for medical treatment.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 80 mg blend, 3 mL bac water = 26.67 mg/mL)",
            "standard": {
                "route": "Subcutaneous",
                "frequency": "1-3 times per week",
            },
            "dosages": [
                {
                    "indication": "Maintenance / mild support",
                    "schedule": "1x per week, SC",
                    "dose": "5 units (0.05 mL) — ≈ 833 mcg GHK-Cu + 167 mcg KPV + 167 mcg BPC-157 + 167 mcg TB-500",
                },
                {
                    "indication": "Standard skin / anti-inflammatory",
                    "schedule": "2-3x per week, SC",
                    "dose": "10 units (0.10 mL) — ≈ 1.67 mg GHK-Cu + 333 mcg KPV + 333 mcg BPC-157 + 333 mcg TB-500",
                },
                {
                    "indication": "Acute / aggressive protocol",
                    "schedule": "3x per week, SC",
                    "dose": "15 units (0.15 mL) — ≈ 2.5 mg GHK-Cu + 500 mcg KPV + 500 mcg BPC-157 + 500 mcg TB-500",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "5 units × 1-2x per week SC"},
                {"number": 2, "phase": "Build-up (Weeks 3-4)", "dose": "10 units × 2x per week SC"},
                {"number": 3, "phase": "Peak (Weeks 5-8)", "dose": "10-15 units × 2-3x per week SC"},
                {"number": 4, "phase": "Maintenance (Weeks 9+)", "dose": "5-10 units × 1-2x per week SC (continuous)"},
            ],
            "reconstitution": (
                "Reconstitute the 80 mg blend vial with 3 mL of bacteriostatic water "
                "(final concentration 26.67 mg/mL total blend). "
                "Standard dose 10 units (0.10 mL) delivers: "
                "1.67 mg GHK-Cu + 333 mcg KPV + 333 mcg BPC-157 + 333 mcg TB-500. "
                "Solution will appear light blue (copper from GHK-Cu) — this is normal. "
                "Store at 2-8°C and protect from light. Stable for 30 days after reconstitution."
            ),
            "reconstitution_steps": [
                "Prepare a sterile work area; wipe both vials with alcohol swabs",
                "Aspirate 3.0 mL of bacteriostatic water with a sterile syringe",
                "Inject slowly down the side of the Klow Blend vial — do NOT spray directly on powder",
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
    print(f"BATCH 6 UPDATE — {len(UPDATES)} blend (Klow)")
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
    print("Done. Klow Blend fully updated and now visible in /library.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
