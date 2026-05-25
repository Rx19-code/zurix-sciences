"""
Seed 5 additional stack hubs:
- BPC-157 (15 protocols)
- CJC-1295 (15 protocols)
- PT-141 (1 protocol)
- DSIP (2 protocols)
- GHK-Cu (7 protocols)

Data extracted from user-provided PDFs (May 2026).
"""
import asyncio
import os
import uuid
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


def _proto(order, name, goal, compounds, steps, best_for, duration):
    return {
        "id": str(uuid.uuid4()),
        "order": order,
        "name": name,
        "goal": goal,
        "compounds": compounds,
        "protocol": steps,
        "best_for": best_for,
        "duration": duration,
    }


def _c(n, d):
    return {"name": n, "dose": d}


HUBS = []

# ─────────────────── BPC-157 ───────────────────
HUBS.append({
    "slug": "bpc-157",
    "peptide_slug": "bpc-157",
    "peptide_name": "BPC-157",
    "title": "BPC-157 Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "Healing & Recovery",
    "category_slug": "nootropic-cognitive",
    "classification": "Pentadecapeptide (15 amino acids)",
    "also_known_as": ["Body Protection Compound 157"],
    "description": (
        "BPC-157 is a synthetic peptide derived from the Body Protection Compound found in gastric juice. "
        "Known for tissue repair, anti-inflammatory and cytoprotective effects, with applications spanning "
        "gut health, joints, tendons, and muscle recovery."
    ),
    "core_info": {
        "function": "Accelerates healing of muscles, tendons, ligaments, and gut tissue. Anti-inflammatory and cytoprotective.",
        "typical_dosage": "250\u2013500 mcg, 1\u20132x daily",
        "administration": "Subcutaneous injection (oral also possible)",
        "best_timing": "Anytime; often near training or injury site",
        "common_cycle": "4\u20138 weeks",
        "common_pairings": ["TB-500", "IGF-1 LR3", "CJC-1295/Ipamorelin", "GHK-Cu", "L-Glutamine", "Collagen Hydrolysate", "Curcumin", "Fish Oil"],
    },
    "protocols": [
        _proto(1, "Gut Repair & Integrity Stack", "Heal the GI tract, reduce digestive inflammation, recover after antibiotic use.",
               [_c("BPC-157", "500 mcg"), _c("Zinc Carnosine", "75 mg"), _c("L-Glutamine", "5 g")],
               ["Combine BPC-157, Zinc Carnosine, and L-Glutamine.", "Administer as per individual compound instructions."],
               "Leaky gut, digestive inflammation, post-antibiotic recovery", "4 weeks"),
        _proto(2, "Joint & Connective Tissue Stack", "Promote repair and regeneration of joints, tendons, and ligaments.",
               [_c("BPC-157", "500 mcg"), _c("TB-500", "5 mg"), _c("Collagen Hydrolysate", "10 g")],
               ["Combine BPC-157 and TB-500.", "Take Collagen Hydrolysate daily."],
               "Joint degeneration, tendon stress, osteoarthritis", "4\u20136 weeks"),
        _proto(3, "Chronic Inflammation Reset Stack", "Reduce systemic inflammation and autoimmune-related fatigue.",
               [_c("BPC-157", "500 mcg"), _c("Curcumin", "500 mg"), _c("Fish Oil", "2 g EPA/DHA")],
               ["Administer BPC-157 daily.", "Take Curcumin and Fish Oil with meals."],
               "Chronic inflammation, autoimmune discomfort, systemic fatigue", "4 weeks"),
        _proto(4, "Anti-Aging Regeneration Stack", "Support longevity, cellular regeneration, and optimize recovery.",
               [_c("Epitalon", "10 mg"), _c("BPC-157", "500 mcg"), _c("GHK-Cu", "2 mg")],
               ["Combine Epitalon, BPC-157, and GHK-Cu.", "Administer as per individual compound instructions."],
               "Longevity, cellular regeneration, recovery optimization", "20-day cycles"),
        _proto(5, "Tendon & Ligament Rapid Repair Stack", "Accelerate healing of microtears and strains in soft tissue.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "2 mg")],
               ["Combine BPC-157 and TB-500.", "Administer as per individual compound instructions."],
               "Tendon microtears, ligament strain, soft tissue injuries", "7\u201314 days"),
        _proto(6, "Daily Recovery Maintenance Stack", "Support daily recovery and adaptation for high-volume training.",
               [_c("BPC-157", "250 mcg")],
               ["Take BPC-157 as per instructions."],
               "High-volume training and daily recovery", "2\u20134 weeks"),
        _proto(7, "High-Volume Training Recovery Stack", "Enhance recovery and support hypertrophy during high-frequency training.",
               [_c("BPC-157", "250 mcg"), _c("IGF-1 LR3", "30 mcg"), _c("TB-500", "optional")],
               ["Combine BPC-157 and IGF-1 LR3.", "Add TB-500 if desired for enhanced connective tissue support."],
               "High-frequency training and hypertrophy phases", "4\u20136 weeks"),
        _proto(8, "CrossFit & HIIT Recovery Stack", "Optimize recovery from HIIT and CrossFit activities.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "2 mg"), _c("IGF-1 LR3", "30 mcg")],
               ["Combine BPC-157, TB-500, and IGF-1 LR3.", "Administer as per individual compound instructions."],
               "CrossFit, HIIT, functional training", "4\u20136 weeks"),
        _proto(9, "Endurance Joint Protection Stack", "Protect joints and support recovery for endurance athletes.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "2 mg"), _c("Magnesium Glycinate", "200 mg")],
               ["Combine BPC-157 and TB-500.", "Take Magnesium Glycinate daily."],
               "Marathon prep, triathlon, endurance athletes", "6\u20138 weeks"),
        _proto(10, "Plantar Fascia & Foot Recovery Stack", "Aid healing of plantar fasciitis and running foot injuries.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "2 mg")],
               ["Combine BPC-157 and TB-500.", "Administer as per individual compound instructions."],
               "Plantar fasciitis, running injuries", "2\u20134 weeks"),
        _proto(11, "Functional Fitness Tissue Conditioning Stack", "Enhance tissue conditioning and overall mobility.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "2 mg"), _c("Collagen Peptides", "10 g")],
               ["Combine BPC-157 and TB-500.", "Take Collagen Peptides daily."],
               "Functional fitness and mobility", "3\u20136 weeks"),
        _proto(12, "Deload Week Regenerative Stack", "Facilitate recovery and regeneration during deload phases.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "2 mg")],
               ["Combine BPC-157 and TB-500.", "Administer as per individual compound instructions."],
               "Deload blocks and recovery phases", "1\u20132 weeks"),
        _proto(13, "Fasted Training Preservation Stack", "Preserve muscle mass and aid recovery during fasted training.",
               [_c("IGF-1 LR3", "20 mcg"), _c("BPC-157", "250 mcg")],
               ["Combine IGF-1 LR3 and BPC-157.", "Administer as per individual compound instructions."],
               "Fasted training and muscle preservation", "4 weeks"),
        _proto(14, "Injury Prevention & Prehab Stack", "Support injury prevention and prepare tissues for high-volume training.",
               [_c("BPC-157", "250 mcg"), _c("TB-500", "1 mg"), _c("Fish Oil", "2000 mg")],
               ["Combine BPC-157 and TB-500.", "Take Fish Oil daily."],
               "Injury prevention and high-volume training", "4\u20138 weeks"),
        _proto(15, "Gut-Muscle Axis Recovery Stack", "Support GI stress and digestive recovery for the gut-muscle axis.",
               [_c("BPC-157", "250 mcg"), _c("Probiotic Complex", "daily")],
               ["Take BPC-157 as per instructions.", "Take Probiotic Complex daily."],
               "GI stress and digestive recovery", "2\u20133 weeks"),
    ],
})

