# Zurix Sciences - PRD (Product Requirements Document)

## Original Problem Statement
Professional e-commerce website (Zurix Sciences) for selling peptide research products. PWA with product catalog, shopping cart, checkout, product verification (QR), and downloadable research protocols with automated watermarking/emailing. Admin panel for managing products, codes, and leads.

## Peptide Library Feature
Comprehensive "Peptide Library" with 96 peptides + 43 stacks. Toggle "Peptides | Stacks" on /protocols. All PRO (paid access $39.99 USDT lifetime). ALL content in English.

## Architecture
```
/app/
├── backend/
│   ├── server.py
│   ├── database.py
│   ├── routes/
│   │   ├── auth.py          # Email+password + Google OAuth (Emergent Auth)
│   │   ├── payments.py      # NOWPayments USDT lifetime access ($39.99)
│   │   ├── library.py       # Peptides + Stacks API
│   │   ├── products.py, admin.py, verification.py, protocols.py
│   ├── utils/security.py
│   ├── seed_library_production.json (96 peptides)
│   ├── seed_stacks_production.json (43 stacks)
│   ├── seed_stacks.py
├── frontend/
│   ├── src/
│   │   ├── context/ AuthContext.js, CartContext.js
│   │   ├── pages/ Login.js, AuthCallback.js, Library.js, PeptideDetail.js, StackDetail.js, ...
│   │   ├── components/ Navbar.js (auth buttons), ProductCard.js (placeholder), ...
│   │   └── App.js
```

## Key DB Collections
- `users`: {id, email, name, password_hash?, auth_provider, has_lifetime_access, payment_id}
- `lifetime_orders`: {order_id, user_id, np_payment_id, pay_address, pay_amount, status}
- `peptide_library`: {slug, name, category, is_free: false, protocols{}, research{}, synergy{}}
- `peptide_stacks`: {id, slug, name, category, goal, peptides[], why_it_works, how_to_use[], is_free: false}
- `products`, `unique_codes`, `protocol_leads`, `protocol_orders`

## Key API Endpoints
- Auth: POST /api/auth/register, /login, /google | GET /api/auth/me
- Payment: POST /api/payment/create-invoice | GET /api/payment/check/{id}, /my-status
- Library: GET /api/library, /api/library/{slug}
- Stacks: GET /api/stacks, /api/stacks/{slug}

## What's Been Implemented
- [x] Full e-commerce catalog (28 products, placeholder images)
- [x] Peptide Library: 96 peptides, all PRO, 3 batches of PDFs processed
- [x] Peptide Stacks: 43 stacks in 9 categories (Fat Loss, Female Optimization, Hormonal Recovery, Fertility, Muscle Growth, Strength, CrossFit, Combat Sports, Sprinting)
- [x] Toggle "Peptides (96) | Stacks (43)" on /protocols page
- [x] Auth: Email+password + Google OAuth (Emergent Auth)
- [x] NOWPayments USDT payment ($39.99 lifetime access)
- [x] Locked content: Overview visible, Protocols/Research/Synergy behind paywall
- [x] Stack detail page with locked "Why It Works" and "How to Use"
- [x] Navbar: Sign In / User / Logout
- [x] Product verification (QR), Calculator, Admin panel, Labels, Maintenance mode

## Pending Tasks
- [ ] P1: Deploy auth + payment + stacks to production
- [ ] P1: Admin panel - manage users (grant/revoke lifetime access)
- [ ] P2: Product images (waiting for correct images from user)
- [ ] P2: Automated MongoDB backups
- [ ] P3: React Native mobile app

## Credentials
- Backend: /app/backend/.env
- Test user: test@test.com / test123
- Admin: Rx050217!
- NOWPayments: ER8A5WS-34840WY-NGHX1VS-7PF129J
- Production: root@80.78.19.40

## Critical Notes
- PeptideDetail.js/StackDetail.js: NEVER use .map() on member expressions. Always assign to local variable first.
- All Library content in English (user communicates in Portuguese)
- Production DB: zurix_sciences (dev: test_database)
