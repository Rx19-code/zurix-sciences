"""Seed the BPC-157 + TB4 (TB-500) Blend: dedicated Stack Hub + full visible peptide card.
Idempotent. peptide_name = full blend name so the matcher picks THIS hub over BPC-157/TB-500.
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
    "slug": "bpc-tb500-blend",
    "peptide_slug": "bpc-tb500-blend",
    "peptide_name": "BPC-157 + TB4 Blend",
    "title": "BPC-157 + TB4 Blend Stack Library",
    "subtitle": "Premium Protocol Collection",
    "category": "Recovery / Repair",
    "category_slug": "recovery-repair",
    "classification": "Synergistic Healing Blend (BPC-157 + TB-500/TB4)",
    "also_known_as": ["BPC-157 + TB-500 Blend", "Wolverine Stack", "Healing Blend"],
    "description": "The classic recovery blend combining BPC-157 (localized tissue repair, gut and tendon healing) with TB-500/TB4 (systemic cell migration, flexibility and vascularization). Together they accelerate whole-body healing — one of the most researched recovery stacks.",
    "core_info": {
        "function": "Accelerated tissue repair, tendon/ligament & gut healing, systemic recovery.",
        "typical_dosage": "250 mcg + 250 mcg SC daily (loading), then taper",
        "administration": "Subcutaneous injection",
        "best_timing": "Daily during loading; near the injury area where possible",
        "common_cycle": "4-6 weeks loading, then maintenance",
        "common_pairings": ["GHK-Cu", "HGH", "Cartalax", "KPV"],
    },
    "protocols": [
        proto(1, "Foundational Healing Protocol", "Baseline daily blend dosing for general recovery.",
              [{"name": "BPC-157 + TB4 Blend", "dose": "250 mcg + 250 mcg SC once daily"}],
              ["Reconstitute the 5mg+5mg vial with 2 mL bacteriostatic water (0.1 mL = 250 mcg of each).",
               "Inject 0.1 mL (250/250 mcg) SC once daily.",
               "Where possible, inject subcutaneously near the area of interest.",
               "Run 4 weeks, then reassess; taper to maintenance."],
              "General recovery and healing research", "4-6 weeks"),
        proto(2, "Injury Repair Stack (Local + Systemic)", "Combine local BPC action with systemic TB coverage.",
              [{"name": "BPC-157 + TB4 Blend", "dose": "250/250 mcg SC 2x daily (loading)"}],
              ["Loading phase: 250/250 mcg twice daily for the first 2 weeks.",
               "Inject one dose near the injury site, one systemic.",
               "Reduce to once daily from week 3.",
               "Avoid maximal loading of the tissue for the first 3 weeks."],
              "Acute tendon/ligament/muscle injuries", "6 weeks"),
        proto(3, "Gut & Tendon Recovery Protocol", "Leverage BPC-157's gut/tendon affinity with TB support.",
              [{"name": "BPC-157 + TB4 Blend", "dose": "250/250 mcg SC daily"},
               {"name": "KPV", "dose": "250-500 mcg daily (optional, gut inflammation)"}],
              ["Blend 250/250 mcg SC daily.",
               "Optional KPV for inflammatory gut components.",
               "Support with an anti-inflammatory diet.",
               "Run 4-6 weeks."],
              "Gut integrity and tendon complaints", "4-6 weeks"),
        proto(4, "Connective Tissue Longevity Stack", "Pair the blend with collagen and bioregulator support.",
              [{"name": "BPC-157 + TB4 Blend", "dose": "250/250 mcg daily"},
               {"name": "GHK-Cu", "dose": "1-2 mg SC nightly"},
               {"name": "Cartalax", "dose": "10 mg daily x20-day block (optional)"}],
              ["Blend daily; GHK-Cu nightly for collagen/skin.",
               "Optional Cartalax bioregulator block for cartilage.",
               "Progressive, controlled loading only.",
               "Prioritize sleep and protein for tissue repair."],
              "Comprehensive connective-tissue support", "6-8 weeks"),
        proto(5, "Maintenance Protocol", "Sustain recovery after the loading phase.",
              [{"name": "BPC-157 + TB4 Blend", "dose": "250/250 mcg SC 2-3x/week"}],
              ["Reduce to 2-3 injections per week.",
               "Continue near any lingering area of concern.",
               "Re-intensify to daily if symptoms return.",
               "Keep the vial refrigerated at 2-8°C."],
              "Maintaining gains after an injury block", "Ongoing"),
    ],
}

CARD = {
    "slug": "bpc-157-tb4-blend-5-plus-5",
    "name": "BPC-157 + TB4 Blend",
    "description": "Synergistic recovery blend of BPC-157 (local repair) and TB-500/TB4 (systemic healing) for tissue regeneration",
    "category": "Recovery",
    "is_free": False,
    "presentations": ["5mg+5mg"],
    "also_known_as": ["BPC-157 + TB-500 Blend", "Wolverine Stack", "Healing Blend"],
    "has_product": True,
    "overview": {
        "function": "Accelerated tissue repair, tendon/ligament and gut healing, systemic recovery.",
        "mechanism_of_action": (
            "This blend pairs two complementary healing peptides. BPC-157 (Body Protection Compound) promotes "
            "angiogenesis, upregulates growth factor receptors and accelerates localized repair of tendon, ligament, "
            "muscle and gut tissue. TB-500 (a synthetic fragment of Thymosin Beta-4/TB4) regulates actin and promotes "
            "cell migration, flexibility and vascularization systemically. Together they cover both local and "
            "whole-body healing pathways."
        ),
        "considerations": (
            "Research use. Generally well tolerated. Mild injection-site reactions or transient fatigue possible. "
            "Inject near the area of interest when feasible. Avoid maximal loading of injured tissue during early weeks."
        ),
    },
    "administration": {
        "route": "Subcutaneous",
        "notes": "SC injection, ideally near the area of interest for the BPC-157 component. Reconstitute 5mg+5mg with 2 mL bacteriostatic water (0.1 mL = 250 mcg of each). Store refrigerated at 2-8°C.",
    },
    "protocols": {
        "title": "Subcutaneous Protocol (vial 5mg+5mg, 2 mL bac water)",
        "standard": {"route": "Subcutaneous", "frequency": "Daily (loading), then 2-3x/week"},
        "dosages": [
            {"indication": "General recovery", "schedule": "Once daily, SC", "dose": "250 + 250 mcg (0.1 mL)"},
            {"indication": "Acute injury (loading)", "schedule": "Twice daily, SC", "dose": "250 + 250 mcg (0.1 mL) each"},
            {"indication": "Maintenance", "schedule": "2-3x per week, SC", "dose": "250 + 250 mcg (0.1 mL)"},
        ],
        "phases": [
            {"number": 1, "phase": "Loading (Weeks 1-2)", "dose": "250/250 mcg 2x daily"},
            {"number": 2, "phase": "Standard (Weeks 3-6)", "dose": "250/250 mcg once daily"},
            {"number": 3, "phase": "Maintenance (Weeks 7+)", "dose": "250/250 mcg 2-3x/week"},
        ],
        "reconstitution_steps": [
            "Reconstitute the 5mg+5mg vial with 2 mL bacteriostatic water (0.1 mL = 250 mcg of each).",
            "Gently swirl until dissolved (do not shake).",
            "Draw 0.1 mL (10 units on a 100-unit insulin syringe) for a 250/250 mcg dose.",
            "Store reconstituted vial refrigerated at 2-8°C; use within 28 days.",
        ],
        "reconstitution": "Reconstitute 5mg+5mg with 2 mL bacteriostatic water (0.1 mL = 250 mcg of each). Store at 2-8°C.",
    },
    "research": {
        "mechanism": "BPC-157 drives localized repair/angiogenesis; TB-500/TB4 drives systemic cell migration and flexibility.",
        "steps": [
            "BPC-157 upregulates growth factor receptors and promotes angiogenesis",
            "BPC-157 accelerates tendon, ligament, muscle and gut healing locally",
            "TB-500/TB4 regulates actin and promotes cell migration systemically",
            "Combined local + systemic coverage for faster whole-body recovery",
        ],
        "references": [],
    },
    "synergy": {
        "interactions": [
            {"peptide": "BPC-157", "status": "SYNERGISTIC", "description": "Local repair component of the blend"},
            {"peptide": "TB-500", "status": "SYNERGISTIC", "description": "Systemic healing component of the blend"},
            {"peptide": "GHK-Cu", "status": "SYNERGISTIC", "description": "Collagen and connective-tissue support"},
            {"peptide": "KPV", "status": "COMPATIBLE", "description": "Anti-inflammatory support for gut-focused recovery"},
        ],
        "stacks": [],
    },
    "benefits": [
        "Accelerates tendon, ligament and muscle repair",
        "Combines local (BPC-157) and systemic (TB-500) healing",
        "Supports gut integrity and reduces inflammation",
        "Promotes angiogenesis and tissue vascularization",
        "One of the most researched recovery stacks",
    ],
    "legal_status": {
        "us": "Research compound — not FDA-approved for therapeutic use.",
        "uk": "Research chemical — laboratory use only.",
        "canada": "Research-only; not approved for therapeutic use.",
    },
    "side_effects": {
        "common": ["Mild injection site reactions"],
        "less_common": ["Transient fatigue or lightheadedness", "Temporary flushing"],
        "rare": ["Allergic reactions"],
    },
    "timing_goals": [
        {"goal": "Injury recovery", "timing": "250/250 mcg daily (loading) for 4-6 weeks"},
        {"goal": "Acute injury", "timing": "250/250 mcg 2x daily for 2 weeks, then taper"},
        {"goal": "Maintenance", "timing": "250/250 mcg 2-3x/week"},
    ],
}


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    h_existing = await db.stack_hubs.find_one({"slug": HUB["slug"]}, {"_id": 1})
    await db.stack_hubs.replace_one({"slug": HUB["slug"]}, HUB, upsert=True)
    print(f"hub {'updated' if h_existing else 'created'}: {HUB['slug']} ({len(HUB['protocols'])} protocols)")

    c_existing = await db.peptide_library.find_one({"slug": CARD["slug"]}, {"_id": 1})
    await db.peptide_library.replace_one({"slug": CARD["slug"]}, CARD, upsert=True)
    print(f"card {'updated' if c_existing else 'created'}: {CARD['slug']} (has_product=True)")

    print("total hubs:", await db.stack_hubs.count_documents({}))
    print("peptides with has_product:", await db.peptide_library.count_documents({"has_product": True}))


asyncio.run(main())
