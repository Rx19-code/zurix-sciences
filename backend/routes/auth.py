import logging
import uuid
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import APIRouter, Request, Depends, HTTPException, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import db, JWT_SECRET, JWT_ALGORITHM
from models import UserRegisterRequest, UserLoginRequest
from utils.security import hash_password, verify_password, create_jwt_token, get_current_user

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)

EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"


@router.post("/auth/register")
@limiter.limit("5/minute")
async def register_user(request: Request, body: UserRegisterRequest):
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "id": str(uuid.uuid4()),
        "email": body.email.lower(),
        "password_hash": hash_password(body.password),
        "name": body.name,
        "auth_provider": "email",
        "has_lifetime_access": False,
        "payment_id": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.users.insert_one(user)
    token = create_jwt_token(user["id"], user["email"])

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "has_lifetime_access": False,
            "auth_provider": "email",
            "unlocked_slugs": [],
        }
    }


@router.post("/auth/login")
@limiter.limit("10/minute")
async def login_user(request: Request, body: UserLoginRequest):
    user = await db.users.find_one({"email": body.email.lower()}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="This account uses Google login. Please sign in with Google.")

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt_token(user["id"], user["email"])

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "has_lifetime_access": user.get("has_lifetime_access", False),
            "auth_provider": user.get("auth_provider", "email"),
            "unlocked_slugs": user.get("unlocked_slugs", []),
        }
    }


@router.post("/auth/google")
async def google_auth(request: Request):
    """Exchange Emergent Auth session_id for user data and JWT token."""
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            EMERGENT_AUTH_URL,
            headers={"X-Session-ID": session_id}
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google session")

    gdata = resp.json()
    email = gdata.get("email", "").lower()
    name = gdata.get("name", "")
    picture = gdata.get("picture", "")

    if not email:
        raise HTTPException(status_code=400, detail="No email from Google")

    existing = await db.users.find_one({"email": email}, {"_id": 0})

    if existing:
        await db.users.update_one(
            {"email": email},
            {"$set": {"name": name, "picture": picture, "last_login": datetime.now(timezone.utc).isoformat()}}
        )
        user_id = existing["id"]
        has_access = existing.get("has_lifetime_access", False)
    else:
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "auth_provider": "google",
            "has_lifetime_access": False,
            "payment_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(user)
        has_access = False

    token = create_jwt_token(user_id, email)

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user_id,
            "email": email,
            "name": name,
            "has_lifetime_access": has_access,
            "auth_provider": "google",
            "unlocked_slugs": existing.get("unlocked_slugs", []) if existing else [],
        }
    }


@router.get("/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "has_lifetime_access": user.get("has_lifetime_access", False),
            "auth_provider": user.get("auth_provider", "email"),
            "unlocked_slugs": user.get("unlocked_slugs", []),
        }
    }


@router.post("/auth/unlock-protocol")
async def unlock_protocol_with_code(request: Request, user: dict = Depends(get_current_user)):
    """Unlock a peptide protocol using a product QR code."""
    body = await request.json()
    code = body.get("code", "").strip().upper()

    if not code:
        raise HTTPException(status_code=400, detail="Code is required")

    # Master code — grants lifetime access
    MASTER_CODE = "ZX050217080225"
    if code == MASTER_CODE:
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"has_lifetime_access": True}}
        )
        return {
            "success": True,
            "message": "Full access granted!",
            "slug": "all",
            "unlocked_slugs": ["all"],
        }

    # Find the code in unique_codes
    unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})
    db_code = code
    if not unique_code:
        code_no_hyphens = code.replace("-", "")
        all_codes = await db.unique_codes.find({}, {"_id": 0}).to_list(None)
        for c in all_codes:
            if c["code"].replace("-", "").upper() == code_no_hyphens:
                unique_code = c
                db_code = c["code"]
                break

    if not unique_code:
        raise HTTPException(status_code=404, detail="Code not found. Please check the code and try again.")

    # Map product name to peptide slug
    product_name = unique_code.get("product_name", "")
    slug = await _find_slug_for_product(product_name)

    if not slug:
        raise HTTPException(status_code=404, detail="Could not match this product to a protocol.")

    # Add slug to user's unlocked list
    current_slugs = user.get("unlocked_slugs", [])
    if slug not in current_slugs:
        current_slugs.append(slug)
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"unlocked_slugs": current_slugs}}
        )

    peptide = await db.peptide_library.find_one({"slug": slug}, {"_id": 0, "name": 1, "slug": 1})

    return {
        "success": True,
        "message": f"Protocol unlocked: {peptide['name'] if peptide else slug}",
        "slug": slug,
        "unlocked_slugs": current_slugs,
    }


async def _find_slug_for_product(product_name: str) -> str:
    """Map a product name to a peptide library slug."""
    pn = product_name.lower().strip()

    PRODUCT_SLUG_MAP = {
        "5-amino-1mq": "5-amino-1mq",
        "ahk-cu": "ahk-cu",
        "aod-9604": "aod-9604",
        "bpc-157": "bpc-157",
        "bpc-157 + tb4": "bpc-157",
        "bacteriostatic water": "bacteriostatic-water",
        "cjc-1295": "cjc-1295-dac",
        "cjc1295": "cjc-1295-dac",
        "cartalax": "cartalax",
        "ghk-cu": "ghk-cu",
        "glow blend": "ghk-cu",
        "hgh": "hgh-fragment-176-191",
        "igf-1": "igf-1-lr3",
        "ipamorelin": "ipamorelin",
        "kisspeptin": "kisspeptin",
        "kpv": "kpv",
        "klow": "kpv",
        "mots-c": "mots-c",
        "nad+": "nad-plus-",
        "oxytocin": "oxytocin",
        "pt141": "pt-141",
        "pt-141": "pt-141",
        "retatrutide": "retatrutide",
        "selank": "selank",
        "semax": "semax",
        "tb-500": "tb-500",
        "thymosin": "tb-500",
        "tesamorelin": "tesamorelin",
        "tirzepatide": "tirzepatide",
    }

    for key, slug in PRODUCT_SLUG_MAP.items():
        if key in pn:
            return slug

    return ""
