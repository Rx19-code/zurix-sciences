"""
Process PDF batch 2 from Google Drive.
Extract text from PDFs, combine per peptide, send to LLM, update DB.
"""
import asyncio
import json
import os
import re
import pymongo
import pdfplumber
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test_database"]
col = db["peptide_library"]

API_KEY = os.environ.get("EMERGENT_LLM_KEY")
PDF_DIR = "/tmp/peptide_pdfs_batch2/PDF PEPTIDES 2"

# Map PDF base names (lowercase) to DB slugs
SLUG_MAP = {
    "aod-9604": "aod-9604",
    "cagrilintide": "cagrilintide",
    "cardiogen": "cardiogen",
    "chonluten": "chonluten",
    "hgh frag": "hgh-fragment-176-191",
    "hgh-frag": "hgh-fragment-176-191",
    "livagen": "livagen",
    "mazdutide": "mazdutide",
    "ovagen": "ovagen",
    "prostamax": "prostamax",
    "retatrutide": "retatrutide",
    "semaglutida": "semaglutide",
    "vesugen": "vesugen",
    "versugen": "vesugen",
}

SYSTEM_PROMPT = """You are a peptide research expert. Extract and structure protocol data from raw PDF text (in Portuguese).
Translate EVERYTHING to English. Remove any competitor references (PeptideosHealth, Peptídeos Health, etc.).

Return ONLY valid JSON with this structure:
{
  "overview": {
    "what_is": "Brief description of what this peptide is and its primary function",
    "mechanism_summary": "How it works at a molecular/cellular level"
  },
  "protocols": {
    "title": "Standard Protocol title",
    "standard": {
      "route": "SC/IM/IV/Oral/etc",
      "frequency": "Daily/Weekly/etc"
    },
    "dosages": [
      {"indication": "Primary use", "schedule": "Route and frequency details", "dose": "Amount with units (mcg/mg/IU)"}
    ],
    "phases": [
      {"number": 1, "phase": "Phase description (e.g. Weeks 1-4)", "dose": "Amount"}
    ],
    "reconstitution_steps": [
      "Step 1...",
      "Step 2..."
    ],
    "reconstitution": "Brief reconstitution note"
  },
  "research": {
    "mechanism": "Detailed mechanism of action",
    "steps": ["Key research finding 1", "Key research finding 2"],
    "references": ["Reference 1", "Reference 2"]
  },
  "synergy": {
    "interactions": [
      {"peptide": "Name", "status": "SYNERGISTIC/COMPATIBLE/CAUTION", "description": "Brief description"}
    ]
  }
}

Rules:
- ALL text must be in English
- Extract dosages, phases, reconstitution steps from the protocol pages
- Include 2-4 dosage indications with specific amounts
- Include reconstitution steps if mentioned
- Include research mechanism and references if present
- Include synergy/interaction data if present
- Remove competitor names/URLs
- Keep all numerical values (mg, mcg, IU) exactly as they appear"""


