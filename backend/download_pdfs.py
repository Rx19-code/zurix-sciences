"""Download all PDFs from Google Drive and extract text."""
import os
import json
import subprocess

# Files from Google Drive
FILES = [
    {"name": "Cartalax", "id": "1omzPvnF9Uzy69TNPLXgipY-OxP_scTEJ"},
    {"name": "Cartalax 2", "id": "1hqeYoa3ET7PfDB6pGWSMqHydzfsayRlp"},
    {"name": "Cartalax 3", "id": "1mXFD9osE05AXIud76XueJh7lf6Pvs00d"},
    {"name": "Cartalax 4", "id": "1li6rCPx5l5ex3fLdTsj9gwW9slMjhWDv"},
    {"name": "Cebrosylin", "id": "1gHTsZbftZaavM22pp2Pyvy21e3tQHhJl"},
    {"name": "Cebrosylin 2", "id": "1Y0N5eNdw7rxzrT_lL_qU8AUrbHcL0YR1"},
    {"name": "Cebrosylin 3", "id": "1Djj9_7X0Pn4GlehGE6rPO4fpnqxfJHzo"},
    {"name": "Cebrosylin 4", "id": "102ikcp2TdJ8SElz6iQGOQfSefgIE2LAp"},
    {"name": "Cerebrosylin", "id": "1LYlefJaSd_QpJF2y8SorLBR2HI9KQlBm"},
    {"name": "Cerebrosylin 2", "id": "1Jj4K_ZvxHj8h2MOSljluEv0f7WQT8rW8"},
    {"name": "Cerebrosylin 3", "id": "1L5X8Zl2_agCYV5FxpSbFou6RaX7hYt0I"},
    {"name": "Cerebrosylin 4", "id": "1LkFE39F7qqAp9DQOA7sXP8VYY3J2RBJ-"},
    {"name": "Cortagen", "id": "15TP_q3HSgcajlbvTQt57A9GEj7v9FY9O"},
    {"name": "Cortagen 2", "id": "19feMckOxGOE1hm4AZa3YJN-dfYPLVW3_"},
    {"name": "Cortagen 3", "id": "1mZZ-FmgMb2ll3Phm1jnqycfDh-nM5WtU"},
    {"name": "Cortagen 4", "id": "1zm2HdtK2iK6eGRBIvAdIoY__n1UzNePq"},
    {"name": "Dihexa", "id": "1AKGdWOLWidovIW1_Z43O5opEZSrpZeOf"},
    {"name": "Dihexa 2", "id": "1QuztgWoa46634KaOdCYRgT6XXOtruOXe"},
    {"name": "Dihexa 3", "id": "1NbREEeFAfEhse7lk47IDtDqT4NZsc-54"},
    {"name": "Dihexa 4", "id": "1TXAnH-aZthR0eFnlNI0G2W8Z7VHPrPLT"},
    {"name": "Ephitalon", "id": "18UjOs6YG355nr0NwSLrFDrNDTnhmt_Mu"},
    {"name": "Ephitalon 2", "id": "1aPhYBeqfz5JRSSSThW53BywTh3rt2v2q"},
    {"name": "Ephitalon 3", "id": "19k38vmK8K3urNj1vbp3VdPHJOmrHGh5y"},
    {"name": "Ephitalon 4", "id": "1gRlQERhUpq0SYfTLNa-R7WRsvttnnhOp"},
    {"name": "Foxo-4-dri", "id": "1VU50QAhQG4mXS09HybB56YYfNddP9o22"},
    {"name": "Foxo-4-dri 2", "id": "1d3N5KY-SbKvbOply8hnCsaR8cVidztvg"},
    {"name": "Foxo-4-dri 3", "id": "1SEuVS5cruGiECA5wcmIyGw3L8o-e-Pm_"},
    {"name": "Foxo-4-dri 4", "id": "1mHpjW5Fcw8Bic3JZz9236zxMQ5mUqsXR"},
    {"name": "Gluthadione", "id": "1bImtlPExd83K7guw45DwjQ1EDLePrQBV"},
    {"name": "Gluthadione 2", "id": "1btf0_eiBnIB5GesAyM8qoSZAO_eT93Se"},
    {"name": "Gluthadione 3", "id": "1u0Tt4KnQkkcIq1CQNG__6IV7XSGcv4DY"},
    {"name": "Gluthadione 4", "id": "1-oPBOgGCCM3S8cwqCFjMydQaVe15FS5j"},
    {"name": "Nad+", "id": "1jNFrz4ddMjbpw3IP-a4sW2o_ZUBoKCtj"},
    {"name": "NAD+ 2", "id": "1WBM6oN8_-iEY_DNLuvYtNtw6ySBvLSid"},
    {"name": "Nad+ 3", "id": "1ZhrhkeI3BuDAeckCJISrixtc-KHFmhXy"},
    {"name": "Nad+ 4", "id": "1WbOADXCm2IlkxLsoTnbw3zqqPSPLBg4L"},
    {"name": "P21", "id": "1J-yd3PM3gdEizwma5U1bTkhQ-GgAWSpQ"},
    {"name": "P21 2", "id": "1opC7SdEMIhmHeZ8C7w7kcHHR1lq0n2vN"},
    {"name": "P21 3", "id": "1AB_PmCpqurNszQ1Ejmp8alJqPZ507mzy"},
    {"name": "P21 4", "id": "13LYM-JGsnQ1dWYGrM0wC0bJ-xDJPirZs"},
    {"name": "P22-28 1", "id": "121MVY7kaZz7VdMkZ4QSrIOVukrFsJvTS"},
    {"name": "P22-28 2", "id": "1aD5VFdG-W6-7JsTVfBlgHpidtYfHRoLD"},
    {"name": "P22-28 3", "id": "15Ut7tuaIHfvaoxb0kdEIG4QsFMvaRXSt"},
    {"name": "P22-28 4", "id": "14B_pyKH8T3gCkZ09mNc-WxLd0Wg6UO-5"},
    {"name": "Pinealon", "id": "1h-iW7pp77pECqLlVz1yflGhjcOA2pD_R"},
    {"name": "Pinealon 2", "id": "15vxHnNMygzC5RMN9SmsVQPub5zpVTxFE"},
    {"name": "Pinealon 3", "id": "1JNjHz4-_ashss3uVACrNMZGUSAFRRaaM"},
    {"name": "Pinealon 4", "id": "1m6YMt3rJkRd4_6Wlf97HNP73IgyeBL2E"},
    {"name": "Pn27", "id": "1AcdHHnL8yGXypuFOpdwvfd6tWc1xFghD"},
    {"name": "Pnc27 2", "id": "1wQZ2paGmrDl4Afx-VWLDiiCxa9Myt80f"},
]

