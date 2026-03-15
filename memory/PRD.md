# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### March 15, 2026 - Product Images Complete
- [x] **All 32 products now have local images**: Downloaded 16 missing images from uploaded assets (customer-assets CDN)
- [x] **Images served locally** via `/api/images/products/{filename}` endpoint - no external CDN dependency
- [x] **Full testing passed**: Backend 100%, Frontend 100% - all pages verified (Home, Products, Product Detail)

### March 14, 2026 - Security Hardening
- [x] **Credentials moved to .env**: Admin password, JWT secret, USDT wallet address removed from code
- [x] **Rate limiting** (slowapi) on sensitive endpoints
- [x] **CORS restricted** to zurixsciences.com in production
- [x] **JWT secret fixed** in .env
- [x] **Failed auth logging** for admin and user login attempts
- [x] **Security headers, IP blocking, request size limits**
- [x] **In-memory caching** on high-traffic endpoints
- [x] **MongoDB indexes** for performance
- [x] **Health check endpoint** `/api/health`

### March 14, 2026 - Protocol System V3 (Single-Use Code + Watermarking)
- [x] Refactored protocol system: validation by single-use unique QR code
- [x] Auto-detects matching protocol from product name
- [x] PDF watermarking with "ZURIX SCIENCES - FOR RESEARCH ONLY" + "Downloaded by: [email]"
- [x] All 8 free protocols with 24 PDFs (8 x 3 languages: EN/ES/PT)

### Previous Implementations
- [x] Full-stack website (FastAPI + React PWA)
- [x] Product verification with QR scanner
- [x] USDT Payment System (TRC20) for Advanced Protocols
- [x] Admin panel with pagination, batch editing
- [x] Resend email integration
- [x] 32 product images uploaded and served locally

## Prioritized Backlog

### P1 - Next
- [ ] Deploy Security & Stability Overhaul to production (guide user to update .env + git pull + pm2 restart)
- [ ] Admin panel - Leads tab (view/export collected contacts from protocol downloads)
- [ ] Clarify paid "Advanced Protocols" future (USDT payment - keep hidden or remove?)

### P2 - Future
- [ ] Refactor `server.py` into separate FastAPI routers (auth, admin, products, protocols, security)
- [ ] Mobile app (on hold, code in /mobile/)
- [ ] MongoDB authentication
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

## Architecture
```
/app/
├── backend/
│   ├── server.py              # FastAPI - all endpoints (needs refactor)
│   ├── product_images/        # 32 local product images
│   ├── protocols_pdf/         # 24 PDFs (8 protocols x 3 languages)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/             # Home, Products, ProductDetail, Protocols, Admin, etc.
│   │   └── components/        # ProductCard, Navbar, Footer, CartDrawer
│   └── package.json
└── mobile/                    # React Native (on hold)
```

## Key API Endpoints
- `GET /api/products` - Product catalog (cached 15min)
- `GET /api/products/{id}` - Product detail
- `GET /api/images/products/{filename}` - Serves local product images
- `POST /api/protocols/v3/validate-code` - Validate unique code (rate-limited)
- `POST /api/protocols/v3/send-protocol` - Watermark + email PDF (rate-limited)
- `GET /api/health` - Health check
- `POST /api/admin/login` - Admin auth (rate-limited + IP blocking)
