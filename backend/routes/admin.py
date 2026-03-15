import logging
import uuid
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header, File, UploadFile, Request
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
            "created_at": now
        })

    await db.unique_codes.insert_many(documents)

    return {
        "success": True,
        "message": f"Successfully imported {len(new_codes)} codes",
        "imported": len(new_codes),
        "duplicates": len(existing_codes)
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


@router.get("/admin/codes")
async def get_admin_codes(
    x_admin_password: str = Header(None),
    batch_number: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = {}
    if batch_number:
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
