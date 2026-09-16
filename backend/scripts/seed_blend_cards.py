"""Activate the two existing blend cards and create the Semax + Selank blend card.
Idempotent. FOXO4 intentionally NOT touched (per user).
"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

ACTIVATE_SLUGS = ["tesamorelin-ipamorelin-blend", "cjc-1295-ipamorelin-blend"]

SEMAX_SELANK = {
    "slug": "semax-selank-blend",
    "name": "Semax + Selank Blend",
    "description": "Nootropic blend pairing Semax (focus, BDNF) with Selank (calm, anxiolytic) for balanced cognitive research",
    "category": "Nootropic / Cognitive",
    "is_free": False,
    "presentations": ["10mg+10mg"],
    "also_known_as": ["Semax/Selank Stack", "Focus & Calm Blend"],
    "has_product": True,
    "overview": {
        "function": "Balanced cognitive support — focus and drive (Semax) with calm and anxiety reduction (Selank).",
        "mechanism_of_action": (
            "This blend combines two Russian-developed regulatory peptides. Semax (an ACTH 4-10 analogue) increases "
            "BDNF and modulates dopaminergic/serotonergic systems to enhance focus, memory and neuroprotection. Selank "
            "(a tuftsin analogue) modulates GABAergic tone and enkephalin degradation for anxiolytic, calming effects "
            "without sedation. Together they deliver stimulation-with-calm — sharp focus without the jittery edge."
        ),
        "considerations": (
            "Research use, intranasal. Generally well tolerated. Mild nasal irritation possible. Semax can be "
            "stimulating (use earlier in the day); Selank balances this. Start at lower doses and titrate."
        ),
    },
    "administration": {
        "route": "Intranasal",
        "notes": "Intranasal administration; alternate nostrils. Semax component is stimulating — favor morning/midday. Store reconstituted solution refrigerated at 2-8°C, protected from light.",
    },
    "protocols": {
        "title": "Intranasal Protocol (vial 10mg+10mg)",
        "standard": {"route": "Intranasal", "frequency": "1-2x daily"},
        "dosages": [
            {"indication": "Focus + calm (standard)", "schedule": "Once daily, AM", "dose": "~300 mcg each intranasal"},
            {"indication": "High-demand cognitive days", "schedule": "AM + early afternoon", "dose": "~300 mcg each, 2x daily"},
        ],
        "phases": [
            {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "~300 mcg each, once daily AM"},
            {"number": 2, "phase": "Standard (Weeks 3-6)", "dose": "~300 mcg each, 1-2x daily"},
            {"number": 3, "phase": "Break (Weeks 7-8)", "dose": "2-week off period, then repeat"},
        ],
        "reconstitution_steps": [
            "Reconstitute the vial with bacteriostatic water per label into an intranasal solution.",
            "Transfer to a nasal spray/dropper if applicable.",
            "Administer intranasally, alternating nostrils; favor morning/midday.",
            "Store refrigerated at 2-8°C, protected from light; use within 28 days.",
        ],
        "reconstitution": "Reconstitute per label into an intranasal solution. Semax is stimulating — dose earlier in the day. Store at 2-8°C.",
    },
    "research": {
        "mechanism": "Semax raises BDNF and modulates monoamines; Selank modulates GABA/enkephalin systems for calm.",
        "steps": [
            "Semax increases BDNF and neurotrophic signaling for focus and neuroprotection",
            "Selank modulates GABAergic tone for anxiolytic, calming effects",
            "Combined: enhanced focus and memory without stimulant-type anxiety",
            "Both cross mucosa efficiently via intranasal delivery",
        ],
        "references": [],
    },
    "synergy": {
        "interactions": [
            {"peptide": "Semax", "status": "SYNERGISTIC", "description": "Focus/BDNF component of the blend"},
            {"peptide": "Selank", "status": "SYNERGISTIC", "description": "Calm/anxiolytic component of the blend"},
            {"peptide": "NAD+", "status": "COMPATIBLE", "description": "Cellular energy support for cognition"},
        ],
        "stacks": [],
    },
    "benefits": [
        "Sharp focus and drive without the jittery edge",
        "Anxiolytic, calming support from Selank",
        "BDNF and neuroprotective support from Semax",
        "Convenient intranasal, non-injectable delivery",
    ],
    "legal_status": {
        "us": "Research compound — not FDA-approved for therapeutic use.",
        "uk": "Research chemical — laboratory use only.",
        "canada": "Research-only; not approved for therapeutic use.",
    },
    "side_effects": {
        "common": ["Mild nasal irritation"],
        "less_common": ["Transient headache", "Overstimulation if dosed late in the day"],
        "rare": ["Allergic reaction"],
    },
    "timing_goals": [
        {"goal": "Focus + calm", "timing": "~300 mcg each intranasal, morning"},
        {"goal": "High cognitive demand", "timing": "AM + early afternoon dosing"},
        {"goal": "Anxiety balance", "timing": "Selank-weighted timing later in the day if needed"},
    ],
}


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    for slug in ACTIVATE_SLUGS:
        res = await db.peptide_library.update_one({"slug": slug}, {"$set": {"has_product": True}})
        print(f"activated {slug}: matched={res.matched_count}, modified={res.modified_count}")
    existing = await db.peptide_library.find_one({"slug": SEMAX_SELANK["slug"]}, {"_id": 1})
    await db.peptide_library.replace_one({"slug": SEMAX_SELANK["slug"]}, SEMAX_SELANK, upsert=True)
    print(f"{'updated' if existing else 'created'}: {SEMAX_SELANK['slug']}")
    total = await db.peptide_library.count_documents({"has_product": True})
    print("peptides with has_product:", total)


asyncio.run(main())
