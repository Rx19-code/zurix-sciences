#!/usr/bin/env bash
# Zurix full backup: MongoDB + product images + .env + nginx config.
# Produces a single timestamped tarball in $BACKUP_ROOT and rotates old ones.
# IMPORTANT: copy the tarball OFF the server (see instructions at bottom).
set -euo pipefail

APP_DIR="/var/www/zurix"
ENV_FILE="$APP_DIR/backend/.env"
BACKUP_ROOT="/root/zurix-backups"
KEEP=14   # how many daily backups to keep on the server

# --- read DB config from .env (handles '=' inside the URI) ---
MONGO_URL="$(grep -E '^MONGO_URL=' "$ENV_FILE" | cut -d= -f2-)"
DB_NAME="$(grep -E '^DB_NAME=' "$ENV_FILE" | cut -d= -f2-)"

if [ -z "$MONGO_URL" ] || [ -z "$DB_NAME" ]; then
  echo "❌ Could not read MONGO_URL / DB_NAME from $ENV_FILE"; exit 1
fi

TS="$(date +%F_%H%M%S)"
STAGE="$BACKUP_ROOT/stage-$TS"
mkdir -p "$STAGE"

echo "→ Dumping MongoDB ($DB_NAME)..."
mongodump --uri="$MONGO_URL" --db="$DB_NAME" \
  --archive="$STAGE/mongo-$DB_NAME.archive.gz" --gzip

echo "→ Archiving product images + .env..."
tar czf "$STAGE/assets.tar.gz" -C "$APP_DIR/backend" product_images .env

echo "→ Saving nginx config..."
cp /etc/nginx/sites-available/zurix "$STAGE/nginx-zurix.conf" 2>/dev/null || true

echo "→ Packing single tarball..."
OUT="$BACKUP_ROOT/zurix-backup-$TS.tar.gz"
tar czf "$OUT" -C "$BACKUP_ROOT" "stage-$TS"
rm -rf "$STAGE"

echo "→ Rotating (keeping last $KEEP)..."
ls -1t "$BACKUP_ROOT"/zurix-backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP+1)) | xargs -r rm -f

echo "✅ Backup ready: $OUT ($(du -h "$OUT" | cut -f1))"

# ─────────────────────────────────────────────────────────────
# OFF-SITE COPY (Backblaze B2 via rclone).
# Reads the destination from /etc/zurix-backup.conf so it is NOT tracked in git
# and survives every git pull. Create that file with a single line, e.g.:
#     RCLONE_DEST="b2:zurix-backups"
# If the file/rclone is missing, the local backup still succeeds.
OFFSITE_CONF="/etc/zurix-backup.conf"
if [ -f "$OFFSITE_CONF" ]; then
  # shellcheck disable=SC1090
  . "$OFFSITE_CONF"
  if [ -n "${RCLONE_DEST:-}" ] && command -v rclone >/dev/null 2>&1; then
    echo "→ Uploading off-site to $RCLONE_DEST ..."
    if rclone copy "$OUT" "$RCLONE_DEST" --transfers=1; then
      echo "✅ Off-site upload complete: $RCLONE_DEST"
      # keep only the last 30 backups in the cloud bucket
      rclone delete "$RCLONE_DEST" --min-age 30d --include "zurix-backup-*.tar.gz" 2>/dev/null || true
    else
      echo "⚠️  Off-site upload FAILED — local backup kept at $OUT"
    fi
  fi
else
  echo "ℹ️  No off-site config ($OFFSITE_CONF) — local backup only."
fi