# ─────────────────── CJC-1295 ───────────────────
HUBS.append({
    "slug": "cjc-1295",
    "peptide_slug": "cjc-1295-dac",
    "peptide_name": "CJC-1295",
    "title": "CJC-1295 Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "GH / Secretagogues",
    "category_slug": "gh-secretagogues",
    "classification": "GHRH Analog",
    "also_known_as": ["CJC-1295 DAC", "CJC-1295 no DAC", "Modified GRF 1-29 with DAC"],
    "description": (
        "CJC-1295 is a synthetic analog of growth hormone-releasing hormone (GHRH) that stimulates "
        "the pituitary to increase natural GH secretion. The DAC version offers a long half-life "
        "(weekly dosing); the no-DAC version is short-acting (pulse-style)."
    ),
    "core_info": {
        "function": "Growth hormone stimulation, recovery optimization, anti-aging support, body recomposition and fat loss.",
        "typical_dosage": "DAC: 1\u20132 mg weekly  |  no-DAC: 100\u2013300 mcg daily",
        "administration": "Subcutaneous injection",
        "best_timing": "Varies by protocol — often pre-workout or pre-bed",
        "common_cycle": "8\u201312 weeks",
        "common_pairings": ["Ipamorelin", "Epitalon", "BPC-157", "L-Carnitine", "Beta-Alanine", "Berberine", "Magnesium Glycinate", "Ashwagandha", "5-HTP", "L-Tyrosine", "DIM"],
    },
    "protocols": [
        _proto(1, "GH Optimization & Recomposition Stack", "Body recomposition and lean muscle retention.",
               [_c("CJC-1295 DAC", "2 mg weekly"), _c("Ipamorelin", "300 mcg nightly")],
               ["Administer CJC-1295 DAC at 2 mg weekly.", "Administer Ipamorelin at 300 mcg nightly."],
               "Body recomposition and lean muscle retention", "8\u201312 weeks"),
        _proto(2, "Muscle Preservation & Sarcopenia Stack", "Muscle preservation and combating sarcopenia.",
               [_c("CJC-1295 no DAC", "200 mcg"), _c("Ipamorelin", "200 mcg"), _c("Creatine", "5 g")],
               ["Administer CJC-1295 no DAC at 200 mcg.", "Administer Ipamorelin at 200 mcg.", "Take 5 g of Creatine daily."],
               "40+ athletes and catabolic states", "8 weeks"),
        _proto(3, "Longevity & Hormonal Optimization Stack", "Longevity and hormonal optimization.",
               [_c("Epitalon", "10 mg"), _c("CJC-1295", "200 mcg"), _c("Ipamorelin", "200 mcg")],
               ["Administer Epitalon at 10 mg.", "Administer CJC-1295 at 200 mcg.", "Administer Ipamorelin at 200 mcg."],
               "Anti-aging optimization", "20-day cycles + 8-week GH cycle"),
        _proto(4, "Post-Fast GH Pulse Stack", "GH pulse after fasting.",
               [_c("CJC-1295", "100 mcg"), _c("Ipamorelin", "100 mcg"), _c("BPC-157", "optional")],
               ["Administer CJC-1295 at 100 mcg.", "Administer Ipamorelin at 100 mcg.", "Consider BPC-157 if desired."],
               "Intermittent fasting users", "2\u20133x weekly"),
        _proto(5, "Pre-Workout Fat Oxidation Stack", "Fat oxidation before workouts.",
               [_c("CJC-1295", "100 mcg"), _c("Ipamorelin", "100 mcg"), _c("L-Carnitine", "500 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Administer Ipamorelin at 100 mcg.", "Take 500 mg of L-Carnitine."],
               "Cutting phases and fat-loss training", "6\u20138 weeks"),
        _proto(6, "HIIT Performance & Fat Adaptation Stack", "Performance and fat adaptation during HIIT.",
               [_c("CJC-1295", "100 mcg"), _c("Ipamorelin", "100 mcg"), _c("Beta-Alanine", "2 g")],
               ["Administer CJC-1295 at 100 mcg.", "Administer Ipamorelin at 100 mcg.", "Take 2 g of Beta-Alanine."],
               "HIIT and CrossFit athletes", "6 weeks"),
        _proto(7, "Glycemic Reset Stack", "Glycemic reset and glucose control.",
               [_c("CJC-1295", "100 mcg"), _c("Berberine", "500 mg"), _c("Chromium Picolinate", "200 mcg")],
               ["Administer CJC-1295 at 100 mcg.", "Take 500 mg of Berberine.", "Take 200 mcg of Chromium Picolinate."],
               "Carb reintroduction and glucose control", "30 days"),
        _proto(8, "Sleep Optimization GH Stack", "Sleep support, especially during dieting.",
               [_c("CJC-1295", "100 mcg"), _c("Magnesium Glycinate", "400 mg"), _c("Valerian Root", "optional")],
               ["Administer CJC-1295 at 100 mcg.", "Take 400 mg of Magnesium Glycinate.", "Consider Valerian Root if needed."],
               "Sleep support during dieting", "4\u20138 weeks"),
        _proto(9, "Post-Cheat Day Metabolic Reset Stack", "Metabolic reset after cheat days or refeeds.",
               [_c("CJC-1295", "100 mcg"), _c("Ipamorelin", "100 mcg"), _c("Berberine", "500 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Administer Ipamorelin at 100 mcg.", "Take 500 mg of Berberine."],
               "Cheat days and refeeds", "24\u201348 hour reset"),
        _proto(10, "Slow Metabolism Repair Stack", "Repair slow metabolism in low-energy/chronic dieting.",
               [_c("CJC-1295", "100 mcg"), _c("Ipamorelin", "100 mcg"), _c("L-Tyrosine", "500 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Administer Ipamorelin at 100 mcg.", "Take 500 mg of L-Tyrosine."],
               "Low-energy and chronic dieting", "6 weeks"),
        _proto(11, "Appetite & Mood Stability Stack", "Appetite and mood stability.",
               [_c("CJC-1295", "100 mcg"), _c("5-HTP", "100 mg"), _c("Magnesium Glycinate", "200 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Take 100 mg of 5-HTP.", "Take 200 mg of Magnesium Glycinate."],
               "Stress eating and cravings", "4\u20136 weeks"),
        _proto(12, "Insulin Sensitivity Enhancement Stack", "Enhance insulin sensitivity and metabolic flexibility.",
               [_c("CJC-1295", "100 mcg"), _c("Berberine", "500 mg 2x/day")],
               ["Administer CJC-1295 at 100 mcg.", "Take 500 mg of Berberine twice per day."],
               "Insulin resistance and metabolic flexibility", "4\u20138 weeks"),
        _proto(13, "Anti-Cortisol Body Composition Stack", "Reduce cortisol and improve body composition.",
               [_c("CJC-1295", "100 mcg"), _c("Ashwagandha", "600 mg"), _c("Phosphatidylserine", "300 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Take 600 mg of Ashwagandha.", "Take 300 mg of Phosphatidylserine."],
               "Stress-related fat retention", "6 weeks"),
        _proto(14, "High-Stress Metabolism Support Stack", "Support metabolism during high stress.",
               [_c("CJC-1295", "100 mcg"), _c("Rhodiola Rosea", "200 mg"), _c("L-Theanine", "100 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Take 200 mg of Rhodiola Rosea.", "Take 100 mg of L-Theanine."],
               "Burnout and mental fatigue", "4\u20136 weeks"),
        _proto(15, "Post-Menopause Body Composition Stack", "Body composition support post-menopause.",
               [_c("CJC-1295", "100 mcg"), _c("Ipamorelin", "100 mcg"), _c("DIM", "150 mg")],
               ["Administer CJC-1295 at 100 mcg.", "Administer Ipamorelin at 100 mcg.", "Take 150 mg of DIM."],
               "Postmenopausal body composition support", "6\u20138 weeks"),
    ],
})

# ─────────────────── PT-141 ───────────────────
HUBS.append({
    "slug": "pt-141",
    "peptide_slug": "pt-141",
    "peptide_name": "PT-141",
    "title": "PT-141 Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "Hormonal / Sexual Health",
    "category_slug": "hormonal-sexual-health",
    "classification": "Melanocortin Receptor Agonist",
    "also_known_as": ["Bremelanotide"],
    "description": (
        "PT-141 is a melanocortin receptor agonist that stimulates MC-3 and MC-4 receptors in the brain, "
        "enhancing sexual arousal through central nervous system pathways \u2014 not direct vascular mechanisms."
    ),
    "core_info": {
        "function": "Libido enhancement, erectile support, sexual desire enhancement for men and women.",
        "typical_dosage": "1.25\u20132 mg subcutaneous injection",
        "administration": "Subcutaneous injection",
        "best_timing": "30\u201360 minutes before sexual activity",
        "common_cycle": "As-needed only \u2014 not for daily use",
        "common_pairings": ["Melanotan II", "Selank", "Sildenafil / Tadalafil", "Oxytocin", "Kisspeptin"],
    },
    "protocols": [
        _proto(1, "Libido & Performance Enhancement Stack",
               "Enhance libido, arousal, mood, confidence, and overall sexual performance.",
               [_c("PT-141", "1.75 mg"), _c("Melanotan II", "0.25\u20131 mg"), _c("Selank", "250\u2013500 mcg / nostril")],
               ["PT-141: Inject 1.75 mg subcutaneously 45\u201360 min before sexual activity. Not for daily use.",
                "Melanotan II: 0.25\u20131 mg, 2\u20133x weekly. Start low to assess tolerance.",
                "Selank: 250\u2013500 mcg intranasally 1\u20132x daily or as needed for calmness and mood."],
               "Libido support, sexual wellness optimization, confidence enhancement", "As needed"),
    ],
})

# ─────────────────── DSIP ───────────────────
HUBS.append({
    "slug": "dsip",
    "peptide_slug": "dsip",
    "peptide_name": "DSIP",
    "title": "DSIP Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "Sleep & Recovery",
    "category_slug": "nootropic-cognitive",
    "classification": "Sleep / Neuroendocrine Peptide",
    "also_known_as": ["Delta Sleep-Inducing Peptide"],
    "description": (
        "DSIP (Delta Sleep-Inducing Peptide) is a naturally occurring peptide in mammals that promotes "
        "delta-wave activity during deep sleep stages. It influences corticotropin release and "
        "neuroendocrine regulation, supporting adrenal recovery and reducing chronic stress."
    ),
    "core_info": {
        "function": "Sleep induction, stress reduction, hormonal balance, nervous system recovery.",
        "typical_dosage": "100\u2013500 mcg",
        "administration": "Subcutaneous injection",
        "best_timing": "30\u201360 minutes before bedtime",
        "common_cycle": "4\u20136 weeks",
        "common_pairings": ["Epitalon", "CJC-1295", "Ipamorelin", "Magnesium Glycinate", "Glycine"],
    },
    "protocols": [
        _proto(1, "Sleep Optimization + Recovery Stack",
               "Enhance deep sleep cycles, hormonal balance, and overnight recovery.",
               [_c("DSIP", "300 mcg nightly"), _c("Epitalon", "5 mg twice weekly"),
                _c("CJC-1295 + Ipamorelin", "100 mcg each nightly"), _c("Magnesium Glycinate", "200 mg nightly")],
               ["Administer DSIP subcutaneously 30 min before bedtime.",
                "Inject Epitalon subcutaneously twice weekly in the evening.",
                "Combine CJC-1295 and Ipamorelin and inject subcutaneously at night.",
                "Take magnesium glycinate orally with a light evening meal."],
               "Poor sleep quality, nighttime restlessness, stress-related fatigue", "4\u20136 weeks"),
        _proto(2, "Deep Sleep & Regenerative Hormone Support Stack",
               "Increase deep sleep quality, improve GH pulses, and enhance overnight recovery.",
               [_c("DSIP", "300 mcg"), _c("Magnesium Glycinate", "300 mg"), _c("Glycine powder", "3 g")],
               ["Inject DSIP subcutaneously 30 min before bedtime.",
                "Take magnesium and glycine together 1 hour before sleep."],
               "Sleep disturbances, burnout recovery, nighttime cortisol issues", "5 nights/week; cycle monthly"),
    ],
})

# ─────────────────── GHK-Cu ───────────────────
HUBS.append({
    "slug": "ghk-cu",
    "peptide_slug": "ghk-cu",
    "peptide_name": "GHK-Cu",
    "title": "GHK-Cu Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "Aesthetics / Skin",
    "category_slug": "aesthetics-skin",
    "classification": "Signal Peptide (Copper-Binding)",
    "also_known_as": ["Copper Peptide", "GHK-Copper"],
    "description": (
        "GHK-Cu is a copper-binding tripeptide naturally present in human plasma. It supports collagen "
        "synthesis, tissue remodeling, antioxidant defense, and hair follicle stimulation."
    ),
    "core_info": {
        "function": "Skin regeneration, wound healing, anti-aging, hair growth.",
        "typical_dosage": "Topical 0.05\u20130.5% or injectable 2\u20135 mg subcutaneously",
        "administration": "Topical or subcutaneous injection",
        "best_timing": "Varies by protocol",
        "common_cycle": "Varies (typically 4\u201312 weeks)",
        "common_pairings": ["TB-500", "Epitalon", "Collagen Peptides", "Vitamin C", "Hyaluronic Acid", "L-Arginine", "CoQ10"],
    },
    "protocols": [
        _proto(1, "Skin Collagen Remodeling & Firmness Stack",
               "Stimulate collagen production, improve elasticity, and reduce wrinkles.",
               [_c("GHK-Cu", "2 mg"), _c("Microneedling roller", "0.25 mm"), _c("Distilled water", "5 mL")],
               ["Mix 2 mg of GHK-Cu with 5 mL distilled water.",
                "Apply topically after microneedling 2\u20133x weekly.",
                "Do not wash off for at least 6 hours."],
               "Aging skin and firmness enhancement", "8 weeks"),
        _proto(2, "Anti-Fibrotic & Skin Elasticity Restoration Stack",
               "Improve elasticity and skin structure.",
               [_c("GHK-Cu", "2 mg"), _c("TB-500", "2.5 mg"), _c("Vitamin A serum", "0.5%")],
               ["Inject GHK-Cu and TB-500 twice weekly.",
                "Apply vitamin A serum nightly.",
                "Continue for 6 weeks."],
               "Stretch marks and loose skin", "6 weeks"),
        _proto(3, "Anti-Glycation Skin Rejuvenation Protocol",
               "Reduce glycation damage and improve tone.",
               [_c("GHK-Cu topical serum", "1\u20132 mg"), _c("Carnosine", "500 mg"), _c("Alpha-lipoic acid", "100 mg")],
               ["Apply GHK-Cu daily to face and neck.",
                "Take carnosine and ALA with meals.",
                "Cycle every 3 months."],
               "Dull or sugar-damaged skin", "3 months (cycled)"),
        _proto(4, "Cardiovascular & Endothelial Protection Stack",
               "Support circulation and vascular health.",
               [_c("GHK-Cu injectable", "2 mg"), _c("L-Arginine", "3 g"), _c("CoQ10 Ubiquinol", "200 mg")],
               ["Inject GHK-Cu 3x weekly.",
                "Take L-arginine in the morning.",
                "Take CoQ10 with meals."],
               "Healthy aging support", "8 weeks"),
        _proto(5, "Advanced Collagen Synthesis & Firmness Stack",
               "Enhance collagen density and firmness.",
               [_c("GHK-Cu", "2 mg"), _c("Vitamin C", "1000 mg"), _c("Proline + Lysine Complex", "500 mg")],
               ["Apply GHK-Cu serum daily.",
                "Take vitamin C and amino acids with meals.",
                "Maintain for at least 8 weeks."],
               "Post-weight loss or mature skin", "8+ weeks"),
        _proto(6, "Aging Skin Rejuvenation Stack",
               "Improve elasticity and reduce fine lines.",
               [_c("GHK-Cu", "2 mg"), _c("Epitalon", "5 mg"), _c("Collagen Peptides", "10 g")],
               ["Inject GHK-Cu in the morning on alternating days.",
                "Inject Epitalon in the evening twice weekly.",
                "Mix collagen into a morning smoothie."],
               "Visible anti-aging support", "20-day cycles"),
        _proto(7, "Light Rejuvenation & Beginner Anti-Aging Stack",
               "Promote collagen support and hydration.",
               [_c("GHK-Cu injectable", "1 mg"), _c("Hyaluronic acid serum", "2%"), _c("CoQ10", "100 mg")],
               ["Inject GHK-Cu twice weekly.",
                "Apply hyaluronic acid serum daily.",
                "Take CoQ10 with breakfast."],
               "Beginner anti-aging protocol", "4\u20136 weeks"),
    ],
})


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    for hub in HUBS:
        await db.stack_hubs.delete_many({"slug": hub["slug"]})
        await db.stack_hubs.insert_one(hub.copy())
        print(f"INSERTED hub: {hub['title']} ({len(hub['protocols'])} protocols)")

    total = await db.stack_hubs.count_documents({})
    print(f"\nTotal hubs in DB: {total}")

    # Export to JSON for production
    docs = await db.stack_hubs.find({}, {"_id": 0}).to_list(None)
    with open("seed_stack_hubs_all.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False, default=str)
    print(f"Exported {len(docs)} hubs to seed_stack_hubs_all.json")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
