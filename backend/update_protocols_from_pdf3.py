"""
Update peptide library with detailed protocol data from user's PDF.
All content already in English.
"""
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test_database"]
col = db["peptide_library"]

UPDATES = {
    "ss-31": {
        "protocols": {
            "title": "Standard Anti-aging Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Daily or every other day"},
            "dosages": [
                {"indication": "Anti-aging / Longevity", "schedule": "Daily or every other day", "dose": "5 mg SC"},
                {"indication": "Neuroprotection", "schedule": "Daily", "dose": "5 mg SC"},
                {"indication": "Sarcopenia", "schedule": "Daily", "dose": "5-10 mg SC"},
                {"indication": "Cardiovascular", "schedule": "Daily", "dose": "5 mg SC"}
            ],
            "phases": [
                {"number": 1, "phase": "Initial Phase", "dose": "5 mg/day SC"},
                {"number": 2, "phase": "Maintenance Phase", "dose": "5 mg every other day"}
            ],
            "reconstitution_steps": [
                "Aspirate 1-2 mL of bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial.",
                "Gently swirl (do not shake) until completely dissolved.",
                "Label with date and concentration.",
                "Store refrigerated at 2-8°C for up to 28 days."
            ],
            "reconstitution": "Reconstitute with 1-2 mL bacteriostatic water. Store at 2-8°C for up to 28 days."
        }
    },
    "semax": {
        "protocols": {
            "title": "Subcutaneous Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Consult a healthcare professional"},
            "dosages": [
                {"indication": "General Use", "schedule": "Consult a professional", "dose": "Variable"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "Consult specific protocol"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "selank": {
        "protocols": {
            "title": "Intranasal / SC Protocol",
            "standard": {"route": "Intranasal or Subcutaneous", "frequency": "1-3x per day"},
            "dosages": [
                {"indication": "Anxiety", "schedule": "1-3x per day intranasal", "dose": "300-600 mcg/day"}
            ],
            "phases": [
                {"number": 1, "phase": "Intranasal (standard)", "dose": "300-600 mcg/day"},
                {"number": 2, "phase": "Subcutaneous", "dose": "250-500 mcg/day"}
            ],
            "reconstitution_steps": [
                "For SC use: reconstitute with bacteriostatic water.",
                "For intranasal: use ready-made formulation.",
                "Refrigerate at 2-8°C.",
                "Use within 30 days."
            ],
            "reconstitution": "For SC: reconstitute with bacteriostatic water. For intranasal: use ready-made formulation. Store at 2-8°C."
        }
    },
    "pnc-27": {
        "protocols": {
            "title": "Subcutaneous Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Consult a healthcare professional"},
            "dosages": [
                {"indication": "General Use", "schedule": "Consult a professional", "dose": "Variable"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "Consult specific protocol"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "pinealon": {
        "protocols": {
            "title": "Subcutaneous Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Consult a healthcare professional"},
            "dosages": [
                {"indication": "General Use", "schedule": "Consult a professional", "dose": "Variable"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "Consult specific protocol"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "pe-22-28": {
        "protocols": {
            "title": "Subcutaneous Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Consult a healthcare professional"},
            "dosages": [
                {"indication": "General Use", "schedule": "Consult a professional", "dose": "Variable"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "Consult specific protocol"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "p-21": {
        "protocols": {
            "title": "Subcutaneous Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Consult a healthcare professional"},
            "dosages": [
                {"indication": "General Use", "schedule": "Consult a professional", "dose": "Variable"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "Consult specific protocol"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "nad-plus-": {
        "protocols": {
            "title": "Standard Protocol",
            "standard": {"route": "IV, IM or SC", "frequency": "Variable"},
            "dosages": [
                {"indication": "Energy / mitochondrial metabolism", "schedule": "1x per day in the morning", "dose": "250-500 mg"},
                {"indication": "Insulin sensitivity", "schedule": "1x per day", "dose": "500-1000 mg"},
                {"indication": "Fatigue / stress resilience", "schedule": "1x per day or EOD", "dose": "250-500 mg"},
                {"indication": "Anti-aging / metabolic support", "schedule": "1x per day", "dose": "250-500 mg"}
            ],
            "phases": [
                {"number": 1, "phase": "Oral standard (NMN/NR)", "dose": "250-500 mg/day"}
            ],
            "reconstitution_steps": [
                "Aspirate 1-2 mL of bacteriostatic water (if lyophilized).",
                "Slowly inject into the vial.",
                "Gently swirl until dissolved.",
                "Label and refrigerate at 2-8°C for up to 7 days."
            ],
            "reconstitution": "Reconstitute with 1-2 mL bacteriostatic water. Store at 2-8°C for up to 7 days."
        }
    },
    "glutathione": {
        "protocols": {
            "title": "Standard IM Protocol",
            "standard": {"route": "Intramuscular", "frequency": "1-2x per week"},
            "dosages": [
                {"indication": "Antioxidant support / well-being", "schedule": "IM 1-2x per week", "dose": "300-600 mg"},
                {"indication": "Skin lightening / cosmetic", "schedule": "IM weekly", "dose": "600 mg"},
                {"indication": "Post-viral fatigue / immune support", "schedule": "IM weekly", "dose": "600 mg"},
                {"indication": "Liver support", "schedule": "IM weekly", "dose": "600 mg"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "300-600 mg IM"}
            ],
            "reconstitution_steps": [
                "Aspirate 1-2 mL of bacteriostatic water.",
                "Slowly inject into the vial.",
                "Gently swirl until dissolved.",
                "Label and refrigerate at 2-8°C for up to 7 days."
            ],
            "reconstitution": "Reconstitute with 1-2 mL bacteriostatic water. Store at 2-8°C for up to 7 days."
        }
    },
    "foxo4-dri": {
        "protocols": {
            "title": "Senolytic (Pulse) Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Pulse protocol"},
            "dosages": [
                {"indication": "Anti-aging Senolytic", "schedule": "Pulse: 1 dose every 2-3 days", "dose": "5-10 mg/dose"}
            ],
            "phases": [
                {"number": 1, "phase": "Senolytic cycle", "dose": "5-10 mg/dose"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial.",
                "Gently swirl until dissolved.",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "epithalon": {
        "protocols": {
            "title": "Standard Protocol (2 mL = 5 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "Once a day"},
            "dosages": [
                {"indication": "Anti-aging / telomeres", "schedule": "1x per day for 10 days", "dose": "0.5-1.0 mg/day"},
                {"indication": "Sleep quality / circadian rhythm", "schedule": "1x per day before bed", "dose": "0.5-1.0 mg/day"},
                {"indication": "Post-surgical recovery", "schedule": "1x per day", "dose": "0.5 mg/day"},
                {"indication": "Longevity (prolonged course)", "schedule": "1x per day for 20 days", "dose": "1.0 mg/day"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard cycle (10 days)", "dose": "5 mg/day"},
                {"number": 2, "phase": "Intensive cycle (20 days)", "dose": "10 mg/day"}
            ],
            "reconstitution_steps": [
                "Aspirate 2.0 mL of bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with 2.0 mL bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "dihexa": {
        "protocols": {
            "title": "Oral / Topical Protocol",
            "standard": {"route": "Oral or Topical (with DMSO)", "frequency": "1-2x per week"},
            "dosages": [
                {"indication": "Cognitive Regeneration", "schedule": "1-2x per week", "dose": "5-20 mg"}
            ],
            "phases": [
                {"number": 1, "phase": "Low dose", "dose": "5-10 mg, 1x/week"},
                {"number": 2, "phase": "Standard dose", "dose": "10-20 mg, 1-2x/week"}
            ],
            "reconstitution_steps": [
                "Generally sold in capsules or powder.",
                "For topical use, DMSO is required as a solvent.",
                "Store in a cool, dry place.",
                "Protect from light and humidity."
            ],
            "reconstitution": "Available in capsules or powder. For topical use, requires DMSO as solvent."
        }
    },
    "cortagen": {
        "protocols": {
            "title": "Subcutaneous Protocol",
            "standard": {"route": "Subcutaneous", "frequency": "Consult a healthcare professional"},
            "dosages": [
                {"indication": "General Use", "schedule": "Consult a professional", "dose": "Variable"}
            ],
            "phases": [
                {"number": 1, "phase": "Standard", "dose": "Consult specific protocol"}
            ],
            "reconstitution_steps": [
                "Aspirate bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not shake).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
    "cartalax": {
        "protocols": {
            "title": "Standard Protocol (3 mL = ~6.67 mg/mL)",
            "standard": {"route": "Subcutaneous", "frequency": "Once a day"},
            "dosages": [
                {"indication": "Joint Health", "schedule": "1x per day", "dose": "200-500 mcg/day"}
            ],
            "phases": [
                {"number": 1, "phase": "Weeks 1-2", "dose": "200 mcg"},
                {"number": 2, "phase": "Weeks 3-4", "dose": "400 mcg"},
                {"number": 3, "phase": "Weeks 5-10", "dose": "500 mcg"}
            ],
            "reconstitution_steps": [
                "Aspirate 3.0 mL of bacteriostatic water with a sterile syringe.",
                "Slowly inject into the vial; avoid foam.",
                "Gently swirl until dissolved (do not agitate).",
                "Label and refrigerate at 2-8°C, protected from light."
            ],
            "reconstitution": "Reconstitute with 3.0 mL bacteriostatic water. Store at 2-8°C, protected from light."
        }
    },
}

def main():
    updated = 0
    for slug, data in UPDATES.items():
        pep = col.find_one({"slug": slug}, {"_id": 0, "name": 1})
        if not pep:
            print(f"SKIP: slug '{slug}' not found in DB")
            continue

        col.update_one({"slug": slug}, {"$set": data})
        nd = len(data["protocols"].get("dosages", []))
        np_ = len(data["protocols"].get("phases", []))
        ns = len(data["protocols"].get("reconstitution_steps", []))
        print(f"OK: {slug} ({pep['name']}) - {nd} dosages, {np_} phases, {ns} recon steps")
        updated += 1

    print(f"\n=== Updated {updated}/{len(UPDATES)} peptides ===")


if __name__ == "__main__":
    main()
