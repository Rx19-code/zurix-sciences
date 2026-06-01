"""
Batch 9: Update BPC-157 protocol.
Vial 10 mg + 3 mL bac water = 3.33 mg/mL.

NOTE: "IGF-1" (não LR3) NÃO existe na biblioteca atualmente.
      Apenas IGF-1 LR3 está disponível (já atualizado em batch 8).
      Se o usuário quiser criar entrada nova para IGF-1 base, será necessário
      adicionar primeiro o documento no peptide_library + criar produto.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch9.py
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
    # ═══════════ BPC-157 ═══════════
    "bpc-157": {
        "overview": {
            "function": "Tissue healing, anti-inflammatory, gut repair, neuroprotection",
            "mechanism_of_action": (
                "BPC-157 (Body Protection Compound 157) is a stable synthetic pentadecapeptide "
                "derived from a protective protein in human gastric juice. It promotes "
                "angiogenesis (new blood vessel formation), modulates the nitric oxide (NO) "
                "system, upregulates VEGF and growth factor expression, and accelerates the "
                "healing of tendons, ligaments, muscles, and gastrointestinal tissues. It also "
                "shows neuroprotective effects via modulation of dopaminergic and serotonergic "
                "systems."
            ),
            "considerations": (
                "Highly versatile peptide — works systemically via SC/IM and also locally near "
                "injury sites. For GI/gut issues, oral administration can be effective. "
                "Generally well-tolerated with minimal side effects."
            ),
        },
        "benefits": [
            "Accelerates healing of tendons, ligaments, and muscles",
            "Reduces inflammation and pain",
            "Promotes repair of gastrointestinal tissues (ulcers, IBS, IBD research)",
            "Enhances wound healing and tissue regeneration",
            "Improves recovery from muscle injuries",
            "Supports overall tissue regeneration via angiogenesis",
            "Neuroprotective effects (mood, anxiety, brain injury research)",
            "May help with leaky gut and gut barrier integrity",
        ],
        "side_effects": {
            "common": [
                "Redness, itchiness, or swelling at the injection site",
                "Mild nausea (especially with oral use)",
                "Temporary discomfort at the injection site",
            ],
            "less_common": [
                "Dizziness",
                "Mild headache",
                "Fatigue (transient)",
            ],
            "rare": [
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "Acute injury recovery", "timing": "1-2x daily SC/IM near the injury site until healed"},
            {"goal": "General healing / maintenance", "timing": "Once daily for ongoing tissue repair"},
            {"goal": "Gastrointestinal health", "timing": "Take orally on empty stomach for direct GI absorption"},
            {"goal": "Tendon / ligament rehab", "timing": "Inject near (not into) the affected tendon/ligament 1-2x daily"},
        ],
        "administration": {
            "route": "Subcutaneous, Intramuscular, or Oral",
            "notes": (
                "SC injection is most common for systemic effects. IM near the injury site "
                "is excellent for localized healing (e.g. tendon, joint). Oral administration "
                "(direct from syringe into mouth, swallow with water) is effective for gut "
                "and GI issues — peptide is stable in stomach acid. Rotate injection sites."
            ),
        },
        "legal_status": {
            "us": "Research substance — not FDA-approved for human use. Recently restricted by FDA from compounding pharmacies.",
            "uk": "Classified as research chemical. Not approved for medical treatment.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Subcutaneous / Oral Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "standard": {
                "route": "Subcutaneous (or Oral for GI issues)",
                "frequency": "1-2 times daily",
            },
            "dosages": [
                {
                    "indication": "Maintenance / mild healing",
                    "schedule": "1x daily, SC",
                    "dose": "200 mcg/day (≈6 units / 0.06 mL)",
                },
                {
                    "indication": "Standard injury recovery",
                    "schedule": "1-2x daily, SC near injury site",
                    "dose": "250 mcg/dose (≈7.5 units / 0.075 mL)",
                },
                {
                    "indication": "Acute injury / aggressive healing",
                    "schedule": "2x daily, SC or IM near injury",
                    "dose": "400 mcg/dose (≈12 units / 0.12 mL)",
                },
                {
                    "indication": "Gastrointestinal health (oral)",
                    "schedule": "1-2x daily on empty stomach, oral",
                    "dose": "250-500 mcg/dose",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "200 mcg × 1x daily SC"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "200-400 mcg × 1-2x daily SC"},
                {"number": 3, "phase": "Peak (Weeks 5-6, acute injuries)", "dose": "400 mcg × 2x daily SC/IM"},
                {"number": 4, "phase": "Off cycle (Weeks 7-10)", "dose": "Washout — 2 to 4 weeks rest"},
            ],
            "reconstitution": (
                "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 3.33 mg/mL ≈ 3333 mcg/mL). "
                "200 mcg = 0.06 mL (6 units on a 100-unit insulin syringe). "
                "400 mcg = 0.12 mL (12 units). "
                "For 20 mg vial + 3 mL: 6.67 mg/mL (halve volume per dose). "
                "For 40 mg vial + 3 mL: 13.33 mg/mL. "
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
    print(f"BATCH 9 UPDATE — {len(UPDATES)} peptide (BPC-157)")
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
        print(f"     • Route: {payload['administration']['route']}")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. BPC-157 fully updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
