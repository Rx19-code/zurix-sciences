import os
import logging
from datetime import datetime, timezone

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import db, client
from utils.security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware, IPBlockMiddleware

# Import routers
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.protocols import router as protocols_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router
from routes.verification import router as verification_router
from routes.library import router as library_router

# Create app
app = FastAPI()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Root endpoint
@app.get("/api/")
async def root():
    return {"message": "Zurix Sciences API", "version": "2.0.0"}

# Health check
@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Include routers
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(protocols_router)
app.include_router(payments_router)
app.include_router(admin_router)
app.include_router(verification_router)
app.include_router(library_router)

# Middleware stack (order matters - last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(IPBlockMiddleware)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Unhandled error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# DB indexes on startup
@app.on_event("startup")
async def create_indexes():
    try:
        await db.unique_codes.create_index("code", unique=True)
        await db.unique_codes.create_index("batch_number")
        await db.unique_codes.create_index("product_name")
        await db.products.create_index("name")
        await db.protocol_leads.create_index("email")
        await db.protocol_leads.create_index("verification_code")
        await db.users.create_index("email", unique=True)
        await db.verification_logs.create_index("code")
        await db.verification_logs.create_index("verified_at")
        logging.info("MongoDB indexes created successfully")
    except Exception as e:
        logging.warning(f"Index creation warning: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
