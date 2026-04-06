"""
Phase 1: Fix categories, competitor URLs, and broken dosage values.
No LLM needed - direct DB updates.
"""
import pymongo
import re

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test_database"]
col = db["peptide_library"]

# ── 1. Fix Retatrutide competitor category ──
print("=== Fixing Retatrutide category ===")
res = col.update_one(
    {"slug": "retatrutide"},
    {"$set": {"category": "Weight Loss / GLP-1"}}
)
print(f"  Modified: {res.modified_count}")

# ── 2. Map Portuguese categories to English ──
CATEGORY_MAP = {
    "Emagrecimento": "Weight Loss / GLP-1",
    "Biorregulador": "Bioregulators",
    "Antioxidante": "Metabolism",
    "Cardiovascular": "Recovery",
}
print("\n=== Mapping Portuguese categories ===")
for pt_cat, en_cat in CATEGORY_MAP.items():
    res = col.update_many({"category": pt_cat}, {"$set": {"category": en_cat}})
    if res.modified_count:
        print(f"  {pt_cat} → {en_cat}: {res.modified_count} updated")

# ── 3. Fix broken dosage values (0 mg) ──
# These are peptides where PDF extraction produced wrong "0 mg" values
DOSAGE_FIXES = {
    "semaglutide": [
        {"indication": "Weight Loss (Wegovy)", "schedule": "Titrate every 4 weeks", "dose": "0.25–2.4 mg/week"},
        {"indication": "Type 2 Diabetes (Ozempic)", "schedule": "SC once weekly", "dose": "0.25–1.0 mg/week"},
        {"indication": "Obesity (High dose)", "schedule": "SC once weekly", "dose": "2.4 mg/week"},
    ],
    "aod-9604": [
        {"indication": "Fat loss (standard)", "schedule": "SC daily, fasting", "dose": "300–500 mcg/day"},
        {"indication": "Fat loss (accelerated)", "schedule": "SC daily", "dose": "500 mcg/day"},
        {"indication": "Lipid profile / metabolic support", "schedule": "SC daily", "dose": "300 mcg/day"},
    ],
    "epithalon": [
        {"indication": "Anti-aging (standard cycle)", "schedule": "SC daily, 10-day cycles", "dose": "5–10 mg/day"},
        {"indication": "Sleep quality / circadian", "schedule": "SC before bedtime", "dose": "5 mg/day"},
        {"indication": "Post-surgical recovery", "schedule": "SC daily", "dose": "5 mg/day"},
        {"indication": "Longevity (extended course)", "schedule": "SC daily, 20-day cycle", "dose": "10 mg/day"},
    ],
    "cagrilintide": [
        {"indication": "Weight loss (titration)", "schedule": "SC once weekly", "dose": "0.3–4.5 mg/week"},
        {"indication": "Weight loss (maintenance)", "schedule": "SC once weekly", "dose": "2.4–4.5 mg/week"},
    ],
}

print("\n=== Fixing broken dosage values ===")
for slug, new_dosages in DOSAGE_FIXES.items():
    res = col.update_one(
        {"slug": slug},
        {"$set": {"protocols.dosages": new_dosages}}
    )
    print(f"  {slug}: {res.modified_count} updated ({len(new_dosages)} dosages)")

# ── 4. Fix phases with Portuguese text ──
PHASE_FIXES = {
    "semaglutide": [
        {"number": 1, "phase": "Weeks 1–4", "dose": "250 mcg (0.25 mg)"},
        {"number": 2, "phase": "Weeks 5–8", "dose": "500 mcg (0.5 mg)"},
        {"number": 3, "phase": "Weeks 9–12", "dose": "1000 mcg (1.0 mg)"},
        {"number": 4, "phase": "Weeks 13–16", "dose": "1700 mcg (1.7 mg)"},
        {"number": 5, "phase": "Weeks 17+ (Maintenance)", "dose": "2400 mcg (2.4 mg)"},
    ],
}
print("\n=== Fixing phase data ===")
for slug, new_phases in PHASE_FIXES.items():
    res = col.update_one(
        {"slug": slug},
        {"$set": {"protocols.phases": new_phases}}
    )
    print(f"  {slug}: {res.modified_count} updated")

# ── 5. Clean competitor URLs/names from ALL text fields ──
print("\n=== Scanning and cleaning competitor artifacts ===")
COMPETITOR_PATTERNS = [
    (r'https?://peptideoshealth\.com\.br[^\s]*', ''),
    (r'PeptídeosHealth', ''),
    (r'peptideoshealth', ''),
    (r'Peptídeos\s*Health', ''),
    (r'Era dos Peptídeos \d{4}', ''),
    (r'Início\s*de?\s*P\s*esputídpeeorsior.*?duplos\.?', ''),  # garbled text
    (r'IníciodeP esputídpeeorsior à obFisnederrvada cCoamlcu laadgooranistas Msiemnuples ou duplos\.?', ''),
    (r'Voltar', ''),
]

def clean_text(text):
    if not isinstance(text, str):
        return text
    for pattern, replacement in COMPETITOR_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    # Clean up multiple spaces/newlines
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()

def clean_dict(obj):
    if isinstance(obj, str):
        return clean_text(obj)
    if isinstance(obj, list):
        return [clean_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: clean_dict(v) for k, v in obj.items()}
    return obj

cleaned_count = 0
for pep in col.find({}, {"_id": 1, "slug": 1, "overview": 1, "protocols": 1, "research": 1, "synergy": 1, "category": 1, "description": 1}):
    original = str(pep)
    updates = {}
    for field in ["overview", "protocols", "research", "synergy", "description", "category"]:
        if field in pep and pep[field]:
            cleaned = clean_dict(pep[field])
            if str(cleaned) != str(pep[field]):
                updates[field] = cleaned
    if updates:
        col.update_one({"_id": pep["_id"]}, {"$set": updates})
        cleaned_count += 1
        print(f"  Cleaned: {pep['slug']} ({list(updates.keys())})")

print(f"\nTotal peptides cleaned: {cleaned_count}")

# ── 6. Verify ──
print("\n=== Verification ===")
cats = col.distinct("category")
print(f"Categories ({len(cats)}): {sorted(cats)}")

# Check for remaining competitor references
import json
remaining = 0
for pep in col.find({}, {"_id": 0}):
    text = json.dumps(pep, default=str, ensure_ascii=False).lower()
    if "peptideoshealth" in text or "peptideos health" in text:
        print(f"  STILL HAS competitor ref: {pep['slug']}")
        remaining += 1
print(f"Remaining competitor artifacts: {remaining}")

print("\nPhase 1 complete!")
