"""
Generate protocol data for 62 peptides missing dosage/phase/reconstitution info.
Uses GPT-4o-mini to create accurate, research-based protocol data.
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

SYSTEM_PROMPT = """You are a peptide research protocol expert. Generate accurate protocol data for a research peptide.
Return ONLY valid JSON with this exact structure:
{
  "dosages": [
    {"indication": "Primary use case", "schedule": "Route and frequency", "dose": "Amount with units"}
  ],
  "phases": [
    {"number": 1, "phase": "Week range or description", "dose": "Amount with units"}
  ],
  "reconstitution_steps": [
    "Step 1 text",
    "Step 2 text"
  ]
}

Rules:
- Use standard research dosages from published literature
- Include 2-4 dosage indications
- Include 3-5 titration phases if applicable (omit if single-dose protocol)
- Include 4-6 reconstitution steps
- All in English
- Use mcg, mg, IU as appropriate
- For blends, include dosages for each component
- For non-injectable items (bacteriostatic water, sodium chloride), use appropriate handling steps
- Do NOT add markdown or explanations, ONLY JSON"""


async def generate_protocol(name, category, description, existing_protocol):
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"proto-{name[:20]}",
        system_message=SYSTEM_PROMPT,
    )
    chat.with_model("openai", "gpt-4o-mini")

    route = existing_protocol.get("standard", {}).get("route", "")
    freq = existing_protocol.get("standard", {}).get("frequency", "")
    recon = existing_protocol.get("reconstitution", "")

    prompt = f"""Generate research protocol data for:
Peptide: {name}
Category: {category}
Description: {description}
Known route: {route}
Known frequency: {freq}
Known reconstitution note: {recon}

Return ONLY valid JSON."""

    msg = UserMessage(text=prompt)
    response = await chat.send_message(msg)

    resp_text = response.strip()
    if resp_text.startswith("```"):
        resp_text = resp_text.split("\n", 1)[1] if "\n" in resp_text else resp_text[3:]
    if resp_text.endswith("```"):
        resp_text = resp_text[:-3]

    return json.loads(resp_text.strip())


async def main():
    # Find peptides missing protocol details
    missing = []
    for pep in col.find({}, {"_id": 0, "slug": 1, "name": 1, "category": 1, "description": 1, "protocols": 1}):
        pr = pep.get("protocols", {}) or {}
        has_d = len(pr.get("dosages", []) or []) > 0
        has_p = len(pr.get("phases", []) or []) > 0
        has_s = len(pr.get("reconstitution_steps", []) or []) > 0
        if not has_d and not has_p and not has_s:
            missing.append(pep)

    print(f"Found {len(missing)} peptides missing protocol data\n")

    success = 0
    failed = []

    for i, pep in enumerate(missing):
        slug = pep["slug"]
        name = pep["name"]
        print(f"[{i+1}/{len(missing)}] {name}...", end=" ", flush=True)

        try:
            data = await generate_protocol(
                name,
                pep.get("category", ""),
                pep.get("description", ""),
                pep.get("protocols", {}) or {}
            )

            updates = {}
            if data.get("dosages"):
                updates["protocols.dosages"] = data["dosages"]
            if data.get("phases"):
                updates["protocols.phases"] = data["phases"]
            if data.get("reconstitution_steps"):
                updates["protocols.reconstitution_steps"] = data["reconstitution_steps"]

            if updates:
                col.update_one({"slug": slug}, {"$set": updates})
                success += 1
                nd = len(data.get("dosages", []))
                np = len(data.get("phases", []))
                ns = len(data.get("reconstitution_steps", []))
                print(f"OK ({nd}d {np}p {ns}s)")
            else:
                print("No data")
        except Exception as e:
            failed.append(name)
            print(f"FAILED: {e}")

    print(f"\n=== Complete ===")
    print(f"Success: {success}")
    print(f"Failed: {len(failed)}")
    if failed:
        print(f"Failed: {failed}")


if __name__ == "__main__":
    asyncio.run(main())
