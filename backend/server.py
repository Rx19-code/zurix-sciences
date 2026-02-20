from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, Header, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import hashlib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Admin password (hashed)
ADMIN_PASSWORD = "Rx050217!"

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # GLP-1 Analogs, Peptides, Cognitive Enhancers, Coenzymes
    product_type: str  # Tirzepatide, BPC-157, Semax, etc.
    purity: str  # 99% HPLC, etc.
    dosage: str  # 10mg, 1g, etc.
    description: str
    price: float
    verification_code: str  # CS-ze101208
    storage_info: str
    batch_number: str
    manufacturing_date: str
    expiry_date: str
    coa_url: str  # Certificate of Analysis URL
    featured: bool = False

class Representative(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    country: str
    region: str
    name: str
    whatsapp: str
    flag_emoji: str

class VerifyProductRequest(BaseModel):
    code: str

class VerifyProductResponse(BaseModel):
    success: bool
    product: Optional[dict] = None
    message: str
    verification_count: int = 0
    first_verified_at: Optional[str] = None
    warning_level: Optional[str] = None  # "none", "caution", "danger"

class Protocol(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str  # Basic or Advanced
    price: float  # 4.99 or 9.99
    duration_weeks: int
    products_needed: List[str]  # List of product names
    dosage_instructions: str
    frequency: str
    expected_results: str
    side_effects: str
    contraindications: str
    storage_tips: str
    reconstitution_guide: str
    featured: bool = False

# NEW: Unique QR Code model
class UniqueCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # ZX-261216-RT10-1-00038A (unique per unit)
    batch_number: str  # ZX-261216-RT10-1 (shared by batch)
    product_id: str  # Reference to product
    product_name: str
    verification_count: int = 0
    first_verified_at: Optional[str] = None
    last_verified_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class VerificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    batch_number: str
    product_name: str
    timestamp: str
    verification_number: int  # 1st, 2nd, 3rd verification
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Admin models
class AdminLoginRequest(BaseModel):
    password: str

class ImportCodesRequest(BaseModel):
    product_id: str
    product_name: str
    batch_number: str
    codes: List[str]

class VerifyScanRequest(BaseModel):
    code: str
    device_id: Optional[str] = None

class VerifyScanResponse(BaseModel):
    success: bool
    product: Optional[Product] = None
    message: str
    verification_count: int = 0
    warning: Optional[str] = None

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Zurix Sciences API", "version": "1.0.0"}

# Products endpoints
@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    product_type: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None
):
    """Get all products with optional filters"""
    query = {}
    
    if category:
        query['category'] = category
    if product_type:
        query['product_type'] = product_type
    if featured is not None:
        query['featured'] = featured
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
            {'product_type': {'$regex': search, '$options': 'i'}}
        ]
    
    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    return products

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a single product by ID"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.get("/products/code/{verification_code}", response_model=Product)
async def get_product_by_code(verification_code: str):
    """Get a product by verification code"""
    product = await db.products.find_one({"verification_code": verification_code}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.get("/categories")
async def get_categories():
    """Get all unique categories"""
    categories = await db.products.distinct("category")
    return {"categories": categories}

@api_router.get("/product-types")
async def get_product_types():
    """Get all unique product types"""
    types = await db.products.distinct("product_type")
    return {"types": sorted(types)}

# Representatives endpoints
@api_router.get("/representatives", response_model=List[Representative])
async def get_representatives():
    """Get all representatives"""
    reps = await db.representatives.find({}, {"_id": 0}).to_list(100)
    return reps

# Verification endpoint - NEW SYSTEM with unique codes
@api_router.post("/verify-product", response_model=VerifyProductResponse)
async def verify_product(request: VerifyProductRequest, req: Request):
    """Verify a product by its unique QR code"""
    code = request.code.strip().upper()
    
    # Get client info for tracking
    client_ip = req.headers.get("x-forwarded-for", req.client.host if req.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    user_agent = req.headers.get("user-agent", "unknown")
    
    # Check if code starts with ZX-
    if not code.startswith("ZX-"):
        return VerifyProductResponse(
            success=False,
            message="Invalid code format. All genuine Zurix Sciences products have codes starting with 'ZX-'",
            verification_count=0,
            warning_level="none"
        )
    
    # First, try to find in unique_codes collection (new system)
    unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})
    
    if unique_code:
        # Found in unique codes - update verification count
        verification_count = unique_code.get('verification_count', 0) + 1
        first_verified = unique_code.get('first_verified_at')
        now = datetime.now(timezone.utc).isoformat()
        
        # Update the code record
        update_data = {
            "verification_count": verification_count,
            "last_verified_at": now
        }
        if not first_verified:
            update_data["first_verified_at"] = now
            first_verified = now
        
        await db.unique_codes.update_one(
            {"code": code},
            {"$set": update_data}
        )
        
        # Log verification with IP and device info
        log_entry = {
            "id": str(uuid.uuid4()),
            "code": code,
            "batch_number": unique_code.get('batch_number', ''),
            "product_name": unique_code.get('product_name', ''),
            "timestamp": now,
            "verification_number": verification_count,
            "client_ip": client_ip,
            "user_agent": user_agent
        }
        await db.verification_logs.insert_one(log_entry)
        
        # Determine warning level and message
        if verification_count == 1:
            message = "✅ Product Authenticated! This is the FIRST verification."
            warning_level = "none"
        elif verification_count == 2:
            message = f"⚠️ CAUTION: This code was already verified on {first_verified[:10]}. If this wasn't you, the product may be counterfeit."
            warning_level = "caution"
        else:
            message = f"🚨 ALERT: This code has been verified {verification_count} times! HIGH RISK of counterfeit product."
            warning_level = "danger"
        
        # Get product info
        product = await db.products.find_one({"id": unique_code.get('product_id')}, {"_id": 0})
        
        return VerifyProductResponse(
            success=True,
            product=product,
            message=message,
            verification_count=verification_count,
            first_verified_at=first_verified,
            warning_level=warning_level
        )
    
    # Fallback: try old system (products collection)
    product = await db.products.find_one({"verification_code": code}, {"_id": 0})
    
    if product:
        return VerifyProductResponse(
            success=True,
            product=product,
            message="Product authenticated successfully!",
            verification_count=1,
            warning_level="none"
        )
    
    # Not found anywhere
    return VerifyProductResponse(
        success=False,
        message="❌ Code not found. This product may be COUNTERFEIT. Please contact support immediately.",
        verification_count=0,
        warning_level="danger"
    )

