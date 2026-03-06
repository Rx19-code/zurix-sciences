# Zurix Sciences - Product Requirements Document

## Original Problem Statement
Build a professional e-commerce website (Zurix Sciences) for selling peptide research products. The project pivoted from native mobile app to a Progressive Web App (PWA) approach.

## Core Requirements

### Website & PWA Features
- Product catalog, shopping cart, and checkout process
- Product verification system with QR code scanning (mobile) and manual entry (desktop)
- Free research protocols gated by batch number validation
- Multi-language protocol downloads (EN, ES, PT)
- Automated email system for purchase confirmations
- Admin panel for managing products, verification codes, and logs

### Mobile App (ON HOLD)
- React Native app in `mobile/` directory preserved for future development

## User Personas
- **Researchers**: Need to verify product authenticity and access research protocols
- **Administrators**: Manage products, codes, and view system logs

## Technical Architecture

### Stack
- **Backend**: FastAPI, MongoDB (Motor), Resend (emails)
- **Frontend**: React, TailwindCSS, PWA, html5-qrcode
- **Mobile (ON HOLD)**: React Native, Expo

### Key Endpoints
- `/api/verify-product` - Product verification
- `/api/protocols-v2/validate-batch` - Batch validation for protocols
- `/api/protocols-v2/download` - Protocol PDF download
- `/api/admin/codes` - Server-side search for codes
- `/api/admin/test-email` - Test email via Resend

### Database Schema
- `users`: `{email, hashed_password}`
- `unique_codes`: `{code, product_name, batch_number, ...}`
- `protocols_v2`: Protocol definitions with language-specific PDFs

## What's Been Implemented

### Completed (March 2026)
- [x] Full-stack website (FastAPI + React) deployed
- [x] PWA conversion with manifest and icons
- [x] QR code scanner on `/verify` page for all users
- [x] Dynamic protocol system with batch validation
- [x] Multi-language protocol downloads (9 PDFs uploaded)
- [x] Resend email integration with verified domain
- [x] Server-side admin search (scalable)
- [x] Mobile app network bug fixed (app on hold)

### Code Cleanup (March 6, 2026)
- [x] Removed unused `isMobile` state from Verify.js
- [x] Added data-testid attributes for testing
- [x] Both QR scan and manual entry visible for all users

## Prioritized Backlog

### P0 - Critical (Done)
- ~~QR Scanner not visible on Android~~ → Code fixed, needs production deploy

### P1 - High Priority
- [ ] Implement paid "Advanced Protocols" ($4.99) - Stripe integration

### P2 - Medium Priority
- [ ] Add remaining 20 product images (waiting for designer)
- [ ] Resume native mobile app development

## Credentials & Access

### Production Server
- **Domain**: zurixsciences.com
- **SSH**: `ssh -i "$HOME\.ssh\njalla_key" root@80.78.19.40`

### Admin Panel
- **URL**: `/admin`
- **Password**: `Rx050217!`

### Test Data
- **Valid Batch Numbers**: 
  - `ZX-260312-GHK50-1` (GHK-Cu)
  - `ZX-260209-TB500-1` (TB-500)

## Known Issues
- User has recurring DNS/VPN/network issues (local to their network in Paraguay)
- Workarounds: disconnect VPN, use mobile data, change DNS to 8.8.8.8

## Files of Reference
- `frontend/src/pages/Verify.js` - QR scanner and verification
- `frontend/public/manifest.json` - PWA config
- `backend/server.py` - API endpoints
- `backend/protocols_pdf/` - Protocol PDF files
