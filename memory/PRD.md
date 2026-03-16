# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### March 15, 2026 - Admin Leads Tab
- [x] **New "Leads" tab** in admin panel showing protocol download contacts
- [x] Table with: Name, Email, Phone, Protocol, Language, Source, Downloads, Date
- [x] Search by name/email/phone, filter by protocol
- [x] Export CSV functionality
- [x] Backend endpoints: `GET /api/admin/leads`, `GET /api/admin/leads/export`

### March 15, 2026 - Server.py Refactoring
- [x] Refactored `server.py` (2441 lines) into 11 modular files
- [x] 100% test pass rate (21 backend tests, all frontend pages)

### March 15, 2026 - Product Images Complete
- [x] All 32 products have local images served via `/api/images/products/{filename}`

### Previous Implementations
- [x] Full-stack website (FastAPI + React PWA)
- [x] Product verification with QR scanner
- [x] Protocol system V3 (single-use code + watermarking + email)
- [x] Security hardening (rate limiting, IP blocking, security headers)
- [x] Admin panel (products, batches, codes, leads management)
- [x] USDT Payment System for Advanced Protocols
- [x] Resend email integration

## Architecture
```
backend/
├── server.py              # App init, middleware, health check
├── database.py            # MongoDB + cache + env config
├── models.py              # All Pydantic models
├── routes/
│   ├── auth.py            # Login, register, password reset
│   ├── products.py        # Catalog, images, categories
│   ├── protocols.py       # Protocol definitions + validation + email
│   ├── payments.py        # USDT payment system
│   ├── admin.py           # Admin panel + leads endpoints
│   └── verification.py    # Product verification (web + mobile)
├── utils/
│   ├── security.py        # Middleware, JWT, password helpers
│   └── email.py           # Email, watermark PDF, geolocation
├── product_images/        # 32 local product images
└── protocols_pdf/         # 24 PDFs (8 protocols x 3 languages)
```

## Prioritized Backlog

### P1 - Next
- [ ] Deploy all changes to production (guide user: update .env + git pull + pm2 restart)
- [ ] Clarify paid "Advanced Protocols" future (USDT payment - keep or remove?)

### P2 - Future
- [ ] Mobile app (on hold, code in /mobile/)
- [ ] MongoDB authentication
- [ ] Automated database backups

## Test Data
- **Admin Password:** Rx050217!
- **Valid Test Code:** ZX-260312-GHK50-1-TEST01
