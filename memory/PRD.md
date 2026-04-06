# Zurix Sciences - PRD (Product Requirements Document)

## Original Problem Statement
Professional e-commerce website (Zurix Sciences) for selling peptide research products. PWA with product catalog, shopping cart, checkout, product verification (QR), and downloadable research protocols with automated watermarking/emailing. Admin panel for managing products, codes, and leads.

## NEW: Peptide Library Feature
Comprehensive "Peptide Library" with 96 peptides featuring tabs for Overview, Protocols, Research, and Synergy. Hero images per category. Quick Facts sidebar. Free vs PRO access tiers. ALL content in English.

## Architecture
```
/app/
├── backend/
│   ├── server.py
│   ├── database.py
│   ├── routes/          # auth, products, protocols, admin, library, verification
│   ├── utils/           # security, email
│   ├── product_images/
│   │   └── categories/  # Hero images (nootropic.jpg, recovery.jpg, etc.)
│   ├── protocols_pdf/
│   ├── seed_library.py
│   ├── seed_library_production.json  # Export for production DB
│   └── tests/           # test_library_data_quality.py
├── frontend/
│   ├── src/
│   │   ├── pages/       # Library.js, PeptideDetail.js, Calculator.js, Admin.js...
│   │   ├── components/
│   │   └── App.js
│   └── package.json
└── mobile/              # React Native (ON HOLD)
```

## Key DB Schema
- `peptide_library`: `{slug, name, description, category, is_free, classification, evidence_level, half_life, reconstitution_difficulty, also_known_as[], presentations[], overview{what_is, mechanism_summary}, protocols{title, standard{route, frequency}, dosages[], phases[], reconstitution_steps[]}, research{mechanism, steps[], references[]}, synergy{interactions[], stacks[]}}`
- `products`: `{name, image_url, ...}`
- `unique_codes`: `{code, product_name, ...}`
- `protocol_leads`: `{email, name, phone, ...}`

## Key API Endpoints
- `GET /api/library` - List all peptides (with filters)
- `GET /api/library/{slug}` - Peptide detail
- `GET /api/library/category-image/{category_slug}` - Hero images
- `GET /api/images/products/{filename}` - Product images
- `GET /api/admin/leads` - Admin leads
- `POST /api/protocols/v3/send-protocol` - Send protocol

## What's Been Implemented
- [x] Full e-commerce catalog with local images (28 products)
- [x] Peptide reconstitution calculator with syringe UI
- [x] Product verification system (/verify)
- [x] Protocol delivery with watermarking (Resend)
- [x] Admin panel with Leads tab + CSV export
- [x] Peptide Library: 96 peptides, 4-tab detail pages, hero images, Quick Facts
- [x] Batch PDF import from WeTransfer (72 PDFs processed)
- [x] Light theme consistency across all pages
- [x] Production server synced (via SSH)
- [x] **Data Quality Fixes (Feb 2026)**:
  - [x] Removed competitor URL from Retatrutide category
  - [x] Mapped 12 Portuguese categories to English (11 total categories)
  - [x] Fixed broken "0 mg" dosage values (semaglutide, aod-9604, epithalon, cagrilintide)
  - [x] Cleaned competitor artifacts from 15 peptides
  - [x] Translated all Portuguese content to English (21 peptides overview/protocols/research/synergy)
  - [x] Translated metadata fields (classification, evidence_level, half_life) for 27 peptides
  - [x] Fixed reconstitution_difficulty 'Moderada' -> 'Moderate' for 15 peptides
  - [x] 20/20 data quality tests passing

## Current Status (Feb 2026)
- **36 peptides**: Full content (all 4 tabs populated, English)
- **60 peptides**: Partial content (basic info only, awaiting PDFs)
- **All content in English**: Verified via automated tests

## Pending Tasks
- [ ] P0: Deploy data fixes to production (user needs to run import commands)
- [ ] P1: Receive & process remaining 60 peptide PDFs
- [ ] P1: USDT lifetime access payment for PRO peptides
- [ ] P2: Automated MongoDB backups
- [ ] P3: MongoDB authentication
- [ ] P3: Cloudflare WAF fix for South American users
- [ ] P3: React Native mobile app

## Credentials
- Backend: `/app/backend/.env` (ADMIN_PASSWORD, JWT_SECRET, RESEND_API_KEY, EMERGENT_LLM_KEY)
- Test code: ZX-260312-GHK50-1-TEST01
- Production: root@80.78.19.40 (/var/www/zurix/)

## Critical Notes
- PeptideDetail.js: Avoid `.map()` on member expressions (causes Babel plugin infinite recursion). Always assign to local variables first.
- All Library content must be in English (user communicates in Portuguese)
- User manages live server via SSH - provide exact copy-paste commands
- USDT payment: User wants crypto for anonymity
- Production DB name: `zurix_sciences` (dev uses `test_database`)
