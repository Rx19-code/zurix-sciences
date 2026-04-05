from fastapi import APIRouter, Query
from database import db
from typing import Optional

router = APIRouter()

LIBRARY_PROJECTION = {
    "_id": 0,
    "slug": 1,
    "name": 1,
    "description": 1,
    "category": 1,
    "is_free": 1,
    "presentations": 1,
    "also_known_as": 1,
}

DETAIL_PROJECTION = {"_id": 0}


@router.get("/api/library")
async def get_library(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    free_only: Optional[bool] = Query(None),
):
    query = {}
    if category and category != "All":
        query["category"] = category
    if free_only:
        query["is_free"] = True
    if search:
        query["name"] = {"$regex": search, "$options": "i"}

    peptides = await db.peptide_library.find(query, LIBRARY_PROJECTION).sort("name", 1).to_list(200)
    categories = await db.peptide_library.distinct("category")
    return {"peptides": peptides, "categories": sorted(categories), "total": len(peptides)}


@router.get("/api/library/{slug}")
async def get_peptide_detail(slug: str):
    peptide = await db.peptide_library.find_one({"slug": slug}, DETAIL_PROJECTION)
    if not peptide:
        return {"error": "Peptide not found"}, 404
    return peptide
