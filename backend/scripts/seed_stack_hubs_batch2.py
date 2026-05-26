"""Seed batch 2: IGF-1 LR3, Ipamorelin, Selank, Semax hubs."""
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


HUBS = []

# ─────────── IGF-1 LR3 ───────────
HUBS.append({
    "slug": "igf-1-lr3", "peptide_slug": "igf-1-lr3", "peptide_name": "IGF-1 LR3",
    "title": "IGF-1 LR3 Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "Muscle Growth & Recovery", "category_slug": "muscle-growth",
    "classification": "Long-Acting IGF-1 Analog",
    "also_known_as": ["Insulin-like Growth Factor 1 LR3", "Long R3 IGF-1"],
    "description": "A modified IGF-1 with extended half-life that promotes nitrogen retention, protein synthesis and hyperplasia while resisting IGF-binding proteins for superior bioavailability.",
    "core_info": {
        "function": "Muscle growth, recovery, fat loss, cellular regeneration.",
        "typical_dosage": "20\u201380 mcg post-exercise, 5 days/week",
        "administration": "Subcutaneous or intramuscular injection",
        "best_timing": "Immediately post-workout",
        "common_cycle": "4\u20136 weeks",
        "common_pairings": ["BPC-157", "TB-500", "Creatine", "Acetyl-L-Carnitine", "Fast-digesting carbs"],
    },
    "protocols": [
        _p(1, "Anabolic Response Window", "Boost hypertrophy, glucose uptake, and accelerate recovery.",
           [_c("IGF-1 LR3","40 mcg"), _c("Bacteriostatic water","1 mL")],
           ["Reconstitute IGF-1 LR3 with bacteriostatic water.","Draw 40 mcg post-workout.","Inject intramuscularly into the trained muscle."],
           "Intense workouts", "4\u20136 weeks"),
        _p(2, "Post-Leg Day Reinforcement", "Fast quad/hamstring recovery, reduce soreness, improve adaptation.",
           [_c("IGF-1 LR3","40 mcg"), _c("BPC-157","250 mcg"), _c("TB-500","2 mg (optional)")],
           ["Administer IGF-1 LR3 intramuscularly into quads post-leg training.","Inject BPC-157 subcutaneously near knees/hamstrings.","Use TB-500 weekly if extra repair needed."],
           "Heavy leg sessions, DOMS-prone athletes", "4 weeks"),
        _p(3, "CNS Recovery & Neuromuscular Reset", "Rebalance the nervous system and restore strength output.",
           [_c("IGF-1 LR3","30 mcg"), _c("TB-500","2 mg")],
           ["Inject TB-500 subcutaneously at end of training week.","Use IGF-1 LR3 IM after CNS-heavy training.","Cycle weekly during high neurological loads."],
           "Power training, CNS recovery", "4 weeks"),
        _p(4, "Fasted Training Tissue Preservation", "Prevent muscle loss and aid post-fasted recovery.",
           [_c("IGF-1 LR3","20 mcg"), _c("BPC-157","250 mcg")],
           ["Inject IGF-1 LR3 immediately post fasted training.","Use BPC-157 subcutaneously before bed.","Follow 5-day cycles with 2-day breaks."],
           "Intermittent fasting or empty-stomach training", "4 weeks"),
        _p(5, "High-Volume Recovery Stack", "Prevent overtraining fatigue and restore intensity.",
           [_c("IGF-1 LR3","30 mcg"), _c("BPC-157","250 mcg"), _c("TB-500","2 mg (optional)")],
           ["Inject BPC-157 daily during deload weeks.","Use IGF-1 LR3 post-training every other session.","TB-500 weekly if fatigue is high."],
           "High-frequency splits and advanced hypertrophy", "4\u20136 weeks"),
        _p(6, "Microdosing Power Builder", "Lean muscle growth, recovery, and strength.",
           [_c("IGF-1 LR3","20 mcg"), _c("Bacteriostatic water","1 mL")],
           ["Reconstitute IGF-1 LR3.","Draw 20 mcg and inject IM post-workout.","Use on alternate training days."],
           "Power without bloating", "4 weeks"),
        _p(7, "Age-Adjusted Anabolic Recovery", "Faster recovery for aging athletes, retain strength, protect joints.",
           [_c("IGF-1 LR3","20 mcg"), _c("BPC-157","250 mcg")],
           ["Inject IGF-1 LR3 post-training 2x/week.","Use BPC-157 daily in evening.","Monitor recovery and reduce frequency if needed."],
           "Athletes 40+ training at high intensity", "4 weeks"),
        _p(8, "Lean Mass Rebuilder", "Enhance lean mass retention and faster recovery.",
           [_c("IGF-1 LR3","30 mcg"), _c("Creatine monohydrate","5 g")],
           ["Inject IGF-1 LR3 post-workout.","Take creatine daily with post-workout shake.","Repeat 5 days/week."],
           "Lean muscle gain during low-calorie phases", "4\u20136 weeks"),
        _p(9, "Muscle Density & Repair Stabilization", "Improve muscle quality and aid recovery from overtraining.",
           [_c("IGF-1 LR3","25 mcg"), _c("TB-500","2 mg")],
           ["Inject IGF-1 LR3 into target muscle post heavy session.","Use TB-500 weekly for deeper tissue support.","Run during stabilization training."],
           "Lifters returning to full intensity", "4\u20136 weeks"),
        _p(10, "Lagging Body Parts IM Cycle", "Stimulate underdeveloped muscles via localized hypertrophy.",
           [_c("IGF-1 LR3","30 mcg")],
           ["Inject directly into the lagging muscle group post-training.","Use 4\u20135 days/week targeting different weak points."],
           "Lifters bringing up weak body parts", "3\u20134 weeks"),
        _p(11, "Neural-Muscular Coordination", "Enhance motor control, neural drive, and synaptic plasticity.",
           [_c("IGF-1 LR3","25 mcg"), _c("Acetyl-L-Carnitine","500 mg oral")],
           ["Inject IGF-1 LR3 into trained muscles post fine-motor exercises.","Take ALCAR daily in the morning.","Use 4x/week."],
           "Olympic lifters, gymnasts, martial artists", "3 weeks"),
        _p(12, "Glycogen Recovery Timing Cycle", "Enhance glycogen re-synthesis and restore endurance.",
           [_c("IGF-1 LR3","30 mcg"), _c("Fast-digesting carbs","30 g oral")],
           ["Inject IGF-1 LR3 post workout into large muscle group.","Consume carbs within 15 minutes of injection.","Use on high-depletion days."],
           "Endurance / high-volume athletes", "4 weeks"),
        _p(13, "Strength Plateau Breakthrough", "Boost strength progression and output.",
           [_c("IGF-1 LR3","40 mcg"), _c("Creatine monohydrate","5 g"), _c("BPC-157","250 mcg")],
           ["Inject IGF-1 LR3 post-heavy workout.","Take creatine daily.","Use BPC-157 every other day."],
           "Lifters breaking strength plateaus", "4 weeks"),
        _p(14, "Functional Mass Builder", "Lean muscle gain and joint resilience.",
           [_c("IGF-1 LR3","40 mcg"), _c("BPC-157","250 mcg")],
           ["Inject IGF-1 LR3 IM into trained muscle.","Use BPC-157 at night.","Follow sessions with a protein-rich meal."],
           "Strength without fat gain", "4\u20136 weeks"),
    ],
})

