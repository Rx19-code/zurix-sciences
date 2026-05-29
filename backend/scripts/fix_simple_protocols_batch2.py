"""
Batch 2: Update PT-141, Oxytocin, Kisspeptin, KPV protocols.
All vials reconstituted with 3 mL bacteriostatic water (Zurix Sciences standard).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch2.py
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

# Standard reconstitution for 10 mg vials at Zurix Sciences:
# 10 mg / 3 mL = 3.33 mg/mL (≈ 3333 mcg/mL)
# Insulin syringe 100U scale: 1 mL = 100 units, so 1 unit = 0.01 mL = 33.3 mcg

UPDATES = {
    # ═══════════ PT-141 (Bremelanotide) ═══════════
    "pt-141": {
        "overview": {
            "function": "Sexual desire enhancement, arousal, sexual dysfunction",
            "mechanism_of_action": (
                "PT-141 (Bremelanotide) is a melanocortin receptor agonist (primarily MC3R and MC4R) "
                "that acts on the central nervous system to enhance sexual desire and arousal. "
                "Unlike PDE5 inhibitors (Viagra), it works through the brain rather than vascular "
                "pathways, making it effective for both physical and psychogenic sexual dysfunction "
                "in men and women."
            ),
            "considerations": "Effects typically begin 30-60 minutes after injection and last several hours. May cause transient blood pressure increase.",
        },
        "benefits": [
            "Enhances sexual desire and arousal",
            "Effective for sexual dysfunction in both men and women",
            "Improves sexual satisfaction",
            "Works centrally (in the brain) — not dependent on vascular response",
            "Useful for psychogenic / low-libido cases",
        ],
        "side_effects": {
            "common": [
                "Nausea (especially first doses)",
                "Headache",
                "Flushing",
                "Injection site reactions",
            ],
            "less_common": [
                "Transient increase in blood pressure",
                "Decreased appetite",
                "Skin darkening (hyperpigmentation) with frequent use",
            ],
            "rare": [
                "Severe nausea or vomiting",
                "Significant cardiovascular effects in predisposed individuals",
            ],
        },
        "timing_goals": [
            {"goal": "Sexual desire boost", "timing": "Administer 1-2 hours before planned sexual activity"},
            {"goal": "General sexual health support", "timing": "Use as needed; not recommended more than once per 24 hours"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": "Inject 1-2 hours before activity. Use sterile technique and rotate injection sites.",
        },
        "legal_status": {
            "us": "Bremelanotide (Vyleesi) is FDA-approved for HSDD in premenopausal women. Generic PT-141 is research-only.",
            "uk": "Controlled — legal only for scientific research without authorization.",
            "canada": "Classified as research substance; not approved for human use.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "As needed, max 1x per 24 hours"},
            "dosages": [
                {"indication": "Initial / sensitive users", "schedule": "1-2 hours before activity, SC", "dose": "1 mg per dose (≈30 units / 0.30 mL)"},
                {"indication": "Standard research dose", "schedule": "1-2 hours before activity, SC", "dose": "1.5 mg per dose (≈45 units / 0.45 mL)"},
                {"indication": "High-dose / tolerant users", "schedule": "1-2 hours before activity, SC", "dose": "2 mg per dose (≈60 units / 0.60 mL)"},
            ],
            "phases": [
                {"number": 1, "phase": "Tolerance test", "dose": "0.5 mg SC, observe for 24h"},
                {"number": 2, "phase": "Standard use", "dose": "1-2 mg SC, 1-2h before activity"},
                {"number": 3, "phase": "Frequency limit", "dose": "Max 1x per 24h, ≤8x per month"},
            ],
            "reconstitution": "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water (final concentration 3.33 mg/mL ≈ 3333 mcg/mL). 1 mg dose = 0.30 mL (30 units on a 100-unit insulin syringe). Store at 2-8°C and protect from light.",
        },
    },

    # ═══════════ Oxytocin ═══════════
    "oxytocin": {
        "overview": {
            "function": "Social bonding, emotional well-being, stress reduction",
            "mechanism_of_action": (
                "Oxytocin is a neuropeptide produced in the hypothalamus that acts as both a "
                "hormone and neurotransmitter. It enhances social bonding, trust, empathy, and "
                "emotional connection. Crosses the blood-brain barrier when administered "
                "intranasally, producing rapid effects on mood and social behavior."
            ),
            "considerations": "Most commonly administered intranasally for behavioral effects. SC injection used in some research applications.",
        },
        "benefits": [
            "Enhances social bonding and relationships",
            "Promotes emotional well-being and reduces stress",
            "Improves mood and may reduce symptoms of depression/anxiety",
            "Facilitates childbirth and lactation (clinical use)",
            "Supports overall brain health and emotional resilience",
            "Enhances empathy and trust in social contexts",
        ],
        "side_effects": {
            "common": [
                "Mild headaches",
                "Nausea",
                "Dizziness",
            ],
            "less_common": [
                "Increased heart rate",
                "Mild fluid retention",
            ],
            "rare": [
                "Allergic reactions",
                "Hyponatremia with very high doses",
            ],
        },
        "timing_goals": [
            {"goal": "Social bonding", "timing": "Administer 30-45 minutes before social interactions"},
            {"goal": "Emotional well-being", "timing": "Use as needed to improve mood and reduce stress"},
            {"goal": "Childbirth / lactation", "timing": "Only as prescribed by a healthcare provider"},
        ],
        "administration": {
            "route": "Intranasal (preferred) or Subcutaneous",
            "notes": "Intranasal: 1-2 puffs per nostril. SC: use sterile technique. Store refrigerated.",
        },
        "legal_status": {
            "us": "Prescription drug — FDA approved for specific medical conditions (labor induction, lactation).",
            "uk": "Prescription medicine. Off-label/research use requires authorization.",
            "canada": "Prescription drug; restricted to medical and research applications.",
        },
        "protocols": {
            "title": "Intranasal / Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "standard": {"route": "Intranasal or Subcutaneous", "frequency": "As needed or 1-2x daily"},
            "dosages": [
                {"indication": "Social bonding / mood (intranasal)", "schedule": "30-45 min before interaction", "dose": "24-40 IU intranasal (≈ 40-67 mcg)"},
                {"indication": "Research SC dose (low)", "schedule": "1x daily as needed, SC", "dose": "100 mcg (≈3 units / 0.03 mL)"},
                {"indication": "Research SC dose (standard)", "schedule": "1x daily as needed, SC", "dose": "200 mcg (≈6 units / 0.06 mL)"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "Low dose, observe response"},
                {"number": 2, "phase": "Standard use (Weeks 2-4)", "dose": "Standard dose as needed"},
                {"number": 3, "phase": "Long-term", "dose": "On-demand use; avoid daily long-term unsupervised use"},
            ],
            "reconstitution": "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water (final concentration 3.33 mg/mL ≈ 3333 mcg/mL). For SC: 100 mcg = 0.03 mL (3 units). For intranasal: transfer to nasal spray bottle and dose by puff. Store refrigerated.",
        },
    },

    # ═══════════ Kisspeptin ═══════════
    "kisspeptin": {
        "overview": {
            "function": "Gonadotropin release, reproductive health, hormone regulation",
            "mechanism_of_action": (
                "Kisspeptin is a peptide hormone that stimulates the release of GnRH "
                "(gonadotropin-releasing hormone) from the hypothalamus, which in turn "
                "triggers the release of LH and FSH from the pituitary. It is a master regulator "
                "of the hypothalamic-pituitary-gonadal (HPG) axis and plays a key role in "
                "puberty onset, fertility, and reproductive function."
            ),
            "considerations": "Used in clinical research for hypogonadism, infertility, and pubertal disorders. Dose-dependent effects on LH/FSH.",
        },
        "benefits": [
            "Stimulates endogenous gonadotropin (LH/FSH) release",
            "May aid in treating reproductive disorders and hypogonadism",
            "Potential to regulate puberty onset",
            "Supports natural testosterone/estrogen production",
            "Improves fertility markers in research settings",
        ],
        "side_effects": {
            "common": [
                "Mild headaches",
                "Nausea",
                "Injection site reactions",
            ],
            "less_common": [
                "Transient changes in reproductive hormone levels",
                "Flushing",
            ],
            "rare": [
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "Reproductive health / fertility support", "timing": "Timing depends on specific condition; consult research protocol"},
            {"goal": "Testosterone / LH stimulation", "timing": "Often administered in pulsatile fashion (every 90 min) in clinical research"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": "Use sterile technique. Rotate injection sites. Maintain consistent timing for hormonal response.",
        },
        "legal_status": {
            "us": "Research peptide — not FDA-approved for clinical use. Legal for research purposes.",
            "uk": "Classified as research chemical.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "Daily or as research protocol dictates"},
            "dosages": [
                {"indication": "Low research dose", "schedule": "1x daily, SC", "dose": "50 mcg (≈1.5 units / 0.015 mL)"},
                {"indication": "Standard research dose", "schedule": "1x daily, SC", "dose": "100 mcg (≈3 units / 0.03 mL)"},
                {"indication": "High-dose research", "schedule": "1x daily, SC", "dose": "200 mcg (≈6 units / 0.06 mL)"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "50 mcg/day SC"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "100 mcg/day SC"},
                {"number": 3, "phase": "Off cycle (Weeks 5-6)", "dose": "Washout — 2 weeks rest"},
            ],
            "reconstitution": "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water (final concentration 3.33 mg/mL ≈ 3333 mcg/mL). 100 mcg = 0.03 mL (3 units on a 100-unit insulin syringe). Store refrigerated.",
        },
    },

    # ═══════════ KPV ═══════════
    "kpv": {
        "overview": {
            "function": "Anti-inflammatory, antimicrobial, wound healing",
            "mechanism_of_action": (
                "KPV is the C-terminal tripeptide of alpha-MSH (melanocyte-stimulating hormone). "
                "It exhibits potent anti-inflammatory effects without the pigmentation activity "
                "of the parent molecule. Modulates NF-κB and pro-inflammatory cytokines. "
                "Also demonstrates direct antimicrobial activity, making it useful for IBD, "
                "psoriasis, eczema, and wound healing applications."
            ),
            "considerations": "Generally well-tolerated. Can be used systemically (SC) or topically for skin conditions.",
        },
        "benefits": [
            "Reduces inflammation — especially in skin and GI tissues",
            "Effective in research for IBD, psoriasis, and eczema",
            "Antimicrobial properties — useful against bacteria, fungi, and viruses",
            "Promotes wound healing and tissue repair",
            "Minimal systemic side effects",
            "Can be applied topically for localized skin conditions",
        ],
        "side_effects": {
            "common": [
                "Minimal — generally well-tolerated",
                "Injection site reactions (redness, mild irritation)",
            ],
            "less_common": [
                "Mild GI discomfort",
            ],
            "rare": [
                "Allergic reactions in peptide-sensitive individuals",
            ],
        },
        "timing_goals": [
            {"goal": "Systemic inflammation reduction", "timing": "Administer in the morning or before a workout"},
            {"goal": "Wound healing", "timing": "Shortly after injury or post-surgery for faster recovery"},
            {"goal": "Skin conditions (topical)", "timing": "Apply 1-2x daily to affected area"},
            {"goal": "IBD / gut inflammation", "timing": "Daily SC use; some protocols use oral capsule formulations"},
        ],
        "administration": {
            "route": "Subcutaneous or Topical",
            "notes": "SC for systemic effects; topical for localized skin conditions. Sterile technique for injections.",
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for medical use. Legal for research purposes.",
            "uk": "Classified as research chemical.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 10 mg, 3 mL bac water = 3.33 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "Daily or every other day"},
            "dosages": [
                {"indication": "Low / maintenance dose", "schedule": "1x daily or EOD, SC", "dose": "200 mcg/day (≈6 units / 0.06 mL)"},
                {"indication": "Standard research dose", "schedule": "1x daily, SC", "dose": "300 mcg/day (≈9 units / 0.09 mL)"},
                {"indication": "High dose (acute inflammation)", "schedule": "1x daily, SC", "dose": "400 mcg/day (≈12 units / 0.12 mL)"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "200 mcg/day SC"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "300 mcg/day SC"},
                {"number": 3, "phase": "Peak (acute conditions, Weeks 5-6)", "dose": "400 mcg/day SC"},
                {"number": 4, "phase": "Off cycle / maintenance", "dose": "200 mcg every other day or 2 weeks rest"},
            ],
            "reconstitution": "Reconstitute the 10 mg vial with 3 mL of bacteriostatic water (final concentration 3.33 mg/mL ≈ 3333 mcg/mL). 200 mcg = 0.06 mL (6 units on a 100-unit insulin syringe). Store refrigerated.",
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
    print(f"BATCH 2 UPDATE — {len(UPDATES)} peptides (3 mL reconstitution standard)")
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
        print(f"     • {len(payload['benefits'])} benefits | {sum(len(v) for v in payload['side_effects'].values())} side effects")
        print(f"     • Route: {payload['administration']['route']}")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. Batch 2 (4 peptides) updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
