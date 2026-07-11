# Test Credentials

## User Accounts
- **Test User**: test@test.com / test123 (has_lifetime_access: false)
- **Preview Tester (Lifetime Access)**: preview@zurixsciences.com / Preview2026! (has_lifetime_access: true)

## Admin
- **Admin Password**: Rx050217!

## MongoDB (PRODUCTION SERVER ONLY — dev preview uses no-auth)
- **Auth user**: zurix_admin
- **Auth database**: admin
- **Roles**: userAdminAnyDatabase, readWriteAnyDatabase, dbAdminAnyDatabase
- **Password**: [stored securely by user — rotated 2026-07-11]
- **Backups**: cron @ 3AM UTC → `/var/backups/zurix-mongodb/` (30-day retention)

## API Keys
- **NOWPayments**: ER8A5WS-34840WY-NGHX1VS-7PF129J
- **JWT Secret**: 8f5c0afc04ecbf3b9421e7413437f786a9f7ea5d7a5f795b91ee6d7399fc14cd

## Auth Methods
- Email + Password (JWT)
- Google OAuth (Emergent Auth)
