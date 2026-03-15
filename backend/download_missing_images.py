#!/usr/bin/env python3
"""
Download missing product images from customer-assets CDN and update MongoDB
"""
import asyncio
import urllib.request
import uuid
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
IMG_DIR = os.path.join(os.path.dirname(__file__), 'product_images')

# Mapping: product_name -> CDN URL from uploaded assets
MISSING_IMAGES = {
    "Tirzepatide 10mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/4h27962o_Tirzepatida-10mg.png",
    "Tirzepatide 15mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/16ilzmwr_Tirzepatida-15mg.png",
    "Tirzepatide 20mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/t41psoxk_Tirzepatida-20mg.png",
    "Semax 10mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/6chthxrv_Semax-10mg.png",
    "Selank 10mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/zlbk9h5a_Selank-10mg.png",
    "TB-500/thymosin beta 20mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/deye2haf_TB4-TB500-THYMOSIN-BETA-10mg.png",
    "HGH 10iu": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/owqq3xoo_HGH-10UI.png",
    "HGH 176-191 5mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/7xh4oapp_HGH-Frag-176-191.png",
    "IGF-1 LR3 1mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/l7wr5o13_IGF-1-LR3.png",
    "CJC1295 DAC 5mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/7t42wbdd_CJC-1295-DAC.png",
    "Tesamorelin + Ipamorelin Blend 5mg+5mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/lox01x82_Tesamorelin-%2B-Ipamorelin-5mg%2B5mg.png",
    "Ipamorelin 10mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/kawd60ms_Ipamorelin-10mg.png",
    "Tesamorelin 20mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/t61xd717_Tesamorelin-10mg.png",
    "Glow Blend 70mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/rhukgcb5_Glow-Blend-70mg.png",
    "BPC-157 10mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/deye2haf_TB4-TB500-THYMOSIN-BETA-10mg.png",
    "BPC157,TB4 Blend 5mg+5mg": "https://customer-assets.emergentagent.com/job_976eb93f-304b-4742-845a-2207484ddb78/artifacts/deye2haf_TB4-TB500-THYMOSIN-BETA-10mg.png",
}

async def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    success = 0
    failed = 0
    
    for product_name, url in MISSING_IMAGES.items():
        try:
            # Generate unique filename
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(IMG_DIR, filename)
            
            # Download image
            print(f"Downloading: {product_name}...")
            urllib.request.urlretrieve(url, filepath)
            
            # Verify file was downloaded
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                local_url = f"/api/images/products/{filename}"
                
                # Update MongoDB
                result = await db.products.update_one(
                    {"name": product_name},
                    {"$set": {"image_url": local_url}}
                )
                
                if result.modified_count > 0:
                    print(f"  OK: {product_name} -> {local_url} ({os.path.getsize(filepath)} bytes)")
                    success += 1
                else:
                    print(f"  WARN: Product '{product_name}' not found in DB")
                    failed += 1
            else:
                print(f"  FAIL: Download failed for {product_name}")
                failed += 1
                
        except Exception as e:
            print(f"  ERROR: {product_name} - {e}")
            failed += 1
    
    # Final report
    total_products = await db.products.count_documents({})
    with_images = await db.products.count_documents({"image_url": {"$ne": None, "$ne": ""}})
    without_images = await db.products.count_documents({"$or": [{"image_url": None}, {"image_url": ""}, {"image_url": {"$exists": False}}]})
    
    print(f"\n{'='*50}")
    print(f"RESULT: {success} updated, {failed} failed")
    print(f"DB: {total_products} total, {with_images} with images, {without_images} without images")
    print(f"{'='*50}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
