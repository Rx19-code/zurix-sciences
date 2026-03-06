# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### March 6, 2026 - Major Updates
- [x] QR Code Scanner fixed for Android/iOS (camera permission handling)
- [x] `/protocols` page with free and paid protocols
- [x] Lead collection system (email, phone, name) saved to `protocol_leads` collection
- [x] Email delivery via Resend with PDF attachments
- [x] **USDT Payment System (TRC20)** - Automatic blockchain verification
- [x] 3 Advanced Protocols at $4.99 each (paid via USDT)
- [x] Flag images for Representatives page (using flagcdn.com)
- [x] Admin "All Codes" pagination (250 per page)
- [x] Protocols link added to navbar and footer

### Previous Implementations
- [x] Full-stack website (FastAPI + React)
- [x] PWA conversion with manifest and icons
- [x] Product verification with QR scanner
- [x] Dynamic protocol system with batch validation
- [x] Multi-language protocol downloads (EN, ES, PT)
- [x] Resend email integration
- [x] Server-side admin search

## Technical Architecture

### Stack
- **Backend**: FastAPI, MongoDB (Motor), Resend, httpx (Tron API)
- **Frontend**: React, TailwindCSS, PWA, html5-qrcode
- **Payments**: USDT TRC20 via Tron blockchain

### Key Endpoints
- `/api/protocols-v2` - List all protocols (free + paid)
- `/api/protocols-v2/validate-batch` - Validate batch for free protocols
- `/api/protocols-v2/send-email` - Send free protocol via email
- `/api/payment/create-order` - Create paid protocol order
- `/api/payment/verify` - Verify USDT payment on Tron blockchain
- `/api/admin/codes` - Paginated codes list

### Database Collections
- `users` - User accounts
- `unique_codes` - Product verification codes
- `protocol_leads` - Collected leads from protocol downloads
- `protocol_orders` - Paid protocol orders
- `protocol_downloads` - Download logs

### USDT Wallet
- **Address**: TJKuseoNmGw1TnwskKjaBCw5FrYUynAP9m
- **Network**: TRC20 (Tron)

## Prioritized Backlog

### P0 - Done
- ~~QR Scanner fix~~
- ~~Protocols page~~
- ~~USDT payment system~~

### P1 - Next
- [ ] Admin panel for viewing/exporting leads
- [ ] Create 9 Advanced Protocol PDFs

### P2 - Future
- [ ] Add 20 product images (waiting for designer)
- [ ] Resume mobile app development

## Credentials

### Production Server
- **Domain**: zurixsciences.com
- **SSH**: `ssh -i "$HOME\.ssh\njalla_key" root@80.78.19.40`

### Admin Panel
- **URL**: `/admin`
- **Password**: `Rx050217!`

### Test Data
- **Valid Batch Numbers**: `ZX-260312-GHK50-1`, `ZX-260209-TB500-1`

## Files Reference
- `frontend/src/pages/Protocols.js` - Protocols page with payment flow
- `frontend/src/pages/Verify.js` - QR scanner
- `frontend/src/pages/Admin.js` - Admin panel
- `frontend/src/pages/Representatives.js` - Flag images
- `backend/server.py` - All API endpoints including payment verification
