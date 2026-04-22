import logging
import uuid
from typing import Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import db
from models import (
    VerifyProductRequest, VerifyProductResponse,
    VerifyScanRequest, VerifyScanResponse,
    Product, Protocol
)
from utils.email import get_geolocation

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)


@router.post("/verify-product", response_model=VerifyProductResponse)
@limiter.limit("30/minute")
async def verify_product(request: Request, body: VerifyProductRequest):
    code = body.code.strip().upper()

    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    user_agent = request.headers.get("user-agent", "unknown")

    geo = await get_geolocation(client_ip)

    if not code.startswith("ZX"):
        return VerifyProductResponse(
            success=False,
            message="Invalid code format. All genuine Zurix Sciences products have codes starting with 'ZX'",
            verification_count=0,
            warning_level="none"
        )

    # Search by exact code first, then try without hyphens
    unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})
    db_code = code  # Track the actual code stored in DB for updates
    if not unique_code:
        # Try matching by removing hyphens from both sides
        code_no_hyphens = code.replace("-", "")
        all_codes = await db.unique_codes.find({}, {"_id": 0}).to_list(None)
        for c in all_codes:
            if c["code"].replace("-", "").upper() == code_no_hyphens:
                unique_code = c
                db_code = c["code"]  # Use the actual DB code for updates
                break

    if unique_code:
        current_count = unique_code.get('verification_count', 0)
        verification_count = current_count + 1
        first_verified = unique_code.get('first_verified_at')
        now = datetime.now(timezone.utc).isoformat()

        update_data = {"verification_count": verification_count, "last_verified_at": now}
        if not first_verified:
            update_data["first_verified_at"] = now
            first_verified = now

        await db.unique_codes.update_one({"code": db_code}, {"$set": update_data})

        log_entry = {
            "id": str(uuid.uuid4()),
            "code": db_code,
            "batch_number": unique_code.get('batch_number', ''),
            "product_name": unique_code.get('product_name', ''),
            "timestamp": now,
            "verification_number": verification_count,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "country": geo.get('country', 'Unknown'),
            "city": geo.get('city', 'Unknown'),
            "country_code": geo.get('country_code', 'XX')
        }
        await db.verification_logs.insert_one(log_entry)

        if verification_count <= 2:
            message = f"Product Authenticated! Verification #{verification_count}."
            warning_level = "none"
        elif verification_count == 3:
            message = f"Product Authenticated. This product has been verified {verification_count} times."
            warning_level = "caution"
        else:
            message = f"WARNING: High risk of counterfeit. This code has been verified {verification_count} times. Please contact support."
            warning_level = "danger"

        product = await db.products.find_one({"id": unique_code.get('product_id')}, {"_id": 0})

        return VerifyProductResponse(
            success=True,
            product=product,
            message=message,
            verification_count=verification_count,
            first_verified_at=first_verified,
            warning_level=warning_level,
            product_name=unique_code.get('product_name'),
            batch_number=unique_code.get('batch_number'),
            purity=unique_code.get('purity'),
            expiry_date=unique_code.get('expiry_date')
        )

    product = await db.products.find_one({"verification_code": code}, {"_id": 0})
    if product:
        return VerifyProductResponse(
            success=True,
            product=product,
            message="Product authenticated successfully!",
            verification_count=1,
            warning_level="none"
        )

    return VerifyProductResponse(
        success=False,
        message="Code not found. This product may be COUNTERFEIT. Please contact support immediately.",
        verification_count=0,
        warning_level="danger"
    )


# Mobile app routes
@router.get("/protocols", response_model=List[Protocol])
async def get_protocols(category: Optional[str] = None):
    query = {}
    if category:
        query['category'] = category
    protocols = await db.protocols.find(query, {"_id": 0}).to_list(100)
    return protocols


@router.get("/protocols/{protocol_id}", response_model=Protocol)
async def get_protocol(protocol_id: str):
    protocol = await db.protocols.find_one({"id": protocol_id}, {"_id": 0})
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol


@router.post("/verify-scan", response_model=VerifyScanResponse)
async def verify_scan(request: Request, body: VerifyScanRequest):
    code = body.code.strip().upper()

    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    user_agent = request.headers.get("user-agent", "unknown")

    geo = await get_geolocation(client_ip)

    if code.startswith("ZX-"):
        unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})

        if unique_code:
            current_count = unique_code.get('verification_count', 0)
            verification_count = current_count + 1
            first_verified = unique_code.get('first_verified_at')
            now = datetime.now(timezone.utc).isoformat()

            update_data = {"verification_count": verification_count, "last_verified_at": now}
            if not first_verified:
                update_data["first_verified_at"] = now
                first_verified = now

            await db.unique_codes.update_one({"code": code}, {"$set": update_data})

            log_entry = {
                "id": str(uuid.uuid4()),
                "code": code,
                "batch_number": unique_code.get('batch_number', ''),
                "product_name": unique_code.get('product_name', ''),
                "timestamp": now,
                "verification_number": verification_count,
                "device_id": body.device_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "country": geo.get('country', 'Unknown'),
                "city": geo.get('city', 'Unknown'),
                "country_code": geo.get('country_code', 'XX')
            }
            await db.verification_logs.insert_one(log_entry)

            product = await db.products.find_one({"id": unique_code.get('product_id')}, {"_id": 0})

            warning = None
            if verification_count <= 2:
                message = f"Product Authenticated! Verification #{verification_count}."
            elif verification_count == 3:
                message = f"Product Authenticated. This product has been verified {verification_count} times."
                warning = "caution"
            else:
                message = f"WARNING: High risk of counterfeit. This code has been verified {verification_count} times. Please contact support."
                warning = "danger"

            return VerifyScanResponse(
                success=True,
                product=Product(**product) if product else None,
                message=message,
                verification_count=verification_count,
                warning=warning
            )

    product = await db.products.find_one({"verification_code": code}, {"_id": 0})
    if product:
        verification_log = {
            "id": str(uuid.uuid4()),
            "verification_code": code,
            "batch_number": product['batch_number'],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": body.device_id
        }
        await db.verification_logs.insert_one(verification_log)

        verification_count = await db.verification_logs.count_documents({"batch_number": product['batch_number']})

        warning = None
        if verification_count > 10:
            warning = f"WARNING: This batch has been verified {verification_count} times. This may indicate counterfeiting."
        elif verification_count > 5:
            warning = f"Note: This batch has been verified {verification_count} times."

        return VerifyScanResponse(
            success=True,
            product=Product(**product),
            message="Product authenticated successfully!",
            verification_count=verification_count,
            warning=warning
        )

    return VerifyScanResponse(
        success=False,
        message="Code not found. This product may be COUNTERFEIT. Please contact support immediately.",
        verification_count=0,
        warning="danger"
    )


@router.get("/verification-history")
async def get_verification_history(device_id: Optional[str] = None, limit: int = 50):
    query = {}
    if device_id:
        query['device_id'] = device_id
    logs = await db.verification_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"history": logs, "count": len(logs)}


@router.get("/batch-stats/{batch_number}")
async def get_batch_stats(batch_number: str):
    count = await db.verification_logs.count_documents({"batch_number": batch_number})
    logs = await db.verification_logs.find({"batch_number": batch_number}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
    return {"batch_number": batch_number, "total_verifications": count, "recent_verifications": logs}
