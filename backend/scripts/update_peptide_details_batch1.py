"""
Batch 1: Update 6 peptides with detailed Background, Clinical Applications,
Side Effects, Contraindications, and Interactions.

Peptides: TB-500, Semax, Selank, KPV, CJC-1295 DAC, Tesamorelin
Sources: User-provided PDFs (Feb 2026)

Note: CJC-1295 DAC and Tesamorelin side_effects are derived from clinical class
data (GHRH analogs, similar pattern to Ipamorelin) since the PDF didn't
contain explicit side-effect lists.
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# Common GHRH/GH-class side effects (used for CJC-1295 DAC & Tesamorelin)
GHRH_CLASS_SIDE_EFFECTS = {
    "common": [
        "Mild injection site reactions (redness, itching)",
        "Temporary water retention",
        "Mild hunger increase (appetite stimulation)",
        "Tingling or flushing sensation after injection",
    ],
    "less_common": [
        "Headaches",
        "Dizziness",
        "Lethargy or fatigue",
        "Mild changes in blood glucose (monitor if diabetic)",
    ],
    "rare": [
        "Carpal tunnel-like symptoms (with prolonged or high-dose use)",
        "Changes in insulin sensitivity",
        "Joint stiffness or swelling",
        "Allergic reactions",
    ],
}

UPDATES = {
    "tb-500": {
        "background": "Thymosin Beta-4 (TB-4) is a naturally occurring 43-amino-acid peptide found in virtually all cells except red blood cells. TB-500 is the synthetic version of TB-4. While TB-500 is widely discussed for healing and regeneration, it also exerts potent immune modulatory and inflammation resolving effects.",
        "clinical_applications": [
            "Inflammatory Conditions: Support for chronic inflammatory states, systemic or organ-specific inflammation, and acute inflammatory episodes (joint, pulmonary, GI, post-surgical).",
            "Autoimmune Support: Adjunct to standard care for autoimmune disease management and flare tissue protection (MS, RA models). Aims to balance rather than broadly suppress immunity.",
            "Infection Recovery: Support during recovery from severe infections when the immune system is dysregulated; helps rebuild mucosal barriers post-viral syndromes.",
            "Immune-Related Tissue Damage: Potential applications in lung inflammation/pulmonary fibrosis, neuroinflammation, inflammatory skin conditions, and GI inflammatory diseases.",
            "Tissue Repair & Regeneration: Promotes angiogenesis, cell migration, and accelerates wound healing in soft tissue and muscle injuries.",
            "Anti-fibrotic Support: May reduce scar tissue formation during healing phases.",
        ],
        "side_effects": {
            "common": [
                "Fatigue or mild lethargy",
                "Headache",
                "Injection site reactions (redness, itching, mild pain)",
                "Nausea (usually mild and transient)",
            ],
            "less_common": [
                "Temporary changes in immune parameters (laboratory markers)",
                "Altered response to infections during treatment (often improved defense)",
                "Changes in autoimmune disease activity (commonly improvement)",
            ],
            "rare": [
                "Theoretical risk of impaired infection response at very high/prolonged doses",
                "May theoretically trigger or worsen flares in some autoimmune conditions",
            ],
        },
        "contraindications": [
            "Active, untreated serious infections (particularly bacterial sepsis) without specialist supervision",
            "Uncontrolled autoimmune conditions with very high disease activity",
            "Pregnancy and breastfeeding (insufficient safety data)",
            "Organ transplant recipients without transplant/immunology specialist oversight",
            "Known immune dysregulation disorders where additional modulation may be unpredictable",
        ],
        "interactions": {
            "medications": [
                "Immunosuppressants (corticosteroids, calcineurin inhibitors, biologics): complex interplay requiring specialist supervision",
                "Immunostimulants: potential additive effects; combined use could push immune system toward over-activation",
                "Anti-inflammatory medications (NSAIDs, biologics): generally complementary for resolution and tissue protection",
                "Anticoagulants and antiplatelet agents: theoretical concerns due to angiogenic effects; monitor coagulation",
            ],
            "supplements": [
                "Immune-stimulating herbs (echinacea, medicinal mushrooms): potentially additive immune activation",
                "Anti-inflammatory supplements (omega-3, curcumin): generally complementary",
                "Antioxidants: typically synergistic against oxidative stress",
                "Other peptides (BPC-157, GHK-Cu): complex interactions possible; often used together in advanced protocols",
            ],
            "foods": [],
        },
    },

    "semax": {
        "background": "Semax was developed in Russia in the 1980s-1990s, derived from a fragment of adrenocorticotropic hormone (ACTH) but lacking ACTH's hormonal effects. It has been approved as a medication in Russia and some Eastern European countries for various neurological and cognitive indications.",
        "clinical_applications": [
            "Cognitive Enhancement: Improves focus, attention, memory formation/recall, learning capacity, mental clarity, and processing speed.",
            "Neuroprotection: Protects against neuronal damage, supports recovery after concussion/mild TBI, and may benefit neurodegenerative concerns.",
            "Mood and Anxiety Regulation: Mild anxiolytic effects, mood stabilization, enhanced stress resilience, emotional regulation support.",
            "Neurological Recovery: Accelerates recovery after stroke, supports rehabilitation in TBI cases, aids neurological rehabilitation in clinical settings.",
            "Specific Neurological Conditions: Off-label use for attention deficit disorders, mild cognitive impairment, certain headaches, and asthenic conditions (physical/mental fatigue).",
            "Preventative Neuroprotection: Prevention of age-related cognitive decline, protection during high-risk periods for brain injury, general brain health maintenance.",
        ],
        "side_effects": {
            "common": [
                "Mild headache (typically transient)",
                "Temporary nasal irritation with intranasal application",
                "Mild stimulation or increased alertness",
                "Occasional mild anxiety in sensitive individuals",
            ],
            "less_common": [
                "Mild changes in blood pressure",
                "Insomnia if used too late in the day",
                "Irritability in some individuals",
                "Temporary mood changes",
            ],
            "rare": [
                "Allergic reactions",
                "Significant changes in neurotransmitter balance",
                "Exacerbation of certain psychiatric conditions",
                "Paradoxical reactions (e.g., increased fatigue)",
            ],
        },
        "contraindications": [
            "Pregnancy and breastfeeding (limited research)",
            "Children, unless medically supervised",
            "Severe psychiatric conditions, particularly psychotic disorders",
            "Severe hypertension",
            "History of significant adverse reactions to peptide therapies",
            "Immediately before or after major neurosurgery without specialist oversight",
        ],
        "interactions": {
            "medications": [
                "Stimulants (ADHD medications): potential additive stimulant effects",
                "Antidepressants: complex interactions possible; monitoring recommended",
                "MAO inhibitors: theoretical interactions with monoamine systems",
                "Blood pressure medications: blood pressure should be monitored",
            ],
            "supplements": [
                "Other nootropics: generally synergistic; lower initial doses recommended",
                "Stimulatory supplements (caffeine-heavy products): potential additive stimulation",
                "Choline sources: often complementary, especially for memory support",
                "Adaptogens: generally complementary for stress resilience",
            ],
            "foods": [],
        },
    },

    "selank": {
        "background": "Selank was developed in Russia as a synthetic analog of tuftsin, a natural immunomodulatory peptide. It was designed to combine anxiolytic and nootropic properties. Like Semax, it has been approved as a medication in Russia for certain neurological and psychiatric applications.",
        "clinical_applications": [
            "Anxiety Reduction: Decreased anxiety without sedation, enhanced stress resilience, support for GAD, social anxiety, and performance anxiety.",
            "Cognitive Enhancement: Improves focus, learning, memory, mental clarity, and cognitive performance under stress.",
            "Mood Support: Mild mood stabilization, potential antidepressant-like properties, enhanced emotional resilience.",
            "Immune Modulation: Supports balanced immune function and neuroimmune interactions.",
            "Neurological and Immune Support: Recovery from illness affecting cognition/mood, general neuroimmune health support.",
            "Adjunct Therapy: Adjunct for panic symptoms and mild-to-moderate depression.",
        ],
        "side_effects": {
            "common": [
                "Mild nasal irritation with intranasal use",
                "Temporary mild headache",
                "Slight dizziness (uncommon)",
            ],
            "less_common": [
                "Changes in energy levels (calmer or slightly more energized)",
                "Mild digestive discomfort",
                "Temporary changes in mood",
                "Mild sleep changes (often improved sleep; occasionally insomnia or vivid dreams)",
            ],
            "rare": [
                "Allergic reactions",
                "Significant mood changes",
                "Paradoxical anxiety (very rare)",
                "Immune system changes (mainly theoretical)",
            ],
        },
        "contraindications": [
            "Pregnancy and breastfeeding (limited research)",
            "Children, unless medically supervised",
            "Severe psychiatric conditions, particularly psychotic disorders",
            "History of significant adverse reactions to peptide therapies",
            "Certain immune disorders without appropriate medical oversight",
        ],
        "interactions": {
            "medications": [
                "Benzodiazepines and other anxiolytics: potentially synergistic; may allow dose reduction",
                "Antidepressants: complex interactions possible; careful monitoring recommended",
                "Immunomodulatory drugs: theoretical interactions with immune system function",
                "Cognitive enhancers and stimulants: generally complementary; monitor for overstimulation",
            ],
            "supplements": [
                "GABAergic supplements (GABA, L-theanine, phenibut): potentially synergistic",
                "Adaptogens (ashwagandha, rhodiola): generally complementary",
                "Immune-modulating supplements: interactions may be complex; individual monitoring advised",
                "Other nootropics: usually complementary in cognitive enhancement strategies",
            ],
            "foods": [],
        },
    },

    "kpv": {
        "background": "KPV is the C-terminal tripeptide of α-MSH (alpha melanocyte-stimulating hormone). It retains the potent anti-inflammatory and immunomodulatory properties of α-MSH without its melanotropic (skin darkening) effects, making it suitable for systemic and topical therapeutic use.",
        "clinical_applications": [
            "Inflammatory Bowel Conditions (Experimental/Off-Label): Potential benefit for ulcerative colitis, Crohn's disease, inflammatory IBS, and intestinal permeability/leaky gut — reducing mucosal inflammation and supporting healing.",
            "Skin Conditions: Useful in atopic dermatitis (eczema), psoriasis, contact dermatitis, rosacea, and other localized inflammatory skin rashes. Topical formulations for targeted anti-inflammatory action.",
            "General Inflammatory Support: Balanced reduction of excessive inflammation without full immunosuppression; adjunct to dietary/lifestyle/pharmacologic strategies.",
            "Recovery and Healing Support: Reduces over-exuberant inflammation during healing; supports tissue repair while preserving necessary immune activity; may minimize scarring.",
        ],
        "side_effects": {
            "common": [
                "Mild injection site pain or irritation (systemic use)",
                "Temporary redness, tingling, or stinging at application sites (topical use)",
            ],
            "less_common": [
                "Temporary fatigue or mild lethargy (uncommon and usually transient)",
            ],
            "rare": [
                "Mild skin irritation in sensitive individuals (topical use)",
                "Allergic reactions",
            ],
        },
        "contraindications": [
            "Pregnancy and breastfeeding (insufficient human safety data)",
            "Active infections (inflammation is needed for pathogen clearance; excessive suppression may be detrimental)",
            "Children and adolescents (use only under strict medical supervision)",
            "Known hypersensitivity or allergic reactions to KPV or formulation components",
        ],
        "interactions": {
            "medications": [
                "Immunosuppressants: potential additive immunomodulatory effects; increased infection susceptibility if combined excessively",
                "Other anti-inflammatory medications (NSAIDs, biologics): potentially additive; may allow dose reductions but require monitoring",
                "Corticosteroids: potentially complementary, but combined use increases overall anti-inflammatory load",
            ],
            "supplements": [
                "Anti-inflammatory supplements (omega-3, curcumin, resveratrol): likely additive or synergistic",
                "Immune-stimulating supplements (medicinal mushrooms, echinacea): potentially opposing effects; use deliberately and supervised",
                "Gut-health supplements (glutamine, probiotics, prebiotics): complementary in gut-focused protocols",
            ],
            "foods": [],
        },
    },

    "cjc-1295-dac": {
        "background": "CJC-1295 is a synthetic analog of growth hormone-releasing hormone (GHRH) designed for a longer half-life than natural GHRH. The DAC (Drug Affinity Complex) version binds to albumin in the bloodstream, dramatically extending its half-life to several days, enabling less frequent dosing than 'Modified GRF 1-29' (CJC-1295 without DAC).",
        "clinical_applications": [
            "Anti-Aging and Wellness: Addresses age-related decline in GH production; supports vitality, energy, and body composition with aging.",
            "Athletic Performance and Recovery: Enhances recovery between training sessions, supports tissue repair after exercise, improves training adaptation.",
            "Growth Hormone Optimization: Significant increase in GH release, enhancement of natural GH pulsatility, sustained elevation of IGF-1 (especially with DAC).",
            "Body Composition Effects: Potential fat reduction, support for lean muscle maintenance/growth, improved metabolism and energy utilization.",
            "Convenience-Focused Protocols: Less frequent injections (suitable for travelers); maintains steadier GH levels throughout the week with DAC.",
            "Synergistic Protocols: Commonly combined with GHRPs for enhanced GH release; foundation of comprehensive GH optimization protocols.",
        ],
        "side_effects": GHRH_CLASS_SIDE_EFFECTS,
        "contraindications": [
            "Active or recent cancer",
            "Uncontrolled diabetes or severe insulin resistance",
            "Active pituitary tumors",
            "Uncontrolled hypertension",
            "Pregnancy and breastfeeding",
            "Children and adolescents (unless under strict medical supervision)",
        ],
        "interactions": {
            "medications": [
                "Glucocorticoids: may blunt GH response and reduce effectiveness",
                "Diabetes medications: blood sugar can shift; dosage adjustment may be required",
                "Exogenous growth hormone: overlap may lead to excessive GH/IGF-1 levels",
                "Thyroid medications: GH can influence thyroid hormone metabolism; monitoring may be needed",
            ],
            "supplements": [
                "Arginine and other GH-stimulating amino acids: potentially synergistic",
                "Melatonin: may enhance sleep-related GH release",
                "Blood sugar-regulating supplements: may require adjustment as GH affects glucose balance",
            ],
            "foods": [
                "Carbohydrates and fats within ~2 hours before dosing may reduce GH response",
                "Protein has less impact but can modestly blunt effect",
            ],
        },
    },

    "tesamorelin": {
        "background": "Tesamorelin is an FDA-approved GHRH analog specifically indicated for reducing excess abdominal visceral adipose tissue in HIV-infected patients with lipodystrophy. It is a synthetic 44-amino-acid analog of human GHRH with a trans-3-hexenoic acid group added to the N-terminus for increased stability and potency.",
        "clinical_applications": [
            "Visceral Fat Management: Addresses excess abdominal fat distribution, supports metabolic health improvement, body composition optimization.",
            "Metabolic Health Optimization: Supports healthy lipid profiles, potential benefits for liver health and fatty liver, addresses metabolic syndrome components.",
            "Growth Hormone Optimization: Significant increase in GH release, enhancement of GH pulsatility, elevation of IGF-1 with regular use.",
            "Body Composition Effects: Favorable fat-to-muscle ratio changes, potential preservation of lean body mass during fat loss.",
            "Anti-Aging and Wellness: Combats age-related changes in body composition, supports vitality and metabolic function with aging.",
            "Synergistic Protocols: Combined with GHRPs for greater GH release; included in comprehensive body composition and metabolic health protocols.",
        ],
        "side_effects": GHRH_CLASS_SIDE_EFFECTS,
        "contraindications": [
            "Active or recent cancer",
            "Uncontrolled diabetes or severe insulin resistance",
            "Active pituitary tumors",
            "Critical illness",
            "Pregnancy and breastfeeding",
            "Children and adolescents",
            "Hypersensitivity to Tesamorelin or mannitol",
        ],
        "interactions": {
            "medications": [
                "Glucocorticoids: may reduce effectiveness",
                "Diabetes medications: may require dose adjustments due to changes in glucose handling",
                "Growth hormone: overlapping mechanism can lead to excessive GH/IGF-1",
                "Estrogens: may modulate GH responsiveness",
            ],
            "supplements": [
                "Arginine and GH-stimulating amino acids: potentially synergistic",
                "Blood sugar-regulating supplements: may need adjustment",
            ],
            "foods": [
                "Carbohydrates and fats within ~2 hours before dosing reduce GH response",
                "Protein has less impact but can still modestly blunt effect",
            ],
        },
    },
}


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    for slug, fields in UPDATES.items():
        existing = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "name": 1})
        if not existing:
            print(f"SKIP - slug not found: {slug}")
            continue
        await db.peptide_library.update_one({"slug": slug}, {"$set": fields})
        print(f"UPDATED - {existing['name']} ({slug}): bg={bool(fields.get('background'))}, "
              f"clin={len(fields.get('clinical_applications', []))}, "
              f"se_common={len(fields.get('side_effects', {}).get('common', []))}, "
              f"contra={len(fields.get('contraindications', []))}, "
              f"meds={len(fields.get('interactions', {}).get('medications', []))}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
