"""Seed batch 3: TB-500, Tesamorelin, Thymosin Alpha-1 hubs + Semax merge."""
import asyncio
import os
import uuid
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


def _p(o, n, g, c, s, b, d):
    return {"id": str(uuid.uuid4()), "order": o, "name": n, "goal": g, "compounds": c, "protocol": s, "best_for": b, "duration": d}


def _c(n, d):
    return {"name": n, "dose": d}


# ─────────── TB-500 ───────────
TB500 = {
    "slug": "tb-500", "peptide_slug": "tb-500", "peptide_name": "TB-500",
    "title": "TB-500 Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "Healing & Recovery", "category_slug": "nootropic-cognitive",
    "classification": "Synthetic Thymosin Beta-4",
    "also_known_as": ["TB4", "Thymosin Beta-4"],
    "description": "TB-4 is a naturally occurring peptide that modulates actin dynamics, promotes angiogenesis, supports cell migration, and accelerates tissue repair. TB-500 is the synthetic version used in regenerative and performance protocols.",
    "core_info": {
        "function": "Wound healing, tissue regeneration, anti-inflammatory support.",
        "typical_dosage": "1\u20135 mg subcutaneously, 2\u20133x weekly",
        "administration": "Subcutaneous injection",
        "best_timing": "During recovery or injury phases",
        "common_cycle": "4\u20136 weeks",
        "common_pairings": ["BPC-157", "IGF-1 LR3", "Collagen hydrolysate", "Vitamin D3", "Thymosin Beta-4"],
    },
    "protocols": [
        _p(1, "Full-Body Tissue Regeneration", "Accelerate soft tissue healing, support fascia, reduce inflammation.",
           [_c("TB-500","2 mg (5mg vial in 2 ml water; inject 0.25 ml)")],
           ["Reconstitute 5 mg of TB-500 with 2 mL bacteriostatic water.","Inject 0.25 mL subcutaneously 2x weekly for 4\u20136 weeks.","Reduce to 1 injection every 10\u201314 days for maintenance."],
           "Injury recovery, post-surgery, chronic wear and tear", "4\u20136 weeks"),
        _p(2, "Joint & Connective Tissue Longevity", "Support joint flexibility and connective tissue repair.",
           [_c("TB-500","5 mg"), _c("BPC-157","500 mcg"), _c("Collagen hydrolysate","10 g")],
           ["Inject TB-500 subcutaneously twice weekly for 4 weeks.","Use BPC-157 daily near affected joint or systemically.","Take collagen hydrolysate daily."],
           "Osteoarthritis, joint degeneration, connective tissue stress", "4 weeks"),
        _p(3, "Joint Longevity Performance Support", "Long-term joint resilience and mobility.",
           [_c("TB-500","2 mg"), _c("BPC-157","250 mcg"), _c("Collagen peptides","10 g oral")],
           ["Use TB-500 twice weekly to reduce inflammation.","Inject BPC-157 near commonly stressed joints.","Take collagen daily to support cartilage integrity."],
           "Strength athletes or training over age 40", "4\u20136 weeks"),
        _p(4, "Functional Fitness Tissue Conditioning", "Strengthen connective tissue and reduce stiffness.",
           [_c("TB-500","2 mg"), _c("BPC-157","250 mcg"), _c("Collagen supplement","optional")],
           ["Inject TB-500 every 3\u20134 days for 3 weeks.","Use BPC-157 daily for soft tissue reinforcement.","Combine with collagen post-training."],
           "High-load or high-volume athletic training", "3 weeks"),
        _p(5, "Mid-Season Athlete Regeneration", "Sustain recovery and performance during long competitive seasons.",
           [_c("TB-500","2 mg"), _c("BPC-157","250 mcg"), _c("Vitamin D3","5000 IU oral")],
           ["Inject TB-500 at beginning and midpoint of training weeks.","Use BPC-157 five days weekly.","Supplement Vitamin D3 daily."],
           "Athletes in sports seasons over 8 weeks", "8+ weeks"),
        _p(6, "CNS Recovery & Neuromuscular Reset", "Nervous system recovery and strength restoration.",
           [_c("TB-500","2 mg"), _c("IGF-1 LR3","30 mcg")],
           ["Inject TB-500 subcutaneously at end of training week.","Use IGF-1 LR3 IM after CNS-heavy sessions.","Cycle weekly during neurological stress periods."],
           "Powerlifting or explosive athletic phases", "4\u20136 weeks"),
        _p(7, "3-Day Sprint Interval Repair", "Reduce DOMS and improve sprint recovery.",
           [_c("TB-500","2 mg"), _c("BPC-157","250 mcg")],
           ["Inject TB-500 24 hours before sprint blocks.","Use BPC-157 after sprint sessions.","Repeat weekly for up to 3 weeks."],
           "HIIT, sprinting, track athletes", "Up to 3 weeks"),
        _p(8, "TB-500 + Thymosin Beta-4 Tissue Rescue", "Promote extracellular matrix repair and tissue regeneration.",
           [_c("TB-500","2 mg/week"), _c("Thymosin Beta-4","1 mg 2x weekly"), _c("Collagen peptides","10 g/day")],
           ["Inject both peptides on alternating days.","Take collagen daily with Vitamin C.","Continue for 4\u20136 weeks depending on injury severity."],
           "Tendonitis, post-surgical recovery, ligament injuries", "4\u20136 weeks"),
    ],
}

