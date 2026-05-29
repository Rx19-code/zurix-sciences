"""
Bulk migration v2: update simple protocols + benefits + side effects + timing
+ administration + legal status for 5 peptides.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_simple_protocols_batch1.py
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
    # ═══════════ TB-500 / Thymosin Beta-4 ═══════════
    "tb-500": {
        "overview": {
            "function": "Wound healing, tissue regeneration, anti-inflammatory",
            "mechanism_of_action": (
                "TB-500 is a synthetic version of the naturally occurring Thymosin Beta-4 peptide. "
                "It modulates actin dynamics, promotes angiogenesis (new blood vessel formation), "
                "and accelerates tissue repair. Plays a central role in cell migration and "
                "inflammation resolution. Widely studied for musculoskeletal injuries."
            ),
            "considerations": "Generally well-tolerated. Most commonly used in research for injury recovery and tendon/ligament repair.",
        },
        "benefits": [
            "Accelerates wound healing and tissue repair",
            "Reduces inflammation and scar tissue formation",
            "Promotes angiogenesis (new blood vessel formation)",
            "Enhances recovery from muscle and tendon injuries",
            "Supports cardiovascular health",
            "May improve outcomes in certain chronic conditions",
        ],
        "side_effects": {
            "common": [
                "Redness, itchiness, or swelling at the injection site",
                "Mild nausea",
                "Temporary discomfort at the injection site",
            ],
            "less_common": [
                "Mild fatigue or lethargy",
                "Headache",
            ],
            "rare": [
                "Theoretical risk of impaired infection response at very high prolonged doses",
            ],
        },
        "timing_goals": [
            {"goal": "Acute injury recovery", "timing": "Administer 1-2 times weekly until injury is healed"},
            {"goal": "General healing & anti-inflammatory", "timing": "Once weekly for ongoing tissue repair"},
            {"goal": "Chronic conditions", "timing": "Consult with a healthcare provider for personalized timing"},
        ],
        "administration": {
            "route": "Subcutaneous or Intramuscular",
            "notes": "Use sterile needles and follow hygienic practices. Rotate injection sites.",
        },
        "legal_status": {
            "us": "Research substance — not FDA approved for human use. Legal for research purposes only.",
            "uk": "Classified as research chemical. Not approved for medical treatment.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Subcutaneous or Intramuscular Protocol",
            "standard": {"route": "Subcutaneous or Intramuscular", "frequency": "1-2 times per week"},
            "dosages": [
                {"indication": "Acute injury recovery", "schedule": "1-2x per week, SC or IM, until healed", "dose": "2-2.5 mg per injection"},
                {"indication": "General healing / anti-inflammatory", "schedule": "1x per week, SC or IM", "dose": "2 mg per injection"},
                {"indication": "Muscle / tendon recovery", "schedule": "2x per week, SC or IM", "dose": "2.5 mg per injection"},
            ],
            "phases": [
                {"number": 1, "phase": "Loading (Weeks 1-2)", "dose": "2.5 mg × 2x per week"},
                {"number": 2, "phase": "Maintenance (Weeks 3-6)", "dose": "2 mg × 1-2x per week"},
                {"number": 3, "phase": "Off cycle (Weeks 7-10)", "dose": "Washout — 2 to 4 weeks rest"},
            ],
            "reconstitution": "Reconstitute the vial with bacteriostatic water (typical 2-3 mL for a 10 mg vial). Store at 2-8°C after reconstitution.",
        },
    },

    # ═══════════ Tirzepatide ═══════════
    "tirzepatide": {
        "overview": {
            "function": "Weight loss, glycemic control, appetite regulation",
            "mechanism_of_action": (
                "Tirzepatide is a dual GIP/GLP-1 receptor agonist that mimics two natural incretin "
                "hormones. It enhances insulin secretion, slows gastric emptying, reduces appetite, "
                "and improves insulin sensitivity. The dual mechanism produces greater weight loss "
                "than GLP-1 monotherapy (semaglutide)."
            ),
            "considerations": "FDA-approved (Mounjaro / Zepbound). Always titrate slowly to minimize GI side effects.",
        },
        "benefits": [
            "Significant weight loss in clinical studies (up to 20%+ body weight)",
            "Improved glycemic control (HbA1c reduction)",
            "Enhanced insulin sensitivity",
            "Reduced appetite and food cravings",
            "Cardiometabolic improvements",
        ],
        "side_effects": {
            "common": [
                "Nausea (especially during titration)",
                "Diarrhea or constipation",
                "Decreased appetite",
                "Injection site reactions",
            ],
            "less_common": [
                "Vomiting",
                "Abdominal pain or bloating",
                "Fatigue",
            ],
            "rare": [
                "Hypoglycemia (especially when combined with insulin or sulfonylureas)",
                "Pancreatitis (rare but reported)",
                "Gallbladder disease",
            ],
        },
        "timing_goals": [
            {"goal": "Weight loss", "timing": "Administer once weekly on the same day; rotate injection site"},
            {"goal": "Blood sugar control", "timing": "Take consistently as part of a diabetes management plan"},
            {"goal": "GI tolerability", "timing": "Inject before bed to potentially reduce daytime nausea"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": "Inject abdomen, thigh, or upper arm. Rotate sites. Use sterile technique.",
        },
        "legal_status": {
            "us": "FDA-approved for type 2 diabetes (Mounjaro) and chronic weight management (Zepbound). Prescription required.",
            "uk": "Approved by MHRA for type 2 diabetes and obesity (Mounjaro).",
            "canada": "Health Canada approved for type 2 diabetes management.",
        },
        "protocols": {
            "title": "Weekly Subcutaneous Protocol (titration)",
            "standard": {"route": "Subcutaneous", "frequency": "Once weekly, same day each week"},
            "dosages": [
                {"indication": "Initial titration (weeks 1-4)", "schedule": "Once weekly, SC", "dose": "2.5 mg/week"},
                {"indication": "Standard weight loss / glycemic control", "schedule": "Once weekly, SC", "dose": "5 mg/week"},
                {"indication": "Enhanced dose (per tolerance)", "schedule": "Once weekly, SC", "dose": "7.5-10 mg/week"},
                {"indication": "Maximum research dose", "schedule": "Once weekly, SC", "dose": "15 mg/week"},
            ],
            "phases": [
                {"number": 1, "phase": "Titration (Weeks 1-4)", "dose": "2.5 mg/week SC"},
                {"number": 2, "phase": "Standard (Weeks 5-8)", "dose": "5 mg/week SC"},
                {"number": 3, "phase": "Step-up (Weeks 9-12)", "dose": "7.5 mg/week SC"},
                {"number": 4, "phase": "Maintenance (Weeks 13+)", "dose": "10-15 mg/week SC (per tolerance)"},
            ],
            "reconstitution": "Available as pre-filled pen or lyophilized vial. For vial: reconstitute with bacteriostatic water per concentration; store at 2-8°C.",
        },
    },

    # ═══════════ Sermorelin ═══════════
    "sermorelin": {
        "overview": {
            "function": "Growth hormone secretagogue, anti-aging, recovery",
            "mechanism_of_action": (
                "Sermorelin is a GHRH (Growth Hormone-Releasing Hormone) analog that stimulates "
                "the pituitary gland to release endogenous growth hormone naturally. Unlike "
                "exogenous HGH, it preserves the body's natural pulsatile GH release and feedback "
                "loops, reducing risk of suppression."
            ),
            "considerations": "Must be taken on an empty stomach for optimal results. Best results require 3-6 months of consistent use.",
        },
        "benefits": [
            "Increases endogenous growth hormone release",
            "Promotes lean muscle growth",
            "Enhances fat loss and body recomposition",
            "Improves recovery and tissue repair",
            "Supports anti-aging through enhanced cellular repair",
            "Improves sleep quality (deeper REM and slow-wave sleep)",
            "Boosts immune function",
        ],
        "side_effects": {
            "common": [
                "Redness, itchiness, or swelling at the injection site",
                "Mild headaches",
                "Nausea",
                "Flushing or warmth sensation",
            ],
            "less_common": [
                "Dizziness",
                "Vivid dreams (related to deeper sleep)",
                "Mild fluid retention",
            ],
            "rare": [
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "Fat burning", "timing": "Administer before a workout on an empty stomach"},
            {"goal": "Muscle building", "timing": "Take after a workout on an empty stomach"},
            {"goal": "Sleep improvement", "timing": "Use before bed on an empty stomach"},
            {"goal": "General anti-aging", "timing": "Administer in the evening on an empty stomach"},
        ],
        "administration": {
            "route": "Subcutaneous",
            "notes": "Inject on empty stomach (2+ hours after last meal). Avoid carbs/sugar right after injection.",
        },
        "legal_status": {
            "us": "FDA-approved for treatment of growth hormone deficiency. Prescription required for medical use.",
            "uk": "Restricted to clinical use only; not generally available outside specialist endocrinology.",
            "canada": "Health Canada approved for adult and pediatric GH deficiency by prescription.",
        },
        "protocols": {
            "title": "Daily Subcutaneous Protocol (evening / bedtime)",
            "standard": {"route": "Subcutaneous", "frequency": "Once daily, before bedtime on empty stomach"},
            "dosages": [
                {"indication": "General anti-aging / GH support", "schedule": "1x daily before bed, empty stomach, SC", "dose": "200 mcg/day"},
                {"indication": "Body recomposition / fat loss", "schedule": "1x daily before bed, empty stomach, SC", "dose": "250 mcg/day"},
                {"indication": "Peak research dose", "schedule": "1x daily before bed, empty stomach, SC", "dose": "300 mcg/day"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Month 1)", "dose": "200 mcg/day SC"},
                {"number": 2, "phase": "Standard (Months 2-3)", "dose": "250-300 mcg/day SC"},
                {"number": 3, "phase": "Extended (Months 4-6)", "dose": "300 mcg/day SC"},
                {"number": 4, "phase": "Off cycle (4 weeks)", "dose": "Washout — 4 weeks rest"},
            ],
            "reconstitution": "Reconstitute the vial with bacteriostatic water (typical 2 mL for a 2-5 mg vial). Refrigerate at 2-8°C and protect from light.",
        },
    },

    # ═══════════ Semax (intranasal) ═══════════
    "semax": {
        "overview": {
            "function": "Cognitive enhancement, neuroprotection, mood support",
            "mechanism_of_action": (
                "Semax is a synthetic analog of ACTH (4-10) that modulates BDNF (brain-derived "
                "neurotrophic factor) and dopaminergic/serotonergic signaling. It crosses the "
                "blood-brain barrier via intranasal administration, producing rapid cognitive "
                "and mood effects."
            ),
            "considerations": "Most effective via intranasal route. Originally developed in Russia, where it is used clinically for stroke recovery.",
        },
        "benefits": [
            "Enhances cognitive function and memory",
            "Reduces symptoms of depression and anxiety",
            "Promotes neuroprotection and neurogenesis",
            "Improves focus and attention",
            "Enhances learning capacity",
            "Reduces oxidative stress and inflammation in the brain",
        ],
        "side_effects": {
            "common": [
                "Mild irritation or discomfort at the nostril",
                "Headache",
                "Nausea",
            ],
            "less_common": [
                "Irritability or agitation",
                "Mild insomnia if dosed too late",
            ],
            "rare": [
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "Cognitive enhancement", "timing": "Administer in the morning or early afternoon"},
            {"goal": "Mood improvement", "timing": "Use as needed, typically in the morning"},
            {"goal": "Neuroprotection", "timing": "Consistent daily use over several weeks or months"},
        ],
        "administration": {
            "route": "Intranasal",
            "notes": "Apply 2-3 drops per nostril. Tilt head back slightly for absorption. Avoid blowing nose for 10 minutes after.",
        },
        "legal_status": {
            "us": "Research substance — not FDA approved for human use. Legal for research purposes.",
            "uk": "Classified as research chemical. Not approved for medical treatment.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Intranasal Protocol (5 days on / 2 days off)",
            "standard": {"route": "Intranasal", "frequency": "1-2 times daily (morning / early afternoon)"},
            "dosages": [
                {"indication": "Cognitive enhancement / focus", "schedule": "1x morning, intranasal — 5 on / 2 off", "dose": "300 mcg/day"},
                {"indication": "Mood support / anxiety", "schedule": "1x morning, intranasal — 5 on / 2 off", "dose": "400 mcg/day"},
                {"indication": "Neuroprotection (high dose)", "schedule": "Split AM + early afternoon, intranasal", "dose": "600 mcg/day"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "300 mcg/day intranasal"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "400-600 mcg/day intranasal"},
                {"number": 3, "phase": "Off cycle (Week 5+)", "dose": "Pause or maintain 5 on / 2 off"},
            ],
            "reconstitution": "Most commonly supplied as a pre-made 0.1% nasal spray. Typical application: 2-3 drops per nostril. Store refrigerated.",
        },
    },

    # ═══════════ Selank (intranasal) ═══════════
    "selank": {
        "overview": {
            "function": "Anxiolytic, cognitive support, stress modulation",
            "mechanism_of_action": (
                "Selank is a synthetic heptapeptide (analog of tuftsin) that modulates GABA "
                "neurotransmission and influences enkephalin/serotonin pathways. It produces "
                "anxiolytic effects without sedation, dependence, or cognitive impairment "
                "typical of benzodiazepines."
            ),
            "considerations": "Non-sedating anxiolytic with rapid onset via intranasal route. Originally developed in Russia.",
        },
        "benefits": [
            "Reduces anxiety and stress without sedation",
            "Enhances cognitive function and memory",
            "Promotes neuroprotection and neurogenesis",
            "Improves mood and social behavior",
            "Enhances learning and information processing",
            "Modulates stress response",
        ],
        "side_effects": {
            "common": [
                "Mild irritation or discomfort at the nostril",
                "Drowsiness (occasional)",
                "Headache",
            ],
            "less_common": [
                "Dry mouth",
            ],
            "rare": [
                "Allergic reactions",
            ],
        },
        "timing_goals": [
            {"goal": "Anxiety reduction", "timing": "Administer as needed, typically morning or early afternoon"},
            {"goal": "Cognitive enhancement", "timing": "Use in the morning or early afternoon"},
            {"goal": "Mood improvement", "timing": "Administer as needed, typically in the morning"},
            {"goal": "Acute stress event", "timing": "Apply 30-60 minutes before the stressor"},
        ],
        "administration": {
            "route": "Intranasal",
            "notes": "Apply 2-3 drops per nostril. Tilt head back slightly. Avoid blowing nose for 10 minutes after.",
        },
        "legal_status": {
            "us": "Research substance — not FDA approved for human use. Legal for research purposes.",
            "uk": "Classified as research chemical. Not approved for medical treatment.",
            "canada": "Restricted to research use; not approved for medical treatments.",
        },
        "protocols": {
            "title": "Intranasal Protocol",
            "standard": {"route": "Intranasal", "frequency": "Daily or as needed"},
            "dosages": [
                {"indication": "Mild anxiety / mood support", "schedule": "1-2x daily, intranasal", "dose": "250-500 mcg/day"},
                {"indication": "Standard research dose", "schedule": "1-2x daily, intranasal", "dose": "1 mg/day"},
                {"indication": "High-dose / acute stress", "schedule": "Split AM + afternoon, intranasal", "dose": "2-3 mg/day"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Week 1)", "dose": "250-500 mcg/day intranasal"},
                {"number": 2, "phase": "Standard (Weeks 2-4)", "dose": "1 mg/day intranasal"},
                {"number": 3, "phase": "Acute / on-demand", "dose": "Up to 3 mg/day as needed"},
            ],
            "reconstitution": "Most commonly supplied as a pre-made 0.15% nasal spray. Typical application: 2-3 drops per nostril. Store refrigerated.",
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
    print(f"BATCH UPDATE — {len(UPDATES)} peptides")
    print("=" * 60)

    for slug, payload in UPDATES.items():
        doc = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not doc:
            print(f"\n[SKIP] {slug} — not found in peptide_library")
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
        print(f"     • Overview function: {payload['overview']['function']}")
        print(f"     • {len(payload['benefits'])} benefits | {sum(len(v) for v in payload['side_effects'].values())} side effects | {len(payload['timing_goals'])} timing goals")
        print(f"     • Route: {payload['administration']['route']}")
        print(f"     • Phases:")
        for p in payload["protocols"]["phases"]:
            print(f"        {p['number']}. {p['phase']} → {p['dose']}")

    client.close()
    print("\n" + "=" * 60)
    print("Done. All 5 peptides fully updated (overview + protocols + safety).")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
