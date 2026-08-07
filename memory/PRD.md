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
- [x] Multi-image gallery per product (drag-and-drop, up to 6 images), local hosting via /api/images/products/
- [x] MIME type fix (JPG/WEBP served with correct content-type)
- [x] Nginx 404 fix on /api/images: `location ^~ /api/` priority + full `systemctl restart nginx` (reload was not enough) — resolved 2026-06
- [x] MongoDB auth enabled + automated daily backups (cron)
- [x] Admin Health Dashboard (PM2, DB, disk, backups)
- [x] Wholesale PDF invoice generator
- [x] Dynamic dilution toggle (1ml/2ml/3ml) in HubDetail.js
- [x] Epithalon 10mg + Adamax 10mg products; Thymosin Alpha-1/Epithalon/Adamax protocols enriched

## Pending Tasks
- [ ] P1: Labels tab exports (Export Excel / Download All CSV) — apply 2-line code format (user requested) — DONE 2026-06
- [ ] P1: Print Shop Labels PDF (50x50mm art + 10mm QR) — DEFERRED to future by user (QR 10mm approved; pending: text below vs around QR; grid vs 1/page)
- [ ] P1: New products to add: Orforglipron 6mg, Vitamin B12 10.000mcg — DONE by user via Products tab (2026-06)
- DEFERRED by user (2026-06): Invoice status tracking (Pending/Paid/Canceled); Counterfeit email alert on suspicious scans
- [ ] P1: E2E payment test with $1 USDT (script ready: scripts/e2e_payment_test.py)
- [ ] P2: Invoice status tracking (Pending/Paid/Canceled) + filters in Admin
- [ ] P2: Video verification per product (video_url field + player on product page)
- [ ] P2: SEO — dynamic meta tags, Schema.org, sitemap.xml, Open Graph
- [ ] P2: Populate remaining 14 peptides in Free Library with detailed data
- [ ] P2: Multi-currency support (BTC, ETH, USDC besides USDT-TRC20)
- [ ] P2: Revenue chart in admin (last 30 days)
- [ ] P3: Rate limiting on /api/verify and /api/auth/login
- [ ] P3: JWT migration localStorage → httpOnly cookies
- [ ] P3: Refactor Admin.js (1000+ lines) into sub-components
- [ ] P3: Enable Njalla auto-renew (server paid until June 28, 2026)
- REJECTED by user (do not propose again): automated wholesale invoice email via Resend; shopping cart / multi-product checkout (no shipping operations)

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

## Changelog
- 2026-02-27: Added red "SITE UNDER UPDATE" top banner (UpdateNoticeBanner.js) above the yellow regulatory banner — non-dismissible, English copy, responsive, animated alert icons.
- 2026-06: Fixed production 404 on /api/images/products/* — root cause: Nginx regex block `location ~* \.(png|jpg...)$` intercepting /api/ image URLs; fix: `location ^~ /api/` + full nginx restart (reload insufficient). Verified 200 image/png via curl on live domain.
- 2026-06: Wholesale price list — Tier 3 relabeled to "$2,000 – $4,000"; added highlighted callout box in PDF: orders over $4,000 → "High-volume orders may qualify for exclusive commercial conditions. Please contact our sales team for a personalized quotation." Updated tier labels in WholesaleTab.js and invoice _detect_tier. Verified via curl + pypdf text extraction.
- 2026-06: Auto code generation replacing Google Sheets — new "⚡ Generate Automatically" mode in Admin Import tab (GenerateCodesPanel.js). Admin picks product + fab date + qty → backend generates batch ID (ZX-YYMMDD-CODE-SEQ), compact codes (ZX{CODE}{SEQ}{6hex} via secrets, DB uniqueness check), expiry auto +24 months (day 1, same as sheet formula), CSV download with QR URLs. Endpoints: GET /api/admin/batch-suggestion (suggests product_code + next sequence from last batch), POST /api/admin/generate-codes. Manual paste mode kept. Tested: curl (generation + e2e verify of generated code) + UI screenshot.
- 2026-06: Brand QR tab (BrandQRTab.js) — fixed deterministic QR to https://zurixsciences.com with ZX center badge (EC level H). GET /api/admin/brand-qr?size= (200-6000px, 300 DPI PNG). Downloads: 1000/2000/4000px for keychains, boxes, banners. Verified: identical md5 across generations + pyzbar decode OK + screenshot.
- 2026-06: Brand QR refinements — badge restyled to logo colors (Z black + X blue #3e68b0, bold italic); added transparent PNG option (?transparent=true, PIL-only alpha, no numpy — numpy missing in prod caused JSON error). Checkbox in BrandQRTab. Verified decode over colored background.
- 2026-06: Generate Codes export switched CSV → Excel (.xlsx via xlsx lib) for Niimbot compatibility. Code split in 2 lines (prefix ZXGHK1003 + suffix D746DC): columns Code Line 1, Code Line 2, and Code (2 lines) with embedded newline. Labels tab PNGs also split compact codes into 2 lines. Verified via openpyxl read of downloaded file.
- 2026-06: Labels tab exports updated with 2-line split — Export Excel (client XLSX) got Code Line 1/2 + Code (2 lines) columns; Download All CSV (backend /api/admin/codes/export-all) got Code Line 1/2 columns. Verified: curl CSV + real Excel download via UI + openpyxl.
- 2026-06: New products pending user registration (descriptions provided): Orforglipron 6mg 30 tabs (GLP-1 Analogs) and Vitamin B12 Cyanocobalamin 10,000mcg liquid (storage 2-8°C protect from light). User to add via Products tab or send prices for agent to insert.
- 2026-06: Floating reseller contact widget (FloatingContact.js, mounted in App.js Layout — hidden on admin/login). Green FAB bottom-right → panel with 3 reps from /api/representatives (Paraguay & USA WhatsApp wa.me links, Switzerland Threema threema.id/2D9DAD9R). On /products/:id the WhatsApp message is pre-filled with product name + URL ("About: {product}" shown in header). Verified via screenshot on catalog + product page.
- 2026-06: Verification Scan Map — new admin tab "🌍 Scan Map" (ScanMapTab.js, leaflet 1.9.4 + CARTO dark tiles). Stats cards (total/located/countries/cities), circle markers sized by scan count, Top Countries with flags + Top Cities list. Backend: GET /api/admin/verifications/geo-stats (aggregation on verification_logs); get_geolocation now also captures lat/lon (ip-api) stored in new logs; older logs fall back to country centroids (CENTROIDS dict in component). Verified: seeded 6 test logs, screenshot with 7 markers + stats, cleaned up after.
- PENDING DECISION (user): Print Shop Labels PDF (Option 1 - variable data): QR 10mm bottom-right on 50x50mm label art from /tmp/zurix_labels.pdf (user uploaded "Zurix Label Bags.pdf", vector, ~41 product labels grid 1200x1000pt). User approved 10mm size; choosing between text below QR (aligned w/ EXP) vs text around QR; grid sheets (42/sheet) vs 1-label-per-page; auto-update Batch/EXP text in art.
