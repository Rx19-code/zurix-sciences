"""
Enrich Thymosin Alpha-1 (Tα1 / Zadaxin) protocol with clinical literature data.

References:
- Romani L. et al. Thymosin alpha 1: an endogenous regulator of inflammation,
  immunity, and tolerance. Ann N Y Acad Sci. 2007.
- Andreone P. et al. A randomized controlled trial of thymosin-alpha1 versus
  interferon alpha treatment in patients with hepatitis B e antigen antibody
  and hepatitis B virus DNA positive chronic hepatitis B. Hepatology, 1996.
- Garaci E. et al. Thymosin alpha 1 in clinical use. Ann N Y Acad Sci. 2010.
- Liu Y. et al. Thymosin Alpha 1 Reduces the Mortality of Severe Coronavirus
  Disease 2019. Clin Infect Dis. 2020.
- Wu J. et al. Thymosin α1 treatment in sepsis. Crit Care. 2013.
- Approved in 35+ countries as Zadaxin (Sciclone) for chronic HBV/HCV and
  as adjuvant in hepatitis B vaccine, sepsis, and several cancers.

Run on production:
  cd /var/www/zurix/backend && python3 scripts/fix_thymosin_alpha_1_protocol.py
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


SLUG = "thymosin-alpha-1"

PAYLOAD = {
    "presentations": ["5mg"],
    "also_known_as": ["Tα1", "Ta1", "Zadaxin"],
    "overview": {
        "function": "Immunomodulation, T-cell restoration, antiviral and antitumor immunity",
        "mechanism_of_action": (
            "Thymosin Alpha-1 (Tα1) is a 28-amino-acid peptide naturally produced by the "
            "thymus gland. It acts primarily as a TLR9 (and to a lesser extent TLR2) agonist "
            "on dendritic cells and macrophages, promoting their maturation and Th1 cytokine "
            "polarization. This increases IFN-γ, IL-2 and IL-12 production, restores CD4+ and "
            "CD8+ T-cell counts and function, enhances NK cell activity, and rebalances "
            "immunosenescent or sepsis-induced immunoparalysis. It is approved in 35+ "
            "countries (sold as Zadaxin) for chronic HBV/HCV, as a hepatitis-B vaccine "
            "adjuvant in immunocompromised patients, and is in active research for sepsis, "
            "COVID-19, NSCLC, melanoma and hepatocellular carcinoma."
        ),
        "considerations": (
            "Exceptionally well tolerated across decades of clinical use — no dose-limiting "
            "toxicity reported. Effects are immune-modulatory rather than immunosuppressive, "
            "so it can be combined with most therapies. Plasma half-life is ~2 hours but "
            "biological effects persist for days. Optimal benefit is seen in immunocompromised "
            "or immunosenescent states; effect is more subtle in fully healthy subjects."
        ),
    },
    "benefits": [
        "Restores T-cell counts and function (CD4+/CD8+) in immunocompromised states",
        "Enhances NK cell activity and Th1 antiviral response (IFN-γ, IL-2)",
        "Established efficacy in chronic hepatitis B and C (Zadaxin)",
        "Improves response to hepatitis B vaccination in non-responders and dialysis patients",
        "Adjuvant in melanoma, NSCLC and hepatocellular carcinoma trials",
        "Reduces mortality in severe sepsis and severe COVID-19 (RCT data)",
        "Counters immunosenescence (age-related immune decline)",
        "Excellent safety profile across all studied populations",
    ],
    "side_effects": {
        "common": [
            "Mild, transient pain or erythema at the injection site",
            "Occasional low-grade fatigue during the first days of dosing",
        ],
        "less_common": [
            "Mild headache",
            "Transient muscle aches (myalgia)",
            "Brief flu-like sensation during the first injections",
        ],
        "rare": [
            "Hypersensitivity reaction (skin rash, pruritus)",
            "Mild transient elevation of liver enzymes (clinically irrelevant in most cases)",
        ],
    },
    "timing_goals": [
        {
            "goal": "Chronic viral hepatitis (HBV/HCV) research",
            "timing": "1.6 mg subcutaneously, 2× per week for 6 months",
        },
        {
            "goal": "Hepatitis B vaccine adjuvant / non-responders",
            "timing": "1.6 mg SC 2× per week for 4 weeks alongside vaccine doses",
        },
        {
            "goal": "Immune support in immunosenescence / chronic stress",
            "timing": "1.6 mg SC 2× per week for 4–8 weeks, then re-evaluate",
        },
        {
            "goal": "Severe acute infection (sepsis, severe respiratory infection)",
            "timing": "1.6 mg SC twice daily for 5–10 days (per ICU research protocols)",
        },
        {
            "goal": "Oncology adjuvant research (melanoma, NSCLC, HCC)",
            "timing": "1.6 mg SC 2× per week, cycled with primary therapy",
        },
    ],
    "administration": {
        "route": "Subcutaneous (preferred). IM acceptable but offers no advantage.",
        "notes": (
            "Best injected in the morning. Rotate sites (abdomen, thigh, deltoid). "
            "Use a U-100 insulin syringe for accurate microdosing. Allow vial to reach "
            "room temperature before injection. Discard reconstituted vial after 14 days."
        ),
    },
    "legal_status": {
        "us": "Not FDA approved. Available for research use only in the United States.",
        "uk": "Not licensed by the MHRA. Research-use only.",
        "canada": "Not Health Canada approved. Research-use only.",
        "global": "Approved as Zadaxin in 35+ countries (Italy, China, Mexico, Brazil, etc.) for chronic HBV/HCV and as immune adjuvant.",
    },
    "protocols": {
        "title": "Subcutaneous Immunomodulation Protocol",
        "standard": {
            "route": "Subcutaneous",
            "frequency": "1.6 mg twice weekly (Mon/Thu), morning",
        },
        "dosages": [
            {
                "indication": "Chronic hepatitis B / hepatitis C research",
                "schedule": "Subcutaneous, 2× per week (e.g. Mon & Thu) for 6 months",
                "dose": "1.6 mg (1,600 mcg) per injection",
            },
            {
                "indication": "Hepatitis B vaccine adjuvant (non-responders, dialysis)",
                "schedule": "Subcutaneous, 2× per week for 4 weeks alongside vaccine schedule",
                "dose": "1.6 mg (1,600 mcg) per injection",
            },
            {
                "indication": "Immunosenescence / chronic immune support",
                "schedule": "Subcutaneous, 2× per week for 4–8 weeks; off cycle 4 weeks",
                "dose": "1.6 mg (1,600 mcg) per injection",
            },
            {
                "indication": "Severe sepsis / severe acute respiratory infection (ICU research)",
                "schedule": "Subcutaneous, 2× daily for 5–10 days",
                "dose": "1.6 mg (1,600 mcg) per injection",
            },
            {
                "indication": "Oncology adjuvant (melanoma, NSCLC, HCC research)",
                "schedule": "Subcutaneous, 2× per week, cycled with primary therapy",
                "dose": "1.6 mg (1,600 mcg) per injection",
            },
        ],
        "phases": [
            {
                "number": 1,
                "phase": "Loading (Weeks 1-2)",
                "dose": "1.6 mg × 2× per week — establishes immune priming",
            },
            {
                "number": 2,
                "phase": "Active phase (Weeks 3-12)",
                "dose": "1.6 mg × 2× per week — main immunomodulatory effect",
            },
            {
                "number": 3,
                "phase": "Maintenance (Weeks 13-24)",
                "dose": "1.6 mg × 1× per week (optional, condition-dependent)",
            },
            {
                "number": 4,
                "phase": "Off cycle (Weeks 25+)",
                "dose": "Washout 4-8 weeks before re-evaluating need",
            },
        ],
        "reconstitution": (
            "Reconstitute the 5 mg vial with 2 mL of bacteriostatic water → final "
            "concentration 2.5 mg/mL. A 1.6 mg dose = 0.64 mL = 64 IU on a U-100 "
            "insulin syringe. Alternative: 1.6 mL BAC water → ~3.125 mg/mL, where "
            "1.6 mg = ~0.51 mL ≈ 51 IU. Store reconstituted solution at 2–8 °C and "
            "use within 14 days."
        ),
        "reconstitution_steps": [
            "Step 1: Bring the lyophilized Thymosin Alpha-1 5mg vial and the bacteriostatic water vial to room temperature.",
            "Step 2: Wipe both rubber stoppers with a fresh alcohol swab.",
            "Step 3: Draw 2 mL of bacteriostatic water using a sterile syringe.",
            "Step 4: Inject the bacteriostatic water slowly down the inner wall of the Tα1 vial — do not squirt directly onto the powder.",
            "Step 5: Gently swirl (do NOT shake) until the powder is fully dissolved — the solution should be clear and colorless.",
            "Step 6: Label the vial with the reconstitution date and store at 2–8 °C. Discard 14 days after reconstitution.",
            "Step 7: For each dose, withdraw 64 IU (= 0.64 mL = 1.6 mg) using a U-100 insulin syringe, expel any air bubbles, and inject subcutaneously after rotating injection sites.",
        ],
    },
    "research": {
        "mechanism": (
            "Tα1 binds TLR9 (and partially TLR2) on dendritic cells and plasmacytoid DCs, "
            "driving their maturation toward a Th1-priming phenotype. This boosts IFN-γ, "
            "IL-2 and IL-12 secretion, restores effector and memory T-cell function, "
            "improves NK cell cytotoxicity, and rebalances Treg/effector ratios. It also "
            "modulates indoleamine 2,3-dioxygenase (IDO) and increases dendritic-cell "
            "antigen-presentation capacity, which underlies its synergy with vaccines and "
            "anti-tumor immunotherapy."
        ),
        "steps": [
            "TLR9 / TLR2 engagement on dendritic cells and macrophages",
            "Dendritic-cell maturation and Th1 cytokine polarization",
            "Increased IFN-γ, IL-2, IL-12; reduced excessive IL-10",
            "Restoration of CD4+ / CD8+ T-cell counts and effector function",
            "Enhanced NK-cell cytotoxicity and antibody-dependent cellular cytotoxicity",
            "Re-balancing of Treg/effector ratio and IDO modulation",
        ],
        "references": [
            "Romani L et al. Ann N Y Acad Sci. 2007;1112:326-38.",
            "Garaci E et al. Ann N Y Acad Sci. 2010;1194:158-63.",
            "Andreone P et al. Hepatology. 1996;24(4):774-7.",
            "Liu Y et al. Clin Infect Dis. 2020;71(16):2150-2157 (COVID-19 severe).",
            "Wu J et al. Crit Care. 2013;17(1):R8 (sepsis).",
            "Camerini R, Garaci E. Ann N Y Acad Sci. 2010;1194:153-7.",
        ],
    },
    "synergy": {
        "interactions": [
            "Synergistic with hepatitis B vaccine in non-responders and dialysis patients",
            "Combines well with interferon-α in HBV/HCV protocols",
            "Investigated as immune-restoring adjuvant with chemotherapy and checkpoint inhibitors",
        ],
        "stacks": [
            "TA-1 + BPC-157 — gut/immune recovery during prolonged infection or post-antibiotic",
            "TA-1 + Thymulin / Thymogen — broader thymic peptide stack (research only)",
            "TA-1 + LL-37 — antimicrobial + immune-priming research stack",
        ],
    },
    "has_product": True,
}


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    if not mongo_url:
        print("ERROR: MONGO_URL not set in backend/.env")
        sys.exit(1)

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

    result = await db.peptide_library.update_one(
        {"slug": SLUG},
        {"$set": update_doc},
    )

    print("=" * 60)
    print(f"Thymosin Alpha-1 protocol enriched")
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
    print(f"  • has_product: {PAYLOAD['has_product']}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