DOWNLOAD_DIR = "/tmp/peptide_pdfs_new"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Download all
for f in FILES:
    safe_name = f["name"].replace(" ", "_").replace("+", "plus") + ".pdf"
    path = os.path.join(DOWNLOAD_DIR, safe_name)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print(f"SKIP {f['name']} (already downloaded)")
        continue
    url = f"https://drive.google.com/uc?export=download&id={f['id']}"
    print(f"Downloading {f['name']}...", end=" ", flush=True)
    result = subprocess.run(
        ["curl", "-sL", "-o", path, url],
        capture_output=True, timeout=30
    )
    size = os.path.getsize(path) if os.path.exists(path) else 0
    print(f"{size} bytes")

# Extract text
import pdfplumber

peptide_texts = {}
for f in FILES:
    safe_name = f["name"].replace(" ", "_").replace("+", "plus") + ".pdf"
    path = os.path.join(DOWNLOAD_DIR, safe_name)
    # Get base peptide name (without page number)
    base = f["name"].split(" ")[0].replace("-", "").lower()
    if base == "nad" or base == "nad+":
        base = "nadplus"
    if base == "pnc27" or base == "pn27":
        base = "pnc28"  # Map to pnc-28 in DB
    
    if base not in peptide_texts:
        peptide_texts[base] = []
    
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    peptide_texts[base].append(text)
    except Exception as e:
        print(f"Error extracting {f['name']}: {e}")

# Save combined text per peptide
for base, texts in peptide_texts.items():
    combined = "\n\n--- PAGE BREAK ---\n\n".join(texts)
    out_path = os.path.join(DOWNLOAD_DIR, f"{base}_combined.txt")
    with open(out_path, "w") as fout:
        fout.write(combined)
    print(f"{base}: {len(texts)} pages, {len(combined)} chars")

print(f"\nTotal peptides: {len(peptide_texts)}")