# ─────────── Ipamorelin ───────────
HUBS.append({
    "slug": "ipamorelin", "peptide_slug": "ipamorelin", "peptide_name": "Ipamorelin",
    "title": "Ipamorelin Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "GH / Secretagogues", "category_slug": "gh-secretagogues",
    "classification": "Selective GH Secretagogue (Pentapeptide)",
    "also_known_as": [],
    "description": "Ipamorelin is a synthetic pentapeptide that mimics ghrelin to selectively stimulate GH release from the pituitary, with minimal impact on cortisol or prolactin.",
    "core_info": {
        "function": "Selective growth hormone release without affecting other hormones.",
        "typical_dosage": "100\u2013200 mcg",
        "administration": "Subcutaneous or intramuscular injection",
        "best_timing": "Pre-workout, post-dinner, or bedtime",
        "common_cycle": "8 weeks on / 2 weeks off",
        "common_pairings": ["CJC-1295", "AOD-9604", "GHK-Cu", "Caffeine", "Citrulline Malate", "Melatonin"],
    },
    "protocols": [
        _p(1, "Pre-Workout Mild Energy Enhancer", "Energy enhancement, fat oxidation, GH release, blood flow.",
           [_c("Ipamorelin","100 mcg"), _c("Caffeine","100 mg"), _c("Beetroot powder","1 tsp")],
           ["Inject Ipamorelin 30 min before workout.","Take caffeine and beetroot mixed in water.","Begin workout 15\u201320 minutes later."],
           "Light to medium-intensity workouts", "4\u20136 weeks"),
        _p(2, "Pre-Workout GH Peptide Energy Cycle", "Promotes blood flow, GH spike, and recovery.",
           [_c("Ipamorelin","100 mcg"), _c("Arginine","6 g"), _c("Citrulline Malate","8 g")],
           ["Inject Ipamorelin 30 min before fasted workouts.","Mix Arginine and Citrulline in a pre-workout shake.","Train 30\u201360 minutes after."],
           "Morning or high-intensity training", "6 weeks"),
        _p(3, "Post-Fast GH Pulse Enhancement", "Amplify post-fasting GH surge, retain muscle, speed metabolic recovery.",
           [_c("Ipamorelin","100 mcg"), _c("CJC-1295","100 mcg"), _c("Electrolytes (Na/K/Mg)","blend")],
           ["Inject Ipamorelin + CJC-1295 immediately after breaking a fast.","Rehydrate with a full-spectrum electrolyte drink.","Resume normal nutrition post-dose."],
           "24\u201372h fasts or intermittent fasting", "4 weeks"),
        _p(4, "Hormonal Balance Stack for Women 40+", "Hormonal rhythm support, skin/hair, mood stability.",
           [_c("CJC-1295 + Ipamorelin","100 mcg each nightly"), _c("GHK-Cu","2 mg 3x weekly"), _c("Omega-3","1000 mg daily")],
           ["Inject CJC-1295 + Ipamorelin at bedtime.","Inject GHK-Cu in the morning, 3 days/week.","Take Omega-3 with breakfast."],
           "Perimenopause and menopause", "8 weeks"),
        _p(5, "High-Protein Diet Peptide Enhancer", "Satiety, recovery, optimized protein metabolism.",
           [_c("Ipamorelin","100 mcg"), _c("AOD-9604","250 mcg"), _c("Magnesium glycinate","200 mg")],
           ["Inject AOD-9604 pre-breakfast.","Inject Ipamorelin post-dinner or pre-sleep.","Magnesium before bed for muscle recovery."],
           "High-protein, low-carb cutting diets", "6\u20138 weeks"),
        _p(6, "Nighttime Fat Burn + Deep Sleep", "Sleep quality, GH release overnight, fat burning.",
           [_c("Ipamorelin","200 mcg"), _c("Melatonin","3 mg")],
           ["Inject Ipamorelin 30 min before bed.","Take melatonin capsule immediately after.","Avoid screens and stimulants after injection."],
           "Cutting phases (nightly use)", "6 weeks"),
        _p(7, "Muscle Preservation & Sarcopenia Stack", "Lean muscle, GH release, strength support.",
           [_c("Ipamorelin","200 mcg"), _c("CJC-1295 no DAC","200 mcg"), _c("Creatine monohydrate","5 g")],
           ["Inject Ipamorelin + CJC-1295 together SC before bed.","Daily injections 8 weeks, then 2 weeks off.","Take creatine daily."],
           "40+ athletes and catabolic states", "8 weeks on / 2 weeks off"),
    ],
})

