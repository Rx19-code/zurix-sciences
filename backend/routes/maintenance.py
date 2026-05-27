"""Maintenance mode endpoints.

Toggle: presence of MAINTENANCE_FLAG_FILE (touch/rm).
Bypass: cookie `maintenance_bypass` matching MAINTENANCE_BYPASS_KEY.
"""
import os
from fastapi import APIRouter, Request, Response, HTTPException, Header

from database import MAINTENANCE_FLAG_FILE, MAINTENANCE_BYPASS_KEY

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

router = APIRouter(prefix="/api/maintenance")


def is_maintenance_active() -> bool:
    return os.path.exists(MAINTENANCE_FLAG_FILE)


def has_bypass(request: Request) -> bool:
    return request.cookies.get("maintenance_bypass") == MAINTENANCE_BYPASS_KEY


@router.get("/status")
async def status(request: Request):
    """Returns whether maintenance mode is active and whether this client has bypass."""
    return {
        "active": is_maintenance_active(),
        "bypass": has_bypass(request),
    }


@router.post("/bypass")
async def bypass(request: Request, response: Response):
    """Provide the bypass key to receive a cookie that lets you see the site normally during maintenance."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    key = (body.get("key") or "").strip()
    if not key or key != MAINTENANCE_BYPASS_KEY:
        raise HTTPException(status_code=401, detail="Invalid bypass key")
    response.set_cookie(
        key="maintenance_bypass",
        value=MAINTENANCE_BYPASS_KEY,
        max_age=24 * 3600,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"success": True}


@router.post("/toggle")
async def toggle(request: Request, x_admin_password: str = Header(None)):
    """Admin-only: turn maintenance mode on/off."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        body = await request.json()
    except Exception:
        body = {}
    activate = bool(body.get("active", False))
    if activate:
        with open(MAINTENANCE_FLAG_FILE, "w") as f:
            f.write("1")
    else:
        if os.path.exists(MAINTENANCE_FLAG_FILE):
            os.remove(MAINTENANCE_FLAG_FILE)
    return {"success": True, "active": is_maintenance_active()}
