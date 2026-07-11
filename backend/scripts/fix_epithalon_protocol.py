"""
Enrich Epithalon (Epitalon, Tetrapeptide AEDG) protocol with clinical literature.

References:
- Khavinson VK. Peptides and Ageing. Neuroendocrinol Lett. 2002; Suppl 3:11-144.
- Khavinson VK et al. Epithalamin and epithalon peptide induce telomerase activity
  in human somatic cells. Bull Exp Biol Med. 2003;135(6):590-2.
- Anisimov VN, Khavinson VK. Peptide bioregulation of aging: results and prospects.
  Biogerontology. 2010;11(2):139-49.
- Korkushko OV et al. Peptide geroprotector from the pituitary gland inhibits rapid
  aging of elderly people: results of 15-year follow-up study. Bull Exp Biol Med.
  2011;151(3):366-9.
- Khavinson VK, Bondarev IE, Butyugov AA. Epithalon peptide induces telomerase
  activity and telomere elongation in human somatic cells. Bull Exp Biol Med.
  2003;135(2):155-8.
- Anisimov VN et al. Effect of Epitalon on biomarkers of aging, lifespan and
  spontaneous tumor incidence in female Swiss-derived SHR mice. Biogerontology.
  2003;4(4):193-202.
- Discovered by V.Kh. Khavinson at the St. Petersburg Institute of Bioregulation
  and Gerontology; developed as a synthetic analog of the pineal peptide Epithalamin.

Run:
  cd /var/www/zurix/backend && python3 scripts/fix_epithalon_protocol.py
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


SLUG = "epithalon"

PAYLOAD = {
    "presentations": ["10mg"],
    "also_known_as": ["Epitalon", "Epithalamin analog", "AEDG", "Tetrapeptide-4"],
    "overview": {
        "function": "Telomerase activation, pineal-melatonin rhythm restoration, geroprotection",
        "mechanism_of_action": (
            "Epithalon is a synthetic tetrapeptide (Ala-Glu-Asp-Gly, AEDG) designed by "
            "Prof. Vladimir Khavinson at the St. Petersburg Institute of Bioregulation and "
            "Gerontology as a short analog of the pineal-derived peptide Epithalamin. It "
            "penetrates the cell nucleus, binds AT-rich regions of DNA and regulates the "
            "expression of genes involved in cell cycle and senescence — most notably the "
            "hTERT gene, restoring telomerase activity and elongating shortened telomeres "
            "in senescent human somatic cells. It also restores the amplitude of nocturnal "
            "melatonin secretion, normalizes the cortisol rhythm, and up-regulates "
            "antioxidant defenses. Long-term geroprotective effects have been documented in "
            "rodent lifespan studies and in a 15-year human follow-up trial in elderly "
            "subjects."
        ),
        "considerations": (
            "Effect is cumulative — benefits appear over 2–4 courses per year rather than "
            "immediately. Best paired with sleep hygiene and circadian discipline to "
            "leverage the pineal/melatonin action. No dose-limiting toxicity has been "
            "reported at research doses; combining with other bioregulator peptides "
            "(Cerluten, Vladonix, Ventfort) is well-documented in the Russian literature."
        ),
    },
    "benefits": [
        "Reactivates telomerase and elongates telomeres in senescent human somatic cells",
        "Restores nocturnal melatonin amplitude and circadian rhythm",
        "Improves sleep quality — deeper N3 and REM phases",
        "Normalizes cortisol rhythm and stress axis regulation",
        "Up-regulates endogenous antioxidant defenses (SOD, catalase)",
        "Documented reduction in age-related mortality in elderly (15-yr follow-up)",
        "Extended lifespan and reduced spontaneous tumor incidence in rodents",
        "Improves skin tone, elasticity and cellular hydration (long-term)",
    ],
    "side_effects": {
        "common": [
            "Transient injection-site tenderness (mild)",
        ],
        "less_common": [
            "Mild vivid dreams during first nights (melatonin normalization)",
            "Brief morning drowsiness during the first 2-3 days of a course",
        ],
        "rare": [
            "Mild headache",
            "Hypersensitivity reaction (skin rash) — very rare",
        ],
    },
    "timing_goals": [
        {
            "goal": "Longevity / geroprotection (standard Khavinson course)",
            "timing": "10 mg subcutaneously once daily for 10 consecutive days — 2 courses per year",
        },
        {
            "goal": "Sleep and melatonin rhythm restoration",
            "timing": "5–10 mg SC every evening for 10–20 days — repeat 2× per year",
        },
        {
            "goal": "Extended geroprotection course",
            "timing": "5 mg SC daily for 20 consecutive days — 2× per year",
        },
        {
            "goal": "Maintenance / anti-aging support (research)",
            "timing": "10 mg SC every other day for 10 doses — 2× per year",
        },
    ],
    "administration": {
        "route": "Subcutaneous (preferred). Intranasal 100 mcg is used in some Russian protocols but has lower bioavailability.",
        "notes": (
            "Best injected in the evening (20:00–22:00) to synchronize with the natural "
            "pineal melatonin peak. Rotate sites (abdomen, thigh, deltoid). Use a U-100 "
            "insulin syringe for microdosing. Allow reconstituted vial to reach room "
            "temperature before injection. Discard 14 days after reconstitution."
        ),
    },
    "legal_status": {
        "us": "Not FDA approved. Available for research use only in the United States.",
        "uk": "Not licensed by the MHRA. Research-use only.",
        "canada": "Not Health Canada approved. Research-use only.",
        "global": "Not approved as a medicinal product in any Western jurisdiction. Used in Russia and CIS countries under bioregulator classification.",
    },
    "protocols": {
        "title": "Subcutaneous Geroprotection Protocol (Khavinson standard)",
        "standard": {
            "route": "Subcutaneous",
            "frequency": "10 mg once daily for 10 days; repeat 2× per year",
        },
        "dosages": [
            {
                "indication": "Longevity / geroprotection (Khavinson standard course)",
                "schedule": "Subcutaneous, once daily for 10 consecutive days; repeat 2× per year",
                "dose": "10 mg (10,000 mcg) per injection — the full reconstituted vial",
            },
            {
                "indication": "Sleep quality and melatonin rhythm restoration",
                "schedule": "Subcutaneous, every evening for 10–20 days; repeat 2× per year",
                "dose": "5–10 mg (5,000–10,000 mcg) per injection",
            },
            {
                "indication": "Extended geroprotection course",
                "schedule": "Subcutaneous, once daily for 20 consecutive days; repeat 2× per year",
                "dose": "5 mg (5,000 mcg) per injection",
            },
            {
                "indication": "Maintenance / anti-aging support",
                "schedule": "Subcutaneous, every other day for 10 doses; repeat 2× per year",
                "dose": "10 mg (10,000 mcg) per injection",
            },
        ],
        "phases": [
            {
                "number": 1,
                "phase": "Active course (Days 1-10)",
                "dose": "10 mg SC daily — main telomerase-priming window",
            },
            {
                "number": 2,
                "phase": "Consolidation (Days 11-30)",
                "dose": "No injection — the biological effect persists via gene-expression changes",
            },
            {
                "number": 3,
                "phase": "Wash-out (Months 2-5)",
                "dose": "No injection — allow endogenous regulation to stabilize",
            },
            {
                "number": 4,
                "phase": "Second course (Month 6)",
                "dose": "Repeat 10-day course at 10 mg/day",
            },
        ],
        "reconstitution": (
            "Reconstitute the 10 mg vial with 2 mL of bacteriostatic water → final "
            "concentration 5 mg/mL. A 5 mg dose = 1.0 mL = 100 IU on a U-100 insulin "
            "syringe. For the standard 10 mg full-dose protocol, split into two 1.0 mL "
            "injections at different sites, or use a 3 mL syringe to inject the entire "
            "2 mL reconstituted vial. Store reconstituted solution at 2–8 °C and use "
            "within 14 days."
        ),
        "reconstitution_steps": [
            "Step 1: Bring the lyophilized Epithalon 10mg vial and bacteriostatic water vial to room temperature.",
            "Step 2: Wipe both rubber stoppers with a fresh alcohol swab.",
            "Step 3: Draw 2 mL of bacteriostatic water into a sterile 3 mL syringe.",
            "Step 4: Slowly inject the water down the inner wall of the Epithalon vial — do NOT squirt directly onto the powder.",
            "Step 5: Gently swirl (do NOT shake) until the powder is fully dissolved — the solution should be clear and colorless.",
            "Step 6: Label the vial with the reconstitution date and store at 2–8 °C. Discard 14 days after reconstitution.",
            "Step 7: For a 5 mg dose, withdraw 100 IU (=1.0 mL) on a U-100 insulin syringe. For a 10 mg dose, use a 3 mL syringe with 2.0 mL — or split into two 1.0 mL injections at different sites.",
        ],
    },
    "research": {
        "mechanism": (
            "Epithalon crosses the cell membrane, translocates to the nucleus and binds "
            "specific AT-rich promoter regions of the DNA. This modulates the transcription "
            "of genes controlling telomere maintenance (hTERT), cell-cycle regulation (CDK "
            "inhibitors) and pineal hormone synthesis. The net effect is reactivation of "
            "telomerase, elongation of critically short telomeres, and restoration of the "
            "natural pineal-melatonin nocturnal peak — the two hallmark endpoints of the "
            "Khavinson theory of peptide bioregulation."
        ),
        "steps": [
            "Nuclear translocation and binding to AT-rich DNA promoter regions",
            "Up-regulation of hTERT gene expression → increased telomerase activity",
            "Elongation of critically short telomeres in senescent somatic cells",
            "Restoration of nocturnal pineal melatonin secretion amplitude",
            "Normalization of cortisol circadian rhythm",
            "Induction of endogenous antioxidant enzymes (SOD, catalase)",
        ],
        "references": [
            "Khavinson VK et al. Bull Exp Biol Med. 2003;135(6):590-2 (telomerase reactivation).",
            "Khavinson VK, Bondarev IE, Butyugov AA. Bull Exp Biol Med. 2003;135(2):155-8 (telomere elongation).",
            "Anisimov VN, Khavinson VK. Biogerontology. 2010;11(2):139-49 (rodent lifespan).",
            "Anisimov VN et al. Biogerontology. 2003;4(4):193-202 (lifespan & tumor incidence).",
            "Korkushko OV et al. Bull Exp Biol Med. 2011;151(3):366-9 (15-year human study).",
            "Khavinson VK. Neuroendocrinol Lett. 2002;Suppl 3:11-144 (peptide bioregulation review).",
        ],
    },
    "synergy": {
        "interactions": [
            "Combines well with Thymalin/Thymosin peptides (Khavinson two-peptide theory)",
            "Synergistic with Vladonix / Ventfort in cardiovascular geroprotection protocols",
            "Melatonin supplementation can be reduced during and after an Epithalon course",
        ],
        "stacks": [
            "Epithalon + Thymalin — classic Khavinson two-peptide geroprotection stack",
            "Epithalon + BPC-157 — nightly recovery + tissue-repair research stack",
            "Epithalon + NAD+ — combined mitochondrial + telomeric anti-aging research stack",
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
    print(f"Epithalon protocol enriched")
    print("=" * 60)
    print(f"Matched: {result.matched_count} | Modified: {result.modified_count}")
    print(f"  • Function: {PAYLOAD['overview']['function']}")
    print(f"  • {len(PAYLOAD['benefits'])} benefits")
    print(f"  • {sum(len(v) for v in PAYLOAD['side_effects'].values())} side effects")
    print(f"  • {len(PAYLOAD['timing_goals'])} timing goals")
    print(f"  • {len(PAYLOAD['protocols']['dosages'])} dosage indications")
    print(f"  • {len(PAYLOAD['protocols']['phases'])} phases")
    print(f"  • {len(PAYLOAD['protocols']['reconstitution_steps'])} reconstitution steps")
    print(f"  • {len(PAYLOAD['research']['references'])} literature references")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
