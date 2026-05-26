import asyncio
import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse

from database import db, NOWPAYMENTS_API_KEY, NOWPAYMENTS_IPN_SECRET, ENVIRONMENT, LIFETIME_ACCESS_PRICE, RESEND_API_KEY, SENDER_EMAIL
from utils.security import get_current_user

router = APIRouter(prefix="/api")

NOWPAYMENTS_API = "https://api.nowpayments.io/v1"
SITE_URL = os.environ.get("SITE_URL", "https://zurixsciences.com")


async def _send_welcome_email(user_id: str) -> bool:
    """Send Lifetime Access welcome email via Resend. Idempotent — only sends once per user.

    Returns True if email was sent (or already had been); False on any failure.
    """
    if not RESEND_API_KEY:
        logging.warning("RESEND_API_KEY not set; welcome email skipped.")
        return False

    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        logging.warning(f"Welcome email: user {user_id} not found")
        return False

    if user.get("welcome_email_sent_at"):
        logging.info(f"Welcome email already sent to {user.get('email')} at {user.get('welcome_email_sent_at')}")
        return True

    email = user.get("email")
    if not email:
        return False

    name = user.get("name") or email.split("@")[0]
    html = build_welcome_email_html(name)

    try:
        import resend
        await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [email],
            "subject": "Welcome to Zurix Sciences Lifetime Access 🎉",
            "html": html,
        })
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"welcome_email_sent_at": datetime.now(timezone.utc).isoformat()}},
        )
        logging.info(f"Welcome email sent to {email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send welcome email to {email}: {e}")
        return False


def build_welcome_email_html(name: str | None) -> str:
    greeting = f" {name}" if name else ""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #ffffff; color: #1a1a1a;">
            <div style="text-align: center; padding: 24px 0; border-bottom: 3px solid #7c3aed;">
                <h1 style="color: #2563eb; margin: 0; font-size: 28px;">Zurix Sciences</h1>
                <p style="color: #6b7280; margin: 4px 0 0 0; font-size: 13px; letter-spacing: 1px; text-transform: uppercase;">Premium Research Compounds</p>
            </div>

            <div style="padding: 32px 0;">
                <h2 style="color: #111827; font-size: 22px; margin: 0 0 16px 0;">Welcome to Lifetime Access{greeting}! 🎉</h2>
                <p style="color: #374151; line-height: 1.6; font-size: 15px;">
                    Your payment has been confirmed and your <strong>Lifetime Premium Access</strong> is now active.
                    You now have unlimited access to:
                </p>

                <ul style="color: #374151; line-height: 1.8; font-size: 15px; padding-left: 20px;">
                    <li>📚 <strong>130+ Premium Protocols</strong> across 13 peptide Stack Hubs</li>
                    <li>🔬 <strong>Detailed dosing instructions</strong> with auto-calculated Insulin Units (UI)</li>
                    <li>⭐ <strong>Community-driven Trending protocols</strong> ranked by user ratings</li>
                    <li>🔄 <strong>Future updates</strong> — new protocols and hubs added regularly, free forever</li>
                </ul>

                <p style="text-align: center; margin: 32px 0;">
                    <a href="{SITE_URL}/protocols" style="background: #7c3aed; color: white; padding: 14px 32px; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 15px; display: inline-block;">
                        Explore Your Stack Hubs →
                    </a>
                </p>

                <div style="background: #f3f4f6; border-left: 4px solid #2563eb; padding: 16px; border-radius: 6px; margin: 24px 0;">
                    <p style="margin: 0; color: #4b5563; font-size: 13px;">
                        <strong>Tip:</strong> Bookmark <a href="{SITE_URL}/protocols" style="color: #2563eb;">{SITE_URL}/protocols</a> for quick access to your premium library.
                    </p>
                </div>

                <p style="color: #6b7280; line-height: 1.6; font-size: 13px; margin-top: 32px;">
                    Need help or have questions? Just reply to this email and we'll get back to you.
                </p>
            </div>

            <div style="border-top: 1px solid #e5e7eb; padding-top: 16px; text-align: center; color: #9ca3af; font-size: 12px;">
                <p style="margin: 4px 0;">© 2026 Zurix Sciences — Premium Research Compounds</p>
                <p style="margin: 4px 0;">For research purposes only. Not for human consumption.</p>
            </div>
        </div>
    """


@router.get("/payment/email-preview", response_class=HTMLResponse)
async def payment_email_preview(type: str = "welcome"):
    """Preview payment-related email templates in the browser."""
    if type == "welcome":
        return HTMLResponse(content=build_welcome_email_html("Preview Tester"))
    raise HTTPException(status_code=400, detail=f"Unknown email type: {type}")


def _verify_nowpayments_signature(raw_body: bytes, signature: str) -> bool:
    """Verify NOWPayments IPN signature using HMAC-SHA512.

    NOWPayments sorts JSON keys alphabetically before signing, so we replicate that here.
    Returns True if valid; False otherwise. Uses constant-time comparison to prevent
    timing attacks.
    """
    if not NOWPAYMENTS_IPN_SECRET:
        return False
    if not signature:
        return False
    try:
        parsed = json.loads(raw_body)
        sorted_body = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
    except (ValueError, TypeError):
        return False
    expected = hmac.new(
        NOWPAYMENTS_IPN_SECRET.encode("utf-8"),
        sorted_body.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/payment/create-invoice")
async def create_lifetime_invoice(request: Request, user: dict = Depends(get_current_user)):
    """Create a NOWPayments invoice for lifetime access."""
    if user.get("has_lifetime_access"):
        return {"success": True, "already_paid": True, "message": "You already have lifetime access."}

    order_id = f"LTA-{uuid.uuid4().hex[:12].upper()}"

    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}

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
        await _send_welcome_email(user["id"])
        return {"success": True, "status": "confirmed", "has_lifetime_access": True}

    return {"success": True, "status": status, "has_lifetime_access": False}


@router.post("/payment/nowpayments-webhook")
async def nowpayments_webhook(request: Request):
    """NOWPayments IPN webhook — auto-grant access on confirmed payment.

    Verifies HMAC-SHA512 signature using NOWPAYMENTS_IPN_SECRET to prevent
    forged requests from granting free lifetime access.

    - Production (ENVIRONMENT=production): invalid/missing signature → 401
    - Development: invalid signature logs warning but still processes (for local testing)
    """
    raw_body = await request.body()
    signature = request.headers.get("x-nowpayments-sig", "")
    client_ip = request.client.host if request.client else "unknown"

    is_valid = _verify_nowpayments_signature(raw_body, signature)

    if not is_valid:
        is_prod = ENVIRONMENT == "production"
        if not NOWPAYMENTS_IPN_SECRET:
            logging.warning(
                f"NOWPayments webhook called but NOWPAYMENTS_IPN_SECRET is not configured. "
                f"IP={client_ip}. {'BLOCKING (prod)' if is_prod else 'Allowing (dev mode)'}."
            )
        else:
            logging.warning(
                f"Invalid NOWPayments webhook signature from {client_ip}. "
                f"sig_present={bool(signature)}. "
                f"{'BLOCKING (prod)' if is_prod else 'Allowing (dev mode)'}."
            )
        if is_prod:
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        body = json.loads(raw_body)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    payment_status = body.get("payment_status")
    order_id = body.get("order_id")
    payment_id = body.get("payment_id")

    logging.info(f"NOWPayments webhook: order={order_id} status={payment_status} verified={is_valid}")

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
            await _send_welcome_email(order["user_id"])
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
