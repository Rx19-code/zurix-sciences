import logging
import asyncio
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from database import db, RESEND_API_KEY, SENDER_EMAIL, USDT_WALLET_ADDRESS, TRON_API_URL, PDF_STORAGE_DIR
from models import CreatePaymentRequest, VerifyPaymentRequest
from routes.protocols import PROTOCOL_DEFINITIONS

router = APIRouter(prefix="/api")


async def verify_tron_transaction(txid: str, expected_amount: float, wallet_address: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{TRON_API_URL}/transaction-info",
                params={"hash": txid}
            )

            if response.status_code != 200:
                return {"valid": False, "message": "Could not verify transaction. Please try again."}

            tx_data = response.json()

            if not tx_data or "contractRet" not in tx_data:
                return {"valid": False, "message": "Transaction not found. Please check the TXID."}

            if tx_data.get("contractRet") != "SUCCESS":
                return {"valid": False, "message": "Transaction failed or pending."}

            token_transfers = tx_data.get("trc20TransferInfo", [])

            for transfer in token_transfers:
                to_address = transfer.get("to_address", "")
                amount_str = transfer.get("amount_str", "0")
                decimals = int(transfer.get("decimals", 6))
                symbol = transfer.get("symbol", "")

                if to_address == wallet_address and symbol == "USDT":
                    amount = float(amount_str) / (10 ** decimals)
                    if amount >= expected_amount:
                        return {"valid": True, "message": "Payment verified!", "amount": amount, "txid": txid}
                    else:
                        return {"valid": False, "message": f"Amount too low. Expected ${expected_amount}, received ${amount:.2f}"}

            return {"valid": False, "message": "No USDT transfer found to our wallet in this transaction."}

    except Exception as e:
        logging.error(f"Error verifying Tron transaction: {str(e)}")
        return {"valid": False, "message": "Error verifying transaction. Please try again or contact support."}


@router.get("/payment/wallet-info")
async def get_wallet_info():
    return {
        "success": True,
        "wallet_address": USDT_WALLET_ADDRESS,
        "network": "TRC20 (Tron)",
        "currency": "USDT"
    }


