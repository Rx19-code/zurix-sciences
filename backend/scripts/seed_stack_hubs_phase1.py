"""
PHASE 1 - Migration to new "Stack Hub" architecture.

- Drops the legacy `peptide_stacks` collection (backup saved at
  seed_peptide_stacks_legacy_backup.json).
- Seeds the first hub: AOD-9604 Stack Library with 15 protocols.
- Creates the `protocol_ratings` collection (empty, ready to receive votes).

A "Stack Hub" is a HUB centered on a peptide, containing multiple
protocol variations (e.g., AOD-9604 hub -> 15 protocols).
"""
import asyncio
import os
import uuid

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


AOD_HUB = {
    "slug": "aod-9604",
    "peptide_slug": "aod-9604",
    "peptide_name": "AOD-9604",
    "title": "AOD-9604 Stack Library",
    "subtitle": "Premium Protocol Collection",
    "description": (
        "AOD-9604 is a modified fragment of human growth hormone (176\u2013191) "
        "designed to stimulate lipolysis without significantly affecting IGF-1 "
        "or blood glucose pathways. Below are 15 curated protocol variations "
        "for different goals \u2014 from beginner fat loss to stage prep."
    ),
    "core_info": {
        "function": "Fat loss, metabolic support, lipolysis activation.",
        "typical_dosage": "200\u2013500 mcg daily.",
        "administration": "Subcutaneous injection.",
        "best_timing": "Morning, fasted, pre-cardio, or pre-workout.",
        "common_cycle": "4\u201312 weeks.",
        "common_pairings": [
            "CJC-1295", "Ipamorelin", "Berberine", "L-Carnitine",
            "GHK-Cu", "Yohimbine", "DIM", "BPC-157",
        ],
    },
    "protocols": [
        {
            "id": str(uuid.uuid4()),
            "order": 1,
            "name": "Beginner Fat Loss Stack",
            "goal": "Entry-level fat loss and metabolic activation.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "L-Carnitine Tartrate", "dose": "500 mg"},
            ],
            "protocol": [
                "Morning fasted administration",
                "Optional fasted cardio",
                "4\u20136 week duration",
            ],
            "best_for": "Beginners and first-time users.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 2,
            "name": "Rapid Cut Stack",
            "goal": "Aggressive short-term fat reduction.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg AM"},
                {"name": "CJC-1295", "dose": "100 mcg PM"},
                {"name": "Ipamorelin", "dose": "100 mcg PM"},
            ],
            "protocol": [
                "Morning fasted injection",
                "Night GH support",
                "Low-carb / high-protein nutrition",
            ],
            "best_for": "Photoshoots, rapid cuts, short-term conditioning.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 3,
            "name": "Keto Fat Adaptation Stack",
            "goal": "Ketosis optimization and metabolic flexibility.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Berberine", "dose": "500 mg"},
                {"name": "MCT Oil", "dose": "1 tbsp"},
            ],
            "protocol": [
                "Morning fasted administration",
                "Ketogenic nutrition support",
            ],
            "best_for": "Keto users and biohackers.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 4,
            "name": "Women's Hormonal Shred Stack",
            "goal": "Female hormonal fat-loss support.",
            "compounds": [
                {"name": "AOD-9604", "dose": "250\u2013300 mcg"},
                {"name": "GHK-Cu", "dose": "100 mcg topical"},
                {"name": "DIM", "dose": "150 mg"},
            ],
            "protocol": [
                "Morning dosing",
                "Skin tightening support",
                "Hormonal optimization support",
            ],
            "best_for": "Women over 35 and hormonal fat distribution.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 5,
            "name": "Visceral Fat & Insulin Reset Stack",
            "goal": "Reduce visceral fat and improve insulin sensitivity.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Ipamorelin", "dose": "100 mcg PM"},
                {"name": "Berberine", "dose": "500 mg 2x/day"},
            ],
            "protocol": [
                "Morning fat oxidation",
                "Evening GH support",
                "Insulin sensitivity support",
            ],
            "best_for": "Abdominal fat and metabolic syndrome profiles.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 6,
            "name": "Recomp & Lean Physique Stack",
            "goal": "Body recomposition while preserving lean mass.",
            "compounds": [
                {"name": "AOD-9604", "dose": "250 mcg"},
                {"name": "CJC-1295", "dose": "100 mcg"},
                {"name": "Ipamorelin", "dose": "100 mcg"},
            ],
            "protocol": [
                "Morning fat oxidation",
                "Night GH optimization",
                "High-protein training phase",
            ],
            "best_for": "Athletes and lean physique goals.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 7,
            "name": "Busy Lifestyle Fat Loss Stack",
            "goal": "Stress-friendly fat loss support.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Berberine", "dose": "500 mg"},
                {"name": "L-Theanine", "dose": "200 mg"},
            ],
            "protocol": [
                "Morning administration",
                "Cortisol / stress support",
            ],
            "best_for": "Busy professionals and high-stress lifestyles.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 8,
            "name": "Appetite Control Stack",
            "goal": "Craving reduction and appetite management.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Berberine", "dose": "500 mg"},
                {"name": "5-HTP", "dose": "100 mg"},
            ],
            "protocol": [
                "Morning injection",
                "Appetite support throughout the day",
            ],
            "best_for": "Cravings and appetite dysregulation.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 9,
            "name": "Athletic Conditioning Stack",
            "goal": "Performance-focused cutting and conditioning.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Yohimbine HCl", "dose": "5 mg"},
                {"name": "Ipamorelin", "dose": "100 mcg PM"},
            ],
            "protocol": [
                "Fasted cardio support",
                "Conditioning-focused protocol",
            ],
            "best_for": "Athletes and advanced conditioning phases.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 10,
            "name": "Recovery & Metabolic Reset Stack",
            "goal": "Recovery support with metabolic restoration.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "BPC-157", "dose": "250 mcg"},
                {"name": "Ashwagandha", "dose": "500 mg"},
            ],
            "protocol": [
                "Recovery-focused administration",
                "Stress reduction support",
            ],
            "best_for": "Overtraining and post-diet recovery.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 11,
            "name": "Fasted Morning GH Burn Stack",
            "goal": "Maximum fasted-state fat oxidation.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "CJC-1295", "dose": "100 mcg"},
                {"name": "Ipamorelin", "dose": "100 mcg"},
            ],
            "protocol": [
                "Immediate morning administration",
                "Fasted cardio optimized",
            ],
            "best_for": "Morning training and advanced fat burning.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 12,
            "name": "Anti-Bloat & Dry Look Stack",
            "goal": "Reduce water retention and tighten appearance.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Dandelion Root Extract", "dose": "250 mg"},
                {"name": "Ipamorelin", "dose": "100 mcg"},
            ],
            "protocol": [
                "Morning administration",
                "Water retention support",
            ],
            "best_for": "Travel rebound and cosmetic tightening.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 13,
            "name": "Long-Term Sustainable Cut Stack",
            "goal": "Gradual long-term fat reduction.",
            "compounds": [
                {"name": "AOD-9604", "dose": "250 mcg"},
                {"name": "CJC-1295", "dose": "100 mcg"},
                {"name": "Ipamorelin", "dose": "100 mcg"},
            ],
            "protocol": [
                "Moderate calorie deficit",
                "Long-term cycling",
            ],
            "best_for": "Lifestyle users and sustainable dieting.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 14,
            "name": "Shift Worker Metabolic Stack",
            "goal": "Support metabolism during circadian disruption.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "Berberine", "dose": "500 mg"},
                {"name": "CJC-1295", "dose": "100 mcg"},
            ],
            "protocol": [
                "Flexible administration timing",
                "Circadian-support optimization",
            ],
            "best_for": "Night shifts, travelers, rotating schedules.",
        },
        {
            "id": str(uuid.uuid4()),
            "order": 15,
            "name": "Ultra-Lean Stage Prep Stack",
            "goal": "Extreme conditioning and final-stage fat reduction.",
            "compounds": [
                {"name": "AOD-9604", "dose": "300 mcg"},
                {"name": "CJC-1295", "dose": "100 mcg"},
                {"name": "Yohimbine HCl", "dose": "5 mg"},
            ],
            "protocol": [
                "Fasted cardio optimization",
                "Short-term aggressive conditioning",
            ],
            "best_for": "Stage prep and ultra-lean physique goals.",
        },
    ],
}


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    # 1) Drop legacy stacks (backup already saved)
    legacy_count = await db.peptide_stacks.count_documents({})
    if legacy_count > 0:
        await db.peptide_stacks.drop()
        print(f"Dropped legacy peptide_stacks ({legacy_count} docs)")

    # 2) Seed AOD-9604 hub
    await db.stack_hubs.delete_many({"slug": AOD_HUB["slug"]})
    await db.stack_hubs.insert_one(AOD_HUB.copy())
    print(f"Inserted hub: {AOD_HUB['title']} with {len(AOD_HUB['protocols'])} protocols")

    # 3) Ensure protocol_ratings collection exists with index
    await db.protocol_ratings.create_index(
        [("user_id", 1), ("hub_slug", 1), ("protocol_id", 1)],
        unique=True,
    )
    print("Index on protocol_ratings created")

    hubs = await db.stack_hubs.count_documents({})
    print(f"\nTotal hubs: {hubs}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
