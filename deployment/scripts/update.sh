#!/bin/bash
# ============================================
# Zurix Sciences - Script de Atualizacao
# ============================================
# Uso: bash update.sh
# Executa no servidor apos git pull
# ============================================

set -e

DEPLOY_DIR="/var/www/zurix"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Atualizando Zurix Sciences...${NC}"

cd "$DEPLOY_DIR"
git pull

echo -e "${YELLOW}Reconstruindo frontend...${NC}"
cd "$DEPLOY_DIR/frontend"
npm install --legacy-peer-deps 2>/dev/null || true
npm run build

echo -e "${YELLOW}Reiniciando backend...${NC}"
cd "$DEPLOY_DIR/backend"
pip3 install -r requirements.txt --quiet 2>/dev/null || true
pm2 restart zurix-backend

echo -e "${GREEN}Atualizacao completa!${NC}"
echo -e "${GREEN}Site: https://zurixsciences.com${NC}"