# ─────────── Selank ───────────
HUBS.append({
    "slug": "selank", "peptide_slug": "selank", "peptide_name": "Selank",
    "title": "Selank Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "Nootropic / Cognitive", "category_slug": "nootropic-cognitive",
    "classification": "Synthetic Heptapeptide (Tuftsin Analog)",
    "also_known_as": [],
    "description": "Selank is a synthetic heptapeptide based on tuftsin that modulates immune and nervous systems. Enhances serotonin and GABA activity for anxiety reduction and cognitive clarity.",
    "core_info": {
        "function": "Anxiolytic, cognitive support, immune modulation.",
        "typical_dosage": "250\u2013600 mcg intranasally, 1\u20132x/day",
        "administration": "Intranasal spray",
        "best_timing": "Morning or before stressful tasks",
        "common_cycle": "2\u20136 weeks",
        "common_pairings": ["Ashwagandha", "L-Theanine", "Magnesium Glycinate", "Rhodiola", "Holy Basil", "Vitamin B6", "Ginkgo"],
    },
    "protocols": [
        _p(1, "Weekend Brain Focus + Calm Blend", "Relaxed focus, mental sharpness, emotional balance.",
           [_c("Selank","300 mcg nasal spray"), _c("L-Theanine","200 mg"), _c("Magnesium glycinate","300 mg")],
           ["Administer Selank in the morning via nasal spray.","Take L-Theanine and magnesium with first meal.","Use for 2\u20133 consecutive days during downtime."],
           "Weekend decompression", "2\u20133 days"),
        _p(2, "Stress Resilience & Mood Modulation", "Reduces anxiety, supports stress management, stabilizes mood.",
           [_c("Selank","300 mcg nasal spray"), _c("Ashwagandha extract","600 mg"), _c("Magnesium threonate","1000 mg")],
           ["Administer Selank intranasally in morning.","Take ashwagandha + magnesium with first meal.","Avoid high caffeine intake."],
           "High-stress work or emotional fatigue", "4\u20136 weeks"),
        _p(3, "Adrenal Health + Mood Balance", "Stabilize cortisol, reduce anxiety, recover from chronic stress.",
           [_c("Selank","300 mcg intranasal"), _c("Ashwagandha","600 mg"), _c("BPC-157","250 mcg daily")],
           ["Use Selank during high-stress windows.","Take Ashwagandha with breakfast or lunch.","Inject BPC-157 systemically once daily."],
           "Entrepreneurs, caregivers, prolonged stress", "4\u20136 weeks"),
        _p(4, "Mood Stability + Anxiety Reduction", "Calm anxiety, emotional resilience, mood regulation.",
           [_c("Selank","300 mcg intranasally"), _c("Ashwagandha extract","600 mg daily"), _c("Magnesium glycinate","400 mg nightly")],
           ["Use Selank in morning or before stressful tasks.","Take Ashwagandha after meals.","Magnesium before bed."],
           "Stress-induced mood swings, mild anxiety, burnout", "4\u20136 weeks"),
        _p(5, "Public Speaking Mental Edge", "Vocal clarity, reduced social anxiety, presence.",
           [_c("Selank","300 mcg"), _c("Citicoline","250 mg"), _c("L-Theanine","200 mg"), _c("Rhodiola Rosea","250 mg")],
           ["Take Citicoline + Rhodiola 90 min before event.","Use Selank 15\u201330 min before stage.","L-Theanine earlier to manage jitters."],
           "Keynotes, speeches, presentations", "As needed"),
        _p(6, "Performance Anxiety Reduction", "Reduce anticipatory stress, calm the mind, improve clarity.",
           [_c("Selank","300 mcg"), _c("L-Theanine","200 mg"), _c("Magnesium Glycinate","400 mg"), _c("Holy Basil Extract","250 mg")],
           ["Selank 30\u201360 min before event.","L-Theanine + Holy Basil earlier in the day.","Magnesium at night for regulation."],
           "Speeches, tests, high-pressure meetings", "As needed"),
        _p(7, "Brain Fog Reset with Adaptogens", "Calm mental clutter, reset neurotransmitters, improve energy.",
           [_c("Selank","300 mcg"), _c("Rhodiola Rosea","250 mg"), _c("Ashwagandha","300 mg"), _c("Vitamin C","500 mg")],
           ["Use Selank late morning or before focus tasks.","Adaptogens with breakfast.","Vitamin C mid-afternoon to reduce cortisol."],
           "High-stress periods or post-travel recovery", "2\u20134 weeks"),
        _p(8, "Creative Flow State Enhancer", "Verbal fluency, reduced inner chatter, idea flow.",
           [_c("Selank","300 mcg"), _c("L-Theanine","200 mg"), _c("Phosphatidylserine","100 mg"), _c("Cold-brew green tea","8 oz")],
           ["L-Theanine + phosphatidylserine 30 min before creative task.","Sip cold-brew green tea slowly while working.","Selank just before starting."],
           "Writing, design, brainstorming sessions", "As needed"),
        _p(9, "High-Stakes Presentation Clarity", "Sharpen speech, reduce anxiety, improve confidence and recall.",
           [_c("Selank","300 mcg"), _c("L-Theanine","200 mg"), _c("Vitamin B6","50 mg"), _c("Ginkgo Biloba","120 mg")],
           ["Selank 15\u201320 min before event.","Theanine + B6 an hour prior.","Ginkgo daily for verbal fluidity."],
           "Speaking events, negotiations, on-camera roles", "As needed"),
    ],
})

