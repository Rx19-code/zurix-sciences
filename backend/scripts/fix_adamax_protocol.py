"""
Enrich Adamax protocol with preclinical literature and structural data.

Adamax is a synthetic modified analog of Semax — a nonapeptide derived from the
ACTH(4-7) fragment (MEHFPGPAG) with:
- N-terminal acetylation + adamantane conjugation (BBB penetration, stability)
- C-terminal amidation (protease resistance)
- Proposed mechanism: BDNF upregulation, TrkB receptor agonism, MC4R binding,
  modulation of dopaminergic / serotonergic / cholinergic pathways.

Evidence base: PRECLINICAL — no peer-reviewed human clinical trials exist.
Dosing follows the Semax-family research consensus adjusted for adamantane
half-life extension.

References (open-access reviews and vendor research documentation):
- Semaxpolska structural documentation (adamantane-Semax analog).
- Exploring-Peptides.com peptide encyclopedia entry.
- Preclinical Semax literature (Ashmarin, Kaplan et al. — original ACTH(4-10)
  fragment neurotrophic research).

Run:
  cd /var/www/zurix/backend && python3 scripts/fix_adamax_protocol.py
"""
import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient


SLUG = "adamax"

PAYLOAD = {
    "presentations": ["10mg"],
    "also_known_as": ["Adamantyl-Semax", "N-Acetyl-Adamantyl-MEHFPGPAG-NH₂"],
    "overview": {
        "function": "Nootropic and neurotrophic — BDNF / TrkB signaling, cognitive resilience",
        "mechanism_of_action": (
            "Adamax is a synthetic modified analog of Semax — a nonapeptide derived from "
            "the ACTH(4-7) neurotropic fragment (sequence MEHFPGPAG). Its N-terminus carries "
            "an acetyl group and an adamantane scaffold, while the C-terminus is amidated. "
            "These modifications sharply increase enzymatic stability and lipophilicity, "
            "allowing efficient blood-brain-barrier penetration. Preclinical data indicate "
            "up-regulation of Brain-Derived Neurotrophic Factor (BDNF), direct or indirect "
            "TrkB receptor agonism, binding to melanocortin-4 receptors (MC4R), and "
            "modulation of dopaminergic, serotonergic, cholinergic, glutamatergic and "
            "GABAergic pathways — collectively supporting synaptic plasticity, memory "
            "consolidation and stress-resilience mechanisms."
        ),
        "considerations": (
            "Evidence base is exclusively preclinical (rodent + in-vitro) and vendor "
            "research documentation. No peer-reviewed human clinical trials exist. "
            "Effects are subtle and cumulative — expect subjective changes over 1–3 weeks "
            "rather than immediately. Because of the adamantane-mediated half-life "
            "extension, once-daily dosing is sufficient. Avoid stacking with high-dose "
            "psychostimulants during the first cycle to allow baseline assessment."
        ),
    },
    "benefits": [
        "Up-regulation of BDNF and NGF neurotrophins (preclinical)",
        "TrkB receptor signaling activation → enhanced synaptic plasticity",
        "Improved memory consolidation and learning in rodent models",
        "Neuroprotection against oxidative and ischemic stress (preclinical)",
        "Reported subjective improvement in focus, motivation and mental stamina",
        "Modulation of stress-axis (HPA) with anxiolytic potential",
        "Higher enzymatic stability than Semax due to adamantane / amidation",
        "Efficient blood-brain-barrier penetration via lipophilic scaffold",
    ],
    "side_effects": {
        "common": [
            "Mild injection-site tenderness (subcutaneous route)",
            "Transient headache during the first days of dosing",
        ],
        "less_common": [
            "Mild insomnia if injected in the evening",
            "Increased dream vividness",
            "Brief jaw tension or bruxism (dopaminergic modulation)",
        ],
        "rare": [
            "Anxiety or over-stimulation at supra-physiological doses",
            "Hypersensitivity reaction (skin rash) — very rare",
        ],
    },
    "timing_goals": [
        {
            "goal": "Nootropic / cognitive support (standard research course)",
            "timing": "500 mcg subcutaneously once daily, morning, for 10–20 days",
        },
        {
            "goal": "Neuroprotection / recovery research",
            "timing": "500–750 mcg SC once daily for 20–30 days",
        },
        {
            "goal": "Stress resilience / HPA-axis support",
            "timing": "300–500 mcg SC once daily in the morning for 14 days",
        },
        {
            "goal": "Maintenance / low-dose research",
            "timing": "250 mcg SC every other day for 4 weeks",
        },
    ],
    "administration": {
        "route": "Subcutaneous (preferred). Intranasal 300–500 mcg is also documented in Semax-family protocols but has less predictable absorption.",
        "notes": (
            "Best injected in the morning (before 12:00) to align with the natural "
            "cortisol/dopamine rhythm and minimize sleep disturbance. Rotate sites "
            "(abdomen, thigh, deltoid). Use a U-100 insulin syringe for microdosing. "
            "Allow the reconstituted vial to reach room temperature before injection. "
            "Discard 14 days after reconstitution."
        ),
    },
    "legal_status": {
        "us": "Not FDA approved. Available for research use only in the United States.",
        "uk": "Not licensed by the MHRA. Research-use only.",
        "canada": "Not Health Canada approved. Research-use only.",
        "global": "Not approved as a medicinal product in any jurisdiction. Sold strictly as a research chemical.",
    },
    "protocols": {
        "title": "Subcutaneous Nootropic / Neurotrophic Protocol",
        "standard": {
            "route": "Subcutaneous",
            "frequency": "500 mcg once daily, morning, 10–20 days per cycle",
        },
        "dosages": [
            {
                "indication": "Standard nootropic / cognitive support cycle",
                "schedule": "Subcutaneous, once daily in the morning, for 10–20 consecutive days; cycle 2–3× per year",
                "dose": "500 mcg (0.5 mg) per injection",
            },
            {
                "indication": "Neuroprotection / extended recovery research",
                "schedule": "Subcutaneous, once daily, for 20–30 consecutive days; cycle 2× per year",
                "dose": "500–750 mcg per injection",
            },
            {
                "indication": "Stress resilience / HPA-axis support",
                "schedule": "Subcutaneous, once daily in the morning, for 14 days",
                "dose": "300–500 mcg per injection",
            },
            {
                "indication": "Maintenance / low-dose research",
                "schedule": "Subcutaneous, every other day, for 4 weeks",
                "dose": "250 mcg per injection",
            },
        ],
        "phases": [
            {
                "number": 1,
                "phase": "Ramp-up (Days 1-3)",
                "dose": "250 mcg SC daily — allows baseline tolerance assessment",
            },
            {
                "number": 2,
                "phase": "Active phase (Days 4-17)",
                "dose": "500 mcg SC daily — main nootropic / neurotrophic window",
            },
            {
                "number": 3,
                "phase": "Taper (Days 18-20)",
                "dose": "250 mcg SC daily — smooth transition off cycle",
            },
            {
                "number": 4,
                "phase": "Wash-out (Weeks 4-12)",
                "dose": "No injection — allow endogenous BDNF/TrkB regulation to stabilize before next cycle",
            },
        ],
        "reconstitution": (
            "Reconstitute the 10 mg vial with 2 mL of bacteriostatic water → final "
            "concentration 5 mg/mL (5000 mcg/mL). A 500 mcg dose = 0.1 mL = 10 IU on "
            "a U-100 insulin syringe. A 250 mcg dose = 5 IU. A 750 mcg dose = 15 IU. "
            "Store reconstituted solution at 2–8 °C and use within 14 days."
        ),
        "reconstitution_steps": [
            "Step 1: Bring the lyophilized Adamax 10 mg vial and bacteriostatic water vial to room temperature.",
            "Step 2: Wipe both rubber stoppers with a fresh alcohol swab.",
            "Step 3: Draw 2 mL of bacteriostatic water into a sterile 3 mL syringe.",
            "Step 4: Slowly inject the water down the inner wall of the Adamax vial — do NOT squirt directly onto the powder.",
            "Step 5: Gently swirl (do NOT shake) until the powder is fully dissolved — the solution should be clear and colorless.",
            "Step 6: Label the vial with the reconstitution date and store at 2–8 °C. Discard 14 days after reconstitution.",
            "Step 7: For a 500 mcg dose, withdraw 10 IU (= 0.1 mL) on a U-100 insulin syringe, expel air bubbles, and inject subcutaneously after rotating injection sites.",
        ],
    },
    "research": {
        "mechanism": (
            "Adamax is engineered on the ACTH(4-7) neuropeptide backbone that underlies "
            "Semax and related Russian nootropics. The adamantyl group anchors the peptide "
            "to lipid environments, dramatically increasing membrane partition and cerebral "
            "bioavailability while shielding the peptide from proteolysis. Once in the CNS "
            "compartment, preclinical evidence points to (1) transcriptional up-regulation "
            "of BDNF and NGF in the hippocampus, (2) direct or indirect activation of TrkB "
            "receptors on pyramidal neurons, (3) binding to melanocortin-4 receptors (MC4R) "
            "involved in stress and satiety circuits, and (4) modulation of monoaminergic "
            "and glutamatergic neurotransmission. These converge on enhanced synaptic "
            "plasticity, LTP facilitation and neuroprotection in ischemia / oxidative-"
            "stress models."
        ),
        "steps": [
            "Adamantane-mediated blood-brain-barrier penetration",
            "N-acetyl / C-amide modifications resist enzymatic cleavage",
            "Up-regulation of BDNF and NGF transcription in hippocampus",
            "TrkB receptor activation → CREB and mTOR downstream signaling",
            "MC4R binding — modulates stress and reward circuits",
            "Modulation of dopamine, serotonin, acetylcholine, glutamate, GABA pathways",
        ],
        "references": [
            "Semax structural literature — Ashmarin IP et al. (original ACTH(4-10) fragment research).",
            "Kaplan AY et al. Semax neurotropic effects (preclinical/clinical stroke recovery).",
            "Vendor-research documentation (Semaxpolska structural analog series).",
            "Exploring-Peptides.com peptide encyclopedia — Adamax entry.",
            "No peer-reviewed human clinical trials of Adamax itself as of 2026.",
        ],
    },
    "synergy": {
        "interactions": [
            "Well-tolerated with most other bioregulator peptides",
            "May potentiate other BDNF/nootropic peptides (Selank, Semax, Cerebrolysin)",
            "Avoid combining with high-dose psychostimulants during the first cycle",
        ],
        "stacks": [
            "Adamax + Selank — nootropic + anxiolytic research stack",
            "Adamax + Semax — legacy Russian nootropic combination",
            "Adamax + Cerebrolysin — extended neurotrophic research stack",
        ],
    },
    "has_product": True,
}


