#!/usr/bin/env bash
# Restore a Zurix backup created by backup_zurix.sh onto a (new) server.
# Usage: ./restore_zurix.sh /path/to/zurix-backup-YYYY-MM-DD_HHMMSS.tar.gz
# Assumes /var/www/zurix code is already cloned and backend/.env is in place.
set -euo pipefail

BK="${1:-}"
if [ -z "$BK" ] || [ ! -f "$BK" ]; then
  echo "Usage: $0 /path/to/zurix-backup-*.tar.gz"; exit 1
fi

APP_DIR="/var/www/zurix"
ENV_FILE="$APP_DIR/backend/.env"
MONGO_URL="$(grep -E '^MONGO_URL=' "$ENV_FILE" | cut -d= -f2-)"
DB_NAME="$(grep -E '^DB_NAME=' "$ENV_FILE" | cut -d= -f2-)"

TMP="$(mktemp -d)"
tar xzf "$BK" -C "$TMP"
DIR="$(find "$TMP" -maxdepth 1 -type d -name 'stage-*' | head -1)"

echo "→ Restoring MongoDB ($DB_NAME) [--drop replaces existing data]..."
mongorestore --uri="$MONGO_URL" --db="$DB_NAME" \
  --archive="$DIR/mongo-$DB_NAME.archive.gz" --gzip --drop

echo "→ Restoring product images + .env..."
tar xzf "$DIR/assets.tar.gz" -C "$APP_DIR/backend"

echo "→ nginx config available at: $DIR/nginx-zurix.conf (copy manually if needed)"
rm -rf "$TMP"
echo "✅ Restore complete. Run: pm2 restart zurix-backend && systemctl reload nginx"
