# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### March 15, 2026 - Server.py Refactoring
- [x] **Refactored `server.py` (2441 lines) into 11 modular files**:
  - `server.py` (slim, ~100 lines) - App init, middleware, health check
  - `database.py` - MongoDB connection, cache utilities, env config
  - `models.py` - All Pydantic models
  - `routes/auth.py` - User authentication (register, login, password reset)
  - `routes/products.py` - Product catalog, images, categories
  - `routes/protocols.py` - Protocol definitions, validation, email sending
  - `routes/payments.py` - USDT payment system
  - `routes/admin.py` - Admin panel endpoints
  - `routes/verification.py` - Product verification (web + mobile)
  - `utils/security.py` - Middleware classes, JWT, password helpers
  - `utils/email.py` - Email sending, PDF watermarking, geolocation
- [x] **100% test pass rate** - 21 backend tests, all frontend pages verified

### March 15, 2026 - Product Images Complete
- [x] All 32 products now have local images
- [x] Images served locally via `/api/images/products/{filename}` endpoint

### Previous Implementations
- [x] Full-stack website (FastAPI + React PWA)
- [x] Product verification with QR scanner
- [x] Protocol system V3 (single-use code + watermarking + email)
- [x] Security hardening (rate limiting, IP blocking, security headers, CORS, JWT)
- [x] Admin panel (products, batches, codes management)
- [x] USDT Payment System for Advanced Protocols
- [x] Resend email integration
- [x] MongoDB indexes for performance
- [x] In-memory caching on high-traffic endpoints

## Architecture (Post-Refactor)
```
backend/
├── server.py              # App init, middleware, health check (~100 lines)
├── database.py            # MongoDB + cache + env config
├── models.py              # All Pydantic models
├── routes/
│   ├── auth.py            # Login, register, password reset
│   ├── products.py        # Catalog, images, categories
│   ├── protocols.py       # Protocol definitions + validation + email
│   ├── payments.py        # USDT payment system
│   ├── admin.py           # Admin panel endpoints
│   └── verification.py    # Product verification (web + mobile)
├── utils/
│   ├── security.py        # Middleware, JWT, password helpers
│   └── email.py           # Email, watermark PDF, geolocation
├── product_images/        # 32 local product images
├── protocols_pdf/         # 24 PDFs (8 protocols x 3 languages)
└── tests/                 # Test files

frontend/
├── src/
│   ├── pages/             # Home, Products, ProductDetail, Protocols, Admin, Verify
│   └── components/        # ProductCard, Navbar, Footer, CartDrawer
└── package.json

mobile/                    # React Native (on hold)
```

## Prioritized Backlog

### P1 - Next
- [ ] Deploy all changes to production (guide user: update .env + git pull + pm2 restart)
- [ ] Admin panel - Leads tab (view/export collected contacts from protocol downloads)
- [ ] Clarify paid "Advanced Protocols" future (USDT payment - keep or remove?)

### P2 - Future
- [ ] Mobile app (on hold, code in /mobile/)
- [ ] MongoDB authentication
- [ ] Automated database backups

## Key API Endpoints
- `GET /api/health` - Health check
- `GET /api/products` - Product catalog (cached)
- `GET /api/products/{id}` - Product detail
- `GET /api/images/products/{filename}` - Local product images
- `POST /api/protocols-v2/validate-code` - Validate unique code
- `POST /api/protocols-v2/send-protocol` - Watermark + email PDF
- `POST /api/admin/login` - Admin auth
- `POST /api/verify-product` - Product verification

## Test Data
- **Admin Password:** Rx050217!
- **Valid Test Code:** ZX-260312-GHK50-1-TEST01
