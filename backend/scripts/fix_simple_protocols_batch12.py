"""
Batch 12: HGH 191AA (10 IU vial = 3.33 mg).
Reconstitute with 3 mL bac water → 1.11 mg/mL (1 unit ≈ 11.1 mcg).
Gradual titration protocol from peptidedosages.com (8-12-16 week options).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch12.py
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
        "overview": {
            "function": "Lean body mass, fat loss, recovery, anti-aging, metabolic health",
            "mechanism_of_action": (
                "HGH 191AA is recombinant human growth hormone (somatropin), structurally "
                "identical to endogenous GH secreted by the pituitary gland. It promotes "
                "lipolysis (fat oxidation), protein synthesis, IGF-1 production, lean body "
                "mass gain and metabolic improvements. Daily subcutaneous administration "
                "at bedtime mimics physiological GH pulses, optimizing IGF-1 elevation and "
                "tissue repair during sleep."
            ),
            "considerations": (
                "Dose-dependent effects and side effects. Conservative protocols use "
                "150-500 mcg/day; advanced research protocols may reach 1000-2000 mcg/day. "
                "Gradual weekly titration (~100 mcg/week) minimizes side effects. "
                "Monitor glucose at higher doses."
            ),
        },
        "benefits": [
            "Increases lean body mass and reduces adipose tissue",
            "Enhanced fat oxidation and lipolysis (dose-dependent)",
            "Improved metabolic parameters and recovery",
            "Sustained improvements in muscle strength with long-term use (GH-deficient adults)",
            "Improved body composition (Rudman et al., NEJM 1990)",
            "Skin elasticity, hair quality and connective tissue support",
            "Better sleep quality and energy with proper bedtime dosing",
            "Stimulates IGF-1 production via liver",
        ],
        "side_effects": {
            "common": [
                "Injection site reactions (redness, irritation) — rotate sites",
                "Mild fluid retention",
                "Joint discomfort / arthralgias (especially at higher doses)",
            ],
            "less_common": [
                "Peripheral edema (higher doses)",
                "Carpal tunnel-like symptoms (numbness/tingling)",
                "Glucose metabolism changes",
            ],
            "rare": [
                "Lipoatrophy at injection sites (if rotation inadequate)",
                "Hyperglycemia / insulin resistance (extended high-dose use)",
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "Physiological GH mimicry / sleep", "timing": "Subcutaneous injection at bedtime daily"},
            {"goal": "Fat loss focus", "timing": "Morning fasted OR pre-bed; consider 5 on / 2 off cycling"},
            {"goal": "Muscle / recovery", "timing": "Daily SC bedtime — consistent timing for 8-12 weeks"},
            {"goal": "Gradual titration (recommended)", "timing": "+100 mcg every week starting at 200 mcg/day"},
        ],
        "administration": {
            "route": "Subcutaneous (preferred) or Intramuscular",
            "notes": (
                "SC injection at 45-90° into skinfold (abdomen ≥2 inches from navel, outer "
                "thighs, posterior upper arms). DO NOT aspirate for SC. Inject slowly; wait "
                "few seconds before withdrawing needle. Rotate sites systematically to prevent "
                "lipoatrophy. Use new sterile insulin syringe per injection."
            ),
        },
        "legal_status": {
            "us": "Prescription drug (somatropin) — FDA-approved for GH deficiency, HIV-wasting, etc. Research use otherwise.",
            "uk": "Prescription-only medicine.",
            "canada": "Prescription drug; not approved for performance enhancement.",
            "wada": "BANNED by WADA — prohibited in competitive sports.",
        },
        "protocols": {
            "title": "HGH 191AA Gradual Titration (vial 10 IU = 3.33 mg, 3 mL bac water = 1.11 mg/mL)",
            "standard": {
                "route": "Subcutaneous",
                "frequency": "Once daily at bedtime",
            },
            "dosages": [
                {
                    "indication": "Conservative replacement (anti-aging / wellness)",
                    "schedule": "1x daily SC, bedtime",
                    "dose": "150-500 mcg/day (≈14-45 units / 0.14-0.45 mL)",
                },
                {
                    "indication": "Standard research dose",
                    "schedule": "1x daily SC, bedtime",
                    "dose": "500-900 mcg/day (≈45-81 units / 0.45-0.81 mL)",
                },
                {
                    "indication": "Advanced metabolic / performance research",
                    "schedule": "1x daily SC, bedtime",
                    "dose": "1000-1300 mcg/day (≈90-117 units / 0.90-1.17 mL)",
                },
                {
                    "indication": "Maximum advanced (with monitoring)",
                    "schedule": "1x daily SC, bedtime",
                    "dose": "1500-2000 mcg/day (≈135-180 units)",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Week 1", "dose": "200 mcg/day SC (18 units / 0.18 mL)"},
                {"number": 2, "phase": "Week 2", "dose": "300 mcg/day SC (27 units / 0.27 mL)"},
                {"number": 3, "phase": "Week 3", "dose": "400 mcg/day SC (36 units / 0.36 mL)"},
                {"number": 4, "phase": "Week 4", "dose": "500 mcg/day SC (45 units / 0.45 mL)"},
                {"number": 5, "phase": "Week 5", "dose": "600 mcg/day SC (54 units / 0.54 mL)"},
                {"number": 6, "phase": "Week 6", "dose": "700 mcg/day SC (63 units / 0.63 mL)"},
                {"number": 7, "phase": "Week 7", "dose": "800 mcg/day SC (72 units / 0.72 mL)"},
                {"number": 8, "phase": "Week 8 (conservative end)", "dose": "900 mcg/day SC (81 units / 0.81 mL)"},
                {"number": 9, "phase": "Weeks 9-12 (extended / advanced)", "dose": "1000-1300 mcg/day SC (90-117 units)"},
                {"number": 10, "phase": "Off cycle (4+ weeks)", "dose": "Washout — restore receptor sensitivity"},
            ],
            "reconstitution": (
                "Reconstitute the 10 IU (3.33 mg) vial with 3.0 mL of bacteriostatic water "
                "(final concentration ~1.11 mg/mL ≈ 1111 mcg/mL). "
                "At this concentration on a U-100 insulin syringe: "
                "1 unit = 0.01 mL ≈ 11.1 mcg. "
                "200 mcg = 18 units (0.18 mL). "
                "500 mcg = 45 units (0.45 mL). "
                "1000 mcg = 90 units (0.90 mL). "
                "Lyophilized vial: store at −20°C. Reconstituted: refrigerate at 2-8°C; "
                "AVOID freeze-thaw cycles (denatures protein). Protect from light."
            ),
            "reconstitution_steps": [
                "Draw 3.0 mL of bacteriostatic water with a sterile syringe",
                "Inject slowly down the side of the vial wall — avoid foaming",
                "Gently swirl or roll until dissolved — do NOT shake (preserves protein structure)",
                "Label with reconstitution date and refrigerate at 2-8°C, protected from light",
                "Use new sterile insulin syringe per daily injection",
                "Allow vial to reach room temperature before opening to minimize condensation",
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
    print(f"BATCH 12 UPDATE — HGH 191AA")
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
    print("Done. HGH 191AA fully updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
