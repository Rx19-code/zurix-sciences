"""
Update products:
- Rename "GSH Glutathione 1500mg" → "Glutathione 1500mg"
- Set image_url for Sermorelin 10mg, Glutathione 1500mg, DSIP 5mg

NOTE: Run on production server (where the PNG files exist in PRODUCT_IMG_DIR).
"""
import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


# Filenames stored locally in PRODUCT_IMG_DIR
# (You must upload these PNGs to that folder on the server before running.)
IMAGE_MAP = {
    "Sermorelin 10mg": "/api/images/products/sermorelin-10mg.png",
    "Glutathione 1500mg": "/api/images/products/glutathione-1500mg.png",
    "DSIP 5mg": "/api/images/products/dsip-5mg.png",
}


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    # 1) Rename GSH Glutathione 1500mg → Glutathione 1500mg
    res = await db.products.update_one(
        {"name": "GSH Glutathione 1500mg"},
        {"$set": {
            "name": "Glutathione 1500mg",
            "description": "Glutathione 1500mg - Master antioxidant tripeptide for laboratory research purposes only. Coming soon.",
        }},
    )
    if res.matched_count:
        print("RENAMED: 'GSH Glutathione 1500mg' -> 'Glutathione 1500mg'")
    else:
        print("SKIP rename: 'GSH Glutathione 1500mg' not found (already renamed?)")

    # 2) Set image_url for each product
    for name, image_url in IMAGE_MAP.items():
        r = await db.products.update_one(
            {"name": name},
            {"$set": {"image_url": image_url}},
        )
        if r.matched_count:
            print(f"IMAGE SET: {name} -> {image_url}")
        else:
            print(f"NOT FOUND: {name}")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
