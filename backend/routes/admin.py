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
