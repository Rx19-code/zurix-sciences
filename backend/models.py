from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone


class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    product_type: str
    purity: str
    dosage: str
    description: str
    price: float
    verification_code: str
    storage_info: str
    batch_number: str
    manufacturing_date: str
    expiry_date: str
    coa_url: str
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
    warning_level: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    purity: Optional[str] = None
    expiry_date: Optional[str] = None


class Protocol(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    price: float
    duration_weeks: int
    products_needed: List[str]
    dosage_instructions: str
    frequency: str
    expected_results: str
    side_effects: str
    contraindications: str
    storage_tips: str
    reconstitution_guide: str
    featured: bool = False


class UniqueCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    batch_number: str
    product_id: str
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
    verification_number: int
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
    purity: Optional[str] = "≥99%"
    expiry_date: Optional[str] = None


class UpdateBatchRequest(BaseModel):
    batch_number: str
    purity: Optional[str] = None
    expiry_date: Optional[str] = None


# User Authentication models
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
    purchased_protocols: List[str] = []
    verification_history: List[str] = []


class ProtocolWithPDF(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    price: float
    duration_weeks: int
    products_needed: List[str]
    pdf_filename: Optional[str] = None
    preview_text: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    featured: bool = False


class PurchaseProtocolRequest(BaseModel):
    protocol_id: str
    transaction_id: str
    platform: str


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


class ValidateBatchRequest(BaseModel):
    protocol_id: str
    batch_number: str


class DownloadProtocolRequest(BaseModel):
    protocol_id: str
    batch_number: str
    language: str


class SendProtocolEmailRequest(BaseModel):
    protocol_id: str
    batch_number: str
    language: str
    email: str
    phone: Optional[str] = None
    name: Optional[str] = None


class ValidateUniqueCodeRequest(BaseModel):
    code: str


class SendProtocolByCodeRequest(BaseModel):
    code: str
    language: str
    email: str
    phone: Optional[str] = None
    name: Optional[str] = None


class CreatePaymentRequest(BaseModel):
    protocol_id: str
    email: str
    language: str
    phone: Optional[str] = None
    name: Optional[str] = None


class VerifyPaymentRequest(BaseModel):
    order_id: str
    txid: str


class UpdateProductImageRequest(BaseModel):
    product_name: str
    image_url: str


class TestEmailRequest(BaseModel):
    email: EmailStr
