"""Persistent storage for the self-hosted VPS deployment.

This app is deployed on the user's own Ubuntu VPS (Nginx + PM2) where the
local filesystem is persistent by design: product images are served by
Nginx/FastAPI from backend/product_images and protocol PDFs from disk.
"""
from pathlib import Path
import os


def persist_bytes(path, data: bytes) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(p), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
