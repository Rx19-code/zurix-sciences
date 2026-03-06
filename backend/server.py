from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, Header, Request, UploadFile, File
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import hashlib
import httpx
import bcrypt
import jwt
import secrets
import resend
import asyncio
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend email configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# PDF storage directory
PDF_STORAGE_DIR = ROOT_DIR / "protocols_pdf"
PDF_STORAGE_DIR.mkdir(exist_ok=True)

async def send_protocol_email(user_email: str, user_name: str, protocol: dict, pdf_path: Path = None):
    """Send protocol purchase confirmation email with PDF attachment"""
    if not RESEND_API_KEY:
        logging.warning("Resend API key not configured - email not sent")
        return None
    
    # Build email HTML
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1e3a8a;">Zurix Sciences</h1>
            <p style="color: #666;">Research Peptides</p>
        </div>
        
        <h2 style="color: #333;">Thank you for your purchase, {user_name}!</h2>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #1e3a8a; margin-top: 0;">{protocol['title']}</h3>
            <p style="color: #666;">{protocol['description']}</p>
            <p><strong>Category:</strong> {protocol.get('category', 'Basic')}</p>
            <p><strong>Duration:</strong> {protocol.get('duration_weeks', 4)} weeks</p>
        </div>
        
        {"<p style='color: #333;'><strong>Your protocol PDF is attached to this email.</strong></p>" if pdf_path else "<p style='color: #f59e0b;'><strong>Note:</strong> The PDF for this protocol is being prepared and will be sent separately.</p>"}
        
        <p style="color: #666;">You can also download your protocol anytime from the Zurix Sciences app in the Protocols section.</p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #999; font-size: 12px; text-align: center;">
            This email was sent by Zurix Sciences.<br>
            For research use only. Not for human consumption.
        </p>
    </div>
    """
    
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [user_email],
            "subject": f"Your Protocol: {protocol['title']} - Zurix Sciences",
            "html": html_content
        }
        
        # Add PDF attachment if available
        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                pdf_content = base64.b64encode(f.read()).decode()
            params["attachments"] = [{
                "filename": f"{protocol['title']}.pdf",
                "content": pdf_content
            }]
        
        # Run sync SDK in thread to keep FastAPI non-blocking
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        logging.info(f"Email sent to {user_email} for protocol {protocol['id']}")
        return email_result
    except Exception as e:
        logging.error(f"Failed to send email to {user_email}: {str(e)}")
        return None

# Geolocation cache to avoid repeated API calls
geo_cache = {}

async def get_geolocation(ip: str) -> dict:
    """Get geolocation data for an IP address"""
    if ip in geo_cache:
        return geo_cache[ip]
    
    # Skip private/local IPs
    if ip.startswith(('10.', '172.', '192.168.', '127.', 'unknown')):
        return {"country": "Local", "city": "Local", "country_code": "XX"}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    result = {
                        "country": data.get('country', 'Unknown'),
                        "city": data.get('city', 'Unknown'),
                        "country_code": data.get('countryCode', 'XX')
                    }
                    geo_cache[ip] = result
                    return result
    except Exception as e:
        logging.error(f"Geolocation error for {ip}: {e}")
    
    return {"country": "Unknown", "city": "Unknown", "country_code": "XX"}

# Admin password (hashed)
ADMIN_PASSWORD = "Rx050217!"

# JWT Secret for authentication
JWT_SECRET = os.environ.get('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

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
    image_url: Optional[str] = None

class Representative(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    country: str
    region: str
    name: str
    whatsapp: str
    threema: Optional[str] = None
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

# ==================== USER AUTHENTICATION MODELS ====================

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: str
    purchased_protocols: List[str] = []

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    purchased_protocols: List[str] = []  # List of protocol IDs
    verification_history: List[str] = []  # List of verification IDs

class ProtocolWithPDF(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str  # Basic or Advanced
    price: float  # 4.99 or 9.99
    duration_weeks: int
    products_needed: List[str]
    pdf_filename: Optional[str] = None  # PDF file name
    preview_text: str  # Short preview for non-purchasers
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    featured: bool = False

class PurchaseProtocolRequest(BaseModel):
    protocol_id: str
    transaction_id: str  # From Google Play or Apple Store
    platform: str  # "google" or "apple"

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

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

# ==================== AUTHENTICATION HELPERS ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    """Create a JWT token for a user"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: str = Header(None)) -> dict:
    """Get the current user from the Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_jwt_token(token)
    
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# ==================== USER AUTHENTICATION ROUTES ====================

@api_router.post("/auth/register")
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    # Check if email already exists
    existing = await db.users.find_one({"email": request.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = {
        "id": str(uuid.uuid4()),
        "email": request.email.lower(),
        "password_hash": hash_password(request.password),
        "name": request.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purchased_protocols": [],
        "verification_history": []
    }
    
    await db.users.insert_one(user)
    
    # Create token
    token = create_jwt_token(user["id"], user["email"])
    
    return {
        "success": True,
        "message": "Registration successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"],
            "purchased_protocols": []
        }
    }

@api_router.post("/auth/login")
async def login_user(request: UserLoginRequest):
    """Login a user"""
    user = await db.users.find_one({"email": request.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    token = create_jwt_token(user["id"], user["email"])
    
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"],
            "purchased_protocols": user.get("purchased_protocols", [])
        }
    }

@api_router.get("/auth/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "success": True,
        "user": user
    }

@api_router.post("/auth/request-password-reset")
async def request_password_reset(request: PasswordResetRequest):
    """Request a password reset (sends email with token)"""
    user = await db.users.find_one({"email": request.email.lower()})
    if not user:
        # Don't reveal if email exists
        return {"success": True, "message": "If the email exists, a reset link will be sent"}
    
    # Create reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    await db.password_resets.insert_one({
        "user_id": user["id"],
        "token": reset_token,
        "expires_at": expires_at.isoformat(),
        "used": False
    })
    
    # TODO: Send email with reset link when email service is configured
    # For now, return the token (remove in production)
    return {
        "success": True,
        "message": "Password reset requested",
        "reset_token": reset_token  # Remove this in production
    }

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password with token"""
    reset = await db.password_resets.find_one({
        "token": request.token,
        "used": False
    })
    
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check expiration
    expires_at = datetime.fromisoformat(reset["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    # Update password
    new_hash = hash_password(request.new_password)
    await db.users.update_one(
        {"id": reset["user_id"]},
        {"$set": {"password_hash": new_hash}}
    )
    
    # Mark token as used
    await db.password_resets.update_one(
        {"token": request.token},
        {"$set": {"used": True}}
    )
    
    return {"success": True, "message": "Password reset successful"}

# ==================== PROTOCOLS WITH BATCH VALIDATION ====================

# Protocol definitions - keywords to match batch/product names
PROTOCOL_DEFINITIONS = {
    "proto-bpc157": {
        "title": "BPC-157 Recovery Protocol",
        "description": "A comprehensive healing protocol designed to accelerate tissue repair and reduce inflammation.",
        "category": "Basic",
        "duration_weeks": 4,
        "product_keywords": ["BPC-157", "BPC157", "BPC"],
        "languages": {
            "en": "bpc157_protocol_en.pdf",
            "es": "bpc157_protocol_es.pdf",
            "pt": "bpc157_protocol_pt.pdf"
        },
        "price": 0,
        "requires_batch": True
    },
    "proto-tb500": {
        "title": "TB-500 Tissue Repair Protocol",
        "description": "Advanced protocol for deep tissue healing and muscle recovery.",
        "category": "Basic",
        "duration_weeks": 6,
        "product_keywords": ["TB-500", "TB500", "TB-5", "thymosin beta"],
        "languages": {
            "en": "tb500_protocol_en.pdf",
            "es": "tb500_protocol_es.pdf",
            "pt": "tb500_protocol_pt.pdf"
        },
        "price": 0,
        "requires_batch": True
    },
    "proto-ghkcu": {
        "title": "GHK-Cu Skin Rejuvenation Protocol",
        "description": "Protocol for skin repair and anti-aging using copper peptides.",
        "category": "Basic",
        "duration_weeks": 8,
        "product_keywords": ["GHK-Cu", "GHK-CU", "GHKCU", "GHK50", "GHK100", "GHK"],
        "languages": {
            "en": "ghkcu_protocol_en.pdf",
            "es": "ghkcu_protocol_es.pdf",
            "pt": "ghkcu_protocol_pt.pdf"
        },
        "price": 0,
        "requires_batch": True
    },
    # Advanced Protocols - Paid
    "proto-advanced-stack": {
        "title": "Advanced Peptide Stack Protocol",
        "description": "Comprehensive stacking protocol combining multiple peptides for maximum synergistic effects. Includes dosing schedules, timing, and cycling guidelines.",
        "category": "Advanced",
        "duration_weeks": 12,
        "product_keywords": [],
        "languages": {
            "en": "advanced_stack_protocol_en.pdf",
            "es": "advanced_stack_protocol_es.pdf",
            "pt": "advanced_stack_protocol_pt.pdf"
        },
        "price": 4.99,
        "requires_batch": False
    },
    "proto-advanced-healing": {
        "title": "Advanced Injury Recovery Protocol",
        "description": "Professional-grade recovery protocol for serious injuries. Detailed protocols for tendons, ligaments, and tissue repair with optimized dosing.",
        "category": "Advanced",
        "duration_weeks": 16,
        "product_keywords": [],
        "languages": {
            "en": "advanced_healing_protocol_en.pdf",
            "es": "advanced_healing_protocol_es.pdf",
            "pt": "advanced_healing_protocol_pt.pdf"
        },
        "price": 4.99,
        "requires_batch": False
    },
    "proto-advanced-antiaging": {
        "title": "Advanced Anti-Aging Protocol",
        "description": "Complete longevity and anti-aging protocol using peptide combinations. Includes skin, cognitive, and cellular rejuvenation strategies.",
        "category": "Advanced",
        "duration_weeks": 24,
        "product_keywords": [],
        "languages": {
            "en": "advanced_antiaging_protocol_en.pdf",
            "es": "advanced_antiaging_protocol_es.pdf",
            "pt": "advanced_antiaging_protocol_pt.pdf"
        },
        "price": 4.99,
        "requires_batch": False
    }
}

# USDT Payment Configuration (TRC20 - Tron Network)
USDT_WALLET_ADDRESS = "TJKuseoNmGw1TnwskKjaBCw5FrYUynAP9m"
TRON_API_URL = "https://apilist.tronscanapi.com/api"

class ValidateBatchRequest(BaseModel):
    protocol_id: str
    batch_number: str

class DownloadProtocolRequest(BaseModel):
    protocol_id: str
    batch_number: str
    language: str  # "en", "es", "pt"

class SendProtocolEmailRequest(BaseModel):
    protocol_id: str
    batch_number: str
    language: str  # "en", "es", "pt"
    email: str
    phone: Optional[str] = None
    name: Optional[str] = None

# USDT Payment Models
class CreatePaymentRequest(BaseModel):
    protocol_id: str
    email: str
    language: str
    phone: Optional[str] = None
    name: Optional[str] = None

class VerifyPaymentRequest(BaseModel):
    order_id: str
    txid: str

async def verify_tron_transaction(txid: str, expected_amount: float, wallet_address: str) -> dict:
    """Verify a USDT TRC20 transaction on Tron network"""
    try:
        # Query TronScan API for transaction details
        async with httpx.AsyncClient(timeout=30) as client:
            # Get transaction info
            response = await client.get(
                f"{TRON_API_URL}/transaction-info",
                params={"hash": txid}
            )
            
            if response.status_code != 200:
                return {"valid": False, "message": "Could not verify transaction. Please try again."}
            
            tx_data = response.json()
            
            # Check if transaction exists
            if not tx_data or "contractRet" not in tx_data:
                return {"valid": False, "message": "Transaction not found. Please check the TXID."}
            
            # Check if transaction was successful
            if tx_data.get("contractRet") != "SUCCESS":
                return {"valid": False, "message": "Transaction failed or pending."}
            
            # Check TRC20 token transfers
            token_transfers = tx_data.get("trc20TransferInfo", [])
            
            for transfer in token_transfers:
                to_address = transfer.get("to_address", "")
                amount_str = transfer.get("amount_str", "0")
                decimals = int(transfer.get("decimals", 6))
                symbol = transfer.get("symbol", "")
                
                # Check if it's USDT to our wallet
                if to_address == wallet_address and symbol == "USDT":
                    amount = float(amount_str) / (10 ** decimals)
                    
                    if amount >= expected_amount:
                        return {
                            "valid": True,
                            "message": "Payment verified!",
                            "amount": amount,
                            "txid": txid
                        }
                    else:
                        return {
                            "valid": False,
                            "message": f"Amount too low. Expected ${expected_amount}, received ${amount:.2f}"
                        }
            
            return {"valid": False, "message": "No USDT transfer found to our wallet in this transaction."}
            
    except Exception as e:
        logging.error(f"Error verifying Tron transaction: {str(e)}")
        return {"valid": False, "message": "Error verifying transaction. Please try again or contact support."}

async def check_batch_matches_protocol(batch_number: str, protocol_id: str) -> dict:
    """Check if a batch number matches a protocol by searching unique_codes collection"""
    protocol = PROTOCOL_DEFINITIONS.get(protocol_id)
    if not protocol:
        return {"valid": False, "message": "Protocol not found"}
    
    batch_upper = batch_number.upper().strip()
    keywords = protocol["product_keywords"]
    
    # Check 1: Search in unique_codes collection (Imported Batches from admin)
    # The batch_number format is like ZX-260312-GHK50-1
    unique_code = await db.unique_codes.find_one({
        "batch_number": batch_upper
    }, {"_id": 0})
    
    if unique_code:
        # Found the batch - check if it matches the protocol keywords
        code_batch = unique_code.get("batch_number", "").upper()
        code_product = unique_code.get("product_name", "").upper()
        
        for keyword in keywords:
            keyword_upper = keyword.upper()
            if keyword_upper in code_batch or keyword_upper in code_product:
                return {
                    "valid": True,
                    "message": f"Batch validated for {unique_code.get('product_name', 'product')}!",
                    "product_name": unique_code.get("product_name")
                }
        
        # Batch exists but doesn't match this protocol
        return {
            "valid": False,
            "message": f"This batch is for {unique_code.get('product_name', 'another product')}, not for this protocol."
        }
    
    # Check 2: Check if the batch_number itself contains protocol keywords
    # e.g., ZX-260209-TB500-1 contains "TB500"
    for keyword in keywords:
        if keyword.upper() in batch_upper:
            # Check if any batch with this number exists
            exists = await db.unique_codes.find_one({
                "batch_number": {"$regex": f"^{batch_upper}", "$options": "i"}
            }, {"_id": 0})
            if exists:
                return {
                    "valid": True,
                    "message": f"Batch validated for {exists.get('product_name', 'product')}!",
                    "product_name": exists.get("product_name")
                }
    
    return {"valid": False, "message": "Batch number not found."}

@api_router.get("/protocols-v2")
async def get_protocols_v2():
    """Get all available protocols (free and paid)"""
    protocols = []
    for proto_id, proto_data in PROTOCOL_DEFINITIONS.items():
        protocols.append({
            "id": proto_id,
            "title": proto_data["title"],
            "description": proto_data["description"],
            "category": proto_data["category"],
            "duration_weeks": proto_data["duration_weeks"],
            "languages": list(proto_data["languages"].keys()),
            "requires_batch": proto_data.get("requires_batch", True),
            "price": proto_data.get("price", 0)
        })
    
    return {"success": True, "protocols": protocols}

@api_router.post("/protocols-v2/validate-batch")
async def validate_batch_for_protocol(request: ValidateBatchRequest):
    """Validate if a batch number unlocks a specific protocol"""
    protocol = PROTOCOL_DEFINITIONS.get(request.protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    # Use the dynamic batch checking function
    result = await check_batch_matches_protocol(request.batch_number, request.protocol_id)
    
    if result["valid"]:
        return {
            "success": True,
            "valid": True,
            "message": result["message"],
            "available_languages": [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Español"},
                {"code": "pt", "name": "Português"}
            ]
        }
    
    return {
        "success": True,
        "valid": False,
        "message": result["message"] + " Please enter a valid batch number from your product label."
    }

@api_router.get("/protocols-v2/download")
async def download_protocol_with_batch(
    protocol_id: str,
    batch_number: str,
    language: str
):
    """Download protocol PDF after batch validation"""
    protocol = PROTOCOL_DEFINITIONS.get(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    # Validate language
    if language not in protocol["languages"]:
        raise HTTPException(status_code=400, detail="Invalid language selected")
    
    # Validate batch using the dynamic function
    result = await check_batch_matches_protocol(batch_number, protocol_id)
    
    if not result["valid"]:
        raise HTTPException(status_code=403, detail="Invalid batch number")
    
    # Get PDF filename for the selected language
    pdf_filename = protocol["languages"][language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not available yet for {language.upper()}. Please contact support.")
    
    # Log the download
    await db.protocol_downloads.insert_one({
        "protocol_id": protocol_id,
        "batch_number": batch_number.upper().strip(),
        "language": language,
        "downloaded_at": datetime.now(timezone.utc).isoformat()
    })
    
    return FileResponse(
        path=str(pdf_path),
        filename=f"{protocol['title']} ({language.upper()}).pdf",
        media_type="application/pdf"
    )

@api_router.post("/protocols-v2/send-email")
async def send_protocol_via_email(request: SendProtocolEmailRequest):
    """Send protocol PDF via email and save customer data"""
    protocol = PROTOCOL_DEFINITIONS.get(request.protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    # Validate language
    if request.language not in protocol["languages"]:
        raise HTTPException(status_code=400, detail="Invalid language selected")
    
    # Validate batch using the dynamic function
    result = await check_batch_matches_protocol(request.batch_number, request.protocol_id)
    
    if not result["valid"]:
        raise HTTPException(status_code=403, detail="Invalid batch number")
    
    # Get PDF path
    pdf_filename = protocol["languages"][request.language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not available yet for {request.language.upper()}. Please contact support.")
    
    # Save customer data to database
    customer_data = {
        "email": request.email.lower().strip(),
        "phone": request.phone.strip() if request.phone else None,
        "name": request.name.strip() if request.name else None,
        "protocol_id": request.protocol_id,
        "protocol_title": protocol["title"],
        "batch_number": request.batch_number.upper().strip(),
        "language": request.language,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "website_protocols"
    }
    
    # Insert or update customer record
    await db.protocol_leads.update_one(
        {"email": customer_data["email"]},
        {"$set": customer_data, "$inc": {"download_count": 1}},
        upsert=True
    )
    
    # Send email with PDF attachment
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    # Build language-specific content
    lang_content = {
        "en": {
            "subject": f"Your Research Protocol: {protocol['title']}",
            "greeting": f"Hello{' ' + request.name if request.name else ''}!",
            "intro": "Thank you for your interest in Zurix Sciences research protocols.",
            "attached": "Your requested protocol is attached to this email as a PDF.",
            "duration": f"Protocol Duration: {protocol['duration_weeks']} weeks",
            "footer": "For research use only. Not for human consumption."
        },
        "es": {
            "subject": f"Tu Protocolo de Investigación: {protocol['title']}",
            "greeting": f"¡Hola{' ' + request.name if request.name else ''}!",
            "intro": "Gracias por tu interés en los protocolos de investigación de Zurix Sciences.",
            "attached": "Tu protocolo solicitado está adjunto a este correo como PDF.",
            "duration": f"Duración del Protocolo: {protocol['duration_weeks']} semanas",
            "footer": "Solo para uso en investigación. No para consumo humano."
        },
        "pt": {
            "subject": f"Seu Protocolo de Pesquisa: {protocol['title']}",
            "greeting": f"Olá{' ' + request.name if request.name else ''}!",
            "intro": "Obrigado pelo seu interesse nos protocolos de pesquisa da Zurix Sciences.",
            "attached": "Seu protocolo solicitado está anexado a este email em PDF.",
            "duration": f"Duração do Protocolo: {protocol['duration_weeks']} semanas",
            "footer": "Apenas para uso em pesquisa. Não para consumo humano."
        }
    }
    
    content = lang_content.get(request.language, lang_content["en"])
    
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
            <p><strong>{content['duration']}</strong></p>
        </div>
        
        <p style="color: #333; background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <strong>✓</strong> {content['attached']}
        </p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #999; font-size: 12px; text-align: center;">
            {content['footer']}<br>
            © Zurix Sciences - zurixsciences.com
        </p>
    </div>
    """
    
    try:
        # Read PDF for attachment
        with open(pdf_path, "rb") as f:
            pdf_content = base64.b64encode(f.read()).decode()
        
        params = {
            "from": SENDER_EMAIL,
            "to": [request.email],
            "subject": content["subject"],
            "html": html_content,
            "attachments": [{
                "filename": f"{protocol['title']} ({request.language.upper()}).pdf",
                "content": pdf_content
            }]
        }
        
        # Send email
        email_result = await asyncio.to_thread(resend.Emails.send, params)
        
        # Log the email send
        await db.protocol_downloads.insert_one({
            "protocol_id": request.protocol_id,
            "batch_number": request.batch_number.upper().strip(),
            "language": request.language,
            "email": request.email.lower().strip(),
            "phone": request.phone,
            "sent_via": "email",
            "downloaded_at": datetime.now(timezone.utc).isoformat()
        })
        
        logging.info(f"Protocol email sent to {request.email} for {protocol['title']}")
        
        return {
            "success": True,
            "message": f"Protocol sent to {request.email}",
            "email_id": email_result.get("id") if email_result else None
        }
        
    except Exception as e:
        logging.error(f"Failed to send protocol email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# ==================== USDT PAYMENT ENDPOINTS ====================

@api_router.get("/payment/wallet-info")
async def get_wallet_info():
    """Get USDT wallet address for payment"""
    return {
        "success": True,
        "wallet_address": USDT_WALLET_ADDRESS,
        "network": "TRC20 (Tron)",
        "currency": "USDT"
    }

@api_router.post("/payment/create-order")
async def create_payment_order(request: CreatePaymentRequest):
    """Create a new payment order for a paid protocol"""
    protocol = PROTOCOL_DEFINITIONS.get(request.protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    price = protocol.get("price", 0)
    if price <= 0:
        raise HTTPException(status_code=400, detail="This protocol is free. Use batch validation instead.")
    
    # Generate unique order ID
    order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
    
    # Create order in database
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

@api_router.post("/payment/verify")
async def verify_payment(request: VerifyPaymentRequest):
    """Verify a USDT payment and deliver the protocol"""
    # Find the order
    order = await db.protocol_orders.find_one({"order_id": request.order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] == "completed":
        return {
            "success": True,
            "already_paid": True,
            "message": "This order has already been paid and the protocol was sent."
        }
    
    # Check if TXID was already used
    existing_txid = await db.protocol_orders.find_one({"txid": request.txid, "status": "completed"})
    if existing_txid:
        raise HTTPException(status_code=400, detail="This transaction has already been used for another order.")
    
    # Verify the transaction on Tron network
    verification = await verify_tron_transaction(
        txid=request.txid,
        expected_amount=order["price"],
        wallet_address=USDT_WALLET_ADDRESS
    )
    
    if not verification["valid"]:
        return {
            "success": False,
            "message": verification["message"]
        }
    
    # Payment verified! Update order
    await db.protocol_orders.update_one(
        {"order_id": request.order_id},
        {"$set": {
            "status": "completed",
            "txid": request.txid,
            "paid_at": datetime.now(timezone.utc).isoformat(),
            "verified_amount": verification.get("amount")
        }}
    )
    
    # Get protocol details
    protocol = PROTOCOL_DEFINITIONS.get(order["protocol_id"])
    if not protocol:
        raise HTTPException(status_code=500, detail="Protocol configuration error")
    
    # Send protocol via email
    pdf_filename = protocol["languages"].get(order["language"], protocol["languages"]["en"])
    pdf_path = PDF_STORAGE_DIR / pdf_filename
    
    if not pdf_path.exists():
        # Still mark as paid, but notify about PDF
        return {
            "success": True,
            "message": "Payment verified! However, the PDF is being prepared. You will receive it by email within 24 hours.",
            "paid": True,
            "email_sent": False
        }
    
    # Build email content
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
            <strong>✓</strong> {content['attached']}
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
            © Zurix Sciences - zurixsciences.com
        </p>
    </div>
    """
    
    try:
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
        
        return {
            "success": True,
            "message": f"Payment verified! Protocol sent to {order['email']}",
            "paid": True,
            "email_sent": True
        }
        
    except Exception as e:
        logging.error(f"Failed to send paid protocol email: {str(e)}")
        return {
            "success": True,
            "message": "Payment verified! There was an issue sending the email. Please contact support.",
            "paid": True,
            "email_sent": False,
            "error": str(e)
        }

@api_router.get("/payment/order/{order_id}")
async def get_order_status(order_id: str):
    """Check order status"""
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

# ==================== ADMIN PROTOCOL MANAGEMENT ====================

# Admin endpoint to upload protocol PDFs
@api_router.post("/admin/protocols/upload-pdf")
async def upload_protocol_pdf(
    protocol_id: str,
    language: str,  # "en", "es", "pt"
    pdf: UploadFile = File(...),
    x_admin_password: str = Header(None, alias="X-Admin-Password")
):
    """Upload a protocol PDF for a specific language"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if protocol_id not in PROTOCOL_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    if language not in ["en", "es", "pt"]:
        raise HTTPException(status_code=400, detail="Invalid language. Use: en, es, or pt")
    
    protocol = PROTOCOL_DEFINITIONS[protocol_id]
    pdf_filename = protocol["languages"][language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename
    
    # Save PDF
    content = await pdf.read()
    with open(pdf_path, "wb") as f:
        f.write(content)
    
    return {
        "success": True,
        "message": f"PDF uploaded successfully for {protocol['title']} ({language.upper()})",
        "filename": pdf_filename
    }

@api_router.get("/admin/protocols/status")
async def get_protocols_status(x_admin_password: str = Header(None, alias="X-Admin-Password")):
    """Get status of all protocol PDFs"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    status = []
    for proto_id, proto_data in PROTOCOL_DEFINITIONS.items():
        languages_status = {}
        for lang, filename in proto_data["languages"].items():
            pdf_path = PDF_STORAGE_DIR / filename
            languages_status[lang] = {
                "filename": filename,
                "uploaded": pdf_path.exists()
            }
        
        status.append({
            "id": proto_id,
            "title": proto_data["title"],
            "valid_batches": proto_data["valid_batches"],
            "languages": languages_status
        })
    
    # Get download stats
    downloads = await db.protocol_downloads.count_documents({})
    
    return {
        "success": True,
        "protocols": status,
        "total_downloads": downloads
    }

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
    
    # Get geolocation
    geo = await get_geolocation(client_ip)
    
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
        # Check if code is blocked (3+ verifications)
        current_count = unique_code.get('verification_count', 0)
        if current_count >= 3:
            return VerifyProductResponse(
                success=False,
                message="🚫 CODE BLOCKED - This code has exceeded the maximum number of verifications. Please contact support immediately.",
                verification_count=current_count,
                warning_level="blocked"
            )
        
        # Found in unique codes - update verification count
        verification_count = current_count + 1
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
        
        # Log verification with IP, device info, and geolocation
        log_entry = {
            "id": str(uuid.uuid4()),
            "code": code,
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
        
        # Determine warning level and message
        if verification_count == 1:
            message = "✅ Product Authenticated! This is the FIRST verification."
            warning_level = "none"
        elif verification_count == 2:
            message = f"⚠️ CAUTION: This code was already verified on {first_verified[:10]}. If this wasn't you, the product may be counterfeit."
            warning_level = "caution"
        else:
            message = f"🚨 ALERT: This code has been verified {verification_count} times! This code is now BLOCKED."
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
async def get_admin_codes(
    x_admin_password: str = Header(None), 
    batch_number: Optional[str] = None, 
    search: Optional[str] = None,
    limit: int = 100,
    skip: int = 0
):
    """Get unique codes with pagination (admin only)"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = {}
    if batch_number:
        query["batch_number"] = batch_number.upper()
    
    # Search by code, product_name, or batch_number
    if search:
        search_upper = search.upper()
        query["$or"] = [
            {"code": {"$regex": search_upper, "$options": "i"}},
            {"product_name": {"$regex": search, "$options": "i"}},
            {"batch_number": {"$regex": search_upper, "$options": "i"}}
        ]
    
    # Get total count for the query
    total_matching = await db.unique_codes.count_documents(query)
    total_all = await db.unique_codes.count_documents({})
    
    # Get paginated results
    codes = await db.unique_codes.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "codes": codes, 
        "total": total_all, 
        "total_matching": total_matching,
        "showing": len(codes),
        "skip": skip,
        "has_more": skip + len(codes) < total_matching
    }

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

@api_router.delete("/admin/code/{code}")
async def delete_single_code(code: str, x_admin_password: str = Header(None)):
    """Delete a single code (admin only)"""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await db.unique_codes.delete_one({"code": code.upper()})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Code not found")
    
    return {
        "success": True,
        "message": f"Code {code} deleted successfully"
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
    
    # Get geolocation
    geo = await get_geolocation(client_ip)
    
    # First try unique_codes collection (new system with ZX- prefix)
    if code.startswith("ZX-"):
        unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})
        
        if unique_code:
            # Check if code is blocked (3+ verifications)
            current_count = unique_code.get('verification_count', 0)
            if current_count >= 3:
                return VerifyScanResponse(
                    success=False,
                    message="🚫 CODE BLOCKED - This code has exceeded the maximum number of verifications. Please contact support immediately.",
                    verification_count=current_count,
                    warning="blocked"
                )
            
            # Found in unique codes - update verification count
            verification_count = current_count + 1
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
            
            # Log verification with IP, device info, and geolocation
            log_entry = {
                "id": str(uuid.uuid4()),
                "code": code,
                "batch_number": unique_code.get('batch_number', ''),
                "product_name": unique_code.get('product_name', ''),
                "timestamp": now,
                "verification_number": verification_count,
                "device_id": request.device_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "country": geo.get('country', 'Unknown'),
                "city": geo.get('city', 'Unknown'),
                "country_code": geo.get('country_code', 'XX')
            }
            await db.verification_logs.insert_one(log_entry)
            
            # Get product info
            product = await db.products.find_one({"id": unique_code.get('product_id')}, {"_id": 0})
            
            # Determine warning
            warning = None
            if verification_count == 1:
                message = "✅ Product Authenticated! This is the FIRST verification."
            elif verification_count == 2:
                message = "⚠️ CAUTION: This code was already verified. If this wasn't you, the product may be counterfeit."
                warning = "caution"
            else:
                message = f"🚨 ALERT: This code has been verified {verification_count} times! This code is now BLOCKED."
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

# Test email endpoint (admin only)
class TestEmailRequest(BaseModel):
    email: EmailStr

@api_router.post("/admin/test-email")
async def send_test_email(request: TestEmailRequest, password: str = Header(..., alias="X-Admin-Password")):
    """Send a test email to verify Resend configuration"""
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    
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