@router.post("/payment/create-order")
async def create_payment_order(request: CreatePaymentRequest):
    protocol = PROTOCOL_DEFINITIONS.get(request.protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")

    price = protocol.get("price", 0)
    if price <= 0:
        raise HTTPException(status_code=400, detail="This protocol is free. Use batch validation instead.")

    order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"

    order = {
        "order_id": order_id,
        "protocol_id": request.protocol_id,
        "protocol_title": protocol["title"],
        "price": price,
        "email": request.email.lower().strip(),
        "phone": request.phone.strip() if request.phone else None,
        "name": request.name.strip() if request.name else None,
        "language": request.language,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "txid": None,
        "paid_at": None
    }

    await db.protocol_orders.insert_one(order)

    return {
        "success": True,
        "order_id": order_id,
        "protocol_title": protocol["title"],
        "price": price,
        "wallet_address": USDT_WALLET_ADDRESS,
        "network": "TRC20 (Tron)",
        "instructions": f"Send exactly ${price} USDT to the wallet address above. After payment, enter the transaction ID (TXID) to verify."
    }


@router.post("/payment/verify")
async def verify_payment(request: VerifyPaymentRequest):
    import resend

    order = await db.protocol_orders.find_one({"order_id": request.order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order["status"] == "completed":
        return {"success": True, "already_paid": True, "message": "This order has already been paid and the protocol was sent."}

    existing_txid = await db.protocol_orders.find_one({"txid": request.txid, "status": "completed"})
    if existing_txid:
        raise HTTPException(status_code=400, detail="This transaction has already been used for another order.")

    verification = await verify_tron_transaction(
        txid=request.txid,
        expected_amount=order["price"],
        wallet_address=USDT_WALLET_ADDRESS
    )

    if not verification["valid"]:
        return {"success": False, "message": verification["message"]}

    await db.protocol_orders.update_one(
        {"order_id": request.order_id},
        {"$set": {
            "status": "completed",
            "txid": request.txid,
            "paid_at": datetime.now(timezone.utc).isoformat(),
            "verified_amount": verification.get("amount")
        }}
    )

    protocol = PROTOCOL_DEFINITIONS.get(order["protocol_id"])
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol configuration error")

    pdf_filename = protocol["languages"].get(order["language"], protocol["languages"]["en"])
    pdf_path = PDF_STORAGE_DIR / pdf_filename

    if not pdf_path.exists():
        return {
            "success": True,
            "message": "Payment verified! However, the PDF is being prepared. You will receive it by email within 24 hours.",
            "paid": True,
            "email_sent": False
        }

    lang_content = {
        "en": {
            "subject": f"Your Purchased Protocol: {protocol['title']}",
            "greeting": f"Hello{' ' + order.get('name', '') if order.get('name') else ''}!",
            "intro": "Thank you for your purchase! Your advanced protocol is attached.",
            "attached": "Your protocol PDF is attached to this email.",
            "footer": "For research use only. Not for human consumption."
        },
        "es": {
            "subject": f"Tu Protocolo Comprado: {protocol['title']}",
            "greeting": f"¡Hola{' ' + order.get('name', '') if order.get('name') else ''}!",
            "intro": "¡Gracias por tu compra! Tu protocolo avanzado está adjunto.",
            "attached": "Tu protocolo PDF está adjunto a este correo.",
            "footer": "Solo para uso en investigación. No para consumo humano."
        },
        "pt": {
            "subject": f"Seu Protocolo Comprado: {protocol['title']}",
            "greeting": f"Olá{' ' + order.get('name', '') if order.get('name') else ''}!",
            "intro": "Obrigado pela sua compra! Seu protocolo avançado está anexado.",
            "attached": "Seu protocolo PDF está anexado a este email.",
            "footer": "Apenas para uso em pesquisa. Não para consumo humano."
        }
    }

    content = lang_content.get(order["language"], lang_content["en"])

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1e3a8a;">Zurix Sciences</h1>
            <p style="color: #666;">Premium Research Compounds</p>
        </div>
        <h2 style="color: #333;">{content['greeting']}</h2>
        <p style="color: #666;">{content['intro']}</p>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #1e3a8a; margin-top: 0;">{protocol['title']}</h3>
            <p style="color: #666;">{protocol['description']}</p>
            <p><strong>Duration: {protocol['duration_weeks']} weeks</strong></p>
        </div>
        <p style="color: #333; background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <strong>&#10003;</strong> {content['attached']}
        </p>
        <div style="background: #f0f0f0; padding: 10px; border-radius: 4px; margin: 15px 0;">
            <p style="color: #666; font-size: 12px; margin: 0;">
                Order ID: {order['order_id']}<br>
                Transaction: {request.txid[:20]}...
            </p>
        </div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">
            {content['footer']}<br>
            &copy; Zurix Sciences - zurixsciences.com
        </p>
    </div>
    """

    try:
        import base64
        with open(pdf_path, "rb") as f:
            pdf_content = base64.b64encode(f.read()).decode()

        params = {
            "from": SENDER_EMAIL,
            "to": [order["email"]],
            "subject": content["subject"],
            "html": html_content,
            "attachments": [{
                "filename": f"{protocol['title']} ({order['language'].upper()}).pdf",
                "content": pdf_content
            }]
        }

        await asyncio.to_thread(resend.Emails.send, params)
        logging.info(f"Paid protocol sent to {order['email']} for order {order['order_id']}")

        return {"success": True, "message": f"Payment verified! Protocol sent to {order['email']}", "paid": True, "email_sent": True}

    except Exception as e:
        logging.error(f"Failed to send paid protocol email: {str(e)}")
        return {"success": True, "message": "Payment verified! There was an issue sending the email. Please contact support.", "paid": True, "email_sent": False, "error": str(e)}


@router.get("/payment/order/{order_id}")
async def get_order_status(order_id: str):
    order = await db.protocol_orders.find_one({"order_id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "success": True,
        "order_id": order["order_id"],
        "status": order["status"],
        "protocol_title": order["protocol_title"],
        "price": order["price"],
        "created_at": order["created_at"],
        "paid_at": order.get("paid_at")
    }