# ─────────── Semax ───────────
HUBS.append({
    "slug": "semax", "peptide_slug": "semax", "peptide_name": "Semax",
    "title": "Semax Stack Library", "subtitle": "Premium Protocol Collection",
    "category": "Nootropic / Cognitive", "category_slug": "nootropic-cognitive",
    "classification": "Synthetic ACTH (4-10) Analog",
    "also_known_as": [],
    "description": "A synthetic heptapeptide derived from ACTH fragments that increases BDNF levels and supports neurogenesis, memory, and recovery from brain injuries.",
    "core_info": {
        "function": "Nootropic, neuroprotection, dopamine modulation, stroke recovery.",
        "typical_dosage": "200\u2013600 mcg intranasally, 1\u20132x/day",
        "administration": "Intranasal spray",
        "best_timing": "Morning, before mental tasks, or before high-stakes events",
        "common_cycle": "2\u20136 weeks",
        "common_pairings": ["Selank", "L-Theanine", "Alpha-GPC", "Citicoline", "Lion's Mane", "Caffeine"],
    },
    "protocols": [
        _p(1, "Executive Focus + Decision-Making", "Executive function, working memory, decision clarity.",
           [_c("Semax","300 mcg"), _c("Caffeine + L-Theanine","100 mg / 200 mg"), _c("Creatine","5 g daily")],
           ["Use Semax before high-pressure decision sessions.","Caffeine/theanine combo mid-morning.","Add creatine to a morning shake."],
           "High cognitive load situations", "4 weeks"),
        _p(2, "Cognitive Performance Under Stress", "Calm focus, neuroprotection, improved decision-making.",
           [_c("Semax","300 mcg"), _c("Selank","300 mcg"), _c("L-Theanine","200 mg")],
           ["Semax in the morning for clarity.","Selank in afternoon during high-stress phases.","L-Theanine with or without caffeine as needed."],
           "Deadline pressure, anxiety-prone days", "4\u20136 weeks"),
        _p(3, "Nootropic Focus + Memory Enhancement", "Enhance focus, memory retention, support neurogenesis.",
           [_c("Semax","300 mcg"), _c("Dihexa","10 mg orally"), _c("L-Theanine","200 mg")],
           ["Semax via nasal spray before mental tasks.","Dihexa orally in the morning.","Combine L-Theanine with caffeine for smooth stimulation."],
           "Students, executives, creatives", "4\u20136 weeks"),
        _p(4, "Executive Brain Optimization Cycle", "Strategic thinking, multi-tasking, stress resistance.",
           [_c("Semax","300 mcg"), _c("Dihexa","10 mg"), _c("Alpha-GPC","300 mg"), _c("Magnesium L-Threonate","2000 mg")],
           ["Dihexa + Alpha-GPC in the morning.","Semax before high-stakes decision-making.","Magnesium in the evening to reset the nervous system."],
           "CEOs, team leads, decision-makers", "4 weeks"),
        _p(5, "Podcast Host Verbal Fluidity", "Speech recall, fluidity, on-air mental agility.",
           [_c("Semax","300 mcg"), _c("Citicoline","250 mg"), _c("Rhodiola Rosea","300 mg"), _c("L-Theanine","100 mg")],
           ["Citicoline + Rhodiola 60 min before recording.","Semax right before going on air.","L-Theanine if under pressure."],
           "Podcasting, interviews, webinars", "As needed"),
        _p(6, "Focus + Flow + Recovery Combo", "Enter flow state, calm focus, speed recovery.",
           [_c("Semax","300 mcg"), _c("L-Theanine","200 mg"), _c("GABA","100 mg"), _c("Magnesium Glycinate","400 mg")],
           ["Semax before deep work session.","L-Theanine + GABA with water during breaks.","Magnesium in the evening for recovery."],
           "Long creative or coding sessions", "4\u20136 weeks"),
        _p(7, "Sleep Deprivation Cognitive Support", "Maintain clarity and memory when under-rested.",
           [_c("Semax","300 mcg"), _c("N-Acetyl L-Tyrosine","350 mg"), _c("Alpha-GPC","300 mg"), _c("Ashwagandha","300 mg")],
           ["Semax upon waking from limited sleep.","Alpha-GPC + Tyrosine mid-morning.","Ashwagandha in afternoon to reduce cortisol buildup."],
           "Red-eye flights, late deadlines, parenting", "As needed"),
        _p(8, "Startup Founder Focus & Resilience", "Sharp focus, cognitive endurance, innovation.",
           [_c("Semax","300 mcg"), _c("Caffeine","50\u2013100 mg"), _c("Panax Ginseng","200 mg"), _c("Lion's Mane","1000 mg")],
           ["Lion's Mane + Ginseng at start of workday.","Semax before creative or problem-solving sessions.","Caffeine only as needed."],
           "Long workdays, product launches, brainstorming", "4\u20138 weeks"),
        _p(9, "Cold Shower Morning Wake-Up", "Dopamine boost, alertness, peak performance priming.",
           [_c("Semax","300 mcg"), _c("Vitamin B12","1000 mcg sublingual"), _c("MCT Oil","1 tbsp"), _c("L-Tyrosine","500 mg")],
           ["Semax immediately upon waking.","B12, MCT oil, L-Tyrosine after a cold shower.","Most mentally demanding task within 30 minutes."],
           "Early-morning work or sleep-deprived starts", "As needed"),
        _p(10, "High-Volume Reading & Recall", "Mental stamina, reading comprehension, memory retention.",
            [_c("Semax","300 mcg"), _c("Citicoline","250 mg"), _c("Lion's Mane","1000 mg"), _c("Omega-3 (DHA)","1000 mg")],
            ["Lion's Mane + Omega-3 with breakfast.","Citicoline 30 min before reading sessions.","Semax before starting high-volume study."],
            "Exam prep, research sprints, content absorption", "4 weeks"),
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

    docs = await db.stack_hubs.find({}, {"_id": 0}).to_list(None)
    with open("seed_stack_hubs_all.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False, default=str)
    print(f"Exported {len(docs)} hubs to seed_stack_hubs_all.json")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
