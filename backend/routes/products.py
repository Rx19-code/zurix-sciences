from typing import List, Optional
from pathlib import Path
import uuid

from fastapi import APIRouter, HTTPException, Header, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from database import db, ADMIN_PASSWORD, PRODUCT_IMG_DIR, get_cache, set_cache, clear_cache
from models import Product, Representative, UpdateProductImageRequest

router = APIRouter(prefix="/api")


class ProductCreate(BaseModel):
    name: str
    category: str = "Research Peptides"
    product_type: str
    purity: str = "≥99% HPLC"
    dosage: str
    description: str = ""
    price: float = 0.0
    verification_code: str = ""
    storage_info: str = "Store lyophilized at -20°C. Stable 2-8°C for 30 days after reconstitution."
    batch_number: str = ""
    manufacturing_date: str = ""
    expiry_date: str = ""
    coa_url: str = ""
    featured: bool = False
    image_url: Optional[str] = None
    images: List[str] = []
    coming_soon: bool = False
    out_of_stock: bool = False


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    product_type: Optional[str] = None
    purity: Optional[str] = None
    dosage: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    verification_code: Optional[str] = None
    storage_info: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    coa_url: Optional[str] = None
    featured: Optional[bool] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    coming_soon: Optional[bool] = None
    out_of_stock: Optional[bool] = None


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


# ═══════════════════════════════════════════════════════════════════
#                    ADMIN PRODUCT CRUD
# ═══════════════════════════════════════════════════════════════════

def _slugify(name: str) -> str:
    """Convert product name to safe verification-code suffix."""
    import re
    s = re.sub(r"[^A-Za-z0-9]+", "", name).upper()
    return s[:10] or "PROD"


@router.post("/admin/products")
async def admin_create_product(payload: ProductCreate, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    existing = await db.products.find_one({"name": payload.name}, {"_id": 0, "id": 1})
    if existing:
        raise HTTPException(status_code=409, detail=f"Product '{payload.name}' already exists")

    doc = payload.model_dump()
    doc["id"] = str(uuid.uuid4())
    if not doc.get("verification_code"):
        doc["verification_code"] = f"ZX-{_slugify(payload.name)}"
    if not doc.get("batch_number"):
        doc["batch_number"] = f"ZX-{_slugify(payload.name)}-B01"

    await db.products.insert_one(doc)
    clear_cache("products:")
    clear_cache("product-types")
    doc.pop("_id", None)
    return {"success": True, "product": doc}


@router.put("/admin/products/{product_id}")
async def admin_update_product(product_id: str, payload: ProductUpdate, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.products.update_one({"id": product_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    clear_cache("products:")
    updated = await db.products.find_one({"id": product_id}, {"_id": 0})
    return {"success": True, "product": updated}


@router.delete("/admin/products/{product_id}")
async def admin_delete_product(product_id: str, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    clear_cache("products:")
    return {"success": True, "deleted": product_id}


@router.post("/admin/products/upload-image")
async def admin_upload_product_image(
    file: UploadFile = File(...),
    x_admin_password: str = Header(None),
):
    """Upload a single product image. Returns the public URL to use in Product.images."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    ALLOWED = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
    MAX_BYTES = 5 * 1024 * 1024  # 5 MB

    if file.content_type not in ALLOWED:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: JPEG, PNG, WEBP.",
        )

    contents = await file.read()
    if len(contents) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 5MB limit")

    ext = Path(file.filename or "").suffix.lower() or {
        "image/jpeg": ".jpg", "image/jpg": ".jpg",
        "image/png": ".png", "image/webp": ".webp",
    }.get(file.content_type, ".jpg")

    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = PRODUCT_IMG_DIR / safe_name
    dest.write_bytes(contents)

    public_url = f"/api/images/products/{safe_name}"
    return {
        "success": True,
        "url": public_url,
        "filename": safe_name,
        "size": len(contents),
        "content_type": file.content_type,
    }


@router.get("/admin/products/{product_id}/qr")
async def admin_product_qr(product_id: str, x_admin_password: str = Header(None)):
    """Generate a printable QR code (PNG, base64) for the product's verification_code."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    code = product.get("verification_code") or ""
    if not code:
        raise HTTPException(status_code=400, detail="Product has no verification_code")

    import io
    import base64
    import qrcode

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "product_id": product_id,
        "verification_code": code,
        "qr_image": f"data:image/png;base64,{b64}",
    }
