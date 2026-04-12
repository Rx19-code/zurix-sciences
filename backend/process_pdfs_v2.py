"""
Process extracted PDF text using GPT-4o-mini to generate structured protocol data.
Translates from Portuguese to English.
"""
import asyncio
import json
import os
import pymongo
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test_database"]
col = db["peptide_library"]

API_KEY = os.environ.get("EMERGENT_LLM_KEY")
PDF_DIR = "/tmp/peptide_pdfs_new"

# Map PDF base names to DB slugs
SLUG_MAP = {
    "cartalax": "cartalax",
    "cebrosylin": "cerebrolysin",
    "cerebrosylin": "cerebrolysin",
    "cortagen": "cortagen",
    "dihexa": "dihexa",
    "ephitalon": "epithalon",
    "foxo4dri": "foxo4-dri",
    "gluthadione": "glutathione",
    "nadplus": "nad-plus-",
    "p21": "p21",
    "p2228": "pnc-28",
    "pinealon": "pinealon",
    "pnc28": "pnc-28",
}

SYSTEM_PROMPT = """You are a peptide research expert. Extract and structure protocol data from raw PDF text (in Portuguese).
Translate EVERYTHING to English. Remove any competitor references (PeptídeosHealth, etc.).

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


async def process_peptide(base_name, slug):
    txt_path = os.path.join(PDF_DIR, f"{base_name}_combined.txt")
    if not os.path.exists(txt_path):
        return None

    with open(txt_path) as f:
        raw_text = f.read()

    # Truncate if too long
    if len(raw_text) > 8000:
        raw_text = raw_text[:8000]

    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"proto-{slug}",
        system_message=SYSTEM_PROMPT,
    )
    chat.with_model("openai", "gpt-4o-mini")

    msg = UserMessage(
        text=f"Extract and structure ALL protocol data from this Portuguese PDF text for peptide '{base_name}'. Translate to English. Return ONLY valid JSON:\n\n{raw_text}"
    )

    response = await chat.send_message(msg)
    resp_text = response.strip()
    if resp_text.startswith("```"):
        resp_text = resp_text.split("\n", 1)[1] if "\n" in resp_text else resp_text[3:]
    if resp_text.endswith("```"):
        resp_text = resp_text[:-3]

    return json.loads(resp_text.strip())


async def main():
    processed = 0
    failed = []

    for base_name, slug in SLUG_MAP.items():
        txt_path = os.path.join(PDF_DIR, f"{base_name}_combined.txt")
        if not os.path.exists(txt_path):
            continue

        # Check if peptide exists in DB
        pep = col.find_one({"slug": slug}, {"_id": 0, "slug": 1, "name": 1})
        if not pep:
            print(f"SKIP {base_name}: slug '{slug}' not found in DB")
            continue

        print(f"Processing {base_name} → {slug} ({pep['name']})...", end=" ", flush=True)

        try:
            data = await process_peptide(base_name, slug)
            if not data:
                print("No data")
                continue

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
                ni = len(data.get("synergy", {}).get("interactions", []))
                print(f"OK ({nd} dosages, {ns} recon steps, {ni} interactions)")
                processed += 1
            else:
                print("No updates")
        except Exception as e:
            failed.append(base_name)
            print(f"FAILED: {e}")

    print(f"\n=== Complete ===")
    print(f"Processed: {processed}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    asyncio.run(main())