def extract_text_from_pdf(pdf_path):
    """Extract text from a single PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
    except Exception as e:
        print(f"  Error extracting {pdf_path}: {e}")
    return text


def group_pdfs_by_peptide():
    """Group PDF files by peptide name and return combined text."""
    groups = {}
    
    for filename in sorted(os.listdir(PDF_DIR)):
        if not filename.lower().endswith('.pdf'):
            continue
        
        # Extract base name (remove number suffix and .pdf)
        base = filename.replace('.pdf', '').strip()
        # Remove trailing number like " 2", " 3", " 4", " -2", " -3", " -4"
        base_clean = re.sub(r'\s*-?\s*\d+$', '', base).strip().lower()
        
        # Find matching slug
        slug = None
        for key, val in SLUG_MAP.items():
            if key in base_clean or base_clean in key:
                slug = val
                break
        
        if not slug:
            print(f"  WARNING: No slug mapping for '{filename}' (base: '{base_clean}')")
            continue
        
        if slug not in groups:
            groups[slug] = []
        
        filepath = os.path.join(PDF_DIR, filename)
        text = extract_text_from_pdf(filepath)
        if text.strip():
            groups[slug].append((filename, text))
            print(f"  Extracted: {filename} → {slug} ({len(text)} chars)")
        else:
            print(f"  EMPTY: {filename}")
    
    return groups


async def process_with_llm(slug, combined_text):
    """Send combined text to LLM for structuring."""
    if len(combined_text) > 12000:
        combined_text = combined_text[:12000]
    
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"batch2-{slug}",
        system_message=SYSTEM_PROMPT,
    )
    chat.with_model("openai", "gpt-4o-mini")
    
    msg = UserMessage(
        text=f"Extract and structure ALL protocol data from this Portuguese PDF text for peptide '{slug}'. Translate to English. Return ONLY valid JSON:\n\n{combined_text}"
    )
    
    response = await chat.send_message(msg)
    resp_text = response.strip()
    if resp_text.startswith("```"):
        resp_text = resp_text.split("\n", 1)[1] if "\n" in resp_text else resp_text[3:]
    if resp_text.endswith("```"):
        resp_text = resp_text[:-3]
    
    return json.loads(resp_text.strip())


async def main():
    print("=== Step 1: Extracting text from PDFs ===")
    groups = group_pdfs_by_peptide()
    
    print(f"\n=== Step 2: Processing {len(groups)} peptides with LLM ===")
    processed = 0
    failed = []
    
    for slug, files in sorted(groups.items()):
        # Combine all text for this peptide
        combined = "\n\n--- PAGE BREAK ---\n\n".join([text for _, text in files])
        
        # Check if peptide exists in DB
        pep = col.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not pep:
            print(f"SKIP {slug}: not found in DB")
            continue
        
        print(f"\nProcessing {slug} ({pep['name']}, {len(files)} pages, {len(combined)} chars)...", flush=True)
        
        try:
            data = await process_with_llm(slug, combined)
            
            updates = {}
            if data.get("overview"):
                updates["overview"] = data["overview"]
            if data.get("protocols"):
                updates["protocols"] = data["protocols"]
            if data.get("research"):
                updates["research"] = data["research"]
            if data.get("synergy"):
                updates["synergy"] = data["synergy"]
            
            if updates:
                col.update_one({"slug": slug}, {"$set": updates})
                nd = len(data.get("protocols", {}).get("dosages", []))
                ns = len(data.get("protocols", {}).get("reconstitution_steps", []))
                np_ = len(data.get("protocols", {}).get("phases", []))
                ni = len(data.get("synergy", {}).get("interactions", []))
                print(f"  OK: {nd} dosages, {np_} phases, {ns} recon steps, {ni} interactions")
                processed += 1
            else:
                print(f"  No updates extracted")
        except Exception as e:
            failed.append(slug)
            print(f"  FAILED: {e}")
    
    # Also process p21 from batch 1 (slug was wrong before)
    print("\n=== Step 3: Processing p21 from batch 1 ===")
    p21_txt = "/tmp/peptide_pdfs_new/p21_combined.txt"
    if os.path.exists(p21_txt):
        with open(p21_txt) as f:
            p21_text = f.read()
        
        pep = col.find_one({"slug": "p-21"}, {"_id": 0, "slug": 1, "name": 1})
        if pep:
            print(f"Processing p-21 ({pep['name']}, {len(p21_text)} chars)...", flush=True)
            try:
                data = await process_with_llm("p-21", p21_text)
                updates = {}
                if data.get("overview"):
                    updates["overview"] = data["overview"]
                if data.get("protocols"):
                    updates["protocols"] = data["protocols"]
                if data.get("research"):
                    updates["research"] = data["research"]
                if data.get("synergy"):
                    updates["synergy"] = data["synergy"]
                if updates:
                    col.update_one({"slug": "p-21"}, {"$set": updates})
                    nd = len(data.get("protocols", {}).get("dosages", []))
                    ns = len(data.get("protocols", {}).get("reconstitution_steps", []))
                    np_ = len(data.get("protocols", {}).get("phases", []))
                    print(f"  OK: {nd} dosages, {np_} phases, {ns} recon steps")
                    processed += 1
            except Exception as e:
                failed.append("p-21")
                print(f"  FAILED: {e}")
        else:
            print("  p-21 not found in DB")
    
    print(f"\n=== COMPLETE ===")
    print(f"Processed: {processed}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed list: {failed}")


if __name__ == "__main__":
    asyncio.run(main())
