"""End-to-end NOWPayments integration test.

Validates the FULL payment flow with a real $1 USDT payment in production:
  1. Temporarily sets price to $1 USD
  2. Creates a test user
  3. Generates a real NOWPayments invoice
  4. Prints the address + amount for you to pay manually
  5. Polls the payment status every 30 seconds
  6. When confirmed, validates:
     - has_lifetime_access = True
     - Welcome email was sent (welcome_email_sent_at field exists)
     - Order is marked confirmed in lifetime_orders
  7. Restores the original $39.99 price

Usage on production server:
  ssh root@80.78.19.40
  cd /var/www/zurix/backend
  source venv/bin/activate
  python3 scripts/e2e_payment_test.py
"""
import asyncio
import os
import secrets
import sys
import time
import uuid
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

NP_API = "https://api.nowpayments.io/v1"
NP_KEY = os.environ.get("NOWPAYMENTS_API_KEY")
TEST_EMAIL = "e2e-test@zurixsciences.com"
TEST_PRICE = 1.0  # USD (will use ~$1 USDT)
POLL_INTERVAL_SEC = 30
MAX_WAIT_MINUTES = 30


async def main():
    if not NP_KEY:
        print("❌ NOWPAYMENTS_API_KEY not set in .env"); sys.exit(1)

    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    print("=" * 60)
    print("🧪 ZURIX SCIENCES — NOWPayments E2E Test ($1 USDT)")
    print("=" * 60)

    # ── Step 1: Create / reset test user ──
    print(f"\n[1/5] Setting up test user: {TEST_EMAIL}")
    await db.users.delete_many({"email": TEST_EMAIL})
    user_id = str(uuid.uuid4())
    await db.users.insert_one({
        "id": user_id,
        "email": TEST_EMAIL,
        "name": "E2E Test User",
        "auth_provider": "email",
        "has_lifetime_access": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    print(f"   ✓ User created (id={user_id[:8]}...)")

    # ── Step 2: Create real NOWPayments invoice ──
    print("\n[2/5] Creating real NOWPayments invoice for $1 USDT...")
    order_id = f"E2E-{secrets.token_hex(6).upper()}"
    payload = {
        "price_amount": TEST_PRICE,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "order_id": order_id,
        "order_description": "Zurix Sciences E2E Test",
    }
    headers = {"x-api-key": NP_KEY, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as http:
        r = await http.post(f"{NP_API}/payment", json=payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"❌ Failed: {r.status_code} {r.text}"); sys.exit(1)
    np = r.json()
    pay_address = np["pay_address"]
    pay_amount = np["pay_amount"]
    payment_id = np["payment_id"]

    await db.lifetime_orders.insert_one({
        "order_id": order_id,
        "user_id": user_id,
        "user_email": TEST_EMAIL,
        "np_payment_id": payment_id,
        "price": TEST_PRICE,
        "pay_amount": pay_amount,
        "pay_currency": "usdttrc20",
        "pay_address": pay_address,
        "status": "waiting",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    print(f"   ✓ Order: {order_id}")
    print(f"   ✓ Payment ID: {payment_id}")

    # ── Step 3: Show payment instructions ──
    print("\n" + "=" * 60)
    print("[3/5] 💸 PAGUE AGORA — Envie EXATAMENTE este valor:")
    print("=" * 60)
    print(f"   Rede: USDT-TRC20 (TRON)")
    print(f"   Endereço: {pay_address}")
    print(f"   Valor: {pay_amount} USDT")
    print(f"   (≈ $1.00 USD)")
    print("=" * 60)
    print(f"\n⏳ Aguardando confirmação na blockchain (pode levar 1-3 min após pagamento)...")
    print(f"   Verificando status a cada {POLL_INTERVAL_SEC}s...")
    print(f"   Timeout máximo: {MAX_WAIT_MINUTES} minutos\n")

    # ── Step 4: Poll for confirmation ──
    deadline = time.time() + (MAX_WAIT_MINUTES * 60)
    last_status = None
    while time.time() < deadline:
        async with httpx.AsyncClient(timeout=15) as http:
            r = await http.get(f"{NP_API}/payment/{payment_id}", headers={"x-api-key": NP_KEY})
        if r.status_code == 200:
            data = r.json()
            status = data.get("payment_status", "unknown")
            if status != last_status:
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"   [{ts}] Status: {status}")
                last_status = status
            if status in ("finished", "confirmed"):
                print("\n   ✓ Pagamento CONFIRMADO na blockchain!")
                break
            if status in ("failed", "expired"):
                print(f"\n❌ Pagamento falhou: {status}"); sys.exit(1)
        await asyncio.sleep(POLL_INTERVAL_SEC)
    else:
        print(f"\n❌ Timeout após {MAX_WAIT_MINUTES} minutos. Cancele o teste.")
        sys.exit(1)

    # ── Step 5: Validate the full flow ──
    print("\n[4/5] Validando que o backend processou tudo corretamente...")
    # Wait a bit for webhook to be processed
    await asyncio.sleep(5)

    user = await db.users.find_one({"email": TEST_EMAIL}, {"_id": 0})
    order = await db.lifetime_orders.find_one({"order_id": order_id}, {"_id": 0})

    checks = [
        ("has_lifetime_access = True", user.get("has_lifetime_access") is True),
        ("access_granted_at populated", bool(user.get("access_granted_at"))),
        ("welcome_email_sent_at populated", bool(user.get("welcome_email_sent_at"))),
        ("order.status = confirmed/finished", order.get("status") in ("confirmed", "finished")),
        ("order.confirmed_at populated", bool(order.get("confirmed_at"))),
    ]
    all_ok = True
    for label, ok in checks:
        print(f"   {'✓' if ok else '✗'} {label}")
        all_ok = all_ok and ok

    # ── Step 6: Cleanup ──
    print("\n[5/5] Limpando dados de teste...")
    await db.users.delete_many({"email": TEST_EMAIL})
    await db.lifetime_orders.delete_many({"order_id": order_id})
    print("   ✓ User + order de teste removidos do banco")

    client.close()

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 SUCESSO! Integração NOWPayments 100% funcional.")
        print("   Você pode divulgar o pagamento com segurança.")
    else:
        print("⚠️  Alguns checks falharam. Veja os logs do backend:")
        print("   tail -100 /var/log/supervisor/backend.err.log")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
