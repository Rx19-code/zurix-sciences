"""
Add `duration` to each AOD-9604 hub protocol.
Durations were provided by the user.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

DURATIONS = {
    "Beginner Fat Loss Stack": "4\u20136 weeks",
    "Rapid Cut Stack": "3\u20134 weeks",
    "Keto Fat Adaptation Stack": "6\u20138 weeks",
    "Women's Hormonal Shred Stack": "6\u20138 weeks",
    "Visceral Fat & Insulin Reset Stack": "8\u201312 weeks",
    "Recomp & Lean Physique Stack": "8\u201312 weeks",
    "Busy Lifestyle Fat Loss Stack": "8\u201312 weeks",
    "Appetite Control Stack": "6\u20138 weeks",
    "Athletic Conditioning Stack": "4\u20136 weeks",
    "Recovery & Metabolic Reset Stack": "4 weeks",
    "Fasted Morning GH Burn Stack": "4\u20136 weeks",
    "Anti-Bloat & Dry Look Stack": "2\u20133 weeks",
    "Long-Term Sustainable Cut Stack": "12\u201316 weeks",
    "Shift Worker Metabolic Stack": "8\u201312 weeks",
    "Ultra-Lean Stage Prep Stack": "2\u20134 weeks",
}


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    hub = await db.stack_hubs.find_one({"slug": "aod-9604"}, {"_id": 0})
    if not hub:
        print("Hub aod-9604 not found")
        return

    for p in hub["protocols"]:
        d = DURATIONS.get(p["name"])
        if d:
            p["duration"] = d

    await db.stack_hubs.update_one({"slug": "aod-9604"}, {"$set": {"protocols": hub["protocols"]}})
    updated = sum(1 for p in hub["protocols"] if p.get("duration"))
    print(f"Updated {updated}/{len(hub['protocols'])} protocols with duration")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
