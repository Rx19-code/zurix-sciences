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
│   ├── models.py
│   ├── routes/          # auth, products, protocols, admin, library, verification
│   ├── utils/           # security, email
│   ├── product_images/
│   │   └── categories/  # Hero images (nootropic.jpg, recovery.jpg, etc.)
│   ├── protocols_pdf/
│   ├── seed_library.py
│   ├── seed_library_production.json  # Export for production DB (96 peptides, 273KB)
│   ├── process_pdfs_v2.py           # Batch 1 PDF processor
│   ├── process_pdfs_batch2.py       # Batch 2 PDF processor
│   └── tests/           # test_library_data_quality.py
├── frontend/
│   ├── src/
│   │   ├── pages/       # Library.js, PeptideDetail.js, Calculator.js, Admin.js, Verify.js
│   │   ├── components/
│   │   └── App.js
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
- `POST /api/admin/generate-labels` - Generate QR label images for Niimbot printer
- `POST /api/protocols/v3/send-protocol` - Send protocol

## What's Been Implemented
- [x] Full e-commerce catalog with local images (28 products)
- [x] Peptide reconstitution calculator with syringe UI
- [x] Product verification system (/verify) - URL-based auto-verify via native QR scan
- [x] Protocol delivery with watermarking (Resend)
- [x] Admin panel with Leads tab + CSV export + Labels tab (Excel/Niimbot)
- [x] Peptide Library: 96 peptides, 4-tab detail pages, hero images, Quick Facts
- [x] Batch 1 PDF import (13 peptides: Cartalax, Cerebrolysin, Cortagen, Dihexa, Epithalon, FoxO4-DRI, Glutathione, NAD+, P21, PE-22-28, Pinealon, PNC-27, PNC-28)
- [x] Batch 2 PDF import (12 peptides: AOD-9604, Cagrilintide, Cardiogen, Chonluten, HGH Frag, Livagen, Mazdutide, Ovagen, Prostamax, Retatrutide, Semaglutide, Vesugen)
- [x] Light theme consistency across all pages
- [x] Data Quality: All content in English, no competitor references
- [x] Maintenance Mode with bypass parameter
- [x] Production seed export (seed_library_production.json)

## Current Status (Feb 2026)
- **96/96 peptides**: All have dosages, overview, and reconstitution steps
- **84/96 with phases**: 12 missing are solvents/simple peptides (Bacteriostatic Water, Sodium Chloride, etc.)
- **All content in English**: Verified
- **Production seed**: Exported and ready for deployment

## Pending Tasks
- [ ] P1: Deploy latest DB to production (seed_library_production.json)
- [ ] P1: USDT lifetime access payment for PRO peptides
- [ ] P2: Automated MongoDB backups
- [ ] P3: MongoDB authentication
- [ ] P3: React Native mobile app

## Credentials
- Backend: `/app/backend/.env` (ADMIN_PASSWORD, JWT_SECRET, RESEND_API_KEY, EMERGENT_LLM_KEY)
- Test code: ZX-260312-GHK50-1-TEST01
- Production: root@80.78.19.40 (/var/www/zurix/) via SSH

## Critical Notes
- PeptideDetail.js: Avoid `.map()` on member expressions (causes Babel plugin infinite recursion). Always assign to local variables first.
- All Library content must be in English (user communicates in Portuguese)
- User manages live server via SSH - provide exact copy-paste commands
- USDT payment: User wants crypto for anonymity
- Production DB name: `zurix_sciences` (dev uses `test_database`)
- Niimbot label printer: 14x22mm labels, QR codes need Level H error correction
