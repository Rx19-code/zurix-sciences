"""Seed script for Peptide Library - 97 peptides"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


def slug(name):
    return name.lower().replace(" ", "-").replace("/", "-").replace(",", "").replace("+", "-plus-").replace("(", "").replace(")", "").replace(".", "")


def p(name, desc, category, is_free, presentations, also_known_as=None, overview=None, protocols=None, research=None, synergy=None):
    return {
        "slug": slug(name),
        "name": name,
        "description": desc,
        "category": category,
        "is_free": is_free,
        "presentations": presentations,
        "also_known_as": also_known_as or [],
        "overview": overview or {
            "what_is": f"{name} is a research peptide currently under investigation for its potential therapeutic applications.",
            "mechanism_summary": f"Research suggests {name} may act through specific receptor pathways relevant to its category of {category}."
        },
        "protocols": protocols or {
            "standard": {"route": "Subcutaneous", "frequency": "As per research protocol"},
            "dosages": [],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C after reconstitution.",
        },
        "research": research or {
            "mechanism": f"The mechanism of action of {name} is under active investigation.",
            "steps": [],
            "references": []
        },
        "synergy": synergy or {
            "interactions": [],
            "stacks": []
        }
    }


PEPTIDES = [
    # ============ FREE PEPTIDES ============
    p("Semaglutide", "GLP-1 receptor agonist for metabolic research and appetite regulation studies",
      "Weight Loss / GLP-1", True, ["5mg", "10mg", "20mg"],
      ["Ozempic", "Wegovy", "Rybelsus"],
      {"what_is": "Semaglutide is a glucagon-like peptide-1 (GLP-1) receptor agonist originally developed for type 2 diabetes management. It mimics the natural GLP-1 hormone, enhancing insulin secretion, suppressing glucagon release, and slowing gastric emptying.", "mechanism_summary": "Binds to GLP-1 receptors in the pancreas and brain, promoting satiety and improving glycemic control."},
      {"standard": {"route": "Subcutaneous", "frequency": "Once weekly"}, "dosages": [{"indication": "Metabolic research", "dose": "0.25-2.4mg", "route": "SC weekly", "notes": "Gradual dose escalation recommended"}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "Semaglutide activates GLP-1 receptors, leading to increased insulin secretion, decreased glucagon release, delayed gastric emptying, and reduced appetite through central nervous system signaling.", "steps": ["Binds to GLP-1 receptors on pancreatic beta cells", "Stimulates glucose-dependent insulin secretion", "Suppresses glucagon release from alpha cells", "Delays gastric emptying, promoting satiety", "Acts on hypothalamic neurons to reduce appetite"], "references": ["PMID: 28930518", "PMID: 33567185"]},
      {"interactions": [{"peptide": "Tirzepatide", "status": "AVOID", "description": "Both target GLP-1 pathways; combined use not recommended"}, {"peptide": "BPC-157", "status": "COMPATIBLE", "description": "May support GI protection during GLP-1 agonist use"}], "stacks": []}),

    p("Tirzepatide", "Dual GIP/GLP-1 receptor agonist for advanced metabolic and weight management research",
      "Weight Loss / GLP-1", True, ["10mg", "15mg", "20mg", "60mg"],
      ["Mounjaro", "Zepbound"],
      {"what_is": "Tirzepatide is a dual glucose-dependent insulinotropic polypeptide (GIP) and GLP-1 receptor agonist. It represents a new class of peptides that simultaneously activate two incretin receptors for enhanced metabolic effects.", "mechanism_summary": "Dual agonism of GIP and GLP-1 receptors provides synergistic effects on insulin secretion, appetite suppression, and metabolic regulation."},
      {"standard": {"route": "Subcutaneous", "frequency": "Once weekly"}, "dosages": [{"indication": "Metabolic research", "dose": "2.5-15mg", "route": "SC weekly", "notes": "Start low, titrate gradually"}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "Tirzepatide acts as a dual agonist, binding to both GIP and GLP-1 receptors.", "steps": ["Activates GIP receptors on pancreatic beta cells", "Simultaneously activates GLP-1 receptors", "Enhances insulin sensitivity in peripheral tissues", "Reduces appetite through central mechanisms", "Promotes fat oxidation and energy expenditure"], "references": ["PMID: 35658024", "PMID: 34170647"]},
      {"interactions": [{"peptide": "Semaglutide", "status": "AVOID", "description": "Both target GLP-1 pathways; do not combine"}, {"peptide": "MOTS-c", "status": "SYNERGISTIC", "description": "Complementary metabolic pathways"}], "stacks": []}),

    p("Retatrutide", "Triple GLP-1/GIP/Glucagon receptor agonist for next-generation metabolic research",
      "Weight Loss / GLP-1", True, ["10mg", "20mg", "40mg", "60mg"],
      ["LY3437943"],
      {"what_is": "Retatrutide is a first-in-class triple hormone receptor agonist targeting GLP-1, GIP, and glucagon receptors simultaneously. This triple agonism aims to provide superior metabolic benefits compared to dual agonists.", "mechanism_summary": "Triple agonism provides comprehensive metabolic regulation through three complementary incretin and glucagon pathways."},
      {"standard": {"route": "Subcutaneous", "frequency": "Once weekly"}, "dosages": [{"indication": "Metabolic research", "dose": "1-12mg", "route": "SC weekly", "notes": "Triple agonist - careful dose titration"}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "Retatrutide activates three receptor systems simultaneously for comprehensive metabolic modulation.", "steps": ["Activates GLP-1 receptors for appetite suppression", "Stimulates GIP receptors for enhanced insulin response", "Activates glucagon receptors to increase energy expenditure", "Promotes hepatic fat reduction", "Enhances thermogenesis and fat oxidation"], "references": ["PMID: 37351564"]},
      {"interactions": [{"peptide": "Semaglutide", "status": "AVOID", "description": "Overlapping GLP-1 mechanisms"}, {"peptide": "Tirzepatide", "status": "AVOID", "description": "Overlapping GLP-1/GIP mechanisms"}], "stacks": []}),

    p("NAD+", "Nicotinamide adenine dinucleotide for cellular energy and anti-aging research",
      "Anti-aging", True, ["500mg"],
      ["Nicotinamide Adenine Dinucleotide", "Coenzyme NAD"],
      {"what_is": "NAD+ is a coenzyme found in all living cells, critical for cellular energy metabolism, DNA repair, and sirtuin activation. It plays a central role in mitochondrial function and is being studied extensively for its anti-aging potential.", "mechanism_summary": "NAD+ is essential for redox reactions in metabolism and serves as a substrate for enzymes like sirtuins and PARPs involved in DNA repair and longevity."},
      {"standard": {"route": "Intravenous / Subcutaneous", "frequency": "1-3x per week"}, "dosages": [{"indication": "Anti-aging support", "dose": "250-500mg", "route": "IV infusion", "notes": "Slow infusion recommended"}, {"indication": "Cellular energy", "dose": "100-250mg", "route": "SC injection", "notes": "May cause flushing"}], "reconstitution": "Reconstitute with sterile water. Store at 2-8C. Use within 14 days."},
      {"mechanism": "NAD+ serves as a critical coenzyme in cellular metabolism and aging pathways.", "steps": ["Acts as electron carrier in mitochondrial oxidative phosphorylation", "Activates sirtuins (SIRT1-7) for DNA repair and gene regulation", "Serves as substrate for PARP enzymes in DNA damage response", "Modulates circadian rhythm through CLOCK/BMAL1 pathway", "Supports CD38 enzymatic activity in immune signaling"], "references": ["PMID: 29514064", "PMID: 30457958"]},
      {"interactions": [{"peptide": "Glutathione", "status": "SYNERGISTIC", "description": "Both support cellular protection and anti-aging pathways"}, {"peptide": "Epithalon", "status": "SYNERGISTIC", "description": "Complementary telomere and cellular health support"}, {"peptide": "MOTS-c", "status": "SYNERGISTIC", "description": "Both target mitochondrial function"}], "stacks": [{"name": "Anti-Aging Stack", "peptides": ["NAD+", "Epithalon", "Glutathione"], "description": "Comprehensive cellular rejuvenation protocol"}]}),

    p("Glutathione", "Master antioxidant tripeptide for oxidative stress and detoxification research",
      "Anti-aging", True, ["600mg", "1500mg"],
      ["GSH", "L-Glutathione", "Gamma-L-Glutamyl-L-cysteinyl-glycine"],
      {"what_is": "Glutathione is a tripeptide composed of glutamate, cysteine, and glycine. It is the body's primary endogenous antioxidant, playing crucial roles in neutralizing free radicals, detoxification, and immune function.", "mechanism_summary": "In its reduced form (GSH), glutathione donates electrons to neutralize reactive oxygen species and participates in Phase II liver detoxification."},
      {"standard": {"route": "Intramuscular / Intravenous", "frequency": "1-3x per week"}, "dosages": [{"indication": "Antioxidant support", "dose": "300-600mg", "route": "IM 1-2x/week", "notes": ""}, {"indication": "Skin brightening", "dose": "600mg", "route": "IV weekly", "notes": ""}, {"indication": "Hepatic detox", "dose": "600-1500mg", "route": "IV 2-3x/week", "notes": ""}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "Glutathione is the master endogenous antioxidant with multiple protective mechanisms.", "steps": ["Neutralizes reactive oxygen species (ROS) by donating electrons", "Regenerates oxidized forms of vitamins C and E", "Conjugates with toxins and heavy metals in the liver for excretion", "Supports immune cell function and proliferation", "Modulates melanin synthesis through tyrosinase inhibition"], "references": ["PMID: 12145205", "PMID: 24291091"]},
      {"interactions": [{"peptide": "NAD+", "status": "SYNERGISTIC", "description": "Both act in cellular protection and anti-aging"}, {"peptide": "Vitamin C", "status": "SYNERGISTIC", "description": "Glutathione recycles oxidized vitamin C"}, {"peptide": "BPC-157", "status": "COMPATIBLE", "description": "Complementary hepatic protection"}], "stacks": [{"name": "Detox & Anti-aging Stack", "peptides": ["Glutathione", "NAD+", "Epithalon"], "description": "Comprehensive cellular rejuvenation and detoxification"}]}),

    p("GHK-Cu", "Copper peptide for skin regeneration, collagen synthesis, and wound healing research",
      "Aesthetics / Skin", True, ["50mg", "100mg"],
      ["Copper Peptide", "GHK-Copper"],
      {"what_is": "GHK-Cu is a naturally occurring copper-binding tripeptide found in human plasma, saliva, and urine. It plays important roles in wound healing, tissue remodeling, collagen synthesis, and anti-inflammatory signaling.", "mechanism_summary": "GHK-Cu delivers copper ions to tissues, activating metalloenzymes involved in collagen synthesis, antioxidant defense, and stem cell recruitment."},
      {"standard": {"route": "Subcutaneous / Topical", "frequency": "Daily or as directed"}, "dosages": [{"indication": "Skin rejuvenation", "dose": "1-2mg", "route": "SC daily", "notes": ""}, {"indication": "Hair growth research", "dose": "1-2mg", "route": "SC in scalp area", "notes": ""}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "GHK-Cu modulates gene expression related to tissue repair and regeneration.", "steps": ["Delivers bioavailable copper to tissue metalloenzymes", "Activates collagen I, III synthesis and elastin production", "Recruits mesenchymal stem cells to damaged tissue", "Upregulates antioxidant genes (SOD, glutathione system)", "Suppresses pro-inflammatory cytokines (IL-6, TNF-alpha)"], "references": ["PMID: 22585088", "PMID: 25987413"]},
      {"interactions": [{"peptide": "AHK-Cu", "status": "SYNERGISTIC", "description": "Complementary copper peptide mechanisms for enhanced skin repair"}, {"peptide": "Snap-8", "status": "SYNERGISTIC", "description": "Combined anti-aging: collagen support + expression line reduction"}, {"peptide": "BPC-157", "status": "COMPATIBLE", "description": "Both support tissue regeneration through different pathways"}], "stacks": [{"name": "Skin Rejuvenation Stack", "peptides": ["GHK-Cu", "AHK-Cu", "Snap-8"], "description": "Comprehensive skin regeneration and anti-aging protocol"}]}),

    p("AHK-Cu", "Copper tripeptide analogue for advanced skin regeneration and hair growth research",
      "Aesthetics / Skin", True, ["100mg"],
      ["AHK-Copper", "Alanine-Histidine-Lysine Copper"],
      {"what_is": "AHK-Cu is a copper-binding tripeptide analogue of GHK-Cu with enhanced stability and potentially improved tissue penetration. It is researched for skin rejuvenation, hair follicle stimulation, and wound healing.", "mechanism_summary": "Similar to GHK-Cu, AHK-Cu delivers copper ions to activate tissue repair enzymes, with potentially improved bioavailability."},
      {"standard": {"route": "Subcutaneous / Topical", "frequency": "Daily"}, "dosages": [{"indication": "Skin & hair research", "dose": "1-3mg", "route": "SC daily", "notes": ""}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "AHK-Cu functions as a copper delivery peptide with enhanced stability.", "steps": ["Delivers copper ions with improved tissue penetration", "Activates collagen and elastin synthesis pathways", "Stimulates dermal papilla cells for hair follicle support", "Enhances wound healing through VEGF upregulation"], "references": []},
      {"interactions": [{"peptide": "GHK-Cu", "status": "SYNERGISTIC", "description": "Complementary copper peptide mechanisms"}, {"peptide": "Glow Blend", "status": "COMPATIBLE", "description": "Enhanced aesthetic results when combined"}], "stacks": []}),

    p("Kisspeptin", "Neuropeptide for reproductive endocrinology and hormonal regulation research",
      "Hormonal / Sexual Health", True, ["10mg"],
      ["Kisspeptin-10", "Metastin"],
      {"what_is": "Kisspeptin is a neuropeptide encoded by the KISS1 gene that plays a critical role in the regulation of reproductive hormones. It acts on the hypothalamus to stimulate GnRH release, which in turn triggers LH and FSH secretion.", "mechanism_summary": "Kisspeptin binds to GPR54 receptors in the hypothalamus, stimulating the HPG axis and modulating reproductive function."},
      {"standard": {"route": "Subcutaneous / Intravenous", "frequency": "As per research protocol"}, "dosages": [{"indication": "Hormonal research", "dose": "1-10mcg/kg", "route": "IV or SC", "notes": "Pulsatile dosing mimics natural secretion"}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "Kisspeptin is the master upstream regulator of the reproductive hormone axis.", "steps": ["Binds to GPR54 (KISS1R) receptors on GnRH neurons", "Stimulates pulsatile GnRH release from hypothalamus", "GnRH triggers LH and FSH secretion from anterior pituitary", "LH and FSH drive gonadal steroidogenesis"], "references": ["PMID: 16339064", "PMID: 20060831"]},
      {"interactions": [{"peptide": "HCG", "status": "COMPATIBLE", "description": "Both support reproductive axis through different mechanisms"}, {"peptide": "GnRH analogues", "status": "AVOID", "description": "Competing mechanisms on the HPG axis"}], "stacks": []}),

    p("HGH", "Human Growth Hormone for growth factor and body composition research",
      "GH / Secretagogues", True, ["10iu"],
      ["Somatropin", "Human Growth Hormone", "rhGH"],
      {"what_is": "Human Growth Hormone (HGH) is a 191-amino acid peptide hormone produced by the anterior pituitary gland. It plays a critical role in growth, metabolism, body composition, and cellular repair.", "mechanism_summary": "HGH binds to growth hormone receptors, stimulating IGF-1 production in the liver and directly modulating metabolic processes."},
      {"standard": {"route": "Subcutaneous", "frequency": "Daily"}, "dosages": [{"indication": "Body composition research", "dose": "2-4 IU", "route": "SC daily", "notes": "Morning administration preferred"}, {"indication": "Recovery research", "dose": "4-6 IU", "route": "SC daily", "notes": "Split doses AM/PM"}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C. Do not shake."},
      {"mechanism": "HGH acts through direct and indirect (IGF-1 mediated) pathways.", "steps": ["Binds to GH receptors (GHR) on target tissues", "Stimulates hepatic IGF-1 synthesis and release", "Promotes lipolysis in adipose tissue", "Enhances protein synthesis in muscle tissue", "Stimulates chondrocyte proliferation for bone growth"], "references": ["PMID: 10997684", "PMID: 17284630"]},
      {"interactions": [{"peptide": "CJC-1295", "status": "AVOID", "description": "CJC-1295 stimulates endogenous GH; exogenous GH makes it redundant"}, {"peptide": "IGF-1 LR3", "status": "SYNERGISTIC", "description": "Direct IGF-1 supplementation complements GH pathways"}, {"peptide": "BPC-157", "status": "COMPATIBLE", "description": "BPC-157 may enhance GH receptor sensitivity"}], "stacks": []}),

    p("Oxytocin", "Neuropeptide for social behavior, bonding, and neuroendocrine research",
      "Hormonal / Sexual Health", True, ["10mg"],
      ["OXT", "Pitocin"],
      {"what_is": "Oxytocin is a neuropeptide hormone produced in the hypothalamus and released by the posterior pituitary. Known as the 'bonding hormone,' it plays key roles in social behavior, reproduction, maternal bonding, and stress regulation.", "mechanism_summary": "Oxytocin binds to OXT receptors in the brain and peripheral tissues, modulating social cognition, anxiety, and smooth muscle contraction."},
      {"standard": {"route": "Intranasal / Subcutaneous", "frequency": "As directed"}, "dosages": [{"indication": "Social behavior research", "dose": "20-40 IU", "route": "Intranasal", "notes": ""}, {"indication": "Neuroendocrine research", "dose": "10-20 IU", "route": "SC", "notes": ""}], "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8C."},
      {"mechanism": "Oxytocin acts through central and peripheral receptor systems.", "steps": ["Binds to oxytocin receptors (OXTR) in the brain", "Modulates amygdala activity to reduce fear/anxiety responses", "Enhances social recognition and trust behaviors", "Stimulates uterine smooth muscle contraction", "Promotes milk ejection reflex in lactation"], "references": ["PMID: 19027101", "PMID: 17339099"]},
      {"interactions": [{"peptide": "Kisspeptin", "status": "COMPATIBLE", "description": "Both modulate reproductive neuroendocrine function"}, {"peptide": "DSIP", "status": "COMPATIBLE", "description": "Complementary effects on stress and sleep regulation"}], "stacks": []}),

    # ============ PRO PEPTIDES ============
    p("Cagrilintide", "Long-acting amylin analogue for appetite regulation and metabolic research",
      "Weight Loss / GLP-1", False, ["5mg", "10mg"], ["NN9838"]),

    p("Mazdutide", "Dual GLP-1/Glucagon receptor agonist for obesity and metabolic research",
      "Weight Loss / GLP-1", False, ["10mg"], ["LY3305677", "IBI362"]),

    p("AOD 9604", "Modified HGH fragment for fat metabolism and cartilage repair research",
      "Weight Loss / GLP-1", False, ["5mg"], ["Anti-Obesity Drug 9604", "HGH Fragment 176-191 modified"]),

    p("Semax", "Synthetic ACTH analogue neuropeptide for cognitive enhancement research",
      "Nootropic / Cognitive", False, ["10mg"], ["ACTH 4-10 analogue"]),

    p("Selank", "Synthetic tuftsin analogue for anxiolytic and cognitive research",
      "Nootropic / Cognitive", False, ["10mg"], ["TP-7"]),

    p("NA-Semax", "N-Acetyl Semax with enhanced bioavailability for neuroprotection research",
      "Nootropic / Cognitive", False, ["10mg", "50mg"], ["N-Acetyl Semax Amidate"]),

    p("NA-Selank", "N-Acetyl Selank with enhanced stability for anxiolytic research",
      "Nootropic / Cognitive", False, ["10mg", "50mg"], ["N-Acetyl Selank Amidate"]),

    p("Melanotan I", "Alpha-MSH analogue for melanogenesis and photoprotection research",
      "Aesthetics / Skin", False, ["10mg"], ["MT-I", "Afamelanotide"]),

    p("Melanotan II", "Non-selective melanocortin receptor agonist for tanning and sexual function research",
      "Aesthetics / Skin", False, ["10mg"], ["MT-II"]),

    p("PT-141", "Melanocortin receptor agonist for sexual dysfunction research",
      "Hormonal / Sexual Health", False, ["10mg"], ["Bremelanotide"]),

    p("Snap-8", "Acetyl octapeptide-3 for expression line reduction and anti-aging research",
      "Aesthetics / Skin", False, ["10mg"], ["Acetyl Octapeptide-3", "SNAP-8"]),

    p("Epithalon", "Telomerase-activating tetrapeptide for longevity and anti-aging research",
      "Anti-aging", False, ["10mg", "50mg"], ["Epitalon", "Epithalone"]),

    p("NA-Epithalon", "N-Acetyl Epithalon with enhanced stability for telomere research",
      "Anti-aging", False, ["20mg"], ["N-Acetyl Epithalon Amidate"]),

    p("Slu-pp-332", "ERR agonist for exercise mimetics and endurance research",
      "Metabolism", False, ["250mcg", "500mcg 100Tab"], ["SLU-PP-332"]),

    p("5-Amino-1MQ", "NNMT inhibitor for fat metabolism and energy expenditure research",
      "Metabolism", False, ["10mg", "50mg"], ["5-Amino-1-Methylquinolinium"]),

    p("MOTS-c", "Mitochondrial-derived peptide for metabolic regulation and exercise research",
      "Anti-aging", False, ["10mg", "20mg", "40mg"], ["Mitochondrial ORF of the 12S rRNA type-c"]),

    p("SS-31", "Mitochondria-targeted peptide for cellular energy and cardioprotection research",
      "Anti-aging", False, ["10mg", "30mg", "50mg"], ["Elamipretide", "Bendavia", "MTP-131"]),

    p("DSIP", "Delta sleep-inducing peptide for sleep regulation and stress research",
      "Nootropic / Cognitive", False, ["5mg", "10mg"], ["Delta Sleep-Inducing Peptide"]),

    p("TB-500", "Thymosin Beta-4 for tissue repair, wound healing, and recovery research",
      "Recovery", False, ["10mg", "20mg"], ["Thymosin Beta-4", "TB4"]),

    p("TB500 Frag", "TB-500 active fragment for targeted tissue repair research",
      "Recovery", False, ["10mg"], ["TB-500 Fragment", "Ac-SDKP"]),

    p("Thymosin Alpha-1", "Immune-modulating peptide for immunotherapy and infectious disease research",
      "Immunity", False, ["10mg"], ["Ta1", "Zadaxin"]),

    p("BPC-157", "Body Protection Compound for gastrointestinal and tissue healing research",
      "Recovery", False, ["10mg", "20mg", "40mg"], ["Body Protection Compound-157", "Pentadecapeptide"]),

    p("BPC-157 TB4 Blend 5+5", "Synergistic recovery blend of BPC-157 and Thymosin Beta-4",
      "Recovery", False, ["5mg+5mg"], ["BPC-157/TB-500 Blend"]),

    p("BPC-157 TB4 Blend 10+10", "Higher dose recovery blend for enhanced tissue repair research",
      "Recovery", False, ["10mg+10mg"], []),

    p("BPC-157 TB4 Blend 30+30", "High-concentration recovery blend for advanced research protocols",
      "Recovery", False, ["30mg+30mg"], []),

    p("Humanin", "Mitochondrial-derived peptide for neuroprotection and longevity research",
      "Anti-aging", False, ["10mg"], ["HN", "Mitochondrial Humanin"]),

    p("HCG", "Human Chorionic Gonadotropin for reproductive and hormonal research",
      "Hormonal / Sexual Health", False, ["5000iu"], ["Human Chorionic Gonadotropin"]),

    p("HMG", "Human Menopausal Gonadotropin for fertility and hormonal research",
      "Hormonal / Sexual Health", False, ["75iu"], ["Human Menopausal Gonadotropin", "Menotropin"]),

    p("IGF-1 LR3", "Long-acting IGF-1 analogue for growth factor and muscle research",
      "GH / Secretagogues", False, ["1mg"], ["Long R3 IGF-1", "Insulin-like Growth Factor 1 LR3"]),

    p("GHRP-2", "Growth hormone releasing peptide for GH secretion research",
      "GH / Secretagogues", False, ["10mg"], ["Pralmorelin"]),

    p("GHRP-6", "Growth hormone releasing hexapeptide for appetite and GH research",
      "GH / Secretagogues", False, ["10mg"], ["Growth Hormone Releasing Peptide 6"]),

    p("HGH Fragment 176-191", "GH fragment for fat metabolism research without growth effects",
      "GH / Secretagogues", False, ["5mg"], ["HGH Frag 176-191", "AOD 9604 precursor"]),

    p("CJC-1295 DAC", "Long-acting GHRH analogue with Drug Affinity Complex for sustained GH release",
      "GH / Secretagogues", False, ["5mg"], ["Modified GRF 1-29 with DAC"]),

    p("CJC-1295 No DAC", "GHRH analogue without DAC for pulsatile GH release research",
      "GH / Secretagogues", False, ["10mg"], ["Modified GRF 1-29", "Mod GRF"]),

    p("CJC-1295 Ipamorelin Blend", "Synergistic GHRH/GHRP blend for optimized GH release research",
      "GH / Secretagogues", False, ["5mg+5mg", "10mg+10mg"], []),

    p("Tesamorelin Ipamorelin Blend", "GHRH/GHRP blend for body composition and GH research",
      "GH / Secretagogues", False, ["5mg+5mg", "10mg+3mg"], []),

    p("Tesamorelin Ipamorelin CJC-1295 Blend", "Triple GH secretagogue blend for advanced research",
      "GH / Secretagogues", False, ["6mg+3mg+3mg"], []),

    p("Ipamorelin", "Selective GHRP for clean GH release without appetite or cortisol effects",
      "GH / Secretagogues", False, ["10mg"], []),

    p("Tesamorelin", "GHRH analogue for visceral fat reduction and GH research",
      "GH / Secretagogues", False, ["10mg", "20mg"], ["Egrifta"]),

    p("LL-37", "Human cathelicidin antimicrobial peptide for immunology and wound healing research",
      "Immunity", False, ["5mg"], ["Cathelicidin", "hCAP-18"]),

    p("BAM-15", "Mitochondrial uncoupler for fat burning and metabolic research",
      "Metabolism", False, ["50mg 60Tab"], []),

    p("Glow Blend", "Multi-peptide aesthetic blend for skin rejuvenation research",
      "Aesthetics / Skin", False, ["70mg"], []),

    p("Klow Blend", "Multi-peptide recovery blend for tissue repair research",
      "Recovery", False, ["80mg"], []),

    p("BAM-SLU Blend", "BAM-15 and SLU-PP-332 combination for metabolic research",
      "Metabolism", False, ["25mg+100mcg 60Tab", "35mg+250mcg 60Tab"], []),

    p("Coremend Blend", "Triple peptide recovery blend for comprehensive tissue repair",
      "Recovery", False, ["25mg+10mg+10mg"], []),

    p("Illumineuro", "Quad nootropic blend (Pinealon/NA-Selank/NA-Semax/PE-22-28) for cognitive research",
      "Nootropic / Cognitive", False, ["10mg+10mg+20mg+10mg"], []),

    p("ARA-290", "Erythropoietin-derived peptide for neuroprotection and tissue repair research",
      "Recovery", False, ["10mg"], ["Cibinetide"]),

    p("PE-22-28", "Spadin analogue for antidepressant and neuroplasticity research",
      "Nootropic / Cognitive", False, ["10mg"], ["Spadin analogue"]),

    p("Hexarelin", "Growth hormone secretagogue for cardiac protection and GH research",
      "GH / Secretagogues", False, ["3mg"], ["Examorelin"]),

    p("FoxO4-DRI", "Cell-penetrating peptide for senescent cell clearance and aging research",
      "Anti-aging", False, ["10mg"], ["FOXO4-D-Retro-Inverso"]),

    p("Bronchogen", "Bioregulator peptide for respiratory and bronchial tissue research",
      "Bioregulators", False, ["20mg"], []),

    p("Survodutide", "Dual GLP-1/Glucagon agonist for liver and metabolic disease research",
      "Weight Loss / GLP-1", False, ["10mg"], ["BI 456906"]),

    p("Prostamax", "Bioregulator peptide for prostate tissue support research",
      "Bioregulators", False, ["20mg"], []),

    p("Vesugen", "Bioregulator peptide for vascular and cardiovascular tissue research",
      "Bioregulators", False, ["20mg"], []),

    p("Pinealon", "Bioregulator peptide for pineal gland and neuroendocrine research",
      "Bioregulators", False, ["20mg"], []),

    p("Ovagen", "Bioregulator peptide for hepatic and liver tissue research",
      "Bioregulators", False, ["20mg"], []),

    p("Sermorelin", "GHRH analogue for growth hormone stimulation research",
      "GH / Secretagogues", False, ["5mg", "10mg"], ["GRF 1-29"]),

    p("KPV", "Alpha-MSH fragment for anti-inflammatory and gut health research",
      "Immunity", False, ["10mg", "30mg"], ["Alpha-MSH Fragment 11-13"]),

    p("PNC-27", "Anticancer peptide targeting HDM2 for oncology research",
      "Immunity", False, ["30mg"], []),

    p("Cerebrolysin", "Neurotrophic peptide mixture for neuroprotection and brain repair research",
      "Nootropic / Cognitive", False, ["30mg"], []),

    p("Vilon", "Dipeptide bioregulator for immune system and thymus research",
      "Bioregulators", False, ["20mg"], []),

    p("Cartalax", "Tripeptide bioregulator for cartilage and musculoskeletal research",
      "Bioregulators", False, ["20mg"], []),

    p("Cortagen", "Bioregulator peptide for cerebral cortex and neurological research",
      "Bioregulators", False, ["20mg"], []),

    p("Chonluten", "Bioregulator peptide for bronchial mucosa and respiratory research",
      "Bioregulators", False, ["20mg"], []),

    p("Livagen", "Bioregulator peptide for liver tissue and hepatic function research",
      "Bioregulators", False, ["20mg"], []),

    p("Cardiogen", "Bioregulator peptide for cardiac muscle and cardiovascular research",
      "Bioregulators", False, ["20mg"], []),

    p("Pancragen", "Bioregulator peptide for pancreatic tissue and metabolic research",
      "Bioregulators", False, ["20mg"], []),

    p("Crystagen", "Bioregulator peptide for immune system and thymus research",
      "Immunity", False, ["20mg"], []),

    p("Vesilute", "Bioregulator peptide for urinary system and bladder research",
      "Bioregulators", False, ["20mg"], []),

    p("Testagen", "Bioregulator peptide for testicular function and hormonal research",
      "Bioregulators", False, ["20mg"], []),

    p("Thymogen", "Bioregulator peptide for thymus and immune modulation research",
      "Immunity", False, ["20mg"], []),

    p("Teriparatide", "Parathyroid hormone fragment for bone density and osteoporosis research",
      "Hormonal / Sexual Health", False, ["750mcg"], ["PTH 1-34", "Forteo"]),

    p("Abaloparatide", "PTHrP analogue for bone formation and osteoporosis research",
      "Hormonal / Sexual Health", False, ["3mg"], ["Tymlos"]),

    p("VIP", "Vasoactive Intestinal Peptide for neuroprotection and immune research",
      "Immunity", False, ["6mg", "10mg"], ["Vasoactive Intestinal Peptide"]),

    p("Adamax", "Nootropic peptide for cognitive function and memory research",
      "Nootropic / Cognitive", False, ["10mg"], ["Semax derivative"]),

    p("Adipotide", "Pro-apoptotic peptide targeting adipose vasculature for obesity research",
      "Weight Loss / GLP-1", False, ["10mg"], ["CKGGRAKDC-GG-D(KLAKLAK)2", "Prohibitin-targeting peptide"]),

    p("Thymulin", "Thymic peptide for immune regulation and anti-aging research",
      "Immunity", False, ["10mg", "20mg"], ["Facteur Thymique Serique", "FTS-Zn"]),

    p("Dermorphin", "Opioid peptide for pain modulation and analgesic research",
      "Hormonal / Sexual Health", False, ["5mg"], []),

    p("Tadalafil", "PDE5 inhibitor for vascular and erectile function research",
      "Hormonal / Sexual Health", False, ["20mg 100Tab"], ["Cialis"]),

    p("Toxin Botulinium", "Botulinum toxin for neuromuscular and aesthetic research",
      "Aesthetics / Skin", False, ["100ui"], ["Botox", "Botulinum Toxin Type A"]),

    # ============ DILUENTS ============
    p("Bacteriostatic Water", "Sterile water with 0.9% benzyl alcohol for peptide reconstitution",
      "Diluents", False, ["3ml", "10ml"], ["Bac Water", "BAC"]),

    p("GA Water", "Sterile water for injection for sensitive peptide reconstitution",
      "Diluents", False, ["10ml"], ["Sterile Water for Injection"]),

    p("Sodium Chloride 0.9%", "Normal saline solution for peptide dilution and reconstitution",
      "Diluents", False, ["10ml"], ["Normal Saline", "NaCl 0.9%"]),
]


async def seed():
    # Drop existing collection
    await db.peptide_library.drop()
    print(f"Dropped existing peptide_library collection")

    # Insert all peptides
    await db.peptide_library.insert_many(PEPTIDES)
    print(f"Inserted {len(PEPTIDES)} peptides")

    # Create indexes
    await db.peptide_library.create_index("slug", unique=True)
    await db.peptide_library.create_index("category")
    await db.peptide_library.create_index("is_free")
    await db.peptide_library.create_index([("name", "text")])
    print("Indexes created")

    # Summary
    free_count = sum(1 for p in PEPTIDES if p["is_free"])
    pro_count = sum(1 for p in PEPTIDES if not p["is_free"])
    categories = set(p["category"] for p in PEPTIDES)
    print(f"\nSummary: {free_count} FREE, {pro_count} PRO, {len(categories)} categories")
    for cat in sorted(categories):
        count = sum(1 for p in PEPTIDES if p["category"] == cat)
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    asyncio.run(seed())
