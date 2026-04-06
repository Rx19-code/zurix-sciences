"""
Phase 2: Translate all Portuguese content to English using GPT-4o-mini.
Processes 21 peptides with PT text in overview, protocols, research, synergy fields.
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

SYSTEM_PROMPT = """You are a professional scientific translator specializing in peptide and pharmaceutical research.
Your task is to translate Portuguese text to English while:
1. Maintaining scientific accuracy and proper terminology
2. Keeping all numerical values, units (mg, mcg, IU), and dosages EXACTLY as they are
3. Keeping proper nouns (drug names, peptide names) unchanged
4. Converting Portuguese medical terms to their standard English equivalents
5. Cleaning up any garbled text or PDF extraction artifacts (random characters, broken words)
6. Removing any references to competitor websites or brands

You will receive a JSON object with the peptide's text fields. Return ONLY a valid JSON object with the same structure but translated to English. Do not add any markdown formatting, code blocks, or explanations."""


async def translate_peptide(pep_data, slug):
    """Translate a single peptide's text fields."""
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"translate-{slug}",
        system_message=SYSTEM_PROMPT,
    )
    chat.with_model("openai", "gpt-4o-mini")

    # Build the text payload to translate
    fields_to_translate = {}
    
    if pep_data.get("overview"):
        fields_to_translate["overview"] = pep_data["overview"]
    
    if pep_data.get("protocols"):
        pr = pep_data["protocols"]
        proto = {}
        if pr.get("title"):
            proto["title"] = pr["title"]
        if pr.get("dosages"):
            proto["dosages"] = pr["dosages"]
        if pr.get("phases"):
            proto["phases"] = pr["phases"]
        if pr.get("reconstitution_steps"):
            proto["reconstitution_steps"] = pr["reconstitution_steps"]
        if pr.get("reconstitution"):
            proto["reconstitution"] = pr["reconstitution"]
        if proto:
            fields_to_translate["protocols"] = proto
    
    if pep_data.get("research"):
        fields_to_translate["research"] = pep_data["research"]
    
    if pep_data.get("synergy"):
        fields_to_translate["synergy"] = pep_data["synergy"]

    if pep_data.get("also_known_as"):
        fields_to_translate["also_known_as"] = pep_data["also_known_as"]

    payload = json.dumps(fields_to_translate, ensure_ascii=False)
    
    msg = UserMessage(
        text=f"Translate the following peptide data from Portuguese to English. Keep the exact same JSON structure. Return ONLY valid JSON:\n\n{payload}"
    )
    
    response = await chat.send_message(msg)
    
    # Parse the response - strip any markdown code block markers
    resp_text = response.strip()
    if resp_text.startswith("```"):
        resp_text = resp_text.split("\n", 1)[1] if "\n" in resp_text else resp_text[3:]
    if resp_text.endswith("```"):
        resp_text = resp_text[:-3]
    resp_text = resp_text.strip()
    
    translated = json.loads(resp_text)
    return translated


async def main():
    # Find peptides with Portuguese content
    PT_INDICATORS = ["é ", "ão ", "ção", "mente ", "uma ", "para ", "com ", "dos ", "das "]
    
    peptides_to_translate = []
    for pep in col.find({}, {"_id": 0}):
        text = json.dumps(pep, default=str, ensure_ascii=False)
        pt_count = sum(1 for ind in PT_INDICATORS if ind in text)
        if pt_count >= 2:
            peptides_to_translate.append(pep)
    
    print(f"Found {len(peptides_to_translate)} peptides to translate\n")
    
    success = 0
    failed = []
    
    for i, pep in enumerate(peptides_to_translate):
        slug = pep["slug"]
        print(f"[{i+1}/{len(peptides_to_translate)}] Translating {slug}...", end=" ", flush=True)
        
        try:
            translated = await translate_peptide(pep, slug)
            
            # Build update dict
            updates = {}
            if "overview" in translated:
                updates["overview"] = translated["overview"]
            if "protocols" in translated:
                # Merge translated protocol fields into existing protocol
                existing_proto = pep.get("protocols", {})
                for key, val in translated["protocols"].items():
                    existing_proto[key] = val
                updates["protocols"] = existing_proto
            if "research" in translated:
                updates["research"] = translated["research"]
            if "synergy" in translated:
                updates["synergy"] = translated["synergy"]
            if "also_known_as" in translated:
                updates["also_known_as"] = translated["also_known_as"]
            
            if updates:
                col.update_one({"slug": slug}, {"$set": updates})
                success += 1
                print("OK")
            else:
                print("No changes")
        except Exception as e:
            failed.append(slug)
            print(f"FAILED: {e}")
    
    print(f"\n=== Translation Complete ===")
    print(f"Success: {success}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed slugs: {failed}")
    
    # Verify - check for remaining Portuguese
    remaining_pt = 0
    for pep in col.find({}, {"_id": 0, "slug": 1, "overview": 1}):
        ov = pep.get("overview", {})
        if isinstance(ov, dict):
            text = ov.get("what_is", "") + " " + ov.get("mechanism_summary", "")
            pt_count = sum(1 for ind in PT_INDICATORS if ind in text)
            if pt_count >= 2:
                remaining_pt += 1
                print(f"  Still PT: {pep['slug']}")
    print(f"Remaining with Portuguese overview: {remaining_pt}")


if __name__ == "__main__":
    asyncio.run(main())