# ─────────── Tesamorelin ───────────
TESAMORELIN = {
    "slug": "tesamorelin", "peptide_slug": "tesamorelin", "peptide_name": "Tesamorelin",
    "title": "Tesamorelin Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "GH / Secretagogues", "category_slug": "gh-secretagogues",
    "classification": "Synthetic GHRH Analog",
    "also_known_as": ["GHRH analog", "Egrifta"],
    "description": "Tesamorelin is a synthetic GHRH analog that stimulates endogenous growth hormone release. Originally approved for HIV-related lipodystrophy, it is researched for visceral fat reduction, metabolic support, and cognitive benefits.",
    "core_info": {
        "function": "GH stimulation, visceral fat reduction, body composition optimization.",
        "typical_dosage": "2 mg subcutaneously daily",
        "administration": "Subcutaneous injection",
        "best_timing": "Morning, pre-cardio, or before sleep",
        "common_cycle": "8\u201312 weeks",
        "common_pairings": ["AOD-9604", "CJC-1295", "Ipamorelin", "DHEA", "Berberine", "Amlexanox", "Omega-3", "Magnesium Glycinate", "L-Theanine"],
    },
    "protocols": [
        _p(1, "Longevity Hormonal Synergy Support", "Hormonal optimization and age-related metabolic support.",
           [_c("Tesamorelin","2 mg (reconstituted with 1 mL water; inject 0.2\u20130.25 mL SC daily)"), _c("DHEA","25 mg capsule")],
           ["Reconstitute Tesamorelin with 1 mL bacteriostatic water.","Inject 0.2\u20130.25 mL subcutaneously daily.","Take DHEA each morning with food."],
           "Hormonal optimization and age-related metabolic support", "3 months"),
        _p(2, "The Fasted Burner Stack", "Maximize fat oxidation and visceral fat reduction during fasting.",
           [_c("Tesamorelin","2 mg daily"), _c("Amlexanox","100\u2013200 mg oral"), _c("AOD-9604","300 mcg")],
           ["Use Tesamorelin daily.","Take Amlexanox in the morning before fasted cardio.","Use AOD-9604 pre-cardio or during fasting windows."],
           "Intermittent fasting and cardio cutting phases", "8\u201312 weeks"),
        _p(3, "Lean & Toned Stack for Women", "Lean physique support while preserving muscle and feminine shape.",
           [_c("Tesamorelin","1\u20132 mg PM"), _c("CJC-1295 + Ipamorelin","100 mcg each"), _c("AOD-9604","300 mcg")],
           ["Use Tesamorelin nightly.","Inject CJC-1295 + Ipamorelin 5 days weekly before sleep.","Take AOD-9604 in morning or pre-workout."],
           "Body recomposition and toned physique goals", "8\u201312 weeks"),
        _p(4, "Visceral Fat Reduction Optimization", "Support abdominal fat reduction and metabolic flexibility.",
           [_c("Tesamorelin","2 mg"), _c("Berberine","500 mg"), _c("Omega-3 DHA/EPA","2 g")],
           ["Inject Tesamorelin before sleep daily.","Take Berberine with carbohydrate-heavy meals.","Supplement Omega-3 daily with food."],
           "Metabolic syndrome or stubborn midsection fat", "12 weeks"),
        _p(5, "Advanced GH Pulse Recovery", "Enhance sleep-related GH pulses and recovery.",
           [_c("Tesamorelin","2 mg"), _c("Magnesium Glycinate","400 mg"), _c("L-Theanine","200 mg")],
           ["Inject Tesamorelin before bedtime.","Take Magnesium and L-Theanine 30\u201360 min before sleep.","Maintain deep sleep hygiene during the cycle."],
           "Recovery phases, sleep support, hormonal restoration", "8 weeks"),
    ],
}

