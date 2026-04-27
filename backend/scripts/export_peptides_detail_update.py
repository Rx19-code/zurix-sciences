"""
Export the 9 updated peptides (Ipamorelin, TB-500, Semax, Selank, KPV,
CJC-1295 DAC, Tesamorelin, BPC-157, GHK-Cu) to a seed JSON so they
can be applied to production DB.
"""
import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

UPDATED_SLUGS = [
    "ipamorelin",
    "tb-500",
    "semax",
    "selank",
    "kpv",
    "cjc-1295-dac",
    "tesamorelin",
    "bpc-157",
    "ghk-cu",
]


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    docs = await db.peptide_library.find(
        {"slug": {"$in": UPDATED_SLUGS}}, {"_id": 0}
    ).to_list(None)

    out_path = "/app/backend/seed_peptides_detail_update.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False, default=str)

    print(f"Exported {len(docs)} peptides to {out_path}")
    for d in docs:
        print(f"  - {d['name']} ({d['slug']})")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
