from fastapi import FastAPI, APIRouter, HTTPException, Query
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
    product: Optional[Product] = None
    message: str

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

class VerificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    verification_code: str
    batch_number: str
    timestamp: str
    device_id: Optional[str] = None
    location: Optional[str] = None

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

# Verification endpoint
@api_router.post("/verify-product", response_model=VerifyProductResponse)
async def verify_product(request: VerifyProductRequest):
    """Verify a product by its verification code"""
    code = request.code.strip().upper()
    
    # Check if code starts with ZX-
    if not code.startswith("ZX-"):
        return VerifyProductResponse(
            success=False,
            message="Invalid code format. All genuine Zurix Sciences products have codes starting with 'ZX-'"
        )
    
    # Find product
    product = await db.products.find_one({"verification_code": code}, {"_id": 0})
    
    if not product:
        return VerifyProductResponse(
            success=False,
            message="Product not found. This code may be counterfeit. Please contact support immediately."
        )
    
    return VerifyProductResponse(
        success=True,
        product=Product(**product),
        message="Product authenticated successfully!"
    )

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
async def verify_scan(request: VerifyScanRequest):
    """Verify a product and log the verification (for mobile app)"""
    code = request.code.strip().upper()
    
    # Check if code starts with CS-
    if not code.startswith("CS-"):
        return VerifyScanResponse(
            success=False,
            message="Invalid code format. All genuine Zurix Sciences products have codes starting with 'ZX-'",
            verification_count=0
        )
    
    # Find product
    product = await db.products.find_one({"verification_code": code}, {"_id": 0})
    
    if not product:
        return VerifyScanResponse(
            success=False,
            message="Product not found. This code may be counterfeit. Please contact support immediately.",
            verification_count=0
        )
    
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
