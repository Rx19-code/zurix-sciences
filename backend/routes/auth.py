import logging
import secrets
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import db
from models import UserRegisterRequest, UserLoginRequest, PasswordResetRequest, PasswordResetConfirm
from utils.security import hash_password, verify_password, create_jwt_token, get_current_user

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)


@router.post("/auth/register")
@limiter.limit("5/minute")
async def register_user(request: Request, body: UserRegisterRequest):
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "id": str(uuid.uuid4()),
        "email": body.email.lower(),
        "password_hash": hash_password(body.password),
        "name": body.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purchased_protocols": [],
        "verification_history": []
    }

    await db.users.insert_one(user)
    token = create_jwt_token(user["id"], user["email"])

    return {
        "success": True,
        "message": "Registration successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"],
            "purchased_protocols": []
        }
    }


@router.post("/auth/login")
@limiter.limit("10/minute")
async def login_user(request: Request, body: UserLoginRequest):
    from fastapi import HTTPException
    user = await db.users.find_one({"email": body.email.lower()})
    if not user:
        logging.warning(f"Failed login attempt for email: {body.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt_token(user["id"], user["email"])

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"],
            "purchased_protocols": user.get("purchased_protocols", [])
        }
    }


@router.get("/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    return {"success": True, "user": user}


@router.post("/auth/request-password-reset")
@limiter.limit("3/minute")
async def request_password_reset(request: Request, body: PasswordResetRequest):
    user = await db.users.find_one({"email": body.email.lower()})
    if not user:
        return {"success": True, "message": "If the email exists, a reset link will be sent"}

    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    await db.password_resets.insert_one({
        "user_id": user["id"],
        "token": reset_token,
        "expires_at": expires_at.isoformat(),
        "used": False
    })

    return {
        "success": True,
        "message": "Password reset requested",
        "reset_token": reset_token
    }


@router.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm):
    from fastapi import HTTPException
    reset = await db.password_resets.find_one({"token": request.token, "used": False})

    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    expires_at = datetime.fromisoformat(reset["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Reset token expired")

    new_hash = hash_password(request.new_password)
    await db.users.update_one(
        {"id": reset["user_id"]},
        {"$set": {"password_hash": new_hash}}
    )

    await db.password_resets.update_one(
        {"token": request.token},
        {"$set": {"used": True}}
    )

    return {"success": True, "message": "Password reset successful"}