# ==================== ADMIN ROUTES ====================

@api_router.post("/admin/login")
async def admin_login(request: AdminLoginRequest):
    """Admin login"""
    if request.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid password")

@api_router.post("/admin/import-codes")
async def import_codes(request: ImportCodesRequest, x_admin_password: str = Header(None)):
    """Import unique verification codes for a product batch"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    codes = [c.strip().upper() for c in request.codes if c.strip()]
    
    if not codes:
        raise HTTPException(status_code=400, detail="No valid codes provided")
    
    # Check for duplicates in database
    existing = await db.unique_codes.find({"code": {"$in": codes}}, {"code": 1}).to_list(len(codes))
    existing_codes = {doc['code'] for doc in existing}
    
    new_codes = [c for c in codes if c not in existing_codes]
    
    if not new_codes:
        return {
            "success": False,
            "message": "All codes already exist in database",
            "imported": 0,
            "duplicates": len(codes)
        }
    
    # Prepare documents for insertion
    now = datetime.now(timezone.utc).isoformat()
    documents = []
    for code in new_codes:
        documents.append({
            "id": str(uuid.uuid4()),
            "code": code,
            "batch_number": request.batch_number.strip().upper(),
            "product_id": request.product_id,
            "product_name": request.product_name,
            "verification_count": 0,
            "first_verified_at": None,
            "last_verified_at": None,
            "created_at": now
        })
    
    # Insert all at once
    await db.unique_codes.insert_many(documents)
    
    return {
        "success": True,
        "message": f"Successfully imported {len(new_codes)} codes",
        "imported": len(new_codes),
        "duplicates": len(existing_codes)
    }

@api_router.get("/admin/codes")
async def get_admin_codes(x_admin_password: str = Header(None), batch_number: Optional[str] = None, limit: int = 100):
    """Get all unique codes (admin only)"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = {}
    if batch_number:
        query["batch_number"] = batch_number.upper()
    
    codes = await db.unique_codes.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    total = await db.unique_codes.count_documents(query)
    
    return {"codes": codes, "total": total, "showing": len(codes)}

@api_router.get("/admin/batches")
async def get_admin_batches(x_admin_password: str = Header(None)):
    """Get all unique batches (admin only)"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    pipeline = [
        {"$group": {
            "_id": "$batch_number",
            "product_name": {"$first": "$product_name"},
            "total_codes": {"$sum": 1},
            "verified_codes": {"$sum": {"$cond": [{"$gt": ["$verification_count", 0]}, 1, 0]}},
            "created_at": {"$min": "$created_at"}
        }},
        {"$sort": {"created_at": -1}}
    ]
    
    batches = await db.unique_codes.aggregate(pipeline).to_list(100)
    
    return {"batches": batches}

@api_router.get("/admin/verification-logs")
async def get_admin_verification_logs(x_admin_password: str = Header(None), limit: int = 100):
    """Get verification logs (admin only)"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logs = await db.verification_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"logs": logs, "total": len(logs)}

