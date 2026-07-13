"""Regression: /api/images/products/{filename} must return correct Content-Type
based on the file's actual extension (not hardcoded image/png)."""
import io
import os
import pytest
import requests
from PIL import Image

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://peptide-catalog-3.preview.emergentagent.com").rstrip("/")
ADMIN_PW = "Rx050217!"


def _make_image_bytes(fmt: str) -> bytes:
    img = Image.new("RGB", (40, 40), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def _upload(fmt: str, ext: str, mime: str):
    files = {"file": (f"test_mime.{ext}", _make_image_bytes(fmt), mime)}
    headers = {"X-Admin-Password": ADMIN_PW}
    r = requests.post(f"{BASE_URL}/api/admin/products/upload-image", files=files, headers=headers, timeout=30)
    return r


class TestServeImageMime:
    def test_upload_jpg_and_serve_with_jpeg_mime(self):
        r = _upload("JPEG", "jpg", "image/jpeg")
        assert r.status_code == 200, r.text
        url = r.json()["url"]
        assert url.endswith(".jpg"), f"expected .jpg url, got {url}"

        g = requests.get(f"{BASE_URL}{url}", timeout=15)
        assert g.status_code == 200
        assert g.headers.get("Content-Type", "").lower().startswith("image/jpeg"), \
            f"Expected image/jpeg, got {g.headers.get('Content-Type')}"
        assert len(g.content) > 0

    def test_upload_webp_and_serve_with_webp_mime(self):
        r = _upload("WEBP", "webp", "image/webp")
        assert r.status_code == 200, r.text
        url = r.json()["url"]
        assert url.endswith(".webp"), f"expected .webp url, got {url}"

        g = requests.get(f"{BASE_URL}{url}", timeout=15)
        assert g.status_code == 200
        assert g.headers.get("Content-Type", "").lower().startswith("image/webp"), \
            f"Expected image/webp, got {g.headers.get('Content-Type')}"

    def test_upload_png_still_returns_png_mime(self):
        r = _upload("PNG", "png", "image/png")
        assert r.status_code == 200, r.text
        url = r.json()["url"]
        assert url.endswith(".png")

        g = requests.get(f"{BASE_URL}{url}", timeout=15)
        assert g.status_code == 200
        assert g.headers.get("Content-Type", "").lower().startswith("image/png")

    def test_missing_image_returns_404(self):
        g = requests.get(f"{BASE_URL}/api/images/products/does-not-exist-xyz.png", timeout=10)
        assert g.status_code == 404
