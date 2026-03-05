# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website for selling peptide research products and a companion mobile application for Zurix Sciences.

## Core Features

### Website
- Product catalog with shopping cart and checkout
- QR code product verification system (tracks scans, blocks after 3 scans)
- Private admin panel (`/admin`) for managing products and verification codes
- Representatives page with international contacts

### Mobile App (React Native/Expo)
- Multi-tab layout: Home, Verify, Protocols, Profile
- User authentication system (email/password)
- QR code scanning for product verification
- Research protocols as downloadable PDFs (In-App Purchase)
- Order and verification history

## Tech Stack
- **Backend:** FastAPI, MongoDB (Motor), JWT authentication
- **Frontend (Web):** React, TailwindCSS
- **Frontend (Mobile):** React Native, Expo
- **Deployment:** Cloudflare (DNS/Proxy), PM2, manual git pull
- **Domain:** zurixsciences.com (via Njalla)

## Current Status

### ✅ Completed
- Full website with product catalog, cart, checkout
- Admin panel with code management (import/delete)
- QR verification system with scan tracking
- User authentication backend (register/login/JWT)
- Mobile app with auth modals and profile screen
- Protocol system (PDF-based) structure
- 12 product images updated
- Representatives page with Threema support

### 🚧 In Progress / Blocked
- **P0 - Mobile Network Bug:** "Network request failed" prevents API access
- **Blocked:** Email service (Resend) - awaiting API key
- **Blocked:** Protocol PDFs - awaiting content
- **Blocked:** 20 remaining product images - awaiting designer

### 📋 Backlog (Freelancer)
- Implement In-App Purchases (Google/Apple)
- Publish to app stores
- Improve app icon design

## Key Files
- `mobile/App.js` - Monolithic file (1500+ lines), needs refactoring
- `backend/server.py` - All API routes including auth
- `frontend/src/pages/Admin.js` - Admin panel
- `mobile/app.json` - App configuration and permissions

## API Endpoints
- `/api/auth/register` (POST)
- `/api/auth/login` (POST)
- `/api/products` (GET)
- `/api/verify-product` (POST)
- `/api/protocols-v2` (GET)
- `/api/admin/codes/{code_id}` (DELETE)

## Database Collections
- `products` - Product catalog
- `verification_codes` - QR codes with scan history
- `users` - User accounts (email, hashed_password)
- `protocols_v2` - Protocol metadata (name, price, pdf_filename)
- `user_purchases` - Purchase records

## Credentials
- **Admin Panel:** `/admin` - Password: `Rx050217!`
- **Server SSH:** `ssh -i "$HOME\.ssh\njalla_key" root@80.78.19.40`

## Notes for Development
- Production DB updates must use Python scripts (pattern established)
- Mobile app works only with `--tunnel` flag (network issue)
- User struggles with deployment - provide clear numbered commands
