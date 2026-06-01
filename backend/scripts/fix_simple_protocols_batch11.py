"""
Batch 11: Enrich Ipamorelin, Tesamorelin, AOD 9604, Cartalax, AHK-Cu
with missing fields (benefits, side_effects, timing_goals, administration,
legal_status). Preserves existing dosages/phases that are already good.

AHK-Cu: also removes topical option (SC injection only).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch11.py
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


# Each entry uses $set to only add/replace specific fields, NOT replacing
# existing protocols.dosages/phases (unless explicitly listed).

UPDATES = {
    # ═══════════ IPAMORELIN ═══════════
    "ipamorelin": {
        "$set": {
            "benefits": [
                "Stimulates pulsatile growth hormone (GH) release",
                "Increases lean muscle mass and strength",
                "Enhances fat loss without affecting cortisol or prolactin",
                "Improves sleep quality and recovery",
                "Anti-aging effects via natural GH/IGF-1 elevation",
                "Bone density support",
                "Selective GHRP — minimal hunger spike compared to GHRP-6",
            ],
            "timing_goals": [
                {"goal": "Anti-aging / GH optimization", "timing": "Before bed on empty stomach (≥2h after last meal)"},
                {"goal": "Athletic recovery", "timing": "Post-workout + pre-bed dosing schedule"},
                {"goal": "Fat loss", "timing": "Morning fasted + before bed (2-3x daily)"},
                {"goal": "Sleep quality", "timing": "Single dose 15-30 min before sleep on empty stomach"},
            ],
            "administration": {
                "route": "Subcutaneous",
                "notes": (
                    "Must be administered on empty stomach (≥2h after last meal, ≥30 min "
                    "before next meal). Avoid carbs/sugars near dose — blunt GH response. "
                    "Rotate injection sites; use insulin syringe."
                ),
            },
            "legal_status": {
                "us": "Research compound — not FDA-approved for human use. Legal for research purposes.",
                "uk": "Classified as research chemical; not approved for medical use.",
                "canada": "Restricted to research use; not approved for medical treatments.",
                "wada": "BANNED by WADA — prohibited in competitive sports.",
            },
            "protocols.title": "Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "protocols.reconstitution": (
                "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 3.33 mg/mL ≈ 3333 mcg/mL). "
                "200 mcg = 0.06 mL (6 units on a 100-unit insulin syringe). "
                "300 mcg = 9 units. Store at 2-8°C and protect from light."
            ),
        },
    },

    # ═══════════ TESAMORELIN ═══════════
    "tesamorelin": {
        "$set": {
            "benefits": [
                "Reduces visceral adipose tissue (belly fat) — FDA-approved indication",
                "Improves lipid profile and insulin sensitivity",
                "Stimulates endogenous growth hormone release (GHRH analog)",
                "Improves cognitive function in research settings",
                "May benefit non-alcoholic fatty liver disease (NAFLD)",
                "Better tolerability than GHRH peptides (long half-life)",
                "Synergizes well with Ipamorelin in stacks",
            ],
            "timing_goals": [
                {"goal": "Visceral fat reduction", "timing": "Once daily SC, preferably at bedtime"},
                {"goal": "GH / IGF-1 elevation", "timing": "Daily SC, on empty stomach"},
                {"goal": "Stack with Ipamorelin", "timing": "Combine in same syringe at bedtime for synergistic GH pulse"},
            ],
            "administration": {
                "route": "Subcutaneous",
                "notes": (
                    "Inject SC in abdomen, thigh or upper arm. Rotate sites. "
                    "Take on empty stomach for best results (≥2h post-meal). "
                    "Store refrigerated; stable up to 28 days after reconstitution."
                ),
            },
            "legal_status": {
                "us": "FDA-approved (Egrifta) for HIV-associated lipodystrophy. Research use otherwise.",
                "uk": "Available for specific clinical indications by prescription.",
                "canada": "Approved for HIV-associated lipodystrophy by prescription.",
            },
            "protocols.title": "Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "protocols.reconstitution": (
                "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 3.33 mg/mL ≈ 3333 mcg/mL). "
                "1 mg = 0.30 mL (30 units on a 100-unit insulin syringe). "
                "2 mg = 60 units. For 20 mg vial + 3 mL: 6.67 mg/mL (halve volume). "
                "Store at 2-8°C, protected from light."
            ),
        },
    },

    # ═══════════ AOD 9604 ═══════════
    "aod-9604": {
        "$set": {
            "benefits": [
                "Selective fat oxidation (lipolysis) without affecting blood glucose",
                "Does NOT promote muscle growth (unlike full HGH) — pure fat loss focus",
                "Improves lipid profile (cholesterol, triglycerides)",
                "May support cartilage regeneration",
                "No appetite suppression — good for cut phases without hunger management",
                "Well-tolerated with minimal hormonal disruption",
                "Originally developed by Monash University as obesity therapeutic",
            ],
            "side_effects": {
                "common": [
                    "Mild injection site reactions",
                    "Minimal — one of the safest fat-loss peptides",
                ],
                "less_common": [
                    "Mild headache",
                    "Transient fatigue",
                ],
                "rare": [
                    "Allergic reactions",
                ],
            },
            "timing_goals": [
                {"goal": "Fat loss / weight management", "timing": "Once daily in the morning on empty stomach"},
                {"goal": "Pre-workout fat oxidation", "timing": "Inject 30-60 min before fasted cardio"},
                {"goal": "Cartilage / joint support", "timing": "Daily, consistent timing"},
            ],
            "administration": {
                "route": "Subcutaneous",
                "notes": (
                    "Inject SC on empty stomach in the morning. Rotate injection sites "
                    "(abdomen preferred for fat-targeted effect). Use insulin syringe."
                ),
            },
            "legal_status": {
                "us": "Research compound — not FDA-approved as a therapeutic. Legal for research.",
                "uk": "Classified as research chemical.",
                "canada": "Restricted to research use.",
            },
            "protocols.title": "Subcutaneous Protocol (vial 5 mg, 3 mL bac water = 1.67 mg/mL)",
            "protocols.reconstitution": (
                "Reconstitute the 5 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 1.67 mg/mL ≈ 1667 mcg/mL). "
                "300 mcg = 0.18 mL (18 units on a 100-unit insulin syringe). "
                "500 mcg = 30 units. 1 mg = 60 units. "
                "Store at 2-8°C and protect from light."
            ),
        },
    },

    # ═══════════ CARTALAX ═══════════
    "cartalax": {
        "$set": {
            "overview": {
                "function": "Joint health, cartilage regeneration, connective tissue support",
                "mechanism_of_action": (
                    "Cartalax is a synthetic short peptide (Ala-Glu-Asp-Gly) developed in Russia "
                    "as a tissue-specific bioregulator targeting cartilage and connective tissue. "
                    "It modulates gene expression in chondrocytes (cartilage cells), supporting "
                    "synthesis of collagen, proteoglycans and other extracellular matrix "
                    "components. Used in research for osteoarthritis, joint degeneration and "
                    "post-injury cartilage repair."
                ),
                "considerations": (
                    "Tissue-specific peptide — slow but cumulative effects on joints. "
                    "Best results require consistent use over 4-8 weeks. "
                    "Often stacked with BPC-157 or TB-500 for synergistic joint healing."
                ),
            },
            "benefits": [
                "Supports cartilage regeneration in joints",
                "Slows progression of osteoarthritis (research)",
                "Improves joint mobility and reduces stiffness",
                "Promotes collagen synthesis in connective tissues",
                "Synergistic with BPC-157 and TB-500 for joint stacks",
                "Russian bioregulator with peptide-specific tissue affinity",
            ],
            "side_effects": {
                "common": [
                    "Minimal — generally very well tolerated",
                    "Mild injection site reactions",
                ],
                "less_common": [
                    "Transient mild fatigue",
                ],
                "rare": [
                    "Allergic reactions",
                ],
            },
            "timing_goals": [
                {"goal": "Joint health / cartilage regeneration", "timing": "Once daily SC for 4-8 weeks"},
                {"goal": "Post-injury joint repair", "timing": "Daily SC near affected joint for 6+ weeks"},
                {"goal": "Maintenance / anti-aging joints", "timing": "10-day course every 3-6 months"},
            ],
            "administration": {
                "route": "Subcutaneous",
                "notes": (
                    "SC injection in abdomen, thigh, or near affected joint. "
                    "Rotate sites. For joint-specific use, inject SC near (not into) the joint. "
                    "Use sterile technique."
                ),
            },
            "legal_status": {
                "us": "Research compound — not FDA-approved. Legal for research purposes.",
                "uk": "Classified as research chemical.",
                "canada": "Restricted to research use; not approved for medical treatments.",
            },
            "protocols.title": "Subcutaneous Protocol (vial 20 mg, 3 mL bac water = 6.67 mg/mL)",
            "protocols.reconstitution": (
                "Reconstitute the 20 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 6.67 mg/mL ≈ 6667 mcg/mL). "
                "200 mcg = 0.03 mL (3 units on a 100-unit insulin syringe). "
                "500 mcg = 0.075 mL (7.5 units). "
                "Store at 2-8°C and protect from light."
            ),
        },
    },

    # ═══════════ AHK-Cu (SC ONLY — remove topical) ═══════════
    "ahk-cu": {
        "$set": {
            "benefits": [
                "Stimulates hair follicle growth and reduces hair loss",
                "Promotes vascular endothelial growth factor (VEGF) expression in scalp",
                "Supports angiogenesis in skin and scalp tissue",
                "Anti-inflammatory and antioxidant effects",
                "Synergizes well with GHK-Cu for combined skin/hair protocols",
                "Copper-binding tripeptide — supports collagen and elastin",
            ],
            "side_effects": {
                "common": [
                    "Mild injection site reactions",
                    "Light blue color of solution (copper) — normal",
                ],
                "less_common": [
                    "Mild flushing",
                    "Transient headache",
                ],
                "rare": [
                    "Allergic reactions",
                    "Copper sensitivity (extremely rare)",
                ],
            },
            "timing_goals": [
                {"goal": "Hair growth / anti-hair-loss", "timing": "1x daily or every other day SC for 8-12 weeks"},
                {"goal": "Combined with GHK-Cu", "timing": "Alternate or combine for skin+hair synergy"},
                {"goal": "Anti-aging maintenance", "timing": "1-2x per week continuously"},
            ],
            "administration": {
                "route": "Subcutaneous",
                "notes": (
                    "SC injection only (topical formulations excluded from this protocol). "
                    "Solution appears light blue due to copper — this is normal. "
                    "Rotate sites; use sterile technique. Store refrigerated at 2-8°C."
                ),
            },
            "legal_status": {
                "us": "Research and cosmetic compound — not FDA-approved for therapeutic use.",
                "uk": "Research chemical; allowed in cosmetic formulations.",
                "canada": "Permitted in cosmetic products; research-only for therapeutic use.",
            },
            "protocols.title": "Subcutaneous Protocol (vial 100 mg, 3 mL bac water = 33.33 mg/mL)",
            "protocols.standard": {
                "route": "Subcutaneous",
                "frequency": "Daily or every other day",
            },
            "protocols.dosages": [
                {
                    "indication": "Standard hair growth dose",
                    "schedule": "Once daily or every other day, SC",
                    "dose": "1 mg/day (≈3 units / 0.03 mL)",
                },
                {
                    "indication": "Enhanced research dose",
                    "schedule": "Once daily, SC",
                    "dose": "1.5 mg/day (≈4.5 units / 0.045 mL)",
                },
                {
                    "indication": "Peak research dose",
                    "schedule": "Once daily, SC",
                    "dose": "2 mg/day (≈6 units / 0.06 mL)",
                },
            ],
            "protocols.phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "1 mg/day SC (every other day)"},
                {"number": 2, "phase": "Standard (Weeks 3-8)", "dose": "1-1.5 mg/day SC"},
                {"number": 3, "phase": "Peak (Weeks 9-12)", "dose": "2 mg/day SC"},
                {"number": 4, "phase": "Maintenance (Weeks 13+)", "dose": "1 mg every other day SC (continuous)"},
            ],
            "protocols.reconstitution": (
                "Reconstitute the 100 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 33.33 mg/mL ≈ 33,333 mcg/mL). "
                "1 mg = 0.03 mL (3 units on a 100-unit insulin syringe). "
                "Solution appears light blue (copper) — normal, not contamination. "
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
    print(f"BATCH 11 UPDATE — enriching {len(UPDATES)} peptides")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found")
            continue

        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": payload["$set"]},
        )
        print(f"\n[OK] {doc['name']} ({slug})")
        print(f"     Matched: {result.matched_count} | Modified: {result.modified_count}")
        print(f"     Fields updated: {list(payload['$set'].keys())[:5]}...")

    client.close()
    print("\n" + "=" * 60)
    print(f"Done. {len(UPDATES)} peptides enriched.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
