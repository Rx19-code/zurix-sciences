#!/bin/bash
# ============================================================================
# Zurix Sciences — Daily MongoDB Backup Script
# ============================================================================
# Creates a timestamped mongodump of the zurix database.
# Keeps the last 30 days of backups, auto-deletes older ones.
# Logs to /var/log/zurix-backup.log
#
# Usage (manual):    bash /var/www/zurix/backend/scripts/backup_mongodb.sh
# Usage (cron):      0 3 * * * bash /var/www/zurix/backend/scripts/backup_mongodb.sh
# ============================================================================

set -e

# ─── Config ─────────────────────────────────────────────────────────────────
BACKUP_ROOT="/var/backups/zurix-mongodb"
RETENTION_DAYS=30
LOG_FILE="/var/log/zurix-backup.log"
DB_NAME="${DB_NAME:-zurix_sciences}"

# MongoDB connection — reads MONGO_URL from backend/.env if available
ENV_FILE="/var/www/zurix/backend/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -E '^(MONGO_URL|DB_NAME)=' "$ENV_FILE" | xargs -d '\n' -I {} echo {})
fi
MONGO_URL="${MONGO_URL:-mongodb://localhost:27017}"

# ─── Setup ──────────────────────────────────────────────────────────────────
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="$BACKUP_ROOT/$TODAY"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log "=========================================="
log "Starting MongoDB backup for database: $DB_NAME"
log "Backup directory: $BACKUP_DIR"

# ─── Backup ─────────────────────────────────────────────────────────────────
mkdir -p "$BACKUP_DIR"

if mongodump --uri="$MONGO_URL" --db="$DB_NAME" --out="$BACKUP_DIR" --quiet >> "$LOG_FILE" 2>&1; then
    SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    log "✓ Backup completed successfully (size: $SIZE)"

    # Compress
    ARCHIVE="$BACKUP_ROOT/zurix-backup-$TIMESTAMP.tar.gz"
    tar -czf "$ARCHIVE" -C "$BACKUP_ROOT" "$TODAY" 2>> "$LOG_FILE"
    ARCHIVE_SIZE=$(du -sh "$ARCHIVE" | cut -f1)
    log "✓ Compressed to $ARCHIVE ($ARCHIVE_SIZE)"

    # Remove uncompressed directory (we keep only the .tar.gz)
    rm -rf "$BACKUP_DIR"
else
    log "✗ Backup FAILED — check $LOG_FILE"
    exit 1
fi

# ─── Retention: delete backups older than RETENTION_DAYS ────────────────────
DELETED=$(find "$BACKUP_ROOT" -name "zurix-backup-*.tar.gz" -mtime +$RETENTION_DAYS -type f -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    log "✓ Deleted $DELETED backup(s) older than $RETENTION_DAYS days"
fi

# ─── Report ─────────────────────────────────────────────────────────────────
TOTAL=$(find "$BACKUP_ROOT" -name "zurix-backup-*.tar.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" 2>/dev/null | cut -f1)
log "✓ Total backups on disk: $TOTAL ($TOTAL_SIZE)"
log "Done."

exit 0