async def main():
    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    existing = await db.peptide_library.find_one({"slug": SLUG}, {"_id": 0, "slug": 1, "name": 1})
    if not existing:
        print(f"ERROR: peptide_library entry with slug='{SLUG}' not found.")
        client.close()
        sys.exit(1)

    update_doc = {
        "presentations": PAYLOAD["presentations"],
        "also_known_as": PAYLOAD["also_known_as"],
        "overview": PAYLOAD["overview"],
        "benefits": PAYLOAD["benefits"],
        "side_effects": PAYLOAD["side_effects"],
        "timing_goals": PAYLOAD["timing_goals"],
        "administration": PAYLOAD["administration"],
        "legal_status": PAYLOAD["legal_status"],
        "protocols": PAYLOAD["protocols"],
        "research": PAYLOAD["research"],
        "synergy": PAYLOAD["synergy"],
        "has_product": PAYLOAD["has_product"],
    }

    result = await db.peptide_library.update_one({"slug": SLUG}, {"$set": update_doc})

    print("=" * 60)
    print("Adamax protocol enriched")
    print("=" * 60)
    print(f"Matched: {result.matched_count} | Modified: {result.modified_count}")
    print(f"  • Function: {PAYLOAD['overview']['function']}")
    print(f"  • {len(PAYLOAD['benefits'])} benefits")
    print(f"  • {sum(len(v) for v in PAYLOAD['side_effects'].values())} side effects")
    print(f"  • {len(PAYLOAD['timing_goals'])} timing goals")
    print(f"  • {len(PAYLOAD['protocols']['dosages'])} dosage indications")
    print(f"  • {len(PAYLOAD['protocols']['phases'])} phases")
    print(f"  • {len(PAYLOAD['protocols']['reconstitution_steps'])} reconstitution steps")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
