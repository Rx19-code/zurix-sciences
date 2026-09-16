"""Seed the peptide_library entry (Peptides tab card) for GHK-Cu + AHK-Cu Hair Growth Spray.
Idempotent upsert by slug. has_product=True so it appears in the Peptides list.
"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DOC = {
    "slug": "ghkcu-ahkcu-hair-growth-spray",
    "name": "GHK-Cu + AHK-Cu Hair Growth Spray",
    "description": "Topical copper peptide spray combining GHK-Cu and AHK-Cu for hair follicle stimulation and scalp health",
    "category": "Aesthetics / Skin",
    "is_free": False,
    "presentations": ["55mg spray"],
    "also_known_as": ["Copper Peptide Hair Spray", "GHK/AHK Hair Spray"],
    "has_product": True,
    "overview": {
        "function": "Hair follicle stimulation, scalp angiogenesis, collagen support and improved hair density.",
        "mechanism_of_action": (
            "A leave-on topical spray combining two copper-binding peptides. GHK-Cu drives collagen/elastin "
            "synthesis and tissue remodeling, while AHK-Cu stimulates dermal papilla cells and upregulates VEGF "
            "to support follicle vascularization. Together they promote a healthier scalp environment and improved "
            "hair density without injections."
        ),
        "considerations": (
            "For topical/cosmetic research use. Mild scalp irritation, redness or itching can occur — patch test "
            "before full use. Results are gradual; hair cycles require 12-16+ weeks of consistent application."
        ),
    },
    "administration": {
        "route": "Topical (leave-on spray)",
        "notes": (
            "Apply to a clean, dry scalp, parting hair to reach the skin. Massage in gently and leave on (do not "
            "rinse for several hours). Best used morning and/or before bed. Store at 2-8\u00b0C, protect from light."
        ),
    },
    "protocols": {
        "title": "Topical Application Protocol (55 mg spray bottle)",
        "standard": {"route": "Topical", "frequency": "1-2x daily"},
        "dosages": [
            {"indication": "Standard hair-density routine", "schedule": "Once or twice daily", "dose": "5-8 sprays to thinning areas"},
            {"indication": "Intensive phase (with microneedling)", "schedule": "Twice daily", "dose": "5-8 sprays; post-needling on separate days"},
            {"indication": "Maintenance", "schedule": "Once daily", "dose": "5 sprays to maintenance areas"},
        ],
        "phases": [
            {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "5 sprays once daily"},
            {"number": 2, "phase": "Standard (Weeks 3-8)", "dose": "5-8 sprays 1-2x daily"},
            {"number": 3, "phase": "Intensive (Weeks 9-12)", "dose": "5-8 sprays 2x daily + weekly microneedling"},
            {"number": 4, "phase": "Maintenance (Weeks 13+)", "dose": "5 sprays once daily"},
        ],
        "reconstitution_steps": [
            "Ready-to-use topical spray \u2014 no reconstitution required.",
            "Shake gently before first use.",
            "Store refrigerated at 2-8\u00b0C between uses; protect from light.",
            "Patch test on a small scalp area before full application.",
        ],
        "reconstitution": "Ready-to-use leave-on spray. No mixing required. Keep refrigerated and protected from light.",
    },
    "research": {
        "mechanism": "Dual copper-peptide topical delivery for follicle stimulation and scalp remodeling.",
        "steps": [
            "GHK-Cu activates collagen and elastin synthesis pathways in the dermis",
            "AHK-Cu stimulates dermal papilla cells that drive the hair growth cycle",
            "VEGF upregulation supports angiogenesis and follicle nourishment",
            "Combined copper delivery improves scalp environment and hair density",
        ],
        "references": [],
    },
    "synergy": {
        "interactions": [
            {"peptide": "AHK-Cu", "status": "SYNERGISTIC", "description": "Injectable AHK-Cu amplifies follicle stimulation"},
            {"peptide": "PTD-DBM", "status": "SYNERGISTIC", "description": "Wnt/\u03b2-catenin activation complements copper peptides"},
            {"peptide": "GHK-Cu", "status": "COMPATIBLE", "description": "Additional collagen and skin-quality support"},
        ],
        "stacks": [],
    },
    "benefits": [
        "Non-injectable, convenient daily scalp application",
        "Stimulates hair follicles and dermal papilla cells",
        "Promotes VEGF expression and scalp angiogenesis",
        "Supports collagen/elastin for scalp skin health",
        "Combines two synergistic copper peptides (GHK-Cu + AHK-Cu)",
    ],
    "legal_status": {
        "us": "Research and cosmetic compound \u2014 not FDA-approved for therapeutic use.",
        "uk": "Research chemical; allowed in cosmetic formulations.",
        "canada": "Permitted in cosmetic products; research-only for therapeutic use.",
    },
    "side_effects": {
        "common": ["Mild scalp irritation or redness", "Temporary itchiness at application site"],
        "less_common": ["Dryness or flaking", "Blue-tinted residue (copper) \u2014 normal"],
        "rare": ["Allergic reaction", "Copper sensitivity (extremely rare)"],
    },
    "timing_goals": [
        {"goal": "Hair growth / anti-hair-loss", "timing": "1-2x daily topically for 12-16 weeks"},
        {"goal": "Intensive regrowth", "timing": "2x daily + weekly microneedling"},
        {"goal": "Maintenance", "timing": "1x daily continuously"},
    ],
}


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    existing = await db.peptide_library.find_one({"slug": DOC["slug"]}, {"_id": 1})
    await db.peptide_library.replace_one({"slug": DOC["slug"]}, DOC, upsert=True)
    print(f"{'updated' if existing else 'created'}: {DOC['slug']}")
    total = await db.peptide_library.count_documents({"has_product": True})
    print("peptides with has_product:", total)


asyncio.run(main())
