"""
Activate 5 peptides on /protocols page:
- Glutathione, DSIP, Sermorelin, SLU-PP-332, HGH
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    # Normalize SLU-PP-332 capitalization
    await db.peptide_library.update_one(
        {"slug": "slu-pp-332"},
        {"$set": {"name": "SLU-PP-332"}},
    )

    slugs = ["glutathione", "dsip", "sermorelin", "slu-pp-332", "hgh"]
    res = await db.peptide_library.update_many(
        {"slug": {"$in": slugs}},
        {"$set": {"has_product": True}},
    )
    print(f"Activated {res.modified_count} peptides ({slugs})")

    visible = await db.peptide_library.count_documents({"has_product": True})
    print(f"Total visible on /protocols: {visible}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
