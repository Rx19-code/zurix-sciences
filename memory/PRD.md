# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### March 14, 2026 - Security Hardening
- [x] **Credentials moved to .env**: Admin password, JWT secret, USDT wallet address removed from code
- [x] **Rate limiting** (slowapi) on sensitive endpoints:
  - Login: 10/min, Register: 5/min, Password reset: 3/min
  - Admin login: 5/min, Protocol validate: 20/min, Protocol send: 5/min
  - Product verification: 30/min
- [x] **CORS restricted** to zurixsciences.com in production .env
- [x] **JWT secret fixed** in .env (doesn't change on restart, tokens persist)
- [x] **Failed auth logging** for admin and user login attempts

### March 14, 2026 - Protocol System V3 (Single-Use Code + Watermarking)
- [x] Refactored protocol system: validation by single-use unique QR code
- [x] Auto-detects matching protocol from product name
- [x] PDF watermarking with "ZURIX SCIENCES - FOR RESEARCH ONLY" + "Downloaded by: [email]"
- [x] All 8 free protocols with 24 PDFs (8 x 3 languages: EN/ES/PT)
- [x] New endpoints: validate-code, send-protocol

### Previous Implementations
- [x] Full-stack website (FastAPI + React PWA)
- [x] Product verification with QR scanner
- [x] USDT Payment System (TRC20) for Advanced Protocols
- [x] Admin panel with pagination, batch editing
- [x] Resend email integration
- [x] 27 product images uploaded

## Prioritized Backlog

### P1 - Next
- [ ] Admin panel - Leads tab (view/export collected contacts)
- [ ] Clarify paid "Advanced Protocols" future

### P2 - Future
- [ ] Complete 5 missing product images
- [ ] Mobile app (on hold)
- [ ] MongoDB authentication (currently local-only access)
- [ ] Automated database backups

## Production Deploy Notes

### .env for production server must include:
```
ADMIN_PASSWORD=Rx050217!
JWT_SECRET=8f5c0afc04ecbf3b9421e7413437f786a9f7ea5d7a5f795b91ee6d7399fc14cd
USDT_WALLET_ADDRESS=TJKuseoNmGw1TnwskKjaBCw5FrYUynAP9m
CORS_ORIGINS=https://zurixsciences.com,https://www.zurixsciences.com
```

### Test Data
- **Valid Test Codes**: ZX-260312-GHK50-1-TEST01, ZX-260209-TB500-1-TEST01, ZX-260115-BPC157-1-TEST01

## Files Reference
- `backend/server.py` - All API endpoints
- `backend/.env` - All credentials (NOT in code)
- `frontend/src/pages/Protocols.js` - Protocols page
- `frontend/src/pages/Admin.js` - Admin panel
