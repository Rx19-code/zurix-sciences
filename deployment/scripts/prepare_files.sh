#!/bin/bash
# ============================================
# NEXGEN SCIENCES - PREPARAÇÃO DE ARQUIVOS
# Script para preparar arquivos para deployment
# ============================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NEXGEN SCIENCES - PREPARAÇÃO DE ARQUIVOS       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Diretório de saída
OUTPUT_DIR="/tmp/nexgen_deploy"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="nexgen_deploy_$TIMESTAMP.tar.gz"

echo -e "${BLUE}[1/5] Limpando diretório de saída...${NC}"
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

echo -e "${BLUE}[2/5] Copiando Backend...${NC}"
mkdir -p $OUTPUT_DIR/backend
cp -r /app/backend/*.py $OUTPUT_DIR/backend/ 2>/dev/null || true
cp /app/backend/requirements.txt $OUTPUT_DIR/backend/ 2>/dev/null || true

# Criar .env limpo para produção
cat > $OUTPUT_DIR/backend/.env << 'EOF'
# CONFIGURAR ANTES DE USAR!
MONGO_URL=mongodb://localhost:27017
DB_NAME=nexgen_db
CORS_ORIGINS=https://SEU_DOMINIO.com
EOF

echo -e "${BLUE}[3/5] Copiando Frontend...${NC}"
mkdir -p $OUTPUT_DIR/frontend

# Copiar código fonte
cp -r /app/frontend/src $OUTPUT_DIR/frontend/
cp -r /app/frontend/public $OUTPUT_DIR/frontend/
cp /app/frontend/package.json $OUTPUT_DIR/frontend/
cp /app/frontend/tailwind.config.js $OUTPUT_DIR/frontend/ 2>/dev/null || true
cp /app/frontend/postcss.config.js $OUTPUT_DIR/frontend/ 2>/dev/null || true

# Criar .env limpo para produção
cat > $OUTPUT_DIR/frontend/.env << 'EOF'
# CONFIGURAR ANTES DE USAR!
REACT_APP_BACKEND_URL=https://SEU_DOMINIO.com
EOF

echo -e "${BLUE}[4/5] Copiando Scripts de Deployment...${NC}"
mkdir -p $OUTPUT_DIR/deployment
cp -r /app/deployment/scripts $OUTPUT_DIR/deployment/
cp -r /app/deployment/guides $OUTPUT_DIR/deployment/

echo -e "${BLUE}[5/5] Criando arquivo compactado...${NC}"
cd /tmp
tar -czf $ARCHIVE_NAME -C $OUTPUT_DIR .

# Mover para diretório de saída
mv $ARCHIVE_NAME $OUTPUT_DIR/

echo ""
echo -e "${GREEN}✅ Arquivos preparados com sucesso!${NC}"
echo ""
echo -e "${YELLOW}📦 Arquivos disponíveis em:${NC}"
echo "   Diretório: $OUTPUT_DIR"
echo "   Arquivo:   $OUTPUT_DIR/$ARCHIVE_NAME"
echo ""
echo -e "${YELLOW}📤 Para copiar para o VPS:${NC}"
echo ""
echo "   # Opção 1: Copiar arquivo compactado"
echo "   scp $OUTPUT_DIR/$ARCHIVE_NAME root@SEU_VPS_IP:/root/"
echo ""
echo "   # Opção 2: Copiar diretórios separados"
echo "   scp -r $OUTPUT_DIR/backend root@SEU_VPS_IP:/var/www/nexgen/"
echo "   scp -r $OUTPUT_DIR/frontend root@SEU_VPS_IP:/var/www/nexgen/"
echo ""
echo -e "${YELLOW}⚠️  LEMBRE-SE:${NC}"
echo "   1. Use VPN antes de conectar"
echo "   2. Configure os arquivos .env no servidor"
echo "   3. Execute o deploy.sh no VPS"
echo ""

# Listar conteúdo
echo -e "${BLUE}📁 Conteúdo do pacote:${NC}"
ls -la $OUTPUT_DIR/
echo ""
du -sh $OUTPUT_DIR/*
echo ""
