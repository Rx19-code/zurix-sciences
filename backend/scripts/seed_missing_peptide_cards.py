"""Seed peptide_library cards (Peptides tab) for ACE-031, PTD-DBM, GHK Basic.
Idempotent upsert by slug. has_product=True so each appears in the Peptides list.
"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DOCS = [
    {
        "slug": "ace-031",
        "name": "ACE-031",
        "description": "Soluble activin receptor (ActRIIB-Fc) that neutralizes myostatin for muscle growth research",
        "category": "Recovery",
        "is_free": False,
        "presentations": ["1mg"],
        "also_known_as": ["ActRIIB-Fc", "Ramatercept"],
        "has_product": True,
        "overview": {
            "function": "Muscle mass and strength support via myostatin/activin inhibition.",
            "mechanism_of_action": (
                "ACE-031 is a soluble form of the activin receptor type IIB (ActRIIB) fused to an antibody Fc region. "
                "It acts as a decoy receptor, binding and neutralizing myostatin and related ligands (activins, GDF-11) "
                "before they can signal muscle-growth inhibition. Removing this brake allows increased muscle mass and "
                "strength independent of direct androgen or GH pathways."
            ),
            "considerations": (
                "Long-acting — infrequent dosing. Trials noted off-target effects from activin inhibition (e.g. "
                "nosebleeds, gum bleeding, dilated vessels) at higher doses. Use conservative research doses; monitor "
                "for peripheral effects."
            ),
        },
        "administration": {
            "route": "Subcutaneous",
            "notes": "SC injection on a fixed schedule (long half-life — dosed roughly every 2-4 weeks). Reconstitute with bacteriostatic water; store refrigerated at 2-8°C.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 1 mg)",
            "standard": {"route": "Subcutaneous", "frequency": "Every 2-4 weeks"},
            "dosages": [
                {"indication": "Conservative research dose", "schedule": "Every 3-4 weeks, SC", "dose": "per label, low mg-range"},
                {"indication": "Standard research dose", "schedule": "Every 2-3 weeks, SC", "dose": "per label"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-4)", "dose": "Single low-range SC dose"},
                {"number": 2, "phase": "Build (Weeks 5-8)", "dose": "Repeat dose per schedule with progressive training"},
                {"number": 3, "phase": "Peak (Weeks 9-12)", "dose": "Maintain schedule; monitor for peripheral effects"},
            ],
            "reconstitution_steps": [
                "Reconstitute the 1 mg vial with bacteriostatic water per label concentration.",
                "Gently swirl until dissolved (do not shake).",
                "Draw the labeled research dose into an insulin syringe.",
                "Store reconstituted solution refrigerated at 2-8°C; use within 28 days.",
            ],
            "reconstitution": "Reconstitute the 1 mg vial with bacteriostatic water per label. Long-acting compound — infrequent dosing. Store at 2-8°C.",
        },
        "research": {
            "mechanism": "Decoy activin receptor that sequesters myostatin and related muscle-inhibitory ligands.",
            "steps": [
                "Binds myostatin, activins and GDF-11 as a soluble decoy receptor",
                "Prevents ActRIIB signaling that normally limits muscle growth",
                "Increases muscle fiber size and strength in research models",
                "Effects are independent of androgen or GH pathways",
            ],
            "references": [],
        },
        "synergy": {
            "interactions": [
                {"peptide": "HGH", "status": "SYNERGISTIC", "description": "GH-axis support complements myostatin inhibition"},
                {"peptide": "IGF-1 LR3", "status": "SYNERGISTIC", "description": "Local anabolic support for lean mass"},
                {"peptide": "CJC-1295 + Ipamorelin", "status": "COMPATIBLE", "description": "Endogenous GH pulse support"},
            ],
            "stacks": [],
        },
        "benefits": [
            "Increases muscle mass by neutralizing myostatin",
            "Supports strength and lean-tissue gains",
            "Long-acting — infrequent dosing",
            "Works independently of androgen/GH pathways",
        ],
        "legal_status": {
            "us": "Research compound — not FDA-approved for therapeutic use.",
            "uk": "Research chemical — laboratory use only.",
            "canada": "Research-only; not approved for therapeutic use.",
        },
        "side_effects": {
            "common": ["Mild injection site reactions"],
            "less_common": ["Nosebleeds or gum bleeding", "Dilated small blood vessels"],
            "rare": ["Allergic reactions"],
        },
        "timing_goals": [
            {"goal": "Muscle mass / hypertrophy", "timing": "Dosed every 2-4 weeks with progressive resistance training"},
            {"goal": "Strength support", "timing": "Maintain schedule over an 8-12 week block"},
        ],
    },
    {
        "slug": "ptd-dbm",
        "name": "PTD-DBM",
        "description": "Wnt/β-catenin pathway peptide for hair follicle regeneration research",
        "category": "Aesthetics / Skin",
        "is_free": False,
        "presentations": ["5mg"],
        "also_known_as": ["PTD-DBM peptide", "CXXC5 inhibitor peptide"],
        "has_product": True,
        "overview": {
            "function": "Hair follicle regeneration via Wnt/β-catenin pathway activation.",
            "mechanism_of_action": (
                "PTD-DBM is a cell-penetrating peptide that inhibits CXXC5, a negative regulator of the Wnt/β-catenin "
                "signaling pathway. By blocking the CXXC5–Dishevelled interaction, it reactivates Wnt signaling in hair "
                "follicle stem cells, promoting follicle neogenesis and regrowth. It is typically applied topically, "
                "often combined with microneedling or valproic acid in research."
            ),
            "considerations": (
                "Topical/research use. Hair cycles are slow — expect 12-16+ weeks before assessing. Mild scalp "
                "irritation possible. Patch test before full use."
            ),
        },
        "administration": {
            "route": "Topical (scalp)",
            "notes": "Apply to clean, dry scalp, often paired with weekly microneedling to enhance uptake. Avoid applying immediately after needling. Store reconstituted solution refrigerated at 2-8°C.",
        },
        "protocols": {
            "title": "Topical Protocol (vial 5 mg)",
            "standard": {"route": "Topical", "frequency": "Daily"},
            "dosages": [
                {"indication": "Standard hair regeneration", "schedule": "Once daily, topical", "dose": "Apply to affected scalp areas"},
                {"indication": "With microneedling", "schedule": "On non-needling days", "dose": "Apply topically; needle weekly"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-4)", "dose": "Daily topical application"},
                {"number": 2, "phase": "Build (Weeks 5-12)", "dose": "Daily topical + weekly microneedling"},
                {"number": 3, "phase": "Assess & Maintain (Weeks 13-16+)", "dose": "Continue daily; evaluate density"},
            ],
            "reconstitution_steps": [
                "Reconstitute the 5 mg vial with bacteriostatic water per label into a topical solution.",
                "Apply to clean, dry scalp; massage in gently.",
                "Leave on overnight; avoid rinsing for several hours.",
                "Store refrigerated at 2-8°C; use within 28 days.",
            ],
            "reconstitution": "Reconstitute the 5 mg vial with bacteriostatic water per label. Apply topically to the scalp. Store at 2-8°C.",
        },
        "research": {
            "mechanism": "CXXC5 inhibition reactivates Wnt/β-catenin signaling in follicle stem cells.",
            "steps": [
                "Blocks the CXXC5–Dishevelled interaction",
                "Restores Wnt/β-catenin signaling in hair follicles",
                "Promotes follicle neogenesis and anagen re-entry",
                "Synergizes with microneedling for delivery",
            ],
            "references": [],
        },
        "synergy": {
            "interactions": [
                {"peptide": "AHK-Cu", "status": "SYNERGISTIC", "description": "Copper peptide follicle stimulation complements Wnt activation"},
                {"peptide": "GHK-Cu + AHK-Cu Hair Growth Spray", "status": "SYNERGISTIC", "description": "Topical copper peptides pair well with Wnt activation"},
                {"peptide": "GHK-Cu", "status": "COMPATIBLE", "description": "Additional scalp skin support"},
            ],
            "stacks": [],
        },
        "benefits": [
            "Reactivates dormant hair follicles via Wnt signaling",
            "Targets CXXC5, a key hair-loss regulator",
            "Non-injectable topical application",
            "Synergizes with microneedling and copper peptides",
        ],
        "legal_status": {
            "us": "Research and cosmetic compound — not FDA-approved for therapeutic use.",
            "uk": "Research chemical; allowed in cosmetic formulations.",
            "canada": "Permitted in cosmetic products; research-only for therapeutic use.",
        },
        "side_effects": {
            "common": ["Mild scalp irritation or redness"],
            "less_common": ["Dryness or itchiness at application site"],
            "rare": ["Allergic reaction"],
        },
        "timing_goals": [
            {"goal": "Hair regeneration", "timing": "Daily topical for 12-16 weeks"},
            {"goal": "Enhanced uptake", "timing": "Pair with weekly microneedling"},
            {"goal": "Maintenance", "timing": "Continue daily application"},
        ],
    },
    {
        "slug": "ghk-basic",
        "name": "GHK Basic",
        "description": "Copper-free GHK tripeptide for collagen synthesis and skin regeneration research",
        "category": "Aesthetics / Skin",
        "is_free": False,
        "presentations": ["50mg"],
        "also_known_as": ["GHK", "Glycyl-Histidyl-Lysine"],
        "has_product": True,
        "overview": {
            "function": "Collagen synthesis, tissue remodeling and skin regeneration.",
            "mechanism_of_action": (
                "GHK Basic is the copper-free glycyl-histidyl-lysine tripeptide. It stimulates collagen, elastin and "
                "glycosaminoglycan synthesis, supports tissue remodeling and has been shown to reset gene expression "
                "toward a younger profile. A gentler entry point than copper-bound GHK-Cu, without the blue copper tint."
            ),
            "considerations": (
                "Research use. Generally well tolerated. Mild injection-site reactions possible. Start low and titrate; "
                "use SPF during skin protocols as turnover increases."
            ),
        },
        "administration": {
            "route": "Subcutaneous",
            "notes": "SC injection into or near the area of interest, typically in the evening. Reconstitute with bacteriostatic water; store refrigerated at 2-8°C.",
        },
        "protocols": {
            "title": "Subcutaneous Protocol (vial 50 mg, 2 mL bac water = 25 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "Daily (evening)"},
            "dosages": [
                {"indication": "Standard skin remodeling", "schedule": "Once daily, SC (evening)", "dose": "1 mg/day (≈0.04 mL / 4 units)"},
                {"indication": "Advanced rejuvenation", "schedule": "Once daily, SC", "dose": "1-2 mg/day"},
            ],
            "phases": [
                {"number": 1, "phase": "Initiation (Weeks 1-2)", "dose": "1 mg/day SC"},
                {"number": 2, "phase": "Standard (Weeks 3-6)", "dose": "1-2 mg/day SC"},
                {"number": 3, "phase": "Off (Weeks 7-10)", "dose": "4-week break, then repeat cycle"},
            ],
            "reconstitution_steps": [
                "Reconstitute the 50 mg vial with 2 mL bacteriostatic water (25 mg/mL).",
                "For 1 mg: draw 0.04 mL (4 units on a 100-unit insulin syringe).",
                "Gently swirl until dissolved (do not shake).",
                "Store refrigerated at 2-8°C; use within 28 days.",
            ],
            "reconstitution": "Reconstitute the 50 mg vial with 2 mL bacteriostatic water (25 mg/mL). 1 mg ≈ 0.04 mL (4 units). Store at 2-8°C.",
        },
        "research": {
            "mechanism": "Copper-free GHK tripeptide driving collagen synthesis and tissue remodeling.",
            "steps": [
                "Stimulates collagen, elastin and glycosaminoglycan synthesis",
                "Supports dermal remodeling and wound healing",
                "Resets gene expression toward a younger profile",
                "Provides antioxidant and anti-inflammatory support",
            ],
            "references": [],
        },
        "synergy": {
            "interactions": [
                {"peptide": "GHK-Cu", "status": "SYNERGISTIC", "description": "Alternate with copper-bound GHK for stronger remodeling"},
                {"peptide": "Glutathione", "status": "COMPATIBLE", "description": "Brightening and antioxidant support"},
                {"peptide": "Epithalon", "status": "COMPATIBLE", "description": "Longevity block synergy"},
            ],
            "stacks": [],
        },
        "benefits": [
            "Stimulates collagen and elastin synthesis",
            "Gentler, copper-free alternative to GHK-Cu",
            "Supports skin firmness, tone and texture",
            "No blue copper tint in solution",
        ],
        "legal_status": {
            "us": "Research and cosmetic compound — not FDA-approved for therapeutic use.",
            "uk": "Research chemical; allowed in cosmetic formulations.",
            "canada": "Permitted in cosmetic products; research-only for therapeutic use.",
        },
        "side_effects": {
            "common": ["Mild injection site reactions"],
            "less_common": ["Transient redness or itching"],
            "rare": ["Allergic reactions"],
        },
        "timing_goals": [
            {"goal": "Skin regeneration / anti-aging", "timing": "1 mg daily SC for 6 weeks, then 4 weeks off"},
            {"goal": "Advanced rejuvenation", "timing": "Alternate with GHK-Cu for stronger remodeling"},
            {"goal": "Maintenance", "timing": "1 mg every other day"},
        ],
    },
]


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    for doc in DOCS:
        existing = await db.peptide_library.find_one({"slug": doc["slug"]}, {"_id": 1})
        await db.peptide_library.replace_one({"slug": doc["slug"]}, doc, upsert=True)
        print(f"{'updated' if existing else 'created'}: {doc['slug']}")
    total = await db.peptide_library.count_documents({"has_product": True})
    print("peptides with has_product:", total)


asyncio.run(main())
