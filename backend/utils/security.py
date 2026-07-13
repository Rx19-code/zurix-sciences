import logging
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from fastapi import HTTPException, Header
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from database import db, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

# IP block tracker
ip_fail_tracker = defaultdict(lambda: {"count": 0, "blocked_until": 0})
IP_BLOCK_THRESHOLD = 15
IP_BLOCK_DURATION = 900


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with oversized bodies.

    The default limit protects JSON APIs from resource exhaustion.
    File-upload routes are exempt — they enforce their own size check
    (see routes/products.py `admin_upload_product_image` MAX_BYTES).
    """
    MAX_SIZE = 2_097_152  # 2 MB default (was 1MB — was rejecting normal image uploads)

    # Paths that are allowed to receive large bodies (file uploads).
    # Each route enforces its own size limit internally.
    UPLOAD_PATH_PREFIXES = (
        "/api/admin/products/upload-image",
        "/api/admin/upload",
    )
    UPLOAD_MAX_SIZE = 26_214_400  # 25 MB hard ceiling for uploads

    async def dispatch(self, request, call_next):
        path = request.url.path
        is_upload = any(path.startswith(p) for p in self.UPLOAD_PATH_PREFIXES)
        limit = self.UPLOAD_MAX_SIZE if is_upload else self.MAX_SIZE

        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > limit:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": (
                        f"Request too large. Maximum size for this endpoint is "
                        f"{limit // (1024 * 1024)}MB."
                    )
                },
            )
        return await call_next(request)


class IPBlockMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        client_ip = request.headers.get("x-forwarded-for", "")
        if client_ip and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        tracker = ip_fail_tracker[client_ip]
        now = time.time()

        if tracker["blocked_until"] > now:
            remaining = int(tracker["blocked_until"] - now)
            return JSONResponse(
                status_code=403,
                content={"detail": f"IP temporarily blocked. Try again in {remaining} seconds."}
            )

        response = await call_next(request)

        path = request.url.path
        is_auth_endpoint = "/auth/login" in path or "/admin/login" in path
        if is_auth_endpoint and response.status_code == 401:
            tracker["count"] += 1
            if tracker["count"] >= IP_BLOCK_THRESHOLD:
                tracker["blocked_until"] = now + IP_BLOCK_DURATION
                logging.warning(f"IP {client_ip} blocked after {tracker['count']} failed attempts")
        elif is_auth_endpoint and response.status_code == 200:
            ip_fail_tracker[client_ip] = {"count": 0, "blocked_until": 0}

        return response


# Password helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# JWT helpers
def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.replace("Bearer ", "")
    payload = decode_jwt_token(token)
    user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
