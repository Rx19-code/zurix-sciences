"""Merge protocols from Expanded_Thymosin_Alpha1_Protocol_Collection.pdf into the
existing Thymosin Alpha-1 hub. Adds new protocols only (skips duplicates by name)."""
import asyncio
import os
import uuid
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


def _c(name, dose):
    return {"name": name, "dose": dose}


# Protocols from Expanded_Thymosin_Alpha1_Protocol_Collection.pdf
NEW_PROTOCOLS = [
    {
        "name": "Thymosin Alpha-1 Immune Priming Cycle",
        "goal": "Supports T-cell activation and immune readiness.",
        "compounds": [
            _c("Thymosin Alpha-1", "1.5 mg per dose"),
            _c("Bacteriostatic water", "as needed"),
            _c("Insulin syringe", "1 mL"),
        ],
        "protocol": [
            "Reconstitute with bacteriostatic water.",
            "Inject subcutaneously into the abdominal area.",
            "Use 5 days weekly for 4 weeks.",
        ],
        "best_for": "Useful before travel, seasonal exposure, or immune reset",
        "duration": "4 weeks",
    },
    {
        "name": "Triple Shield: Ta1 + LL-37 + TB-500",
        "goal": "Comprehensive immune and recovery support.",
        "compounds": [
            _c("Thymosin Alpha-1", "750 mcg"),
            _c("LL-37", "100 mcg"),
            _c("TB-500", "2 mg"),
        ],
        "protocol": [
            "Administer Ta1 and LL-37 daily.",
            "Use TB-500 twice weekly.",
            "Cycle 3 weeks on, 1 week off.",
        ],
        "best_for": "High-stress environments or immune recovery",
        "duration": "3 weeks on, 1 week off",
    },
    {
        "name": "Long COVID Immune Reboot Cycle",
        "goal": "Supports post-viral recovery and inflammation reduction.",
        "compounds": [
            _c("Thymosin Alpha-1", "1.5 mg 2x/week"),
            _c("TB-500", "2 mg 2x/week"),
            _c("LL-37", "100 mcg daily"),
        ],
        "protocol": [
            "Administer peptides subcutaneously.",
            "Continue for 6 weeks.",
            "Optional mitochondrial support may be added.",
        ],
        "best_for": "Long COVID and post-viral fatigue recovery",
        "duration": "6 weeks",
    },
    {
        "name": "Autoimmune Inflammation Modulation Stack",
        "goal": "Helps calm systemic inflammation and immune overactivation.",
        "compounds": [
            _c("Thymosin Alpha-1", "750 mcg 3x/week"),
            _c("BPC-157", "250 mcg daily"),
            _c("Omega-3", "2–3 g/day"),
        ],
        "protocol": [
            "Administer peptides subcutaneously.",
            "Take Omega-3 daily.",
            "Monitor symptoms with practitioner oversight.",
        ],
        "best_for": "Autoimmune flare prevention cycles",
        "duration": "Cycle-based",
    },
    {
        "name": "Chronic Fatigue Immune Recovery Plan",
        "goal": "Supports energy recovery and immune regulation.",
        "compounds": [
            _c("Thymosin Alpha-1", "1 mg 3x/week"),
            _c("TB-500", "2 mg weekly"),
            _c("Adaptogenic herbs", "as directed"),
        ],
        "protocol": [
            "Inject Ta1 Monday/Wednesday/Friday.",
            "Administer TB-500 weekly.",
            "Continue for 6 weeks.",
        ],
        "best_for": "After illness or immune burnout",
        "duration": "6 weeks",
    },
    {
        "name": "Seasonal Immune Prep Stack",
        "goal": "Enhances seasonal immune resistance.",
        "compounds": [
            _c("Thymosin Alpha-1", "1 mg 3x/week"),
            _c("LL-37", "100 mcg/day"),
            _c("Vitamin D3", "5000 IU/day"),
        ],
        "protocol": [
            "Begin protocol 2 weeks before exposure season.",
            "Use Ta1 Monday/Wednesday/Friday.",
            "Continue Vitamin D3 daily.",
        ],
        "best_for": "Before winter season or travel",
        "duration": "2 weeks pre-season + ongoing",
    },
    {
        "name": "Thymus Rejuvenation & Immune Optimization",
        "goal": "Supports thymic regeneration and immune resilience.",
        "compounds": [
            _c("Thymosin Alpha-1", "1.5 mg"),
            _c("Thymosin Beta-4", "2.5 mg"),
            _c("Vitamin D3", "5000 IU"),
        ],
        "protocol": [
            "Inject Ta1 and TB-4 twice weekly.",
            "Use for 6 weeks.",
            "Repeat every 6 months if needed.",
        ],
        "best_for": "Aging adults or post-viral recovery",
        "duration": "6 weeks (repeat every 6 months)",
    },
    {
        "name": "Cellular Inflammation Suppression & Oxidative Defense",
        "goal": "Supports antioxidant defense and inflammatory balance.",
        "compounds": [
            _c("Thymosin Alpha-1", "1.5 mg"),
            _c("NAC", "600 mg"),
            _c("Curcumin", "500 mg"),
        ],
        "protocol": [
            "Inject Ta1 2–3x weekly.",
            "Take NAC and curcumin daily.",
            "Cycle curcumin 3 months on, 1 month off.",
        ],
        "best_for": "Chronic inflammatory states",
        "duration": "3 months on, 1 month off (curcumin)",
    },
    {
        "name": "Inflammaging Reduction & Immune Rebalancing",
        "goal": "Supports immune modulation and healthy aging.",
        "compounds": [
            _c("Thymosin Alpha-1", "1.5 mg"),
            _c("Bacteriostatic water", "as needed"),
            _c("Insulin syringe", "1 mL"),
        ],
        "protocol": [
            "Reconstitute peptide with bacteriostatic water.",
            "Inject 3x weekly for 6–8 weeks.",
            "Repeat 2–4 cycles yearly.",
        ],
        "best_for": "Low-grade chronic inflammation",
        "duration": "6–8 weeks per cycle",
    },
]


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    hub = await db.stack_hubs.find_one({"peptide_slug": "thymosin-alpha"}, {"_id": 0})
    if not hub:
        print("ERROR: Thymosin Alpha-1 hub not found.")
        return

    existing_names = {p["name"].strip().lower() for p in hub.get("protocols", [])}
    existing_max_order = max((p.get("order", 0) for p in hub.get("protocols", [])), default=0)

    appended = 0
    skipped = []
    new_list = list(hub["protocols"])
    next_order = existing_max_order + 1

    for np in NEW_PROTOCOLS:
        if np["name"].strip().lower() in existing_names:
            skipped.append(np["name"])
            continue
        new_list.append({
            "id": str(uuid.uuid4()),
            "order": next_order,
            **np,
        })
        next_order += 1
        appended += 1

    await db.stack_hubs.update_one(
        {"peptide_slug": "thymosin-alpha"},
        {"$set": {"protocols": new_list}},
    )

    print(f"MERGED into Thymosin Alpha-1 hub: +{appended} new protocols (total: {len(new_list)})")
    if skipped:
        print("Skipped (duplicate name):", skipped)

    # Re-export seed_stack_hubs_all.json so production sync stays in sync
    docs = await db.stack_hubs.find({}, {"_id": 0}).to_list(None)
    with open(os.path.join(os.path.dirname(__file__), "..", "seed_stack_hubs_all.json"), "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False, default=str)

    total_protocols = sum(len(h.get("protocols", [])) for h in docs)
    print(f"Total hubs: {len(docs)}  |  Total protocols: {total_protocols}")
    print("Exported seed_stack_hubs_all.json")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
