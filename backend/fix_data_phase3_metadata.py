"""
Phase 3: Translate remaining Portuguese fields (classification, evidence_level, half_life)
using GPT-4o-mini in a single batch call.
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

PT_WORDS = ['agonista', 'receptor', 'análogo', 'aprovado', 'dias', 'horas', 'minutos',
            'semana', 'modulador', 'peptídeo', 'sintético', 'hormônio', 'crescimento',
            'regulador', 'inibidor', 'proteína', 'fator', 'estimulador', 'liberação',
            'composto', 'biorregulador', 'tripeptídeo', 'tetrapeptídeo', 'heptapeptídeo',
            'oligopeptídeo', 'derivado', 'direcionado', 'duplo', 'triplo', 'curta',
            'prolongados', 'prolongada', 'variável', 'endógeno', 'acilado']


async def main():
    # Collect all fields needing translation
    items_to_translate = []
    for pep in col.find({}, {"_id": 0, "slug": 1, "classification": 1, "evidence_level": 1, "half_life": 1}):
        fields = {}
        for field in ["classification", "evidence_level", "half_life"]:
            val = pep.get(field, "")
            if val and any(w in val.lower() for w in PT_WORDS):
                fields[field] = val
        if fields:
            items_to_translate.append({"slug": pep["slug"], "fields": fields})
    
    print(f"Found {len(items_to_translate)} peptides with PT metadata fields")
    
    if not items_to_translate:
        print("Nothing to translate!")
        return
    
    # Build a single batch payload
    batch = {item["slug"]: item["fields"] for item in items_to_translate}
    
    chat = LlmChat(
        api_key=API_KEY,
        session_id="translate-metadata",
        system_message="""You are a scientific translator. Translate Portuguese peptide metadata to English.
Keep scientific terms accurate. Return ONLY valid JSON with the exact same structure.
Examples:
- "Agonista do receptor GLP-1" → "GLP-1 Receptor Agonist"
- "Aprovado (FDA/EMA)" → "Approved (FDA/EMA)"  
- "~7 dias" → "~7 days"
- "Peptídeo sintético" → "Synthetic Peptide"
- "Tetrapeptídeo biorregulador sintético" → "Synthetic Bioregulator Tetrapeptide"
- "~30-60 minutos" → "~30-60 minutes"
- "Curta (minutos); efeitos prolongados" → "Short (minutes); prolonged effects"
- "horas" → "hours"
- "semana" → "weekly"
Do NOT add markdown, code blocks, or explanations. Return ONLY valid JSON.""",
    )
    chat.with_model("openai", "gpt-4o-mini")
    
    msg = UserMessage(
        text=f"Translate all Portuguese values to English. Return the exact same JSON structure:\n\n{json.dumps(batch, ensure_ascii=False)}"
    )
    
    response = await chat.send_message(msg)
    
    # Parse response
    resp_text = response.strip()
    if resp_text.startswith("```"):
        resp_text = resp_text.split("\n", 1)[1] if "\n" in resp_text else resp_text[3:]
    if resp_text.endswith("```"):
        resp_text = resp_text[:-3]
    resp_text = resp_text.strip()
    
    translated = json.loads(resp_text)
    
    # Apply translations
    success = 0
    for slug, fields in translated.items():
        res = col.update_one({"slug": slug}, {"$set": fields})
        if res.modified_count:
            success += 1
            print(f"  Updated {slug}: {fields}")
    
    print(f"\nUpdated {success} peptides")
    
    # Verify
    remaining = 0
    for pep in col.find({}, {"_id": 0, "slug": 1, "classification": 1, "evidence_level": 1, "half_life": 1}):
        for field in ["classification", "evidence_level", "half_life"]:
            val = pep.get(field, "")
            if val and any(w in val.lower() for w in PT_WORDS):
                remaining += 1
                print(f"  STILL PT: {pep['slug']}.{field} = {val}")
    print(f"Remaining PT metadata: {remaining}")


if __name__ == "__main__":
    asyncio.run(main())
