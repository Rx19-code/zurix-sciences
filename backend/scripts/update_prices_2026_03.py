"""
Bulk price update — Feb/Mar 2026 pricing review.
- Sets new prices for all listed products
- Clears coming_soon flag for products being activated
- Sets out_of_stock=True for Thymosin Alpha 5mg (no stock)
- Removes BPC-157 + TB-500 Blend 10mg+10mg from catalog
- Updates SLU-PP-332 to 250 mcg presentation

Run on production:
  cd /var/www/zurix/backend && python3 scripts/update_prices_2026_03.py
"""
import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from motor.motor_asyncio import AsyncIOMotorClient


# Mapping by product name → new pricing + flags
# Note: "clear_coming_soon" activates products that were marked Coming Soon
PRICE_UPDATES = [
    {"name": "HGH 10iu",                                "price": 56.00},
    {"name": "HGH 176-191 5mg",                         "price": 92.00},
    {"name": "IGF-1 LR3 1mg",                           "price": 130.00},
    {"name": "CJC1295 DAC 5mg",                         "price": 112.00},
    {"name": "Ipamorelin 10mg",                         "price": 115.00},
    {"name": "Tesamorelin 10mg",                        "price": 115.00},
    {"name": "Sermorelin 10mg",                         "price": 110.00, "clear_coming_soon": True},
    {"name": "CJC-1295 + Ipamorelin Blend 5mg+5mg",     "price": 120.00},
    {"name": "Tesamorelin + Ipamorelin Blend 5mg+5mg",  "price": 130.00},
    {"name": "Tirzepatide 10mg",                        "price": 30.00},
    {"name": "Tirzepatide 15mg",                        "price": 45.00},
    {"name": "Tirzepatide 20mg",                        "price": 60.00},
    {"name": "Tirzepatide 60mg",                        "price": 110.00},
    {"name": "Retatrutide 10mg",                        "price": 108.00},
    {"name": "Retatrutide 40mg",                        "price": 175.00},
    {"name": "AOD-9604 5mg",                            "price": 115.00},
    {"name": "5-Amino-1MQ 10mg",                        "price": 68.00},
    {"name": "BPC-157 10mg",                            "price": 115.00},
    {"name": "TB-500/thymosin beta 10mg",               "price": 118.00},
    {"name": "KPV 10mg",                                "price": 90.00},
    {"name": "Cartalax 20mg",                           "price": 95.00},
    {"name": "GHK-Cu 50mg",                             "price": 105.00},
    {"name": "GHK-Cu 100mg",                            "price": 150.00},
    {"name": "AHK-Cu 100mg",                            "price": 128.00},
    {"name": "Glow Blend 70mg",                         "price": 140.00},
    {"name": "Klow Blend 80mg",                         "price": 170.00},
    {"name": "GHK-Cu + KPV Blend 50mg+20mg",            "price": 170.00},
    {"name": "Semax 10mg",                              "price": 90.00},
    {"name": "Selank 10mg",                             "price": 90.00},
    {"name": "DSIP 5mg",                                "price": 70.00, "clear_coming_soon": True},
    {"name": "NAD+ 500mg",                              "price": 135.00},
    {"name": "Glutathione 1500mg",                      "price": 88.00, "clear_coming_soon": True},
    {"name": "kisspeptin 10mg",                         "price": 100.00},
    {"name": "Oxytocin 10mg",                           "price": 100.00},
    {"name": "PT141 10mg",                              "price": 100.00},
    {"name": "Bacteriostatic Water 3ml",                "price": 15.00},

    # Thymosin Alpha: no stock — keep visible but mark out_of_stock
    {"name": "Thymosin Alpha 5mg", "price": 0.00, "out_of_stock": True, "clear_coming_soon": True},

    # SLU-PP-332: renamed to 250mcg + price $60
    {
        "name": "SLU-PP-332 500mcg",
        "rename_to": "SLU-PP-332 250mcg",
        "new_dosage": "250mcg x 25 tablets",
        "price": 60.00,
        "clear_coming_soon": True,
    },
]

# Products to remove from catalog
PRODUCTS_TO_REMOVE = [
    "BPC-157 + TB-500 Blend 10mg+10mg",
]


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "zurix_sciences")
    if not mongo_url:
        print("ERROR: MONGO_URL not set in backend/.env")
        sys.exit(1)

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print("=" * 70)
    print("PRICE UPDATE — Feb/Mar 2026")
    print("=" * 70)

    updated = 0
    not_found = 0
    removed = 0
    skipped = 0

    # 1) Update prices and flags
    print("\n▶ Updating prices and flags:\n")
    for item in PRICE_UPDATES:
        name = item["name"]
        doc = await db.products.find_one({"name": name}, {"_id": 0, "id": 1, "name": 1, "price": 1, "coming_soon": 1})
        if not doc:
            print(f"  ❌ NOT FOUND: {name}")
            not_found += 1
            continue

        update_fields = {"price": item["price"]}
        if item.get("clear_coming_soon"):
            update_fields["coming_soon"] = False
        if item.get("out_of_stock"):
            update_fields["out_of_stock"] = True
        else:
            update_fields["out_of_stock"] = False
        if item.get("rename_to"):
            update_fields["name"] = item["rename_to"]
        if item.get("new_dosage"):
            update_fields["dosage"] = item["new_dosage"]

        old_price = doc.get("price", 0)
        old_cs = doc.get("coming_soon", False)
        await db.products.update_one({"name": name}, {"$set": update_fields})

        flags = []
        if item.get("clear_coming_soon") and old_cs:
            flags.append("✓ activated")
        if item.get("out_of_stock"):
            flags.append("✗ out of stock")
        if item.get("rename_to"):
            flags.append(f'→ "{item["rename_to"]}"')

        flag_str = "  ".join(flags)
        new_name = item.get("rename_to") or name
        print(f"  ✓ {new_name:48}  ${old_price:>7.2f} → ${item['price']:>7.2f}  {flag_str}")
        updated += 1

    # 2) Remove products
    print("\n▶ Removing products from catalog:\n")
    for name in PRODUCTS_TO_REMOVE:
        result = await db.products.delete_one({"name": name})
        if result.deleted_count:
            print(f"  ✗ REMOVED: {name}")
            removed += 1
        else:
            print(f"  ⚠ Not found (already removed?): {name}")
            skipped += 1

    print("\n" + "=" * 70)
    print(f"Done. Updated: {updated} | Removed: {removed} | Not found: {not_found} | Skipped: {skipped}")
    print("=" * 70)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
