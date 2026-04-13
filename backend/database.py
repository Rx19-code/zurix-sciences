from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import time

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Environment config
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
USDT_WALLET_ADDRESS = os.environ.get('USDT_WALLET_ADDRESS')
TRON_API_URL = os.environ.get('TRON_API_URL', 'https://apilist.tronscanapi.com/api')
NOWPAYMENTS_API_KEY = os.environ.get('NOWPAYMENTS_API_KEY')
LIFETIME_ACCESS_PRICE = 39.99

# PDF storage directory
PDF_STORAGE_DIR = Path(os.environ.get('PDF_STORAGE_DIR', str(ROOT_DIR / "protocols_pdf")))
PDF_STORAGE_DIR.mkdir(exist_ok=True)

# Product images directory
PRODUCT_IMG_DIR = Path(os.environ.get('PRODUCT_IMG_DIR', str(ROOT_DIR / "product_images")))
PRODUCT_IMG_DIR.mkdir(exist_ok=True)

# Resend email setup
if RESEND_API_KEY:
    import resend
    resend.api_key = RESEND_API_KEY

# In-memory cache
_cache = {}
CACHE_TTL = 60


def get_cache(key):
    if key in _cache:
        value, expires_at = _cache[key]
        if time.time() < expires_at:
            return value
        del _cache[key]
    return None


def set_cache(key, value, ttl=CACHE_TTL):
    _cache[key] = (value, time.time() + ttl)
