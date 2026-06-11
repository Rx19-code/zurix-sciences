import logging
import io
import base64
import uuid
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header, File, UploadFile, Request
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import db, ADMIN_PASSWORD, PDF_STORAGE_DIR
from models import AdminLoginRequest, ImportCodesRequest, UpdateBatchRequest, TestEmailRequest
from routes.protocols import PROTOCOL_DEFINITIONS
from utils.email import send_protocol_email

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)


@router.post("/admin/login")
@limiter.limit("5/minute")
async def admin_login(request: Request, body: AdminLoginRequest):
    if body.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Login successful"}
    logging.warning(f"Failed admin login attempt from {get_remote_address(request)}")
    raise HTTPException(status_code=401, detail="Invalid password")


@router.post("/admin/import-codes")
async def import_codes(request: ImportCodesRequest, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    codes = [c.strip().upper() for c in request.codes if c.strip()]
    if not codes:
        raise HTTPException(status_code=400, detail="No valid codes provided")

    existing = await db.unique_codes.find({"code": {"$in": codes}}, {"code": 1}).to_list(len(codes))
    existing_codes = {doc['code'] for doc in existing}
    new_codes = [c for c in codes if c not in existing_codes]

    if not new_codes:
        return {"success": False, "message": "All codes already exist in database", "imported": 0, "duplicates": len(codes)}

    now = datetime.now(timezone.utc).isoformat()
    import_batch_id = f"IMP-{uuid.uuid4().hex[:8].upper()}"
    documents = []
    for code in new_codes:
        documents.append({
            "id": str(uuid.uuid4()),
            "code": code,
            "batch_number": request.batch_number.strip().upper(),
            "product_id": request.product_id,
            "product_name": request.product_name,
            "purity": request.purity or "≥99%",
            "expiry_date": request.expiry_date,
            "verification_count": 0,
            "first_verified_at": None,
            "last_verified_at": None,
            "created_at": now,
            "import_batch_id": import_batch_id
        })

    await db.unique_codes.insert_many(documents)

    return {
        "success": True,
        "message": f"Successfully imported {len(new_codes)} codes",
        "imported": len(new_codes),
        "duplicates": len(existing_codes),
        "import_batch_id": import_batch_id
    }


@router.put("/admin/batch/update")
async def update_batch_info(request: UpdateBatchRequest, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    update_fields = {}
    if request.purity:
        update_fields["purity"] = request.purity
    if request.expiry_date:
        update_fields["expiry_date"] = request.expiry_date

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.unique_codes.update_many(
        {"batch_number": request.batch_number.upper()},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Batch '{request.batch_number}' not found")

    return {
        "success": True,
        "message": f"Updated {result.modified_count} codes in batch {request.batch_number}",
        "updated": result.modified_count
    }


@router.post("/admin/reset-verifications")
async def reset_verifications(request: Request, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    batch_number = body.get("batch_number", "").strip().upper()
    code = body.get("code", "").strip().upper()

    if code:
        result = await db.unique_codes.update_one(
            {"code": code},
            {"$set": {"verification_count": 0, "first_verified_at": None, "last_verified_at": None}}
        )
        count = result.modified_count
    elif batch_number:
        result = await db.unique_codes.update_many(
            {"batch_number": batch_number},
            {"$set": {"verification_count": 0, "first_verified_at": None, "last_verified_at": None}}
        )
        count = result.modified_count
    else:
        result = await db.unique_codes.update_many(
            {"verification_count": {"$gt": 0}},
            {"$set": {"verification_count": 0, "first_verified_at": None, "last_verified_at": None}}
        )
        count = result.modified_count

    return {"success": True, "message": f"Reset {count} codes", "reset_count": count}


@router.get("/admin/codes")
async def get_admin_codes(
    x_admin_password: str = Header(None),
    batch_number: Optional[str] = None,
    import_batch_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = {}
    if import_batch_id:
        query["import_batch_id"] = import_batch_id
    elif batch_number:
        query["batch_number"] = batch_number.upper()

    if search:
        search_upper = search.upper()
        query["$or"] = [
            {"code": {"$regex": search_upper, "$options": "i"}},
            {"product_name": {"$regex": search, "$options": "i"}},
            {"batch_number": {"$regex": search_upper, "$options": "i"}}
        ]

    total_matching = await db.unique_codes.count_documents(query)
    total_all = await db.unique_codes.count_documents({})
    codes = await db.unique_codes.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "codes": codes,
        "total": total_all,
        "total_matching": total_matching,
        "showing": len(codes),
        "skip": skip,
        "has_more": skip + len(codes) < total_matching
    }


@router.get("/admin/batches")
async def get_admin_batches(x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    pipeline = [
        {"$group": {
            "_id": "$batch_number",
            "product_name": {"$first": "$product_name"},
            "purity": {"$first": "$purity"},
            "expiry_date": {"$first": "$expiry_date"},
            "total_codes": {"$sum": 1},
            "verified_codes": {"$sum": {"$cond": [{"$gt": ["$verification_count", 0]}, 1, 0]}},
            "created_at": {"$min": "$created_at"}
        }},
        {"$sort": {"created_at": -1}}
    ]

    batches = await db.unique_codes.aggregate(pipeline).to_list(100)
    return {"batches": batches}


@router.get("/admin/verification-logs")
async def get_admin_verification_logs(x_admin_password: str = Header(None), limit: int = 100):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logs = await db.verification_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}


# ════════════════════════ VERIFICATIONS DASHBOARD ════════════════════════
@router.get("/admin/verifications")
async def get_verifications(
    x_admin_password: str = Header(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    batch_number: Optional[str] = None,
    code: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
):
    """List verifications with filters, pagination and aggregated stats."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query: dict = {}
    if start_date:
        query.setdefault("timestamp", {})["$gte"] = start_date
    if end_date:
        query.setdefault("timestamp", {})["$lte"] = end_date + "T23:59:59"
    if batch_number:
        query["batch_number"] = batch_number.upper()
    if code:
        query["$or"] = [
            {"code": {"$regex": code, "$options": "i"}},
            {"verification_code": {"$regex": code, "$options": "i"}},
        ]

    total = await db.verification_logs.count_documents(query)
    logs = (
        await db.verification_logs.find(query, {"_id": 0})
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
        .to_list(limit)
    )

    # Aggregated stats (overall, not filtered)
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_7d = (now - timedelta(days=7)).isoformat()
    last_30d = (now - timedelta(days=30)).isoformat()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

    total_all = await db.verification_logs.count_documents({})
    total_today = await db.verification_logs.count_documents({"timestamp": {"$gte": today_start.isoformat()}})
    total_7d = await db.verification_logs.count_documents({"timestamp": {"$gte": last_7d}})
    total_30d = await db.verification_logs.count_documents({"timestamp": {"$gte": last_30d}})
    total_month = await db.verification_logs.count_documents({"timestamp": {"$gte": month_start}})
    total_year = await db.verification_logs.count_documents({"timestamp": {"$gte": year_start}})

    # Top 5 batches
    top_batches = await db.verification_logs.aggregate([
        {"$match": {"batch_number": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$batch_number", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]).to_list(5)

    return {
        "logs": logs,
        "total": total,
        "showing": len(logs),
        "skip": skip,
        "has_more": skip + len(logs) < total,
        "stats": {
            "total_all": total_all,
            "total_today": total_today,
            "total_7d": total_7d,
            "total_30d": total_30d,
            "total_month": total_month,
            "total_year": total_year,
        },
        "top_batches": [{"batch": b["_id"], "count": b["count"]} for b in top_batches],
    }


@router.get("/admin/verifications/export")
async def export_verifications_csv(
    x_admin_password: str = Header(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    batch_number: Optional[str] = None,
):
    """Export verifications as CSV with optional date range and batch filter."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query: dict = {}
    if start_date:
        query.setdefault("timestamp", {})["$gte"] = start_date
    if end_date:
        query.setdefault("timestamp", {})["$lte"] = end_date + "T23:59:59"
    if batch_number:
        query["batch_number"] = batch_number.upper()

    logs = await db.verification_logs.find(query, {"_id": 0}).sort("timestamp", -1).to_list(None)

    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp",
        "Code",
        "Batch Number",
        "Product Name",
        "Verification #",
        "Client IP",
        "Country",
        "City",
        "Country Code",
        "User Agent",
        "Device ID",
    ])
    for log in logs:
        ts = (log.get("timestamp") or "")[:19].replace("T", " ")
        writer.writerow([
            ts,
            log.get("code", log.get("verification_code", "")),
            log.get("batch_number", ""),
            log.get("product_name", ""),
            log.get("verification_number", ""),
            log.get("client_ip", log.get("ip", "")),
            log.get("country", ""),
            log.get("city", ""),
            log.get("country_code", ""),
            log.get("user_agent", ""),
            log.get("device_id", ""),
        ])

    output.seek(0)
    filename_suffix = ""
    if start_date and end_date:
        filename_suffix = f"_{start_date}_to_{end_date}"
    elif start_date:
        filename_suffix = f"_from_{start_date}"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=zurix_verifications{filename_suffix}.csv"},
    )


@router.delete("/admin/batch/{batch_number}")
async def delete_batch(batch_number: str, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.unique_codes.delete_many({"batch_number": batch_number.upper()})
    return {"success": True, "message": f"Deleted {result.deleted_count} codes from batch {batch_number}"}


@router.delete("/admin/code/{code}")
async def delete_single_code(code: str, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.unique_codes.delete_one({"code": code.upper()})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Code not found")

    return {"success": True, "message": f"Code {code} deleted successfully"}


@router.post("/admin/protocols/upload-pdf")
async def upload_protocol_pdf(
    protocol_id: str,
    language: str,
    pdf: UploadFile = File(...),
    x_admin_password: str = Header(None, alias="X-Admin-Password")
):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if protocol_id not in PROTOCOL_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Protocol not found")

    if language not in ["en", "es", "pt"]:
        raise HTTPException(status_code=400, detail="Invalid language. Use: en, es, or pt")

    protocol = PROTOCOL_DEFINITIONS[protocol_id]
    pdf_filename = protocol["languages"][language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename

    content = await pdf.read()
    with open(pdf_path, "wb") as f:
        f.write(content)

    return {"success": True, "message": f"PDF uploaded successfully for {protocol['title']} ({language.upper()})", "filename": pdf_filename}


@router.get("/admin/protocols/status")
async def get_protocols_status(x_admin_password: str = Header(None, alias="X-Admin-Password")):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    status = []
    for proto_id, proto_data in PROTOCOL_DEFINITIONS.items():
        languages_status = {}
        for lang, filename in proto_data["languages"].items():
            pdf_path = PDF_STORAGE_DIR / filename
            languages_status[lang] = {"filename": filename, "uploaded": pdf_path.exists()}

        status.append({
            "id": proto_id,
            "title": proto_data["title"],
            "languages": languages_status
        })

    downloads = await db.protocol_downloads.count_documents({})
    return {"success": True, "protocols": status, "total_downloads": downloads}


@router.post("/admin/test-email")
async def send_test_email(request: TestEmailRequest, password: str = Header(..., alias="X-Admin-Password")):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    from database import RESEND_API_KEY
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Resend API key not configured")

    test_protocol = {
        "id": "test",
        "title": "Test Protocol",
        "description": "This is a test email to verify the email system is working correctly.",
        "category": "Test",
        "duration_weeks": 1
    }

    result = await send_protocol_email(
        user_email=request.email,
        user_name="Test User",
        protocol=test_protocol,
        pdf_path=None
    )

    if result:
        return {"success": True, "message": f"Test email sent to {request.email}", "email_id": result.get("id")}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")


@router.get("/admin/leads")
async def get_admin_leads(
    x_admin_password: str = Header(None),
    search: Optional[str] = None,
    protocol_id: Optional[str] = None,
    limit: int = 200,
    skip: int = 0
):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = {}
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]
    if protocol_id:
        query["protocol_id"] = protocol_id

    total = await db.protocol_leads.count_documents(query)
    leads = await db.protocol_leads.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    return {
        "leads": leads,
        "total": total,
        "showing": len(leads),
        "skip": skip,
        "has_more": skip + len(leads) < total
    }


@router.get("/admin/leads/export")
async def export_leads_csv(
    x_admin_password: str = Header(None),
    protocol_id: Optional[str] = None
):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = {}
    if protocol_id:
        query["protocol_id"] = protocol_id

    leads = await db.protocol_leads.find(query, {"_id": 0}).sort("created_at", -1).to_list(5000)

    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Phone", "Protocol", "Language", "Source", "Downloads", "Date"])

    for lead in leads:
        writer.writerow([
            lead.get("name", ""),
            lead.get("email", ""),
            lead.get("phone", ""),
            lead.get("protocol_title", ""),
            lead.get("language", ""),
            lead.get("source", ""),
            lead.get("download_count", 0),
            lead.get("created_at", "")[:19] if lead.get("created_at") else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=zurix_leads.csv"}
    )


# ════════════════════════ USERS MANAGEMENT ════════════════════════
@router.get("/admin/users")
async def get_admin_users(
    x_admin_password: str = Header(None),
    search: Optional[str] = None,
    provider: Optional[str] = None,
    lifetime: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
):
    """List all registered users with filters and pagination."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query: dict = {}
    if search:
        query["$or"] = [
            {"email": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}},
        ]
    if provider in ("email", "google"):
        query["auth_provider"] = provider
    if lifetime == "yes":
        query["has_lifetime_access"] = True
    elif lifetime == "no":
        query["has_lifetime_access"] = {"$ne": True}

    projection = {
        "_id": 0,
        "id": 1,
        "email": 1,
        "name": 1,
        "auth_provider": 1,
        "has_lifetime_access": 1,
        "welcome_email_sent_at": 1,
        "created_at": 1,
    }

    total = await db.users.count_documents(query)
    users = (
        await db.users.find(query, projection)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(limit)
    )

    # Aggregate stats
    total_all = await db.users.count_documents({})
    total_lifetime = await db.users.count_documents({"has_lifetime_access": True})
    total_google = await db.users.count_documents({"auth_provider": "google"})
    total_email = await db.users.count_documents({"auth_provider": "email"})

    return {
        "users": users,
        "total": total,
        "showing": len(users),
        "skip": skip,
        "has_more": skip + len(users) < total,
        "stats": {
            "total_all": total_all,
            "total_lifetime": total_lifetime,
            "total_google": total_google,
            "total_email": total_email,
        },
    }


@router.get("/admin/users/export")
async def export_users_csv(x_admin_password: str = Header(None)):
    """Export all registered users as CSV (no password hashes)."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    projection = {
        "_id": 0,
        "id": 1,
        "email": 1,
        "name": 1,
        "auth_provider": 1,
        "has_lifetime_access": 1,
        "welcome_email_sent_at": 1,
        "created_at": 1,
    }
    users = await db.users.find({}, projection).sort("created_at", -1).to_list(None)

    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Email",
        "Name",
        "Auth Provider",
        "Lifetime Access",
        "Welcome Email Sent",
        "Created At",
    ])
    for u in users:
        writer.writerow([
            u.get("email", ""),
            u.get("name", ""),
            u.get("auth_provider", ""),
            "Yes" if u.get("has_lifetime_access") else "No",
            (u.get("welcome_email_sent_at") or "")[:19],
            (u.get("created_at") or "")[:19],
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=zurix_users.csv"},
    )


@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, x_admin_password: str = Header(None)):
    """Permanently delete a user account."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "deleted_id": user_id}


@router.get("/admin/codes/export-all")
async def export_all_codes_csv(x_admin_password: str = Header(None)):
    """Export ALL verification codes (every batch) as a single CSV spreadsheet."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    codes = await db.unique_codes.find({}, {"_id": 0}).sort("created_at", -1).to_list(None)

    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Code",
        "Verification URL",
        "Product",
        "Batch",
        "Purity",
        "Expiry Date",
        "Verification Count",
        "Created At",
    ])

    for c in codes:
        code_raw = (c.get("code") or "").replace("-", "")
        writer.writerow([
            c.get("code", ""),
            f"https://zurixsciences.com/verify?code={code_raw}",
            c.get("product_name", ""),
            c.get("batch_number", ""),
            c.get("purity", ""),
            c.get("expiry_date", ""),
            c.get("verification_count", 0),
            (c.get("created_at") or "")[:19] if c.get("created_at") else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=zurix_all_codes.csv"},
    )


@router.post("/admin/generate-labels")
async def generate_labels(request: Request, x_admin_password: str = Header(None)):
    """Generate printable QR code labels for Niimbot 14x22mm labels."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    codes_list = body.get("codes", [])
    if not codes_list:
        raise HTTPException(status_code=400, detail="No codes provided")
    if len(codes_list) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 labels per request")

    import qrcode
    from PIL import Image, ImageDraw, ImageFont

    # Niimbot 14x22mm at 300 DPI
    LABEL_W = 260  # 22mm
    LABEL_H = 165  # 14mm
    QR_SIZE = 130  # ~11mm QR code
    MARGIN = 6

    labels = []
    for code_str in codes_list:  # Process all codes
        # Generate QR with high error correction for small prints
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1,
        )
        qr.add_data(code_str)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.NEAREST)

        # Create label canvas
        label = Image.new("RGB", (LABEL_W, LABEL_H), "white")
        draw = ImageDraw.Draw(label)

        # Place QR on left side, vertically centered
        qr_y = (LABEL_H - QR_SIZE) // 2
        label.paste(qr_img, (MARGIN, qr_y))

        # Text area on the right of QR
        text_x = MARGIN + QR_SIZE + 8
        text_w = LABEL_W - text_x - MARGIN

        # Draw "ZURIX" brand
        try:
            font_brand = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            font_code = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7)
        except OSError:
            font_brand = ImageFont.load_default()
            font_code = ImageFont.load_default()

        draw.text((text_x, qr_y + 5), "ZURIX", fill="black", font=font_brand)

        # Draw the code in small wrapped text
        short_code = code_str.replace("ZX-", "")
        parts = short_code.split("-")
        line1 = "-".join(parts[:2]) if len(parts) >= 2 else short_code[:12]
        line2 = "-".join(parts[2:]) if len(parts) > 2 else ""

        draw.text((text_x, qr_y + 25), line1, fill="#333333", font=font_code)
        if line2:
            draw.text((text_x, qr_y + 36), line2, fill="#333333", font=font_code)

        # Draw "Scan to verify" text
        try:
            font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 6)
        except OSError:
            font_tiny = font_code
        draw.text((text_x, qr_y + QR_SIZE - 18), "Scan to verify", fill="#666666", font=font_tiny)

        # Convert to base64
        buf = io.BytesIO()
        label.save(buf, format="PNG", dpi=(300, 300))
        b64 = base64.b64encode(buf.getvalue()).decode()
        labels.append({"code": code_str, "image": f"data:image/png;base64,{b64}"})

    return {"labels": labels, "count": len(labels)}


@router.get("/admin/download-stacks-pdf")
async def download_stacks_pdf(password: str = None, x_admin_password: str = Header(None)):
    pw = x_admin_password or password
    if pw != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    import os
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "zurix_stacks_all.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(pdf_path, media_type="application/pdf", filename="zurix_stacks_all.pdf")


# ──────────────────── ADMIN: PAYMENTS DASHBOARD ────────────────────

from fastapi.responses import StreamingResponse
import csv


def _require_admin(x_admin_password: str):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/admin/payments/stats")
async def admin_payment_stats(x_admin_password: str = Header(None)):
    """Dashboard KPIs: revenue, paid orders, pending orders, conversion rate."""
    _require_admin(x_admin_password)

    PAID = {"finished", "confirmed"}
    PENDING = {"waiting", "confirming", "sending", "partially_paid"}

    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "revenue": {"$sum": "$price"},
        }}
    ]
    by_status = {x["_id"]: x async for x in db.lifetime_orders.aggregate(pipeline)}

    paid_count = sum(by_status.get(s, {}).get("count", 0) for s in PAID)
    pending_count = sum(by_status.get(s, {}).get("count", 0) for s in PENDING)
    revenue_total = sum(by_status.get(s, {}).get("revenue", 0) for s in PAID)
    total_orders = sum(x.get("count", 0) for x in by_status.values())
    conversion_rate = round((paid_count / total_orders) * 100, 1) if total_orders else 0

    users_with_access = await db.users.count_documents({"has_lifetime_access": True})

    return {
        "success": True,
        "revenue_total": round(revenue_total, 2),
        "paid_orders": paid_count,
        "pending_orders": pending_count,
        "total_orders": total_orders,
        "conversion_rate": conversion_rate,
        "users_with_access": users_with_access,
        "by_status": {k: {"count": v.get("count", 0), "revenue": round(v.get("revenue", 0), 2)} for k, v in by_status.items()},
    }


@router.get("/admin/payments/orders")
async def admin_payment_orders(
    x_admin_password: str = Header(None),
    status: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
):
    """Paginated list of payment orders with optional filters."""
    _require_admin(x_admin_password)

    query = {}
    if status and status != "all":
        if status == "paid":
            query["status"] = {"$in": ["finished", "confirmed"]}
        elif status == "pending":
            query["status"] = {"$in": ["waiting", "confirming", "sending", "partially_paid"]}
        else:
            query["status"] = status
    if q:
        query["$or"] = [
            {"user_email": {"$regex": q, "$options": "i"}},
            {"order_id": {"$regex": q, "$options": "i"}},
            {"pay_address": {"$regex": q, "$options": "i"}},
        ]

    total = await db.lifetime_orders.count_documents(query)
    orders = await db.lifetime_orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(min(limit, 500)).to_list(None)
    return {"success": True, "orders": orders, "total": total, "skip": skip, "limit": limit}


@router.get("/admin/payments/export.csv")
async def admin_payment_export_csv(x_admin_password: str = Header(None)):
    """Export all payment orders as CSV."""
    _require_admin(x_admin_password)

    orders = await db.lifetime_orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(None)

    def gen():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "order_id", "user_email", "user_id", "status", "price_usd",
            "pay_amount", "pay_currency", "pay_address",
            "np_payment_id", "created_at", "confirmed_at",
        ])
        yield buf.getvalue()
        for o in orders:
            buf.seek(0)
            buf.truncate(0)
            writer.writerow([
                o.get("order_id", ""),
                o.get("user_email", ""),
                o.get("user_id", ""),
                o.get("status", ""),
                o.get("price", ""),
                o.get("pay_amount", ""),
                o.get("pay_currency", ""),
                o.get("pay_address", ""),
                o.get("np_payment_id", ""),
                o.get("created_at", ""),
                o.get("confirmed_at", ""),
            ])
            yield buf.getvalue()

    filename = f"zurix_payments_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        gen(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/admin/payments/grant-access")
async def admin_grant_access(request: Request, x_admin_password: str = Header(None)):
    """Manually grant Lifetime Access to a user by email. Creates a manual order record."""
    _require_admin(x_admin_password)
    body = await request.json()
    email = (body.get("email") or "").lower().strip()
    note = (body.get("note") or "").strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {email}")

    if user.get("has_lifetime_access"):
        return {"success": True, "already_had_access": True, "user_id": user["id"]}

    now = datetime.now(timezone.utc).isoformat()
    order_id = f"MANUAL-{uuid.uuid4().hex[:10].upper()}"

    await db.lifetime_orders.insert_one({
        "order_id": order_id,
        "user_id": user["id"],
        "user_email": email,
        "np_payment_id": None,
        "price": 0,
        "pay_amount": 0,
        "pay_currency": "manual",
        "pay_address": None,
        "status": "confirmed",
        "source": "admin_manual",
        "admin_note": note,
        "created_at": now,
        "confirmed_at": now,
    })

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "has_lifetime_access": True,
            "payment_id": order_id,
            "access_granted_at": now,
        }}
    )

    logging.info(f"Admin manually granted Lifetime Access to {email} (order={order_id}, note='{note}')")
    return {"success": True, "user_id": user["id"], "order_id": order_id, "user_email": email}


@router.post("/admin/payments/revoke-access")
async def admin_revoke_access(request: Request, x_admin_password: str = Header(None)):
    """Revoke Lifetime Access from a user (e.g. refund, chargeback)."""
    _require_admin(x_admin_password)
    body = await request.json()
    email = (body.get("email") or "").lower().strip()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found: {email}")

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "has_lifetime_access": False,
            "access_revoked_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    logging.info(f"Admin revoked Lifetime Access from {email}")
    return {"success": True, "user_email": email}