# ─────────── Thymosin Alpha-1 ───────────
THYMOSIN = {
    "slug": "thymosin-alpha", "peptide_slug": "thymosin-alpha", "peptide_name": "Thymosin Alpha-1",
    "title": "Thymosin Alpha-1 Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "Immune Support", "category_slug": "nootropic-cognitive",
    "classification": "Immune-modulating Peptide",
    "also_known_as": ["Ta1", "T\u03b11"],
    "description": "Thymosin Alpha-1 enhances T-cell activity, improves cytokine signaling, and supports immune checkpoint regulation. Researched in hepatitis, oncology support, viral defense, and autoimmune modulation.",
    "core_info": {
        "function": "Immune enhancement, antiviral defense, immune modulation, recovery support.",
        "typical_dosage": "1\u20131.6 mg subcutaneously, 2\u20133x weekly",
        "administration": "Subcutaneous injection",
        "best_timing": "Before high-risk periods or during illness onset",
        "common_cycle": "5 days to 4\u20136 weeks (varies)",
        "common_pairings": ["LL-37", "BPC-157", "TB-500", "Vitamin C", "Vitamin D3", "NAD+", "Resveratrol", "Melatonin", "Omega-3"],
    },
    "protocols": [
        _p(1, "Immunity Booster Stack for Travel Seasons", "Enhance infection resistance and immune readiness during high-risk travel.",
           [_c("Thymosin Alpha-1","1.5 mg 2x weekly"), _c("LL-37","50 mcg daily for 7 days"), _c("Vitamin C","1000 mg 2x daily")],
           ["Inject Ta1 two days apart weekly.","Use LL-37 during the first week of travel.","Take Vitamin C morning and evening with meals."],
           "Before international travel, conferences, or flu season", "2 weeks"),
        _p(2, "Autoimmune Modulation + Resilience", "Immune modulation and inflammation control.",
           [_c("Thymosin Alpha-1","1.5 mg 2x weekly"), _c("TB-500","2 mg weekly"), _c("Vitamin D3","5000 IU daily")],
           ["Inject Ta1 on non-consecutive days.","Use TB-500 weekly.","Take Vitamin D3 with the largest meal."],
           "Immune dysregulation and autoimmune support", "6 weeks"),
        _p(3, "Emergency Immune Boost 5-Day Protocol", "Rapid immune readiness and inflammatory defense.",
           [_c("Thymosin Alpha-1","1 mg daily"), _c("LL-37","100 mcg daily"), _c("Vitamin C","2 g daily"), _c("Quercetin","500 mg 2x daily")],
           ["Inject peptides daily for 5 days.","Split supplements between morning and evening.","Resume normal supplementation after completion."],
           "At first signs of illness or viral exposure", "5 days"),
        _p(4, "Pre-Travel Immune Fortification", "Strengthen immunity against travel stress and airborne pathogens.",
           [_c("Thymosin Alpha-1","1 mg/day for 5 days"), _c("LL-37","100 mcg/day"), _c("Vitamin D3","10000 IU daily")],
           ["Begin injections 5 days before departure.","Take Vitamin D3 daily.","Continue LL-37 for 2\u20133 days after arrival if needed."],
           "Before long flights and crowded events", "5\u20137 days"),
        _p(5, "Immunosenescence Prevention", "Support healthy immune aging and cellular repair.",
           [_c("Thymosin Alpha-1","750 mcg 3x/week"), _c("NAD+","100 mg weekly"), _c("Resveratrol","200 mg daily")],
           ["Inject Ta1 three times weekly.","Administer NAD+ weekly.","Take resveratrol with a fatty meal."],
           "Longevity-focused immune support", "8\u201312 weeks"),
        _p(6, "Nighttime Immune Regeneration", "Sleep-driven immune repair and recovery.",
           [_c("Thymosin Alpha-1","750 mcg before bed"), _c("Melatonin","3 mg"), _c("Magnesium glycinate","200 mg")],
           ["Inject Ta1 in the evening.","Take melatonin and magnesium 30 min before sleep.","Continue nightly for up to 4 weeks."],
           "High stress, poor sleep, or low immunity", "4 weeks"),
        _p(7, "Ta1 + BPC-157 Mucosal Immunity", "Support mucosal immunity and gut-lung barriers.",
           [_c("Thymosin Alpha-1","1 mg 3x/week"), _c("BPC-157","250 mcg daily")],
           ["Inject Ta1 Monday, Wednesday, and Friday.","Use BPC-157 daily.","Continue protocol for 4\u20136 weeks."],
           "Respiratory weakness or gut-immune support", "4\u20136 weeks"),
        _p(8, "Anti-Inflammatory Weekend Defense", "Fast anti-inflammatory and immune support.",
           [_c("TB-500","2 mg Friday"), _c("Thymosin Alpha-1","1 mg Saturday"), _c("Omega-3","2 g/day")],
           ["Inject peptides on consecutive days.","Take Omega-3 with food.","Repeat weekly during inflammatory periods."],
           "Recovery weekends or inflammatory flare-ups", "Weekly cycles"),
    ],
}

