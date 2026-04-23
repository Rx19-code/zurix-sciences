from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from database import db
from typing import Optional

router = APIRouter()

CATEGORY_IMG_DIR = Path(__file__).resolve().parent.parent / "product_images" / "categories"

CATEGORY_IMAGE_MAP = {
    "Nootropic / Cognitive": "nootropic.jpg",
    "Recovery": "recovery.jpg",
    "Anti-aging": "antiaging.jpg",
    "Aesthetics / Skin": "skin.jpg",
    "GH / Secretagogues": "molecule.jpg",
    "Weight Loss / GLP-1": "metabolism.jpg",
    "Metabolism": "metabolism.jpg",
    "Hormonal / Sexual Health": "hormone.jpg",
    "Immunity": "immunity.jpg",
    "Bioregulators": "molecule.jpg",
    "Diluents": "molecule.jpg",
}


@router.get("/api/library/category-image/{category_slug}")
async def get_category_image(category_slug: str):
    # Map slug back to filename
    slug_to_file = {k.lower().replace(" / ", "-").replace(" ", "-"): v for k, v in CATEGORY_IMAGE_MAP.items()}
    filename = slug_to_file.get(category_slug, "molecule.jpg")
    filepath = CATEGORY_IMG_DIR / filename
    if filepath.exists():
        return FileResponse(filepath, media_type="image/jpeg")
    # Fallback
    fallback = CATEGORY_IMG_DIR / "molecule.jpg"
    if fallback.exists():
        return FileResponse(fallback, media_type="image/jpeg")
    return {"error": "Image not found"}

LIBRARY_PROJECTION = {
    "_id": 0,
    "slug": 1,
    "name": 1,
    "description": 1,
    "category": 1,
    "is_free": 1,
    "presentations": 1,
    "also_known_as": 1,
    "classification": 1,
    "evidence_level": 1,
}

DETAIL_PROJECTION = {"_id": 0}


@router.get("/api/library")
async def get_library(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    free_only: Optional[bool] = Query(None),
):
    query = {"has_product": True}
    if category and category != "All":
        query["category"] = category
    if free_only:
        query["is_free"] = True
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    peptides = await db.peptide_library.find(query, LIBRARY_PROJECTION).sort("name", 1).to_list(200)
    categories = await db.peptide_library.distinct("category", {"has_product": True})
    return {"peptides": peptides, "categories": sorted(categories), "total": len(peptides)}


@router.get("/api/library/{slug}")
async def get_peptide_detail(slug: str):
    peptide = await db.peptide_library.find_one({"slug": slug}, DETAIL_PROJECTION)
    if not peptide:
        return {"error": "Peptide not found"}
    return peptide


# ═══════════ STACKS API ═══════════

STACK_LIST_PROJECTION = {
    "_id": 0,
    "id": 1,
    "slug": 1,
    "name": 1,
    "category": 1,
    "goal": 1,
    "peptides": 1,
    "is_free": 1,
}

STACK_DETAIL_PROJECTION = {"_id": 0}


@router.get("/api/stacks")
async def get_stacks(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    query = {}
    if category and category != "All":
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    stacks = await db.peptide_stacks.find(query, STACK_LIST_PROJECTION).sort("name", 1).to_list(200)
    categories = await db.peptide_stacks.distinct("category")
    return {"stacks": stacks, "categories": sorted(categories), "total": len(stacks)}


@router.get("/api/stacks/{slug}")
async def get_stack_detail(slug: str):
    stack = await db.peptide_stacks.find_one({"slug": slug}, STACK_DETAIL_PROJECTION)
    if not stack:
        return {"error": "Stack not found"}
    return stack
