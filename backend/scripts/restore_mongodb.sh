#!/bin/bash
# ============================================================================
# Zurix Sciences — MongoDB Restore Script
# ============================================================================
# Restores a specific backup archive into the zurix database.
# ⚠️  WARNING: This REPLACES the current database. Make a fresh backup first!
#
# Usage:
#   bash /var/www/zurix/backend/scripts/restore_mongodb.sh                    # lists available backups
#   bash /var/www/zurix/backend/scripts/restore_mongodb.sh <archive-name>     # restores the given backup
#
# Example:
#   bash /var/www/zurix/backend/scripts/restore_mongodb.sh zurix-backup-2026-07-10_03-00-05.tar.gz
# ============================================================================

set -e

BACKUP_ROOT="/var/backups/zurix-mongodb"
DB_NAME="${DB_NAME:-zurix_sciences}"

# Load env
ENV_FILE="/var/www/zurix/backend/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -E '^(MONGO_URL|DB_NAME)=' "$ENV_FILE" | xargs -d '\n' -I {} echo {})
fi
MONGO_URL="${MONGO_URL:-mongodb://localhost:27017}"

# ─── List mode if no arg ────────────────────────────────────────────────────
if [ -z "$1" ]; then
    echo "Available backups in $BACKUP_ROOT:"
    echo "─────────────────────────────────────────────────────────"
    ls -lh "$BACKUP_ROOT"/zurix-backup-*.tar.gz 2>/dev/null | awk '{ printf "  %-40s  %6s  %s %s\n", $9, $5, $6, $7 }' | sed 's|.*/||'
    echo "─────────────────────────────────────────────────────────"
    echo ""
    echo "Usage: bash $0 <archive-name>"
    echo "Example: bash $0 zurix-backup-2026-07-10_03-00-05.tar.gz"
    exit 0
fi

ARCHIVE_NAME="$1"
ARCHIVE_PATH="$BACKUP_ROOT/$ARCHIVE_NAME"

if [ ! -f "$ARCHIVE_PATH" ]; then
    echo "✗ Archive not found: $ARCHIVE_PATH"
    exit 1
fi

# ─── Safety confirmation ────────────────────────────────────────────────────
echo "⚠️  You are about to RESTORE database '$DB_NAME' from:"
echo "    $ARCHIVE_PATH"
echo ""
echo "⚠️  This will DROP all existing collections in '$DB_NAME' and replace them."
echo ""
read -p "Type 'YES' to confirm: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
    echo "Cancelled."
    exit 0
fi

# ─── Safety backup before restore ───────────────────────────────────────────
echo ""
echo "→ Making safety backup of current database first..."
bash "$(dirname "$0")/backup_mongodb.sh"

# ─── Extract archive ────────────────────────────────────────────────────────
TMP_DIR=$(mktemp -d)
echo ""
echo "→ Extracting $ARCHIVE_NAME..."
tar -xzf "$ARCHIVE_PATH" -C "$TMP_DIR"

# Locate the dumped DB folder inside the extracted structure
DUMP_DB_DIR=$(find "$TMP_DIR" -maxdepth 3 -type d -name "$DB_NAME" | head -n 1)
if [ -z "$DUMP_DB_DIR" ]; then
    echo "✗ Could not find database dump for '$DB_NAME' inside the archive."
    rm -rf "$TMP_DIR"
    exit 1
fi

# ─── Restore ────────────────────────────────────────────────────────────────
echo ""
echo "→ Restoring database $DB_NAME from $DUMP_DB_DIR..."
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" --drop "$DUMP_DB_DIR"

# ─── Cleanup ────────────────────────────────────────────────────────────────
rm -rf "$TMP_DIR"

echo ""
echo "✓ Restore completed."
echo "→ Restart the backend to pick up any schema changes:"
echo "    pm2 restart zurix-backend"

exit 0
