#!/bin/bash
# ============================================
# Zurix Sciences - Script de Deploy Automatico
# ============================================
# Uso: bash deploy.sh <URL_DO_REPOSITORIO_GITHUB>
# Exemplo: bash deploy.sh https://github.com/seuusuario/zurix-sciences.git
# ============================================

set -e

REPO_URL="$1"
DEPLOY_DIR="/var/www/zurix"
DOMAIN="zurixsciences.com"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Zurix Sciences - Deploy Automatico    ${NC}"
echo -e "${GREEN}========================================${NC}"

# Verificar se URL foi fornecida
if [ -z "$REPO_URL" ]; then
    echo -e "${RED}ERRO: Forneca a URL do repositorio GitHub${NC}"
    echo "Uso: bash deploy.sh https://github.com/seuusuario/zurix-sciences.git"
    exit 1
fi

# ============================================
# PASSO 1: Preparar diretorio
# ============================================
echo -e "\n${YELLOW}[1/7] Preparando diretorio...${NC}"
if [ -d "$DEPLOY_DIR" ]; then
    echo "Backup do diretorio atual..."
    mv "$DEPLOY_DIR" "${DEPLOY_DIR}_backup_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
fi
mkdir -p "$DEPLOY_DIR"

# ============================================
# PASSO 2: Clonar repositorio
# ============================================
echo -e "\n${YELLOW}[2/7] Clonando repositorio...${NC}"
git clone "$REPO_URL" "$DEPLOY_DIR"
cd "$DEPLOY_DIR"
echo -e "${GREEN}Repositorio clonado com sucesso!${NC}"

# ============================================
# PASSO 3: Configurar Backend
# ============================================
echo -e "\n${YELLOW}[3/7] Configurando backend...${NC}"
cd "$DEPLOY_DIR/backend"

# Criar .env do backend
cat > .env << 'ENVEOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=zurix_sciences
CORS_ORIGINS=*
ENVEOF

# Instalar dependencias Python
pip3 install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet
echo -e "${GREEN}Backend configurado!${NC}"

# ============================================
# PASSO 4: Popular banco de dados
# ============================================
echo -e "\n${YELLOW}[4/7] Populando banco de dados...${NC}"
python3 seed_database.py || python seed_database.py
echo -e "${GREEN}Banco de dados populado!${NC}"

# ============================================
# PASSO 5: Configurar Frontend
# ============================================
echo -e "\n${YELLOW}[5/7] Configurando frontend...${NC}"
cd "$DEPLOY_DIR/frontend"

# Criar .env do frontend
cat > .env << ENVEOF
REACT_APP_BACKEND_URL=https://${DOMAIN}
ENVEOF

# Instalar dependencias e fazer build
npm install --legacy-peer-deps 2>/dev/null || yarn install
npm run build 2>/dev/null || yarn build
echo -e "${GREEN}Frontend compilado!${NC}"

# ============================================
# PASSO 6: Configurar PM2 (Backend)
# ============================================
echo -e "\n${YELLOW}[6/7] Configurando PM2...${NC}"
pm2 delete zurix-backend 2>/dev/null || true
pm2 start "uvicorn server:app --host 0.0.0.0 --port 8001" --name zurix-backend --cwd "$DEPLOY_DIR/backend"
pm2 save
echo -e "${GREEN}Backend rodando com PM2!${NC}"

# ============================================
# PASSO 7: Configurar Nginx
# ============================================
echo -e "\n${YELLOW}[7/7] Configurando Nginx...${NC}"

cat > /etc/nginx/sites-available/zurix << NGINXEOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    # Frontend (React build)
    root ${DEPLOY_DIR}/frontend/build;
    index index.html;

    # API proxy para o backend FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # React Router - serve index.html para todas as rotas
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache para arquivos estaticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

# Ativar site
ln -sf /etc/nginx/sites-available/zurix /etc/nginx/sites-enabled/zurix
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Testar e reiniciar Nginx
nginx -t && systemctl restart nginx

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  DEPLOY COMPLETO!                      ${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Site disponivel em: https://${DOMAIN}${NC}"
echo -e "${GREEN}Backend API: https://${DOMAIN}/api/${NC}"
echo -e "\n${YELLOW}Comandos uteis:${NC}"
echo "  pm2 status              - Ver status do backend"
echo "  pm2 logs zurix-backend  - Ver logs do backend"
echo "  pm2 restart zurix-backend - Reiniciar backend"
echo ""
echo -e "${YELLOW}Para atualizar no futuro:${NC}"
echo "  cd $DEPLOY_DIR && git pull"
echo "  cd frontend && npm run build"
echo "  pm2 restart zurix-backend"