@api_router.delete("/admin/batch/{batch_number}")
async def delete_batch(batch_number: str, x_admin_password: str = Header(None)):
    """Delete all codes for a batch (admin only)"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await db.unique_codes.delete_many({"batch_number": batch_number.upper()})
    
    return {
        "success": True,
        "message": f"Deleted {result.deleted_count} codes from batch {batch_number}"
    }

# ==================== MOBILE APP ROUTES ====================

# Protocols endpoints
@api_router.get("/protocols", response_model=List[Protocol])
async def get_protocols(category: Optional[str] = None):
    """Get all protocols"""
    query = {}
    if category:
        query['category'] = category
    
    protocols = await db.protocols.find(query, {"_id": 0}).to_list(100)
    return protocols

@api_router.get("/protocols/{protocol_id}", response_model=Protocol)
async def get_protocol(protocol_id: str):
    """Get a single protocol by ID"""
    protocol = await db.protocols.find_one({"id": protocol_id}, {"_id": 0})
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol

# Enhanced verification with counter (for mobile app)
@api_router.post("/verify-scan", response_model=VerifyScanResponse)
async def verify_scan(request: VerifyScanRequest, req: Request):
    """Verify a product and log the verification (for mobile app)"""
    code = request.code.strip().upper()
    
    # Get client info for tracking
    client_ip = req.headers.get("x-forwarded-for", req.client.host if req.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()
    user_agent = req.headers.get("user-agent", "unknown")
    
    # First try unique_codes collection (new system with ZX- prefix)
    if code.startswith("ZX-"):
        unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})
        
        if unique_code:
            # Found in unique codes - update verification count
            verification_count = unique_code.get('verification_count', 0) + 1
            first_verified = unique_code.get('first_verified_at')
            now = datetime.now(timezone.utc).isoformat()
            
            # Update the code record
            update_data = {
                "verification_count": verification_count,
                "last_verified_at": now
            }
            if not first_verified:
                update_data["first_verified_at"] = now
                first_verified = now
            
            await db.unique_codes.update_one(
                {"code": code},
                {"$set": update_data}
            )
            
            # Log verification
            log_entry = {
                "id": str(uuid.uuid4()),
                "code": code,
                "batch_number": unique_code.get('batch_number', ''),
                "product_name": unique_code.get('product_name', ''),
                "timestamp": now,
                "verification_number": verification_count,
                "device_id": request.device_id
            }
            await db.verification_logs.insert_one(log_entry)
            
            # Get product info
            product = await db.products.find_one({"id": unique_code.get('product_id')}, {"_id": 0})
            
            # Determine warning
            warning = None
            if verification_count == 1:
                message = "✅ Product Authenticated! This is the FIRST verification."
            elif verification_count == 2:
                message = f"⚠️ CAUTION: This code was already verified. If this wasn't you, the product may be counterfeit."
                warning = "caution"
            else:
                message = f"🚨 ALERT: This code has been verified {verification_count} times! HIGH RISK of counterfeit product."
                warning = "danger"
            
            return VerifyScanResponse(
                success=True,
                product=Product(**product) if product else None,
                message=message,
                verification_count=verification_count,
                warning=warning
            )
    
    # Fallback: Try old system with CS- prefix or ZX- in products collection
    product = await db.products.find_one({"verification_code": code}, {"_id": 0})
    
    if product:
        # Log verification
        verification_log = {
            "id": str(uuid.uuid4()),
            "verification_code": code,
            "batch_number": product['batch_number'],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": request.device_id
        }
        await db.verification_logs.insert_one(verification_log)
        
        # Count total verifications for this batch
        verification_count = await db.verification_logs.count_documents({"batch_number": product['batch_number']})
        
        # Warning if verified too many times
        warning = None
        if verification_count > 10:
            warning = f"⚠️ WARNING: This batch has been verified {verification_count} times. This may indicate counterfeiting."
        elif verification_count > 5:
            warning = f"Note: This batch has been verified {verification_count} times."
        
        return VerifyScanResponse(
            success=True,
            product=Product(**product),
            message="Product authenticated successfully!",
            verification_count=verification_count,
            warning=warning
        )
    
    # Not found anywhere
    return VerifyScanResponse(
        success=False,
        message="❌ Code not found. This product may be COUNTERFEIT. Please contact support immediately.",
        verification_count=0,
        warning="danger"
    )

# Verification history
@api_router.get("/verification-history")
async def get_verification_history(device_id: Optional[str] = None, limit: int = 50):
    """Get verification history"""
    query = {}
    if device_id:
        query['device_id'] = device_id
    
    logs = await db.verification_logs.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"history": logs, "count": len(logs)}

# Batch verification stats
@api_router.get("/batch-stats/{batch_number}")
async def get_batch_stats(batch_number: str):
    """Get verification statistics for a batch"""
    count = await db.verification_logs.count_documents({"batch_number": batch_number})
    logs = await db.verification_logs.find({"batch_number": batch_number}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
    
    return {
        "batch_number": batch_number,
        "total_verifications": count,
        "recent_verifications": logs
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
