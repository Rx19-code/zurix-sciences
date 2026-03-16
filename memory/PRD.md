# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### March 16, 2026 - Advanced Protocols (5 new paid protocols)
- [x] Removed 3 old placeholder advanced protocols
- [x] Added 5 new advanced protocols at $4.99 each (English only for now):
  1. Tissue Regeneration & Wound Healing
  2. Body Composition & Physical Performance
  3. Cognitive Support & Stress Reduction
  4. Sexual Health & Libido
  5. Rejuvenation & Skin Health
- [x] PDFs stored at `protocols_pdf/advanced/en/`
- [x] Frontend shows correct available languages per protocol
- [x] Payment flow via USDT (TRC20) active

### March 15, 2026 - Admin Leads Tab
- [x] Leads tab with search, filter by protocol, CSV export

### March 15, 2026 - Server Refactoring
- [x] Refactored server.py (2441 lines) into 11 modular files

### March 15, 2026 - Product Images Complete
- [x] All 32 products with local images

### Previous Implementations
- [x] Full-stack PWA (FastAPI + React)
- [x] Product verification with QR scanner
- [x] Protocol system V3 (single-use code + watermarking + email)
- [x] Security hardening (rate limiting, IP blocking, headers)
- [x] Admin panel (codes, batches, logs, leads)
- [x] Resend email integration

## Architecture
```
backend/
├── server.py              # App init (~100 lines)
├── database.py            # MongoDB + cache
├── models.py              # Pydantic models
├── routes/                # auth, products, protocols, payments, admin, verification
├── utils/                 # security, email
├── product_images/        # 32 product images
└── protocols_pdf/
    ├── en/, es/, pt/      # 8 basic protocols x 3 languages
    └── advanced/en/       # 5 advanced protocols (EN only for now)
```

## Prioritized Backlog

### P0 - Pending User Action
- [ ] Deploy to production (update .env + git pull + pm2 restart)
- [ ] Upload ES and PT versions of advanced protocol PDFs

### P1 - Next
- [ ] Add ES/PT PDFs for advanced protocols when user provides them

### P2 - Future
- [ ] Mobile app (on hold)
- [ ] MongoDB authentication
- [ ] Automated database backups

## Advanced Protocols Configuration
| ID | Title | Price | Languages |
|---|---|---|---|
| proto-adv-tissue | Tissue Regeneration & Wound Healing | $4.99 | EN |
| proto-adv-body | Body Composition & Physical Performance | $4.99 | EN |
| proto-adv-cognitive | Cognitive Support & Stress Reduction | $4.99 | EN |
| proto-adv-sexual | Sexual Health & Libido | $4.99 | EN |
| proto-adv-skin | Rejuvenation & Skin Health | $4.99 | EN |

## Test Data
- **Admin Password:** Rx050217!
- **Valid Test Code:** ZX-260312-GHK50-1-TEST01
