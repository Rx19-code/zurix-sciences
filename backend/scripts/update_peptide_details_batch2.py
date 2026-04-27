"""
Batch 2: BPC-157 and GHK-Cu detailed data.
Source: CJC-1295/Tesamorelin PDF (Feb 2026) - section 3 (BPC-157) and section 5 (GHK-Cu)
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

UPDATES = {
    "bpc-157": {
        "background": "BPC-157 is a partial sequence of the Body Protection Compound (BPC), a protein discovered in gastric juice. A large portion of the early research comes from Eastern Europe, particularly Croatia. It is widely used in research protocols for its broad tissue-repair, anti-inflammatory, and neuroprotective effects.",
        "clinical_applications": [
            "Tendon and Ligament Healing: Accelerated repair, enhanced tensile strength, improved collagen alignment, reduced re-injury risk.",
            "Muscle Recovery: Faster healing of muscle tears/strains, improved recovery from exercise-induced damage, protection against muscle wasting.",
            "Digestive System Health: Healing of gastric ulcers, support in IBD, protection against leaky gut, potential benefit in acid reflux.",
            "Nerve Regeneration: Support for peripheral nerve healing, benefits in nerve crush/compression injuries, possible neuroprotective effects.",
            "Joint and Bone Support: Potential benefits for joint inflammation, support for bone healing, cartilage protection, enhanced healing at bone-tendon junctions.",
            "Sports Injuries: Tendonitis/tendinopathy, muscle strains/tears, ligament sprains, overuse joint inflammation.",
        ],
        "side_effects": {
            "common": [
                "Mild injection site pain or irritation",
                "Temporary fatigue or lethargy",
                "Mild gastrointestinal discomfort with oral use",
            ],
            "less_common": [
                "Headache",
                "Dizziness",
                "Changes in appetite",
                "Mild nausea",
            ],
            "rare": [
                "Potential growth-promoting effects on pre-existing cancers",
                "Possible interaction with autoimmune conditions via altered healing and immune modulation",
                "Unknown long-term effects with extended continuous use",
                "Potential for altered inflammatory responses in certain diseases",
            ],
        },
        "contraindications": [
            "Active or recent cancer",
            "Pregnancy and breastfeeding",
            "Pre-operative period for certain surgeries (due to angiogenic effects)",
            "Uncontrolled autoimmune conditions",
            "Children and adolescents (unless medically supervised)",
            "Individuals with hemostatic disorders or on anticoagulant therapy (use with caution)",
        ],
        "interactions": {
            "medications": [
                "Corticosteroids: may counteract BPC-157's healing effects",
                "NSAIDs: complex interactions with healing and inflammation",
                "Immunosuppressants: theoretical interactions with immune/healing pathways",
                "Anticoagulants: caution due to angiogenesis and vessel effects",
            ],
            "supplements": [
                "Other healing peptides (TB-500, GHK-Cu): potentially synergistic",
                "Anti-inflammatory supplements: interactions may be complex",
                "Growth factors and hormones: potentially synergistic",
                "Physical therapy, PRP, stem cell treatments: often used together for additive benefit",
            ],
            "foods": [],
        },
    },

    "ghk-cu": {
        "background": "GHK-Cu was discovered in the 1970s by Dr. Loren Pickart during research on liver tissue regeneration. It is a naturally occurring tripeptide (Glycyl-L-Histidyl-L-Lysine) that strongly binds copper, found in human plasma, saliva, and urine. Endogenous levels decline significantly with age.",
        "clinical_applications": [
            "Skin Regeneration: Enhanced wound healing, increased collagen/elastin production, improved firmness and elasticity, reduction in fine lines and wrinkles.",
            "Tissue Repair: Accelerated healing across various tissues, improved repair quality, reduced scarring and fibrosis, support for connective tissue resilience.",
            "Anti-Inflammatory Effects: Reduction in inflammatory markers, support for inflammation resolution, potential benefits in chronic inflammatory conditions.",
            "Antioxidant Protection: Enhanced cellular antioxidant defenses, protection against oxidative stress, support for cellular repair, anti-aging effects.",
            "Neurological Benefits: Potential neuroprotective effects (experimental), support for nerve regeneration, possible cognitive benefits and protection against neurotoxicity in models.",
            "Dermatology and Aesthetic Use: Aging skin, sun damage/hyperpigmentation, scarring and wound healing, post-procedure recovery (microneedling, lasers, chemical peels).",
        ],
        "side_effects": {
            "common": [
                "Mild injection site reactions (topical or systemic)",
                "Temporary skin irritation with topical use",
            ],
            "less_common": [
                "Mild headache",
                "Metallic taste (with higher systemic doses)",
                "Transient redness or tingling at application site",
            ],
            "rare": [
                "Allergic reactions",
                "Copper accumulation with very high chronic doses (theoretical)",
                "Exacerbation of conditions involving copper metabolism",
            ],
        },
        "contraindications": [
            "Pregnancy and breastfeeding",
            "Wilson's disease or other disorders of copper metabolism",
            "Known hypersensitivity to copper or GHK-Cu",
            "Children and adolescents (unless medically supervised)",
        ],
        "interactions": {
            "medications": [
                "Copper-chelating drugs (e.g., penicillamine, trientine): can directly oppose GHK-Cu's activity",
                "Immunosuppressants: theoretical interactions with immune modulation",
                "Certain anti-inflammatory medications: may overlap or complicate response",
            ],
            "supplements": [
                "High-dose zinc: competes with copper and can reduce GHK-Cu effectiveness",
                "Other healing peptides (BPC-157, TB-500): can be synergistic",
                "Antioxidant supplements: usually synergistic with GHK-Cu's actions",
            ],
            "foods": [],
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
