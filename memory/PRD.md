# Zurix Sciences - PRD (Product Requirements Document)

## Original Problem Statement
Professional e-commerce website (Zurix Sciences) for selling peptide research products. PWA with product catalog, shopping cart, checkout, product verification (QR), and downloadable research protocols with automated watermarking/emailing. Admin panel for managing products, codes, and leads.

## Peptide Library Feature
Comprehensive "Peptide Library" with 96 peptides featuring tabs for Overview, Protocols, Research, and Synergy. All PRO (paid access). ALL content in English.

## Architecture
```
/app/
├── backend/
│   ├── server.py
│   ├── database.py
│   ├── routes/
│   │   ├── auth.py          # Email+password + Google OAuth (Emergent Auth)
│   │   ├── payments.py      # NOWPayments USDT lifetime access ($39.99)
│   │   ├── library.py
│   │   ├── products.py
│   │   ├── admin.py
│   │   ├── verification.py
│   │   └── protocols.py
│   ├── utils/security.py    # JWT, bcrypt, middleware
│   ├── seed_library_production.json
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   │   ├── AuthContext.js   # Auth provider (JWT + Google)
│   │   │   └── CartContext.js
│   │   ├── pages/
│   │   │   ├── Login.js         # Login/Register (email + Google)
│   │   │   ├── AuthCallback.js  # Google OAuth callback
│   │   │   ├── PeptideDetail.js # Locked content + payment flow
│   │   │   ├── Library.js
│   │   │   └── ...
│   │   ├── components/
│   │   │   ├── Navbar.js        # Auth buttons (Sign In / Logout)
│   │   └── App.js               # AuthProvider + routing
```

## Key DB Schema
- `users`: `{id, email, name, password_hash?, auth_provider, has_lifetime_access, payment_id, created_at}`
- `lifetime_orders`: `{order_id, user_id, np_payment_id, pay_address, pay_amount, status}`
- `peptide_library`: `{slug, name, category, is_free: false, protocols{}, research{}, synergy{}}`
- `products`: `{name, image_url, ...}`
- `unique_codes`: `{code, batch_number, product_name, ...}`

## Key API Endpoints
- `POST /api/auth/register` - Email registration
- `POST /api/auth/login` - Email login
- `POST /api/auth/google` - Google OAuth session exchange
- `GET /api/auth/me` - Current user info
- `POST /api/payment/create-invoice` - Create NOWPayments USDT invoice ($39.99)
- `GET /api/payment/check/{payment_id}` - Check payment & grant access
- `POST /api/payment/nowpayments-webhook` - Auto-grant on payment confirmation
- `GET /api/library` / `GET /api/library/{slug}` - Library endpoints

## What's Been Implemented
- [x] Full e-commerce catalog (28 products, images as placeholders pending update)
- [x] Peptide Library: 96 peptides, all PRO
- [x] Protocol data from 3 batches of PDFs (25+ peptides with full protocol data)
- [x] Auth system: Email+password + Google OAuth (Emergent Auth)
- [x] NOWPayments USDT payment gateway ($39.99 lifetime access)
- [x] Locked content: Overview visible, Protocols/Research/Synergy behind paywall
- [x] Navbar: Sign In / User name / Logout buttons
- [x] Product verification system (QR)
- [x] Calculator, Admin panel, Labels, Maintenance mode

## Pending Tasks
- [ ] P1: Deploy auth + payment to production
- [ ] P1: Admin panel - manage users (grant/revoke access)
- [ ] P2: Product images (waiting for user to provide correct images)
- [ ] P2: Automated MongoDB backups
- [ ] P3: React Native mobile app
