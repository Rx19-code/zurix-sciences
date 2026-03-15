from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse

from database import db, ADMIN_PASSWORD, PRODUCT_IMG_DIR, get_cache, set_cache
from models import Product, Representative, UpdateProductImageRequest

router = APIRouter(prefix="/api")


@router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    product_type: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None
):
    cache_key = f"products:{category}:{product_type}:{search}:{featured}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    query = {}
    if category:
        query['category'] = category
    if product_type:
        query['product_type'] = product_type
    if featured is not None:
        query['featured'] = featured
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'product_type': {'$regex': search, '$options': 'i'}}
        ]

    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    set_cache(cache_key, products)
    return products


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/code/{verification_code}", response_model=Product)
async def get_product_by_code(verification_code: str):
    product = await db.products.find_one({"verification_code": verification_code}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/categories")
async def get_categories():
    categories = await db.products.distinct("category")
    return {"categories": categories}


@router.get("/images/products/{filename}")
async def serve_product_image(filename: str):
    safe_filename = Path(filename).name
    file_path = PRODUCT_IMG_DIR / safe_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"}
    )


@router.get("/product-types")
async def get_product_types():
    types = await db.products.distinct("product_type")
    return {"types": sorted(types)}


@router.put("/admin/products/update-image")
async def update_product_image(request: UpdateProductImageRequest, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.products.update_one(
        {"name": request.product_name},
        {"$set": {"image_url": request.image_url}}
    )

    if result.matched_count == 0:
        result = await db.products.update_one(
            {"name": {"$regex": request.product_name, "$options": "i"}},
            {"$set": {"image_url": request.image_url}}
        )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Product '{request.product_name}' not found")

    return {
        "success": True,
        "message": f"Image updated for '{request.product_name}'",
        "image_url": request.image_url
    }


@router.get("/representatives", response_model=List[Representative])
async def get_representatives():
    reps = await db.representatives.find({}, {"_id": 0}).to_list(100)
    return reps