# ─────────── Semax additional protocols ───────────
SEMAX_NEW = [
    _p(11, "Semax AM Cognitive Sharpness Stack", "Clarity, focus, brain energy for demanding mornings.",
       [_c("Semax","300 mcg (1\u20132 sprays)"), _c("Omega-3 DHA","1000 mg"), _c("Rhodiola Rosea","250 mg"), _c("Vitamin B12","1000 mcg")],
       ["Administer 1\u20132 sprays intranasally upon waking.","Take Omega-3, Rhodiola, and B12 with water.","Begin mentally demanding work within 30 minutes."],
       "Demanding mornings, meetings, mental fatigue", "4 weeks"),
    _p(12, "Academic Study Focus", "Concentration, verbal recall, learning depth.",
       [_c("Semax","300 mcg"), _c("Caffeine","50\u2013100 mg"), _c("Citicoline","250 mg"), _c("L-Tyrosine","500 mg")],
       ["Take Citicoline and L-Tyrosine 30 min before studying.","Use Semax immediately before study session.","Add caffeine only if needed for alertness."],
       "Long reading or dense information absorption", "As needed"),
    _p(13, "Deep Learning Retention Protocol", "Memory encoding and neural efficiency.",
       [_c("Semax","300 mcg"), _c("Uridine Monophosphate","250 mg"), _c("DHA","1000 mg"), _c("Citicoline","250 mg")],
       ["Take uridine, citicoline, and DHA with breakfast.","Use Semax 15\u201330 min before studying.","Take short mental breaks every hour."],
       "Certifications or new skill acquisition", "4 weeks"),
    _p(14, "Semax + Selank Stress-Focus Dual Protocol", "Balance mental alertness with calm.",
       [_c("Semax","300 mcg"), _c("Selank","300 mcg"), _c("Vitamin C","500 mg"), _c("L-Theanine","200 mg")],
       ["Administer Semax in one nostril and Selank in the other.","Take L-Theanine and Vitamin C post-application.","Use during emotionally taxing days."],
       "Interviews, public speaking, emotionally taxing days", "As needed"),
    _p(15, "Jet Lag Brain Realignment", "Reduce brain fog and accelerate circadian reset.",
       [_c("Semax","300 mcg"), _c("Melatonin","0.5\u20131 mg"), _c("Dihexa","10 mg"), _c("Vitamin D3","1000 IU")],
       ["Use Semax upon waking in new time zone.","Take Dihexa in the morning.","Use melatonin at local bedtime."],
       "After long international flights", "1 week"),
]

HUBS = [TB500, TESAMORELIN, THYMOSIN]


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    for hub in HUBS:
        await db.stack_hubs.delete_many({"slug": hub["slug"]})
        await db.stack_hubs.insert_one(hub.copy())
        print(f"INSERTED hub: {hub['title']} ({len(hub['protocols'])} protocols)")

    # Append new protocols to Semax hub
    semax = await db.stack_hubs.find_one({"slug": "semax"}, {"_id": 0})
    if semax:
        existing_names = {p["name"] for p in semax.get("protocols", [])}
        appended = 0
        for sp in SEMAX_NEW:
            if sp["name"] not in existing_names:
                semax["protocols"].append(sp)
                appended += 1
        await db.stack_hubs.update_one({"slug": "semax"}, {"$set": {"protocols": semax["protocols"]}})
        print(f"MERGED into Semax hub: +{appended} new protocols (total: {len(semax['protocols'])})")

    total = await db.stack_hubs.count_documents({})
    total_protocols = 0
    async for h in db.stack_hubs.find({}, {"_id": 0, "protocols": 1}):
        total_protocols += len(h.get("protocols", []))
    print(f"\nTotal hubs: {total}  |  Total protocols: {total_protocols}")

    docs = await db.stack_hubs.find({}, {"_id": 0}).to_list(None)
    with open("seed_stack_hubs_all.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False, default=str)
    print(f"Exported {len(docs)} hubs to seed_stack_hubs_all.json")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
