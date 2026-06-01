"""
Batch 7: SLU-PP-332 (oral capsules only), Retatrutide (titration), NAD+ (multi-protocol).

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch7.py
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
    # ═══════════ SLU-PP-332 (ORAL CAPSULES ONLY) ═══════════
    "slu-pp-332": {
        "overview": {
            "function": "Exercise mimetic, fat oxidation, endurance enhancement",
            "mechanism_of_action": (
                "SLU-PP-332 is a synthetic ERR (Estrogen-Related Receptor) agonist that activates "
                "ERRα, ERRβ and ERRγ — master regulators of mitochondrial biogenesis and oxidative "
                "metabolism. It produces 'exercise-like' effects without physical activity: "
                "increases mitochondrial density, fat oxidation, slow-twitch (type I) muscle fiber "
                "formation and endurance capacity. Pre-clinical research shows dramatic improvements "
                "in running endurance and metabolic flexibility."
            ),
            "considerations": (
                "ORAL ROUTE ONLY (capsules). Take 30 minutes before cardio or training for optimal "
                "effect. Early-stage research compound — long-term safety data still limited."
            ),
        },
        "benefits": [
            "Acts as an exercise mimetic — boosts endurance without training",
            "Increases mitochondrial biogenesis and density",
            "Enhances fat oxidation and metabolic flexibility",
            "Promotes slow-twitch muscle fiber formation",
            "May improve insulin sensitivity and glucose metabolism",
            "Supports cardiovascular and metabolic health markers",
            "Convenient oral administration (capsules)",
        ],
        "side_effects": {
            "common": [
                "Minimal — generally well tolerated in research dosing",
                "Mild GI discomfort possible (taken on empty stomach)",
            ],
            "less_common": [
                "Headache (transient)",
                "Increased perceived energy / mild stimulation",
            ],
            "rare": [
                "Long-term safety data not yet available",
                "Theoretical hormonal modulation via ERR pathway",
            ],
        },
        "timing_goals": [
            {"goal": "Pre-cardio / training boost", "timing": "Take one dose 30 minutes before workout"},
            {"goal": "Fat loss / metabolic boost", "timing": "Daily dosing, split 2-3 times throughout the day"},
            {"goal": "Endurance research", "timing": "Consistent daily use for 4-8 weeks"},
        ],
        "administration": {
            "route": "Oral (capsules)",
            "notes": (
                "Take capsules with water. For best results, dose 30 minutes before cardio or "
                "training. Daily total can be split into 2-3 doses throughout the day. "
                "Do not crush or chew the capsules."
            ),
        },
        "legal_status": {
            "us": "Research compound — not FDA-approved for human use. Legal for research purposes.",
            "uk": "Classified as research chemical.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Oral Capsule Protocol (250 mcg or 500 mcg capsules)",
            "standard": {
                "route": "Oral (capsules)",
                "frequency": "Daily, split 2-3 doses",
            },
            "dosages": [
                {
                    "indication": "Low dose / first-time users",
                    "schedule": "1x daily, 30 min before training",
                    "dose": "200 mcg/day",
                },
                {
                    "indication": "Standard research dose",
                    "schedule": "Split 2 doses (AM + 30 min pre-training)",
                    "dose": "400 mcg/day",
                },
                {
                    "indication": "High-dose / endurance research",
                    "schedule": "Split 2-3 doses throughout the day",
                    "dose": "600 mcg/day",
                },
                {
                    "indication": "Peak research dose",
                    "schedule": "Split 3 doses throughout the day",
                    "dose": "800 mcg/day",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "200 mcg/day (1 capsule 250 mcg)"},
                {"number": 2, "phase": "Standard (Weeks 2-3)", "dose": "400 mcg/day (split 2 doses)"},
                {"number": 3, "phase": "Peak (Weeks 4-6)", "dose": "600-800 mcg/day (split 2-3 doses)"},
                {"number": 4, "phase": "Off cycle (Weeks 7-8)", "dose": "Washout — 2 weeks rest"},
            ],
            "reconstitution": (
                "No reconstitution required — oral capsules. Available in 250 mcg or 500 mcg "
                "strengths. Take with water; can be taken with or without food (empty stomach "
                "preferred 30 min before training)."
            ),
        },
    },

    # ═══════════ Retatrutide ═══════════
    "retatrutide": {
        "overview": {
            "function": "Weight loss, triple receptor agonist (GLP-1 / GIP / glucagon)",
            "mechanism_of_action": (
                "Retatrutide is a triple agonist targeting GLP-1, GIP and glucagon receptors. "
                "Unlike Tirzepatide (dual GLP-1/GIP), Retatrutide adds glucagon receptor "
                "activation, which boosts energy expenditure and fat oxidation in addition to "
                "appetite suppression. Phase 2 trials showed unprecedented weight loss: "
                "−17.5% at 12 mg by week 24, continuing to −24.2% by week 48. "
                "Phase 3 TRIUMPH trials show up to −28.7% weight loss at 68 weeks."
            ),
            "considerations": (
                "Structured 4-week titration is CRITICAL to minimize GI side effects. "
                "Starting at 2 mg (instead of 4 mg) significantly reduced GI symptoms in trials. "
                "Blood tests recommended before starting and at each dose transition (liver, "
                "kidney, thyroid, pancreatic function)."
            ),
        },
        "benefits": [
            "Most powerful weight loss agent in current research (−24% to −28% body weight)",
            "Triple mechanism: appetite reduction + insulin sensitization + energy expenditure",
            "Improved glycemic control and HbA1c reduction",
            "Reduced hepatic fat content",
            "Cardiometabolic improvements (lipids, blood pressure)",
            "Progressive weight loss continuing beyond 48 weeks",
        ],
        "side_effects": {
            "common": [
                "Nausea (especially during titration)",
                "Diarrhea or constipation",
                "Decreased appetite",
                "Vomiting (worse at higher doses)",
                "Injection site reactions",
            ],
            "less_common": [
                "Abdominal pain or bloating",
                "Fatigue",
                "Headache",
                "Elevated heart rate (mild)",
            ],
            "rare": [
                "Hypoglycemia (especially with insulin/sulfonylureas)",
                "Pancreatitis",
                "Gallbladder issues",
                "Thyroid changes (monitor with blood tests)",
            ],
        },
        "timing_goals": [
            {"goal": "Weight loss", "timing": "Once weekly on the same day; rotate injection sites"},
            {"goal": "Minimize GI side effects", "timing": "Start at 2 mg (not 4 mg) and titrate every 4 weeks"},
            {"goal": "Monitor safety", "timing": "Blood panel before starting and at each dose increase"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": (
                "Inject abdomen, thigh, or upper arm. Rotate sites. Use sterile technique. "
                "Same day of the week every week. Storage 2-8°C after reconstitution."
            ),
        },
        "legal_status": {
            "us": "Investigational — currently in Phase 3 trials (TRIUMPH). Not yet FDA-approved.",
            "uk": "Investigational; not approved.",
            "canada": "Investigational; not approved.",
        },
        "protocols": {
            "title": "Weekly Subcutaneous Protocol — Phase 3 TRIUMPH titration",
            "standard": {
                "route": "Subcutaneous",
                "frequency": "Once weekly, same day each week",
            },
            "dosages": [
                {"indication": "Initial titration (Weeks 1-4)", "schedule": "Once weekly, SC", "dose": "2 mg/week"},
                {"indication": "Step 2 (Weeks 5-8)", "schedule": "Once weekly, SC", "dose": "4 mg/week"},
                {"indication": "Step 3 (Weeks 9-12)", "schedule": "Once weekly, SC", "dose": "6 mg/week"},
                {"indication": "Step 4 (Weeks 13-16)", "schedule": "Once weekly, SC", "dose": "9 mg/week"},
                {"indication": "Target dose / maintenance", "schedule": "Once weekly, SC", "dose": "12 mg/week"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-4)", "dose": "2 mg/week SC — low entry to minimize GI"},
                {"number": 2, "phase": "Step-up (Weeks 5-8)", "dose": "4 mg/week SC — average -7% loss"},
                {"number": 3, "phase": "Mid-titration (Weeks 9-12)", "dose": "6 mg/week SC — accelerated loss"},
                {"number": 4, "phase": "Sub-target (Weeks 13-16)", "dose": "9 mg/week SC"},
                {"number": 5, "phase": "Target dose (Weeks 17-48+)", "dose": "12 mg/week SC — up to -28.7% at week 68"},
            ],
            "reconstitution": (
                "Reconstitute the vial with bacteriostatic water based on vial size. "
                "Common protocol: 10mg vial + 2 mL water = 5 mg/mL. "
                "For 2 mg dose = 0.4 mL (40 units). For 12 mg dose = 2.4 mL (use higher concentration vials). "
                "Refrigerate at 2-8°C after reconstitution. Stable up to 30 days."
            ),
        },
    },

    # ═══════════ NAD+ ═══════════
    "nad-plus-": {
        "overview": {
            "function": "Cellular energy, longevity, metabolic restoration",
            "mechanism_of_action": (
                "NAD+ (Nicotinamide Adenine Dinucleotide) is a critical coenzyme involved in "
                "mitochondrial energy production, DNA repair, sirtuin activation (longevity "
                "pathways), and cellular redox balance. Levels decline with age, contributing "
                "to mitochondrial dysfunction, fatigue, and reduced cellular resilience. "
                "Exogenous NAD+ administration restores cellular bioenergetics, activates "
                "SIRT1/SIRT3 pathways, and supports DNA repair via PARP enzymes."
            ),
            "considerations": (
                "Dose-dependent benefits — loading phase recommended for first 7-10 days, "
                "then maintenance. Subcutaneous or intramuscular injection. Solution may have "
                "amber color — normal."
            ),
        },
        "benefits": [
            "Restores cellular energy production (mitochondrial ATP)",
            "Activates sirtuins (SIRT1/SIRT3) — longevity pathways",
            "Supports DNA repair mechanisms",
            "Improves mental clarity and cognitive performance",
            "Enhances athletic recovery and endurance",
            "Reduces fatigue and supports metabolic health",
            "Used in addiction recovery research (NAD+ IV therapy)",
        ],
        "side_effects": {
            "common": [
                "Mild flushing during injection (especially fast push)",
                "Injection site reactions",
                "Transient chest tightness (slow administration helps)",
            ],
            "less_common": [
                "Mild headache",
                "Nausea (rare with SC route)",
                "Fatigue immediately after dose",
            ],
            "rare": [
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "General wellness", "timing": "50-100 mg, 2-3x per week — ongoing"},
            {"goal": "Loading phase (kickstart)", "timing": "100-200 mg daily for 7-10 days, then taper"},
            {"goal": "Athletic recovery", "timing": "200-500 mg, 2-3x per week for 2-4 weeks"},
            {"goal": "Cognitive enhancement", "timing": "100-250 mg, 1-2x per week for 4-6 weeks"},
            {"goal": "Addiction recovery (research)", "timing": "500-1000 mg daily for 7-10 days under supervision"},
        ],
        "administration": {
            "route": "Subcutaneous or Intramuscular",
            "notes": (
                "Inject SLOWLY to avoid flushing. SC route preferred for home use. "
                "Rotate injection sites. Solution may appear amber/yellow — this is normal. "
                "Store refrigerated and protect from light."
            ),
        },
        "legal_status": {
            "us": "Available as a supplement and research compound. Injectable NAD+ is used clinically in some IV therapy settings.",
            "uk": "Available as supplement; injectable form considered research-only.",
            "canada": "Supplement form widely available; injectable NAD+ classified as research compound.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 500 mg, 3 mL bac water = 166.67 mg/mL)",
            "standard": {
                "route": "Subcutaneous or Intramuscular",
                "frequency": "Varies by goal — see dosages below",
            },
            "dosages": [
                {
                    "indication": "General wellness / maintenance",
                    "schedule": "2-3x per week, SC (ongoing)",
                    "dose": "50-100 mg per dose",
                },
                {
                    "indication": "Loading phase (kickstart)",
                    "schedule": "Daily, SC (7-10 days)",
                    "dose": "100-200 mg per dose",
                },
                {
                    "indication": "Athletic recovery",
                    "schedule": "2-3x per week, SC (2-4 weeks)",
                    "dose": "200-500 mg per dose",
                },
                {
                    "indication": "Cognitive enhancement",
                    "schedule": "1-2x per week, SC (4-6 weeks)",
                    "dose": "100-250 mg per dose",
                },
                {
                    "indication": "Addiction recovery (research, supervised)",
                    "schedule": "Daily, SC or IV (7-10 days)",
                    "dose": "500-1000 mg per dose",
                },
            ],
            "phases": [
                {"number": 1, "phase": "Loading (Days 1-10)", "dose": "100-200 mg/day SC"},
                {"number": 2, "phase": "Build-up (Weeks 2-3)", "dose": "200 mg × 3x/week SC"},
                {"number": 3, "phase": "Maintenance (Week 4+)", "dose": "100 mg × 2-3x/week SC (ongoing)"},
            ],
            "reconstitution": (
                "Reconstitute the 500 mg vial with 3 mL of bacteriostatic water "
                "(final concentration 166.67 mg/mL). "
                "100 mg dose = 0.60 mL (60 units on a 100-unit insulin syringe). "
                "Inject SLOWLY (over 1-2 minutes) to minimize flushing and chest tightness. "
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
    print(f"BATCH 7 UPDATE — {len(UPDATES)} peptides")
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
    print("Done. Batch 7 (3 peptides) updated.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
