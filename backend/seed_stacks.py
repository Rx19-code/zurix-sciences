"""
Seed peptide stacks from user's PDF data.
All content in English.
"""
import pymongo
import uuid
from datetime import datetime, timezone


def slug_from_name(name):
    return name.lower().replace(" & ", "-").replace("&", "-").replace("/", "-").replace("(", "").replace(")", "").replace(",", "").replace("'", "").replace("  ", " ").replace(" ", "-").strip("-")


STACKS = [
    # === FAT LOSS ===
    {
        "name": "The Fat-for-Fuel Endurance Stack",
        "category": "Fat Loss",
        "goal": "Enhance endurance performance through better fat oxidation and glycogen sparing.",
        "peptides": ["MOTS-c", "Tesamorelin", "AOD-9604"],
        "why_it_works": "This stack helps the body tap into fat stores for energy — especially powerful during fasted cardio or long sessions.",
        "how_to_use": [
            "MOTS-c: 10 mg/day for 7 days before peak training",
            "Tesamorelin: 1-2 mg/day PM",
            "AOD-9604: 300 mcg/day AM or pre-training"
        ],
    },
    {
        "name": "The Shred Stack",
        "category": "Fat Loss",
        "goal": "Accelerate fat loss while preserving lean muscle.",
        "peptides": ["AOD-9604", "MOTS-c", "5-Amino-1MQ"],
        "why_it_works": "Enhances fat oxidation, mitochondrial activity, NAD+ support, and lipolysis — a modern metabolic peptide blend.",
        "how_to_use": [
            "AOD-9604: 300 mcg SubQ daily (AM)",
            "MOTS-c: 10 mg SubQ 2-3x weekly",
            "5-Amino-1MQ: 10 mg oral daily"
        ],
    },
    {
        "name": "The GH-Boost Metabolic Stack",
        "category": "Fat Loss",
        "goal": "Torch fat while preserving muscle.",
        "peptides": ["CJC-1295 DAC", "Ipamorelin", "AOD-9604"],
        "why_it_works": "CJC-1295 and Ipamorelin synergize to increase natural growth hormone and IGF-1 levels, promoting lipolysis and lean mass retention. AOD-9604 specifically targets adipose tissue.",
        "how_to_use": [
            "5 days on / 2 days off",
            "Evening injections for GH stack (CJC + Ipamorelin)",
            "AOD-9604 can be morning or pre-workout"
        ],
    },
    {
        "name": "Mito-Melt Stack",
        "category": "Fat Loss",
        "goal": "Boost cellular metabolism and mitochondrial efficiency.",
        "peptides": ["MOTS-c", "5-Amino-1MQ", "GHK-Cu"],
        "why_it_works": "MOTS-c and 5-Amino-1MQ hit fat stores from the inside-out by increasing mitochondrial efficiency and altering metabolic gene expression. Great for stubborn belly fat.",
        "how_to_use": [
            "MOTS-c: 5-7 days on, rest 7 days",
            "5-Amino-1MQ: 10-20 mg/day orally, 4-6 weeks",
            "GHK-Cu: 100 mcg/day topical or SubQ"
        ],
    },
    {
        "name": "The Fasted Burner Stack",
        "category": "Fat Loss",
        "goal": "Maximize fat oxidation during intermittent fasting or cardio.",
        "peptides": ["Tesamorelin", "AOD-9604"],
        "why_it_works": "Tesamorelin is FDA-approved for reducing abdominal fat. Pairing with AOD-9604 boosts effect on adipose tissue. Use in fasted state before cardio for best results.",
        "how_to_use": [
            "Tesamorelin: 2 mg daily, 8-12 weeks",
            "AOD-9604: 300 mcg/day AM",
            "Use in fasted state before cardio for best results"
        ],
    },
    {
        "name": "The Belly Fat & Insulin Reset Stack",
        "category": "Fat Loss",
        "goal": "Reduce abdominal weight gain and insulin resistance.",
        "peptides": ["MOTS-c", "5-Amino-1MQ", "AOD-9604"],
        "why_it_works": "Attacks belly fat from the inside out: energy metabolism, hormone sensitivity, and fat oxidation all supported here.",
        "how_to_use": [
            "MOTS-c: 10 mg/day x 7 days on, 7 off",
            "5-Amino-1MQ: 10-20 mg/day orally",
            "AOD-9604: 300 mcg/day AM or pre-cardio"
        ],
    },
    # === FEMALE OPTIMIZATION ===
    {
        "name": "The Female Fat Loss Stack",
        "category": "Female Optimization",
        "goal": "Target stubborn estrogen-related fat (hips, thighs, belly).",
        "peptides": ["TB-500", "CJC-1295", "Ipamorelin", "Kisspeptin"],
        "why_it_works": "For perimenopausal or postmenopausal women, this stack helps reduce inflammatory and hormonal drivers of fat gain.",
        "how_to_use": [
            "TB-500: 2-5 mg/week for 4 weeks",
            "CJC/Ipamorelin: 5 days/week, PM",
            "Kisspeptin: 10-20 mcg 2-3x per week (cycle 4 weeks on / 2 off)"
        ],
    },
    {
        "name": "The Estrogen Reset Stack",
        "category": "Female Optimization",
        "goal": "Balance estrogen dominance or deficiency symptoms.",
        "peptides": ["Kisspeptin", "BPC-157", "GHK-Cu"],
        "why_it_works": "Kisspeptin gently encourages natural estrogen/progesterone cycling. BPC-157 clears gut-driven estrogen reabsorption. GHK-Cu enhances tissue tone.",
        "how_to_use": [
            "Kisspeptin-10: 10-20 mcg 2-3x/week",
            "BPC-157: 250 mcg/day oral or SubQ",
            "GHK-Cu: 100 mcg/day topical or SubQ"
        ],
    },
    {
        "name": "The Perimenopause Balancer Stack",
        "category": "Female Optimization",
        "goal": "Ease mood swings, hot flashes, sleep disruption, and weight changes.",
        "peptides": ["Epithalon", "Tesamorelin", "Selank"],
        "why_it_works": "This stack supports the fading circadian and hormonal rhythms — without synthetic hormone therapy.",
        "how_to_use": [
            "Epitalon: 10 mg/day for 10-20 days",
            "Tesamorelin: 1 mg/day, 5 days/week",
            "Selank: 300 mcg intranasal daily or as needed"
        ],
    },
    {
        "name": "The PCOS & Metabolic Stack",
        "category": "Female Optimization",
        "goal": "Improve insulin sensitivity, ovulation, and reduce androgen symptoms.",
        "peptides": ["MOTS-c", "5-Amino-1MQ", "BPC-157"],
        "why_it_works": "Improves energy regulation, reduces insulin resistance, and supports hormonal harmony — ideal for PCOS body types.",
        "how_to_use": [
            "MOTS-c: 10 mg/day x 7 days (cycle monthly)",
            "5-Amino-1MQ: 10-20 mg/day",
            "BPC-157: 250-500 mcg/day"
        ],
    },
    {
        "name": "The Lean & Toned Stack for Women",
        "category": "Female Optimization",
        "goal": "Burn fat while preserving curves and muscle.",
        "peptides": ["Tesamorelin", "Ipamorelin", "AOD-9604", "CJC-1295"],
        "why_it_works": "GH-based peptides benefit women if dosed smartly — this stack keeps it safe, with minimal androgenic risk.",
        "how_to_use": [
            "Tesamorelin: 1-2 mg/day, PM",
            "CJC/Ipamorelin: 100 mcg each, PM 5 days/week",
            "AOD-9604: 300 mcg AM or pre-workout"
        ],
    },
    {
        "name": "The Skin, Hair & Glow Stack",
        "category": "Female Optimization",
        "goal": "Improve collagen, reduce fine lines, regrow hair, enhance complexion.",
        "peptides": ["GHK-Cu", "TB-500", "BPC-157"],
        "why_it_works": "These peptides support fibroblast activity, vascular tone, and skin regeneration that estrogen normally maintains.",
        "how_to_use": [
            "GHK-Cu: 100-200 mcg/day topical or SubQ",
            "TB-500: 2 mg/week (1x or 2x dosing)",
            "BPC-157: 250 mcg/day oral or SubQ"
        ],
    },
    # === HORMONAL AXIS RECOVERY ===
    {
        "name": "The HPTA Reboot Stack",
        "category": "Hormonal Recovery",
        "goal": "Kickstart hypothalamic-pituitary-testicular axis.",
        "peptides": ["Kisspeptin", "CJC-1295", "Ipamorelin"],
        "why_it_works": "Kisspeptin and Gonadorelin stimulate GnRH and LH; GH peptides support anabolic rebound.",
        "how_to_use": [
            "Kisspeptin: 20-50 mcg, 2-3x/week",
            "Gonadorelin: 100-250 mcg/day for 2-4 weeks",
            "CJC/Ipamorelin: nightly, 5 days/week"
        ],
    },
    {
        "name": "The LH & FSH Recovery Stack",
        "category": "Hormonal Recovery",
        "goal": "Normalize LH/FSH levels and restore testicular function.",
        "peptides": ["HCG", "Kisspeptin"],
        "why_it_works": "Mimics physiologic LH/FSH pulses and testicular stimulation.",
        "how_to_use": [
            "Gonadorelin: 100 mcg/day",
            "hCG: 500 IU 2x/week",
            "Kisspeptin: 20 mcg 2-3x/week"
        ],
    },
    {
        "name": "The Estrogen Control Stack",
        "category": "Hormonal Recovery",
        "goal": "Balance rebound estrogen after cycle cessation.",
        "peptides": ["BPC-157", "GHK-Cu"],
        "why_it_works": "Supports liver detox, gut hormone recycling, and inflammation reduction.",
        "how_to_use": [
            "BPC-157: 250 mcg/day oral",
            "GHK-Cu: 100 mcg/day"
        ],
    },
    {
        "name": "The T-Boost & GH Sync Stack",
        "category": "Hormonal Recovery",
        "goal": "Restore testosterone while supporting GH/IGF balance.",
        "peptides": ["Kisspeptin", "CJC-1295", "Ipamorelin", "IGF-1 LR3"],
        "why_it_works": "Promotes natural hormone synergy to avoid catabolic rebound.",
        "how_to_use": [
            "Kisspeptin: 20-50 mcg 3x/week",
            "CJC/Ipamorelin: PM, 5 on/2 off",
            "IGF-1 LR3: 10-20 mcg post-workout (2-3x/week)"
        ],
    },
    {
        "name": "The TRT Off-Ramp Stack",
        "category": "Hormonal Recovery",
        "goal": "Come off TRT gradually and restart natural production.",
        "peptides": ["Kisspeptin", "BPC-157"],
        "why_it_works": "Stimulates endogenous axis, supports neuroendocrine recovery.",
        "how_to_use": [
            "Kisspeptin: 20 mcg 3x/week",
            "Gonadorelin: 100 mcg/day",
            "BPC-157: 250-500 mcg/day"
        ],
    },
    # === TESTICULAR & SPERM HEALTH ===
    {
        "name": "The Fertility Reboot Stack",
        "category": "Fertility & Sperm Health",
        "goal": "Restore sperm count and motility post-cycle.",
        "peptides": ["HCG", "Kisspeptin"],
        "why_it_works": "hCG maintains spermatogenesis, Kisspeptin restores upstream signaling.",
        "how_to_use": [
            "hCG: 500 IU 2x/week",
            "Kisspeptin: 20 mcg 2-3x/week",
            "Thymalin: 10 mg/day x 10 days"
        ],
    },
    {
        "name": "The Sperm Quality Optimizer Stack",
        "category": "Fertility & Sperm Health",
        "goal": "Improve sperm morphology and DNA integrity.",
        "peptides": ["BPC-157", "GHK-Cu", "Epithalon"],
        "why_it_works": "Enhances testicular microcirculation and antioxidant repair.",
        "how_to_use": [
            "BPC-157: 500 mcg/day",
            "GHK-Cu: 100 mcg/day",
            "Epitalon: 10 mg/day for 10-20 days"
        ],
    },
    {
        "name": "The Leydig Cell Support Stack",
        "category": "Fertility & Sperm Health",
        "goal": "Protect testicular cells from oxidative damage.",
        "peptides": ["GHK-Cu", "TB-500", "MOTS-c"],
        "why_it_works": "Reduces inflammation, improves mitochondrial function in Leydig tissue.",
        "how_to_use": [
            "GHK-Cu: topical or SubQ 100 mcg/day",
            "TB-500: 2 mg/week",
            "MOTS-c: 10 mg/day for 7 days"
        ],
    },
    {
        "name": "The Semen Volume Stack",
        "category": "Fertility & Sperm Health",
        "goal": "Boost seminal fluid and prostate support.",
        "peptides": ["HCG", "Kisspeptin", "BPC-157"],
        "why_it_works": "hCG maintains seminal gland activity; BPC-157 supports prostate healing.",
        "how_to_use": [
            "hCG: 500 IU 2x/week",
            "Kisspeptin: 20 mcg 2-3x/week",
            "BPC-157: 250 mcg/day orally"
        ],
    },
    {
        "name": "The Post-Orchitis Recovery Stack",
        "category": "Fertility & Sperm Health",
        "goal": "Heal inflammation or trauma post-cycle.",
        "peptides": ["TB-500", "BPC-157", "GHK-Cu"],
        "why_it_works": "Accelerates tissue healing and restores microvascular integrity.",
        "how_to_use": [
            "TB-500: 2 mg/week",
            "BPC-157: 500 mcg/day (SubQ or systemic)",
            "GHK-Cu: 100 mcg/day topical"
        ],
    },
    # === MUSCLE GROWTH ===
    {
        "name": "The Anabolic Growth Stack",
        "category": "Muscle Growth",
        "goal": "Maximize hypertrophy via GH/IGF-1 pathway.",
        "peptides": ["CJC-1295 DAC", "Ipamorelin", "IGF-1 LR3"],
        "why_it_works": "GH promotes IGF-1 release from the liver, adding IGF-1 LR3 provides direct action on muscle tissue, enhancing protein synthesis and recovery speed.",
        "how_to_use": [
            "CJC-1295: 2 mg 1-2x/week",
            "Ipamorelin: 300 mcg/day, 5 days on",
            "IGF-1 LR3: 20-40 mcg/day post workout (rotate injection sites)"
        ],
    },
    {
        "name": "The Recovery & Repair Stack",
        "category": "Muscle Growth",
        "goal": "Rebuild faster, reduce soreness, recover tendons and muscle fibers.",
        "peptides": ["BPC-157", "TB-500", "GHK-Cu"],
        "why_it_works": "BPC-157 and TB-500 work systemically to repair microtrauma, while GHK-Cu restores connective tissue and boosts satellite cell recruitment.",
        "how_to_use": [
            "BPC-157: 250-500 mcg/day",
            "TB-500: 2-5 mg/week (loading phase)",
            "GHK-Cu: 100-200 mcg/day (inject or topical)"
        ],
    },
    {
        "name": "The mTOR Activation Stack",
        "category": "Muscle Growth",
        "goal": "Activate muscle-building pathways on a cellular level.",
        "peptides": ["IGF-1 LR3", "Epithalon"],
        "why_it_works": "Follistatin blocks myostatin. Pairing with IGF-1 DES creates a hyper-anabolic microenvironment. Epitalon extends the window of regeneration.",
        "how_to_use": [
            "Follistatin: 100 mcg/day for 10-20 days (cycle carefully)",
            "IGF-1 DES: 20-40 mcg IM post-training",
            "Epitalon: 5-10 mg daily for 10-20 days"
        ],
    },
    {
        "name": "The Natural Test Boost Stack",
        "category": "Muscle Growth",
        "goal": "Support testosterone, pituitary, and downstream anabolic hormones.",
        "peptides": ["Kisspeptin", "CJC-1295", "Ipamorelin"],
        "why_it_works": "Kisspeptin primes the hypothalamus; Gonadorelin delivers the spike; CJC/Ipamorelin supports muscle-building via GH axis.",
        "how_to_use": [
            "Kisspeptin: 20-50 mcg, 2-3x/week",
            "Gonadorelin: 100-250 mcg, 1-2x/week",
            "CJC/Ipamorelin: nightly, 5 on/2 off"
        ],
    },
    {
        "name": "The Lean Mass Builder Stack",
        "category": "Muscle Growth",
        "goal": "Build lean muscle while staying shredded.",
        "peptides": ["Tesamorelin", "5-Amino-1MQ", "BPC-157"],
        "why_it_works": "Tesamorelin shifts body comp toward lean tissue, while 5-Amino-1MQ increases NAD+ and muscle metabolism. Clean bulk or recomp stack.",
        "how_to_use": [
            "Tesamorelin: 2 mg daily (evening)",
            "5-Amino-1MQ: 10-20 mg orally, daily",
            "BPC-157: 250 mcg/day or oral capsule form"
        ],
    },
    # === STRENGTH & POWERLIFTING ===
    {
        "name": "The Raw Power Stack",
        "category": "Strength & Powerlifting",
        "goal": "Build maximal strength via GH and androgenic synergy.",
        "peptides": ["CJC-1295", "Ipamorelin", "IGF-1 LR3", "Kisspeptin"],
        "why_it_works": "GH and IGF-1 increase contractile tissue, Kisspeptin supports T output.",
        "how_to_use": [
            "CJC/Ipamorelin: 100 mcg each pre-bed",
            "IGF-1 LR3: 40 mcg post-workout",
            "Kisspeptin: 20 mcg 3x/week"
        ],
    },
    {
        "name": "The Spartan Stack",
        "category": "Strength & Powerlifting",
        "goal": "Build strength, power, and recovery capacity.",
        "peptides": ["CJC-1295 DAC", "Ipamorelin", "IGF-1 LR3", "BPC-157"],
        "why_it_works": "Stimulates GH release, hypertrophy, plus joint/tendon support — ideal for strength-focused athletes.",
        "how_to_use": [
            "CJC-1295 (DAC): 2 mg SubQ weekly",
            "Ipamorelin: 300 mcg SubQ nightly",
            "IGF-1 LR3: 50 mcg SubQ post-workout",
            "BPC-157: 250 mcg SubQ daily"
        ],
    },
    {
        "name": "The CNS Reset Stack",
        "category": "Strength & Powerlifting",
        "goal": "Recover faster from heavy lifting-induced CNS fatigue.",
        "peptides": ["Cerebrolysin", "BPC-157"],
        "why_it_works": "Supports brain recovery, sleep depth, and systemic repair.",
        "how_to_use": [
            "Cerebrolysin: 5 ml IM 2x/week",
            "DSIP: 100 mcg at night",
            "BPC-157: 250 mcg/day"
        ],
    },
    {
        "name": "The Tendon Armor Stack",
        "category": "Strength & Powerlifting",
        "goal": "Fortify tendons for heavy lifts.",
        "peptides": ["BPC-157", "TB-500"],
        "why_it_works": "Prevents microtears and tendinitis, improves pliability under load.",
        "how_to_use": [
            "BPC-157: near joint or systemic",
            "TB-500: 2 mg/week"
        ],
    },
    # === CROSSFIT ===
    {
        "name": "The WOD Resilience Stack",
        "category": "CrossFit & Functional Fitness",
        "goal": "Recover between intense, multi-modality workouts.",
        "peptides": ["BPC-157", "5-Amino-1MQ", "TB-500"],
        "why_it_works": "Fights inflammation, supports muscle ATP regeneration, reduces DOMS.",
        "how_to_use": [
            "BPC-157: 500 mcg/day",
            "5-Amino-1MQ: 10-20 mg/day",
            "TB-500: 2 mg post-WOD"
        ],
    },
    {
        "name": "The Mobility & Joint Stack",
        "category": "CrossFit & Functional Fitness",
        "goal": "Keep shoulders, knees, and wrists mobile under high volume.",
        "peptides": ["BPC-157", "GHK-Cu"],
        "why_it_works": "Supports cartilage and synovial membrane health.",
        "how_to_use": [
            "BPC-157: near joint",
            "GHK-Cu: inject near or topical"
        ],
    },
    {
        "name": "The Functional VO2 Stack",
        "category": "CrossFit & Functional Fitness",
        "goal": "Improve CrossFit engine for metcons and rowing.",
        "peptides": ["MOTS-c", "Epithalon", "GHK-Cu"],
        "why_it_works": "Boosts aerobic ceiling and endurance output.",
        "how_to_use": [
            "MOTS-c: 10 mg/day, 7 on/7 off",
            "Epitalon: 10 mg/day for 10 days",
            "GHK-Cu: 100 mcg/day"
        ],
    },
    {
        "name": "The Grip & Pull Stack",
        "category": "CrossFit & Functional Fitness",
        "goal": "Strengthen forearms, tendons, and pulling muscles.",
        "peptides": ["IGF-1 LR3", "BPC-157", "TB-500"],
        "why_it_works": "Enhances recovery and growth of high-frequency-use muscles.",
        "how_to_use": [
            "IGF-1 LR3: 20-40 mcg into biceps or forearms",
            "BPC-157: local injection",
            "TB-500: 2 mg/week"
        ],
    },
    {
        "name": "The CNS Reload Stack",
        "category": "CrossFit & Functional Fitness",
        "goal": "Support neural recovery from EMOMs, AMRAPs, PR attempts.",
        "peptides": ["Semax", "Cerebrolysin"],
        "why_it_works": "Targets brain and sleep recovery — often neglected in CrossFit.",
        "how_to_use": [
            "Semax: AM",
            "DSIP: PM",
            "Cerebrolysin: 5 ml IM 2-3x/week"
        ],
    },
    # === COMBAT SPORTS ===
    {
        "name": "The Reaction Speed & Reflex Stack",
        "category": "Combat Sports",
        "goal": "Improve reflexes, twitch response, and mental clarity.",
        "peptides": ["Semax", "Dihexa"],
        "why_it_works": "Enhances neuroplasticity, synapse firing, and visual-motor tracking.",
        "how_to_use": [
            "Semax: 300 mcg intranasal AM",
            "Dihexa: 4 mg pre-session"
        ],
    },
    {
        "name": "The Impact Recovery Stack",
        "category": "Combat Sports",
        "goal": "Heal from bruises, minor sprains, and joint trauma.",
        "peptides": ["TB-500", "BPC-157", "GHK-Cu"],
        "why_it_works": "Reduces inflammation and promotes tissue repair.",
        "how_to_use": [
            "TB-500: 2 mg post-training",
            "BPC-157: daily",
            "GHK-Cu: topical or SubQ"
        ],
    },
    {
        "name": "The Weight-Cut Recovery Stack",
        "category": "Combat Sports",
        "goal": "Bounce back post-cut with gut, brain, and hydration support.",
        "peptides": ["BPC-157", "GHK-Cu"],
        "why_it_works": "Restores gut lining, mood, and immune system.",
        "how_to_use": [
            "BPC-157: 500 mcg oral",
            "GHK-Cu: 100 mcg/day",
            "Thymalin: 10 mg/day for 5 days post-cut"
        ],
    },
    {
        "name": "The Combat Endurance Stack",
        "category": "Combat Sports",
        "goal": "Maintain explosiveness into later rounds.",
        "peptides": ["MOTS-c", "5-Amino-1MQ", "GHK-Cu"],
        "why_it_works": "Boosts ATP, fat metabolism, and reduces central fatigue.",
        "how_to_use": [
            "MOTS-c: 7-day cycle before fight",
            "5-Amino-1MQ: 10-20 mg oral/day",
            "GHK-Cu: 100 mcg/day"
        ],
    },
    {
        "name": "The Knockout Sleep Stack",
        "category": "Combat Sports",
        "goal": "Deepen sleep to improve fight-night recovery.",
        "peptides": ["Epithalon"],
        "why_it_works": "Targets thalamus, sleep hormones, and nervous system tone.",
        "how_to_use": [
            "DSIP: 100 mcg pre-bed",
            "Epitalon: 10 mg/day for 10 days",
            "Oxytocin: 5 IU intranasal at night (optional)"
        ],
    },
    # === SPRINTING & SPEED ===
    {
        "name": "The Explosive Speed Stack",
        "category": "Sprinting & Speed",
        "goal": "Increase fast-twitch muscle fiber recruitment and sprint power.",
        "peptides": ["IGF-1 LR3", "GHK-Cu"],
        "why_it_works": "IGF-1 DES acts locally on trained muscle; Follistatin inhibits myostatin to allow more growth; GHK-Cu improves oxygen delivery.",
        "how_to_use": [
            "IGF-1 DES: 20 mcg IM post-sprint",
            "Follistatin 344: 100 mcg/day, 10-20 days (cycle)",
            "GHK-Cu: 100 mcg/day topical or SubQ"
        ],
    },
    {
        "name": "The Reaction Time Reset Stack",
        "category": "Sprinting & Speed",
        "goal": "Sharpen CNS firing speed and reduce neural fatigue.",
        "peptides": ["Semax", "Cerebrolysin", "Dihexa"],
        "why_it_works": "Boosts neurotransmission, synaptic plasticity, and neuroprotection — ideal for starts and agility.",
        "how_to_use": [
            "Semax: 300 mcg intranasal pre-session",
            "Cerebrolysin: 5 ml IM every other day",
            "Dihexa: 4-8 mg pre-training"
        ],
    },
]


def main():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["test_database"]

    db.peptide_stacks.drop()
    print(f"Dropped existing stacks collection")

    docs = []
    for s in STACKS:
        doc = {
            "id": str(uuid.uuid4()),
            "slug": slug_from_name(s["name"]),
            "name": s["name"],
            "category": s["category"],
            "goal": s["goal"],
            "peptides": s["peptides"],
            "why_it_works": s["why_it_works"],
            "how_to_use": s["how_to_use"],
            "is_free": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        docs.append(doc)

    db.peptide_stacks.insert_many(docs)
    print(f"Inserted {len(docs)} stacks")

    # Print summary
    cats = {}
    for d in docs:
        cats[d["category"]] = cats.get(d["category"], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
