import logging
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Depends, Request

from database import db, NOWPAYMENTS_API_KEY, LIFETIME_ACCESS_PRICE
from utils.security import get_current_user

router = APIRouter(prefix="/api")

NOWPAYMENTS_API = "https://api.nowpayments.io/v1"


@router.post("/payment/create-invoice")
async def create_lifetime_invoice(request: Request, user: dict = Depends(get_current_user)):
    """Create a NOWPayments invoice for lifetime access."""
    if user.get("has_lifetime_access"):
        return {"success": True, "already_paid": True, "message": "You already have lifetime access."}

    order_id = f"LTA-{uuid.uuid4().hex[:12].upper()}"

    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}

    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}

    payload = {
        "price_amount": LIFETIME_ACCESS_PRICE,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "order_id": order_id,
        "order_description": "Zurix Sciences - Lifetime Protocol Access",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{NOWPAYMENTS_API}/payment", json=payload, headers=headers)

    if resp.status_code not in (200, 201):
        logging.error(f"NOWPayments error: {resp.status_code} {resp.text}")
        raise HTTPException(status_code=502, detail="Payment gateway error. Try again.")

    np_data = resp.json()

    order = {
        "order_id": order_id,
        "user_id": user["id"],
        "user_email": user["email"],
        "np_payment_id": np_data.get("payment_id"),
        "price": LIFETIME_ACCESS_PRICE,
        "pay_amount": np_data.get("pay_amount"),
        "pay_currency": np_data.get("pay_currency", "usdttrc20"),
        "pay_address": np_data.get("pay_address"),
        "status": np_data.get("payment_status", "waiting"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.lifetime_orders.insert_one(order)

    return {
        "success": True,
        "order_id": order_id,
        "payment_id": np_data.get("payment_id"),
        "pay_address": np_data.get("pay_address"),
        "pay_amount": np_data.get("pay_amount"),
        "pay_currency": np_data.get("pay_currency", "usdttrc20"),
        "price": LIFETIME_ACCESS_PRICE,
        "status": np_data.get("payment_status", "waiting"),
    }


@router.get("/payment/check/{payment_id}")
async def check_payment_status(payment_id: int, user: dict = Depends(get_current_user)):
    """Check NOWPayments payment status and grant access if confirmed."""
    headers = {"x-api-key": NOWPAYMENTS_API_KEY}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{NOWPAYMENTS_API}/payment/{payment_id}", headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Could not check payment status")

    np_data = resp.json()
    status = np_data.get("payment_status", "unknown")

    await db.lifetime_orders.update_one(
        {"np_payment_id": payment_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    if status in ("finished", "confirmed"):
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "has_lifetime_access": True,
                "payment_id": str(payment_id),
                "access_granted_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        return {"success": True, "status": "confirmed", "has_lifetime_access": True}

    return {"success": True, "status": status, "has_lifetime_access": False}


@router.post("/payment/nowpayments-webhook")
async def nowpayments_webhook(request: Request):
    """NOWPayments IPN webhook — auto-grant access on confirmed payment."""
    body = await request.json()
    payment_status = body.get("payment_status")
    order_id = body.get("order_id")
    payment_id = body.get("payment_id")

    logging.info(f"NOWPayments webhook: order={order_id} status={payment_status}")

    if payment_status in ("finished", "confirmed"):
        order = await db.lifetime_orders.find_one({"order_id": order_id}, {"_id": 0})
        if order:
            await db.lifetime_orders.update_one(
                {"order_id": order_id},
                {"$set": {"status": payment_status, "confirmed_at": datetime.now(timezone.utc).isoformat()}}
            )
            await db.users.update_one(
                {"id": order["user_id"]},
                {"$set": {
                    "has_lifetime_access": True,
                    "payment_id": str(payment_id),
                    "access_granted_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
            logging.info(f"Lifetime access granted to user {order['user_id']} via webhook")

    return {"success": True}


@router.get("/payment/my-status")
async def my_payment_status(user: dict = Depends(get_current_user)):
    """Get current user's payment/access status."""
    return {
        "success": True,
        "has_lifetime_access": user.get("has_lifetime_access", False),
        "price": LIFETIME_ACCESS_PRICE,
    }
