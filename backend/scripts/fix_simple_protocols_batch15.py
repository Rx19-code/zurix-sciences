"""
Batch 15: Enrich HGH Fragment 176-191 and Glutathione with extra context
(overview, benefits, side_effects, timing_goals, administration, legal_status).
DOES NOT TOUCH existing protocols (dosages/phases/reconstitution preserved).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch15.py
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
    # ═══════════ HGH Fragment 176-191 ═══════════
    "hgh-fragment-176-191": {
        "overview": {
            "function": "Targeted fat loss, lipolysis, body recomposition (no anabolic effects)",
            "mechanism_of_action": (
                "HGH Fragment 176-191 (also known as AOD or HGH Frag) is the C-terminal "
                "fragment of human growth hormone — specifically amino acids 176-191. "
                "This region was isolated because it preserves the fat-burning (lipolytic) "
                "activity of full HGH WITHOUT the growth-promoting, insulin-like or "
                "anabolic effects. It activates beta-3 adrenergic receptors in adipose "
                "tissue, increasing lipolysis (fat breakdown) and inhibiting lipogenesis "
                "(fat formation). Critically, it does NOT raise blood sugar, does NOT cause "
                "joint pain, water retention or carpal tunnel symptoms typical of full HGH."
            ),
            "considerations": (
                "Pure fat-loss tool — no muscle/anabolic effect. Stacks well with appetite "
                "suppressants (Tirzepatide, Semaglutide). Best on empty stomach to maximize "
                "lipolytic effect. Often used in 5 on / 2 off cycling for 6-12 weeks. "
                "Considered one of the safest GH-derivative fat-loss peptides because it "
                "avoids the insulin desensitization seen with full HGH."
            ),
        },
        "benefits": [
            "Selective fat oxidation without affecting muscle mass or growth",
            "Does NOT raise blood glucose (unlike full HGH)",
            "No insulin desensitization or diabetic risk",
            "Targets stubborn adipose tissue (abdominal, visceral)",
            "No joint pain, water retention or carpal tunnel symptoms",
            "Improves lipid profile (cholesterol, triglycerides)",
            "Synergizes with GLP-1 agonists (Tirzepatide, Semaglutide) for accelerated cut",
            "Considered one of the safest GH-derivative peptides",
        ],
        "side_effects": {
            "common": [
                "Mild injection site reactions (redness, irritation)",
                "Minimal — one of the safest fat-loss peptides",
            ],
            "less_common": [
                "Mild headache",
                "Transient fatigue",
                "Mild nausea",
            ],
            "rare": [
                "Allergic reactions",
                "Theoretical adrenergic stimulation in sensitive individuals",
            ],
        },
        "timing_goals": [
            {"goal": "Fat loss / lipolysis", "timing": "Morning fasted SC injection — maximizes lipolytic response"},
            {"goal": "Pre-cardio fat burn", "timing": "Inject 30-45 minutes before fasted cardio"},
            {"goal": "Body recomposition cycle", "timing": "Daily 5 on / 2 off for 6-12 weeks, then 2-4 weeks off"},
            {"goal": "Stack with GLP-1", "timing": "Combine with Tirzepatide weekly for synergistic appetite + lipolysis"},
            {"goal": "Stubborn fat targeting", "timing": "Inject SC near targeted area (abdomen) for localized effect"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": (
                "Inject SC preferably in abdomen for local fat-targeting effect. "
                "Empty stomach (≥2h post-meal) maximizes lipolytic response. "
                "Rotate injection sites systematically. Store reconstituted at 2-8°C."
            ),
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for human use. Legal for research purposes.",
            "uk": "Classified as research chemical; not approved for medical use.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
    },

    # ═══════════ Glutathione ═══════════
    "glutathione": {
        "overview": {
            "function": "Master antioxidant, detoxification, skin brightening, immune support",
            "mechanism_of_action": (
                "Glutathione (GSH) is the body's master antioxidant — a tripeptide composed "
                "of glutamate, cysteine and glycine. It acts as the primary intracellular "
                "redox buffer by donating electrons to neutralize reactive oxygen species "
                "(ROS), regenerates other antioxidants (vitamins C and E), conjugates with "
                "toxins for hepatic phase II detoxification, and inhibits tyrosinase "
                "(the enzyme that produces melanin). Levels decline with age, oxidative "
                "stress, alcohol/drug use, and chronic illness. Exogenous administration "
                "(IV, SC, IM) restores intracellular GSH faster than oral supplementation "
                "(which has poor bioavailability)."
            ),
            "considerations": (
                "Injectable glutathione bypasses GI degradation (oral absorption is poor). "
                "SC or IM routes more practical than IV for home protocols. Pair with "
                "vitamin C (oral or co-injection) to recycle oxidized glutathione back to "
                "active form. Effects on skin brightening typically visible after 4-8 weeks. "
                "Solution may have a slight sulfur smell — normal."
            ),
            "what_is": (
                "Glutathione is the master antioxidant of the body, a tripeptide composed "
                "of glutamate, cysteine, and glycine. It serves as a major redox regulator "
                "in every cell."
            ),
            "mechanism_summary": (
                "Glutathione acts as the primary intracellular redox buffer by donating "
                "electrons to neutralize reactive oxygen species (ROS), regenerates other "
                "antioxidants, and supports liver detoxification pathways."
            ),
        },
        "benefits": [
            "Master antioxidant — neutralizes free radicals and oxidative stress",
            "Supports liver detoxification (phase II conjugation of toxins)",
            "Skin brightening — inhibits tyrosinase and melanin production",
            "Anti-aging effects via reduction of cellular oxidative damage",
            "Boosts immune function (T-cell proliferation and lymphocyte activity)",
            "Improves energy and mitochondrial function",
            "Reduces inflammation markers (cytokines, CRP)",
            "Synergistic with NAD+ for cellular energy/longevity protocols",
            "Supports recovery from alcohol or heavy metal exposure",
        ],
        "side_effects": {
            "common": [
                "Mild injection site reactions (redness, irritation)",
                "Slight sulfur smell of solution — normal, not contamination",
            ],
            "less_common": [
                "Mild flushing (especially with rapid IV push)",
                "Transient headache",
                "Mild fatigue immediately after dose",
            ],
            "rare": [
                "Allergic reactions",
                "Asthma exacerbation in sensitive individuals (sulfite sensitivity)",
                "Skin lightening can be permanent in extended high-dose protocols",
            ],
        },
        "timing_goals": [
            {"goal": "Skin brightening", "timing": "1500-2000 mg SC, 2-3x per week for 8-12 weeks"},
            {"goal": "Antioxidant / anti-aging", "timing": "500-1000 mg SC, 1-2x per week ongoing"},
            {"goal": "Liver detox support", "timing": "1000-2000 mg SC, daily for 5-10 days, then taper"},
            {"goal": "Pre-workout antioxidant", "timing": "200-500 mg SC 30-60 min before training"},
            {"goal": "Stack with vitamin C", "timing": "Co-administer or take 1g vitamin C orally to recycle GSH"},
            {"goal": "Stack with NAD+", "timing": "Pair on alternating days for cellular longevity"},
        ],
        "administration": {
            "route": "Subcutaneous, Intramuscular, or Intravenous",
            "notes": (
                "SC for home use (easiest). IM for stronger systemic effect. IV (clinic only) "
                "delivers full dose to bloodstream. Inject SLOWLY (over 1-2 minutes) to "
                "minimize flushing. Solution may smell slightly of sulfur — normal. "
                "Store reconstituted vial refrigerated at 2-8°C, protected from light."
            ),
        },
        "legal_status": {
            "us": "Available as supplement and injectable form for research/cosmetic use. Sometimes used in IV therapy clinics.",
            "uk": "Available as supplement; injectable form considered research/cosmetic.",
            "canada": "Supplement widely available; injectable used in some clinical settings.",
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
    print(f"BATCH 15 UPDATE — enriching {len(UPDATES)} peptides (overview + safety only)")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found")
            continue

        result = await db.peptide_library.update_one(
            {"slug": slug},
            {"$set": payload},
        )
        print(f"\n[OK] {doc['name']} ({slug})")
        print(f"     Matched: {result.matched_count} | Modified: {result.modified_count}")
        print(f"     Fields updated: {list(payload.keys())}")
        print(f"     Benefits added: {len(payload.get('benefits', []))}")
        print(f"     Timing goals: {len(payload.get('timing_goals', []))}")
        print(f"     ✓ Protocols (dosages/phases/reconstitution) NOT touched.")

    client.close()
    print("\n" + "=" * 60)
    print(f"Done. {len(UPDATES)} peptides enriched. Existing protocols preserved.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
