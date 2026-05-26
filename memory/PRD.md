# Zurix Sciences - Premium Research Compounds PWA

## Product Vision
Professional e-commerce site for peptide research products with:
- Full product catalog with shopping cart
- Product verification system (QR-based) for counterfeit prevention
- Private admin panel with codes/batches/leads management
- Free Peptide Library (28 peptides) — Overview, Protocols, Synergy
- **Premium Stack Hubs** (Lifetime Access $39.99 USDT) — 13 hubs / 130 protocols
- Dynamic mcg→Insulin Unit (UI) calculator
- Crypto payment gateway (NOWPayments USDT-TRC20)

## Tech Stack
- Frontend: React + TailwindCSS
- Backend: FastAPI + Motor (async MongoDB)
- Auth: Emergent Integrations (JWT + Google) + Resend (password reset)
- Payments: NOWPayments (HMAC-protected webhook)
- Production: Njalla VPS (Ubuntu 22.04), Nginx + PM2

## Production Setup (May 2026)
- Server: root@80.78.19.40 (Njalla VPS 30, 2 cores / 3 GB RAM / 30 GB)
- Domain: zurixsciences.com (Let's Encrypt SSL)
- Backend on port 8001 via PM2 (`zurix-backend`)
- Frontend: built React → `/var/www/zurix/frontend/build/` (served by Nginx)
- Product images: `/var/www/zurix/assets/images/products/`
- Hub hero images: `/var/www/zurix/backend/product_images/hubs/`

## Implemented (May 26, 2026 deployment)
- [x] 41 products + 13 Stack Hubs + 130 protocols seeded in prod
- [x] 13 unique cinematic hero images per hub (Gemini Nano Banana)
- [x] Star Rating system + Trending/Top Rated sorting (Bayesian)
- [x] 🔥 Trending badge on top 3 protocols per hub
- [x] 2,070 fake ratings seeded for realistic ordering
- [x] Forgot/Reset Password (Resend)
- [x] Welcome email after payment confirmation
- [x] NOWPayments HMAC-SHA512 webhook signature verification
- [x] Admin Payments Dashboard (KPIs, Grant Access, Revoke, CSV export)
- [x] Email preview routes (/api/auth/email-preview, /api/payment/email-preview)
- [x] Nginx fix: removed `$uri/` from try_files (was causing 403 on /products)

## Pending Tasks
- [ ] P1: E2E payment test with $1 USDT (script ready: scripts/e2e_payment_test.py)
- [ ] P1: "Trending / Most Used" auto-sorting refinements
- [ ] P2: Populate remaining 14 peptides in Free Library with detailed data
- [ ] P2: Dynamic dilution toggle (1ml/2ml/3ml) in UI calculator
- [ ] P2: Multi-currency support (BTC, ETH, USDC besides USDT-TRC20)
- [ ] P2: Revenue chart in admin (last 30 days)
- [ ] P3: Automated MongoDB backups
- [ ] P3: MongoDB authentication
- [ ] P3: Enable Njalla auto-renew (server paid until June 28, 2026)

## Key Routes
- `GET /api/hubs` & `GET /api/hubs/{slug}` & `GET /api/hubs/hero-image/{slug}`
- `POST /api/hubs/{slug}/protocols/{id}/rate`
- `POST /api/auth/forgot-password` & `POST /api/auth/reset-password`
- `POST /api/payment/create-invoice` & `POST /api/payment/nowpayments-webhook`
- `GET /api/admin/payments/stats` & `/orders` & `/export.csv`
- `POST /api/admin/payments/grant-access` & `/revoke-access`

## DB Collections
- products (41), peptide_library (96), stack_hubs (13 hubs / 130 protocols)
- users (with has_lifetime_access, welcome_email_sent_at)
- lifetime_orders, protocol_ratings (2,070 seed votes)
- verification_codes, batches, leads

## Critical Production Notes
- DB Name: zurix_sciences
- Backend env: ENVIRONMENT=production, NOWPAYMENTS_IPN_SECRET=set
- PM2 process: zurix-backend
- Nginx config: /etc/nginx/sites-enabled/zurix
- IPN URL configured at NOWPayments: https://zurixsciences.com/api/payment/nowpayments-webhook
