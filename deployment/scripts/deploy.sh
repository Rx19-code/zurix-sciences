#!/bin/bash
# ============================================
# NEXGEN SCIENCES - DEPLOYMENT SCRIPT
# Deployment Anônimo para VPS
# ============================================

set -e

echo "🚀 Iniciando deployment do Zurix Sciences..."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações - ALTERE AQUI
DOMAIN="seu-dominio.com"
BACKEND_PORT=8001
FRONTEND_PORT=3000
APP_DIR="/var/www/zurix"

# ============================================
# 1. ATUALIZAR SISTEMA
# ============================================
echo -e "${BLUE}[1/10] Atualizando sistema...${NC}"
apt update && apt upgrade -y

# ============================================
# 2. INSTALAR DEPENDÊNCIAS
# ============================================
echo -e "${BLUE}[2/10] Instalando dependências...${NC}"
apt install -y nginx mongodb-server python3 python3-pip nodejs npm git curl ufw fail2ban

# Instalar PM2 para gerenciar Node.js
npm install -g pm2 yarn

# ============================================
# 3. CONFIGURAR FIREWALL
# ============================================
echo -e "${BLUE}[3/10] Configurando firewall...${NC}"
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw reload

# ============================================
# 4. CRIAR DIRETÓRIOS
# ============================================
echo -e "${BLUE}[4/10] Criando estrutura de diretórios...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/backend
mkdir -p $APP_DIR/frontend
mkdir -p /var/log/zurix

# ============================================
# 5. COPIAR ARQUIVOS (você fará via SCP/SFTP)
# ============================================
echo -e "${BLUE}[5/10] Preparando para receber arquivos...${NC}"
echo "📁 Diretório preparado em: $APP_DIR"
echo "⚠️  IMPORTANTE: Você precisa copiar os arquivos via SCP:"
echo ""
echo "   scp -r /app/backend root@SEU_VPS_IP:$APP_DIR/"
echo "   scp -r /app/frontend root@SEU_VPS_IP:$APP_DIR/"
echo ""
read -p "Pressione ENTER quando os arquivos estiverem copiados..."

# ============================================
# 6. CONFIGURAR BACKEND
# ============================================
echo -e "${BLUE}[6/10] Configurando Backend...${NC}"
cd $APP_DIR/backend

# Instalar dependências Python
pip3 install -r requirements.txt

# Criar .env se não existir
if [ ! -f .env ]; then
    echo "MONGO_URL=mongodb://localhost:27017" > .env
    echo "DB_NAME=zurix_db" >> .env
    echo "CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN" >> .env
fi

# Popular banco de dados
python3 seed_database.py
python3 seed_protocols.py

# ============================================
# 7. CONFIGURAR FRONTEND
# ============================================
echo -e "${BLUE}[7/10] Configurando Frontend...${NC}"
cd $APP_DIR/frontend

# Atualizar API URL no .env
echo "REACT_APP_BACKEND_URL=https://$DOMAIN" > .env

# Instalar dependências
yarn install

# Build de produção
yarn build

# ============================================
# 8. CONFIGURAR NGINX
# ============================================
echo -e "${BLUE}[8/10] Configurando Nginx...${NC}"
cat > /etc/nginx/sites-available/zurix << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL Configuration (será configurado com certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Frontend
    location / {
        root $APP_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Logs mínimos (privacidade)
    access_log /var/log/nginx/zurix_access.log;
    error_log /var/log/nginx/zurix_error.log;
}
EOF

ln -sf /etc/nginx/sites-available/zurix /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

# ============================================
# 9. CONFIGURAR PM2 PARA BACKEND
# ============================================
echo -e "${BLUE}[9/10] Configurando PM2 para Backend...${NC}"
cd $APP_DIR/backend

# Criar arquivo de configuração PM2
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'zurix-backend',
    script: 'uvicorn',
    args: 'server:app --host 0.0.0.0 --port $BACKEND_PORT',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOF

# Iniciar backend com PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# ============================================
# 10. INSTALAR SSL (CERTBOT)
# ============================================
echo -e "${BLUE}[10/10] Instalando SSL com Certbot...${NC}"
apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${GREEN}✅ Instalação básica concluída!${NC}"
echo ""
echo "🔐 PRÓXIMO PASSO: Configurar SSL"
echo "Execute:"
echo "   certbot --nginx -d $DOMAIN"
echo ""
echo "Depois reinicie os serviços:"
echo "   systemctl restart nginx"
echo "   pm2 restart all"
echo ""
echo -e "${GREEN}🎉 Deployment concluído!${NC}"
echo ""
echo "Acesse seu site em: https://$DOMAIN"
