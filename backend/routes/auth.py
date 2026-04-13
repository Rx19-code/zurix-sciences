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
        }
    }
