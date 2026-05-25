from pathlib import Path

from fastapi import APIRouter, Query, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from database import db
from typing import Optional
from utils.security import get_current_user
from datetime import datetime, timezone

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


# ════════════════════════ LEGACY STACKS (kept for backward compat — empty now) ════════════════════════
@router.get("/api/stacks")
async def get_stacks_legacy():
    """Legacy endpoint — returns empty list. Use /api/hubs instead."""
    return {"stacks": [], "categories": [], "total": 0, "deprecated": True}


# ════════════════════════ STACK HUBS (new architecture) ════════════════════════
HUB_LIST_PROJECTION = {
    "_id": 0,
    "slug": 1,
    "peptide_slug": 1,
    "peptide_name": 1,
    "title": 1,
    "subtitle": 1,
    "description": 1,
    "protocols_count": {"$size": {"$ifNull": ["$protocols", []]}},
}


@router.get("/api/hubs")
async def list_stack_hubs(search: Optional[str] = Query(None)):
    """List all stack hubs (one hub per peptide, each containing N protocols)."""
    pipeline = []
    if search:
        pipeline.append({
            "$match": {"$or": [
                {"peptide_name": {"$regex": search, "$options": "i"}},
                {"title": {"$regex": search, "$options": "i"}},
            ]}
        })
    pipeline.append({"$project": HUB_LIST_PROJECTION})
    pipeline.append({"$sort": {"peptide_name": 1}})
    hubs = await db.stack_hubs.aggregate(pipeline).to_list(200)
    return {"hubs": hubs, "total": len(hubs)}


async def _attach_ratings(hub: dict):
    """Compute avg rating and rating_count per protocol within the hub."""
    if not hub or "protocols" not in hub:
        return hub
    slug = hub.get("slug")
    pipeline = [
        {"$match": {"hub_slug": slug}},
        {"$group": {
            "_id": "$protocol_id",
            "avg": {"$avg": "$stars"},
            "count": {"$sum": 1},
        }},
    ]
    agg = await db.protocol_ratings.aggregate(pipeline).to_list(None)
    by_pid = {a["_id"]: a for a in agg}
    for p in hub["protocols"]:
        pid = p.get("id")
        r = by_pid.get(pid)
        p["rating_avg"] = round(r["avg"], 1) if r else 0.0
        p["rating_count"] = r["count"] if r else 0
    return hub


@router.get("/api/hubs/{slug}")
async def get_stack_hub(slug: str):
    hub = await db.stack_hubs.find_one({"slug": slug}, STACK_DETAIL_PROJECTION)
    if not hub:
        return {"error": "Hub not found"}
    return await _attach_ratings(hub)


@router.post("/api/hubs/{slug}/protocols/{protocol_id}/rate")
async def rate_protocol(slug: str, protocol_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Submit a 1-5 star rating for a protocol within a hub."""
    body = await request.json()
    stars = body.get("stars")
    if not isinstance(stars, int) or stars < 1 or stars > 5:
        raise HTTPException(status_code=400, detail="Stars must be an integer 1-5")

    hub = await db.stack_hubs.find_one({"slug": slug}, {"_id": 0, "protocols.id": 1})
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    if not any(p.get("id") == protocol_id for p in hub.get("protocols", [])):
        raise HTTPException(status_code=404, detail="Protocol not found in hub")

    # Upsert rating (one per user per protocol)
    now = datetime.now(timezone.utc).isoformat()
    await db.protocol_ratings.update_one(
        {"user_id": user["id"], "hub_slug": slug, "protocol_id": protocol_id},
        {
            "$set": {"stars": stars, "updated_at": now},
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )

    # Return updated aggregate for this protocol
    agg = await db.protocol_ratings.aggregate([
        {"$match": {"hub_slug": slug, "protocol_id": protocol_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$stars"}, "count": {"$sum": 1}}},
    ]).to_list(1)
    a = agg[0] if agg else {"avg": stars, "count": 1}
    return {"success": True, "rating_avg": round(a["avg"], 1), "rating_count": a["count"], "your_rating": stars}


@router.get("/api/hubs/{slug}/protocols/{protocol_id}/my-rating")
async def get_my_rating(slug: str, protocol_id: str, user: dict = Depends(get_current_user)):
    r = await db.protocol_ratings.find_one(
        {"user_id": user["id"], "hub_slug": slug, "protocol_id": protocol_id},
        {"_id": 0, "stars": 1},
    )
    return {"your_rating": r["stars"] if r else 0}
