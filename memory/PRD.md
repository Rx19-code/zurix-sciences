# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products with PWA capabilities and product verification system.

## What's Been Implemented

### February 2026 - Protocol System V3 (Single-Use Code + Watermarking)
- [x] Refactored protocol system: validation by **single-use unique QR code** (not batch number)
- [x] Auto-detects matching protocol from product name in QR code
- [x] **PDF watermarking** with "ZURIX SCIENCES - FOR RESEARCH ONLY" + "Downloaded by: [email]"
- [x] Single-use enforcement: each code allows only one protocol download
- [x] New endpoints: `POST /api/protocols-v2/validate-code`, `POST /api/protocols-v2/send-protocol`
- [x] Frontend redesigned: inline code validation flow (no more modal for free protocols)
- [x] Lead data saved to `protocol_leads` with verification code tracking
- [x] Backward compatibility: old batch validation endpoints still functional

### March 6, 2026 - Previous Major Updates
- [x] QR Code Scanner fixed for Android/iOS (camera permission handling)
- [x] `/protocols` page with free and paid protocols
- [x] Lead collection system (email, phone, name) saved to `protocol_leads` collection
- [x] Email delivery via Resend with PDF attachments
- [x] **USDT Payment System (TRC20)** - Automatic blockchain verification
- [x] 3 Advanced Protocols at $4.99 each (paid via USDT)
- [x] Flag images for Representatives page (using flagcdn.com)
- [x] Admin "All Codes" pagination (250 per page)
- [x] Admin batch editing (purity, expiry_date)
- [x] Protocols link added to navbar and footer

### Previous Implementations
- [x] Full-stack website (FastAPI + React)
- [x] PWA conversion with manifest and icons
- [x] Product verification with QR scanner
- [x] Multi-language protocol downloads (EN, ES, PT)
- [x] Resend email integration
- [x] Server-side admin search
- [x] 27 product images uploaded

## Technical Architecture

### Stack
- **Backend**: FastAPI, MongoDB (Motor), Resend, PyPDF2, reportlab, httpx (Tron API)
- **Frontend**: React, TailwindCSS, PWA, html5-qrcode
- **Payments**: USDT TRC20 via Tron blockchain

### Key Endpoints
- `/api/protocols-v2/validate-code` - Validate unique QR code & auto-detect protocol
- `/api/protocols-v2/send-protocol` - Send watermarked PDF via email (single-use)
- `/api/protocols-v2` - List all protocols (free + paid)
- `/api/payment/create-order` - Create paid protocol order
- `/api/payment/verify` - Verify USDT payment on Tron blockchain
- `/api/admin/codes` - Paginated codes list

### Database Collections
- `unique_codes` - Product verification codes (now with `protocol_downloaded_at`, `protocol_downloaded_by`, `protocol_language`)
- `protocol_leads` - Collected leads from protocol downloads (now with `verification_code` field)
- `protocol_orders` - Paid protocol orders
- `protocol_downloads` - Download logs (now with `verification_code`, `watermarked` fields)

## Prioritized Backlog

### P0 - Done
- ~~Protocol system refactor (single-use code + watermarking)~~
- ~~QR Scanner fix~~
- ~~USDT payment system~~

### P1 - Next
- [ ] Admin panel - Leads tab (view/export collected contacts from protocol downloads)
- [ ] Clarify paid "Advanced Protocols" with user (keep or remove USDT UI)

### P2 - Future
- [ ] Complete 5 missing product images (waiting on user assets)
- [ ] Resume mobile app development

## Credentials

### Production Server
- **Domain**: zurixsciences.com
- **SSH**: `ssh -i "$HOME\.ssh\njalla_key" root@80.78.19.40`

### Admin Panel
- **URL**: `/admin`
- **Password**: `Rx050217!`

### Test Data
- **Valid Test Codes**: `ZX-260312-GHK50-1-TEST01` (GHK-Cu), `ZX-260209-TB500-1-TEST01` (TB-500), `ZX-260115-BPC157-1-TEST01` (BPC-157)

## Files Reference
- `frontend/src/pages/Protocols.js` - Protocols page with code validation + paid protocols
- `frontend/src/pages/Verify.js` - QR scanner
- `frontend/src/pages/Admin.js` - Admin panel
- `backend/server.py` - All API endpoints
