"""Tests for NOWPayments IPN webhook HMAC-SHA512 signature verification.

Run: cd /app/backend && pytest tests/test_payments_webhook_hmac.py -v
"""
import hashlib
import hmac
import json
import os
import sys
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

# Ensure backend on path
sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import app  # noqa: E402


TEST_SECRET = "test-ipn-secret-12345"


def _sign(body_dict: dict, secret: str = TEST_SECRET) -> tuple[bytes, str]:
    """Replicate NOWPayments signing: sort keys alphabetically, then HMAC-SHA512."""
    sorted_body = json.dumps(body_dict, sort_keys=True, separators=(",", ":"))
    sig = hmac.new(secret.encode(), sorted_body.encode(), hashlib.sha512).hexdigest()
    return sorted_body.encode(), sig


@pytest.fixture
def client():
    return TestClient(app)


# ─────────── PRODUCTION MODE ───────────

def test_prod_valid_signature_accepted(client):
    """Valid signature in prod → 200 OK."""
    payload = {"payment_status": "waiting", "order_id": "LTA-TEST123", "payment_id": 99999}
    raw, sig = _sign(payload)

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", TEST_SECRET), \
         patch("routes.payments.ENVIRONMENT", "production"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=raw,
            headers={"Content-Type": "application/json", "x-nowpayments-sig": sig},
        )
    assert r.status_code == 200, r.text
    assert r.json()["success"] is True


def test_prod_missing_signature_rejected(client):
    """No signature header in prod → 401."""
    payload = {"payment_status": "finished", "order_id": "LTA-FAKE", "payment_id": 1}
    raw, _ = _sign(payload)

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", TEST_SECRET), \
         patch("routes.payments.ENVIRONMENT", "production"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=raw,
            headers={"Content-Type": "application/json"},
        )
    assert r.status_code == 401


def test_prod_wrong_signature_rejected(client):
    """Wrong signature in prod → 401 (the critical attack scenario)."""
    payload = {"payment_status": "finished", "order_id": "LTA-ATTACK", "payment_id": 2}
    raw, _ = _sign(payload)

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", TEST_SECRET), \
         patch("routes.payments.ENVIRONMENT", "production"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=raw,
            headers={"Content-Type": "application/json", "x-nowpayments-sig": "deadbeef" * 16},
        )
    assert r.status_code == 401


def test_prod_tampered_body_rejected(client):
    """Body modified after signing → 401 (signature no longer matches)."""
    original = {"payment_status": "waiting", "order_id": "LTA-X", "payment_id": 3}
    _, sig = _sign(original)
    # Attacker swaps status to "finished" but keeps the original sig
    tampered = {"payment_status": "finished", "order_id": "LTA-X", "payment_id": 3}
    tampered_raw = json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode()

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", TEST_SECRET), \
         patch("routes.payments.ENVIRONMENT", "production"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=tampered_raw,
            headers={"Content-Type": "application/json", "x-nowpayments-sig": sig},
        )
    assert r.status_code == 401


def test_prod_no_secret_configured_rejected(client):
    """No IPN secret in env + production env → 401 (fail-safe)."""
    payload = {"payment_status": "finished", "order_id": "LTA-NOSEC", "payment_id": 4}
    raw, _ = _sign(payload)

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", None), \
         patch("routes.payments.ENVIRONMENT", "production"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=raw,
            headers={"Content-Type": "application/json", "x-nowpayments-sig": "anything"},
        )
    assert r.status_code == 401


# ─────────── DEVELOPMENT MODE ───────────

def test_dev_invalid_signature_allowed_with_warning(client, caplog):
    """In dev mode, invalid signature still processes (with warning log)."""
    payload = {"payment_status": "waiting", "order_id": "LTA-DEVTEST", "payment_id": 5}
    raw, _ = _sign(payload)

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", TEST_SECRET), \
         patch("routes.payments.ENVIRONMENT", "development"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=raw,
            headers={"Content-Type": "application/json", "x-nowpayments-sig": "bad"},
        )
    assert r.status_code == 200
    assert r.json()["success"] is True


def test_dev_no_secret_no_signature_allowed(client):
    """Dev mode + no secret + no signature → 200 (so local testing works)."""
    payload = {"payment_status": "waiting", "order_id": "LTA-LOCAL", "payment_id": 6}
    raw, _ = _sign(payload)

    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", None), \
         patch("routes.payments.ENVIRONMENT", "development"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=raw,
            headers={"Content-Type": "application/json"},
        )
    assert r.status_code == 200


# ─────────── EDGE CASES ───────────

def test_invalid_json_returns_400(client):
    """Malformed JSON returns 400 even with valid scenario."""
    with patch("routes.payments.NOWPAYMENTS_IPN_SECRET", None), \
         patch("routes.payments.ENVIRONMENT", "development"):
        r = client.post(
            "/api/payment/nowpayments-webhook",
            content=b"{not valid json",
            headers={"Content-Type": "application/json"},
        )
    assert r.status_code == 400
