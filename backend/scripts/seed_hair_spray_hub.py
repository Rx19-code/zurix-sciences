"""Seed the Stack Hub for GHK-Cu + AHK-Cu Hair Growth Spray. Idempotent upsert by slug.
peptide_name is the full product name so the product->hub matcher (longest normalized
substring) selects THIS hub over the generic GHK-Cu / AHK-Cu hubs.
"""
import asyncio
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def proto(order, name, goal, compounds, steps, best_for, duration):
    return {"id": str(uuid.uuid4()), "order": order, "name": name, "goal": goal,
            "compounds": compounds, "protocol": steps, "best_for": best_for, "duration": duration}


HUB = {
    "slug": "hair-growth-spray",
    "peptide_slug": "hair-growth-spray",
    "peptide_name": "GHK-Cu + AHK-Cu Hair Growth Spray",
    "title": "GHK-Cu + AHK-Cu Hair Growth Spray Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "Skin / Regeneration",
    "category_slug": "skin-regeneration",
    "classification": "Topical Copper Peptide Spray (GHK-Cu + AHK-Cu)",
    "also_known_as": ["Hair Growth Spray", "Copper Peptide Hair Spray"],
    "description": "A leave-on topical spray combining GHK-Cu and AHK-Cu — two copper-binding peptides researched for hair follicle stimulation, dermal papilla proliferation, scalp angiogenesis and improved hair density. Non-injectable and convenient for daily scalp application.",
    "core_info": {
        "function": "Hair follicle stimulation, scalp vascularization and improved hair density.",
        "typical_dosage": "Apply to affected scalp areas 1–2x daily",
        "administration": "Topical spray (leave-on)",
        "best_timing": "Clean, dry scalp — morning and/or before bed",
        "common_cycle": "12–16+ weeks (hair cycles are slow)",
        "common_pairings": ["AHK-Cu", "PTD-DBM", "GHK-Cu", "Microneedling"],
    },
    "protocols": [
        proto(1, "Daily Scalp Application Protocol", "Baseline daily topical routine for hair density.",
              [{"name": "GHK-Cu + AHK-Cu Hair Growth Spray", "dose": "5–8 sprays to thinning areas, 1–2x daily"}],
              ["Apply to a clean, dry scalp — part the hair to reach the skin directly.",
               "5–8 sprays over thinning areas; massage in gently for 30–60s.",
               "Leave on (do not rinse for several hours); apply morning and/or before bed.",
               "Commit to at least 12–16 weeks — hair responds slowly.",
               "Photograph density every 2 weeks to track progress."],
              "First-time topical hair research", "12–16 weeks"),
        proto(2, "Microneedling Synergy Protocol", "Enhance peptide uptake with weekly microneedling.",
              [{"name": "GHK-Cu + AHK-Cu Hair Growth Spray", "dose": "daily, plus post-needling application"}],
              ["Microneedle the scalp 0.5–1.0 mm once weekly (clean tool, clean scalp).",
               "Apply the spray daily on non-needling days.",
               "On the needling day, wait ~24h before applying to avoid irritation.",
               "Avoid harsh shampoos/styling products during the protocol.",
               "Reassess density at week 12."],
              "Maximizing topical absorption", "12–16 weeks"),
        proto(3, "Intensive Regrowth Stack", "Layer the spray with injectable follicle stimulation.",
              [{"name": "GHK-Cu + AHK-Cu Hair Growth Spray", "dose": "5–8 sprays 2x daily"},
               {"name": "AHK-Cu", "dose": "1 mg SC scalp-adjacent 3x/week"},
               {"name": "PTD-DBM", "dose": "topical per protocol on alternate days"}],
              ["Spray twice daily on clean scalp.",
               "AHK-Cu into scalp-adjacent sites Mon/Wed/Fri.",
               "PTD-DBM topical on alternate days (not immediately after needling).",
               "Weekly microneedling on a separate day; photograph every 2 weeks."],
              "Advanced hair-regrowth research", "16 weeks"),
        proto(4, "Maintenance Protocol", "Sustain gains after an intensive phase.",
              [{"name": "GHK-Cu + AHK-Cu Hair Growth Spray", "dose": "5 sprays once daily"}],
              ["Reduce to once daily application on the maintenance areas.",
               "Continue gentle scalp care and adequate protein/iron intake.",
               "Optional monthly microneedling to sustain uptake.",
               "Re-intensify if shedding increases for 2+ weeks."],
              "Maintaining results after regrowth", "Ongoing"),
    ],
}


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    existing = await db.stack_hubs.find_one({"slug": HUB["slug"]}, {"_id": 1})
    await db.stack_hubs.replace_one({"slug": HUB["slug"]}, HUB, upsert=True)
    print(f"{'updated' if existing else 'created'}: {HUB['slug']} ({len(HUB['protocols'])} protocols)")
    total = await db.stack_hubs.count_documents({})
    print("total hubs:", total)


asyncio.run(main())
