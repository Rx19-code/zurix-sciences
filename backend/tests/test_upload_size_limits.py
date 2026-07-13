"""Regression tests for request size limit middleware and image upload endpoint.

Covers the fix in /app/backend/utils/security.py where:
- Generic MAX_SIZE raised from 1MB to 2MB
- Upload paths bypassed up to 25MB (UPLOAD_MAX_SIZE)
- /api/admin/products/upload-image should accept 3MB images
"""
import io
import os
import struct
import zlib

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fallback: read from frontend .env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                break

ADMIN_PASSWORD = "Rx050217!"
UPLOAD_URL = f"{BASE_URL}/api/admin/products/upload-image"
LOGIN_URL = f"{BASE_URL}/api/admin/login"


def _make_png(target_bytes: int) -> bytes:
    """Generate a valid PNG whose total size is roughly `target_bytes`.

    A small 8x8 PNG is created, then a large ancillary padding chunk is appended
    before IEND to inflate the file. Uses a custom private chunk 'pdAT' (lowercase
    ancillary, safe-to-copy) so decoders ignore it.
    """
    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        return length + chunk_type + data + crc

    # IHDR: 8x8, 8-bit RGBA
    ihdr = struct.pack(">IIBBBBB", 8, 8, 8, 6, 0, 0, 0)
    # IDAT: 8x8 RGBA raw scanlines (each row prefixed with filter byte 0)
    raw = b""
    for _ in range(8):
        raw += b"\x00" + (b"\xff\x00\x00\xff" * 8)
    idat = zlib.compress(raw)

    # Padding to reach target size. Use ancillary private chunk 'prVt'
    header_overhead = len(sig) + 12 + len(ihdr) + 12 + len(idat) + 12 + 12  # ihdr, idat, iend, prvt hdrs
    pad_size = max(0, target_bytes - header_overhead)
    padding = b"\x00" * pad_size

    png = (
        sig
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"prVt", padding)  # private ancillary chunk (lowercase 1st & 3rd letter)
        + chunk(b"IEND", b"")
    )
    return png


@pytest.fixture(scope="module")
def session():
    return requests.Session()


# --- Tests ---


def test_upload_3mb_png_succeeds(session):
    """Regression: 3MB PNG upload must return 200 (was 413 before fix)."""
    png = _make_png(3 * 1024 * 1024)
    assert len(png) >= 3 * 1024 * 1024, f"Test image too small: {len(png)}"

    files = {"file": ("test_3mb.png", io.BytesIO(png), "image/png")}
    headers = {"X-Admin-Password": ADMIN_PASSWORD}
    r = session.post(UPLOAD_URL, files=files, headers=headers, timeout=60)

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:400]}"
    data = r.json()
    assert data.get("success") is True
    url = data.get("url", "")
    assert url.startswith("/api/images/products/"), f"Unexpected url: {url}"
    assert url.endswith(".png"), f"Expected .png extension: {url}"

    # cleanup: delete file from disk
    filename = url.rsplit("/", 1)[-1]
    fpath = f"/app/backend/product_images/{filename}"
    if os.path.exists(fpath):
        os.remove(fpath)


def test_upload_500kb_png_succeeds(session):
    """Small image still works."""
    png = _make_png(500 * 1024)
    files = {"file": ("test_small.png", io.BytesIO(png), "image/png")}
    headers = {"X-Admin-Password": ADMIN_PASSWORD}
    r = session.post(UPLOAD_URL, files=files, headers=headers, timeout=30)

    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:400]}"
    data = r.json()
    assert data.get("success") is True
    assert data.get("url", "").startswith("/api/images/products/")

    filename = data["url"].rsplit("/", 1)[-1]
    fpath = f"/app/backend/product_images/{filename}"
    if os.path.exists(fpath):
        os.remove(fpath)


def test_upload_without_admin_password_returns_401(session):
    """Missing X-Admin-Password header → 401."""
    png = _make_png(10 * 1024)
    files = {"file": ("nopass.png", io.BytesIO(png), "image/png")}
    r = session.post(UPLOAD_URL, files=files, timeout=15)
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text[:300]}"


def test_upload_txt_file_returns_400(session):
    """Unsupported file type → 400."""
    files = {"file": ("bad.txt", io.BytesIO(b"hello world" * 100), "text/plain")}
    headers = {"X-Admin-Password": ADMIN_PASSWORD}
    r = session.post(UPLOAD_URL, files=files, headers=headers, timeout=15)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}: {r.text[:300]}"
    detail = r.json().get("detail", "").lower()
    assert "unsupported" in detail or "type" in detail or "invalid" in detail, f"Unexpected detail: {detail}"


def test_middleware_blocks_generic_request_over_2mb(session):
    """Defense-in-depth: non-upload route with >2MB body → 413 from middleware."""
    # Send 3MB body to /api/admin/login (not an upload path)
    big_body = b"a" * (3 * 1024 * 1024)
    headers = {"Content-Type": "application/json"}
    r = session.post(LOGIN_URL, data=big_body, headers=headers, timeout=30)
    assert r.status_code == 413, f"Expected 413, got {r.status_code}: {r.text[:300]}"
    detail = r.json().get("detail", "")
    assert "too large" in detail.lower(), f"Unexpected detail: {detail}"
    assert "2MB" in detail or "2 MB" in detail, f"Expected 2MB in detail: {detail}"
