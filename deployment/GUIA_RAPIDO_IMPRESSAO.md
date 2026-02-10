# 🚀 GUIA RÁPIDO - DEPLOYMENT ANÔNIMO
## Zurix Science - Passo a Passo para Impressão

---

## ⏱️ TEMPO TOTAL ESTIMADO: 2-4 HORAS

---

# FASE 1: PREPARAÇÃO (30-60 min)

## 1️⃣ INSTALAR VPN (10 min)

| Passo | Ação |
|-------|------|
| 1 | Acesse: **https://mullvad.net** |
| 2 | Clique **"Generate account"** |
| 3 | Anote o número da conta: `________________` |
| 4 | Baixe o app Mullvad para seu sistema |
| 5 | Instale e conecte usando o número |
| 6 | Pague depois com crypto |

**☐ VPN Configurada**

---

## 2️⃣ CRIAR EMAIL ANÔNIMO (10 min)

⚠️ **VPN DEVE ESTAR LIGADA**

| Passo | Ação |
|-------|------|
| 1 | Acesse: **https://proton.me** |
| 2 | Clique **"Create account"** |
| 3 | Escolha email gratuito |
| 4 | NÃO precisa telefone |
| 5 | Anote os dados abaixo |

**Meu Email:** `_______________________________`

**Minha Senha:** `_______________________________`

**☐ Email Criado**

---

## 3️⃣ PREPARAR CRYPTO (10-30 min)

### 💰 Quanto você precisa:
- VPS: ~$15/mês
- Domínio: ~$15/ano
- **TOTAL: ~$30 (~0.001 BTC)**

### Opções para comprar Bitcoin:
- [ ] Já tenho Bitcoin
- [ ] Bisq (P2P) - https://bisq.network
- [ ] Bitcoin ATM (dinheiro)
- [ ] Pedir para amigo enviar

**Minha Carteira Bitcoin:** `_______________________________`

**☐ Crypto Preparada**

---

# FASE 2: COMPRAR VPS + DOMÍNIO (30-45 min)

## 4️⃣ CRIAR CONTA NJALLA (15 min)

⚠️ **VPN DEVE ESTAR LIGADA**

| Passo | Ação |
|-------|------|
| 1 | Acesse: **https://njal.la** |
| 2 | Clique **"Sign Up"** |
| 3 | Use o email ProtonMail |
| 4 | Crie senha DIFERENTE do email |
| 5 | Confirme email |

**Senha Njalla:** `_______________________________`

**☐ Conta Njalla Criada**

---

## 5️⃣ COMPRAR VPS (15 min)

| Passo | Ação |
|-------|------|
| 1 | Dashboard → **VPS** |
| 2 | Localização: **Sweden** |
| 3 | Plano: **VPS 15** (~$15/mês) |
| 4 | OS: **Ubuntu 22.04** |
| 5 | Checkout → **Bitcoin** |
| 6 | Copie endereço BTC |
| 7 | Envie da sua carteira |
| 8 | Aguarde 10-30 min |

**IP do Servidor:** `_______________________________`

**Senha Root:** `_______________________________`

**☐ VPS Comprado**

---

## 6️⃣ COMPRAR DOMÍNIO (10 min)

| Passo | Ação |
|-------|------|
| 1 | Dashboard → **Domains** |
| 2 | Busque seu domínio desejado |
| 3 | Adicione ao carrinho |
| 4 | Checkout → **Bitcoin** |
| 5 | Aguarde confirmação |

**Meu Domínio:** `_______________________________`

**☐ Domínio Comprado**

---

# FASE 3: CONFIGURAR SERVIDOR (45-60 min)

## 7️⃣ BAIXAR ARQUIVOS DO EMERGENT (5 min)

| Passo | Ação |
|-------|------|
| 1 | No Emergent, clique **"Download"** |
| 2 | Baixe projeto como ZIP |
| 3 | Extraia no computador |

**Local dos arquivos:** `_______________________________`

**☐ Arquivos Baixados**

---

## 8️⃣ CONECTAR AO VPS (5 min)

⚠️ **VPN DEVE ESTAR LIGADA**

### No Terminal (Mac/Linux):
```
ssh root@SEU_IP_DO_VPS
```

### No Windows:
- Use **PuTTY**
- Host: SEU_IP_DO_VPS
- Port: 22

### Primeiro comando após conectar:
```
passwd
```
(Troque a senha imediatamente!)

**Nova Senha Root:** `_______________________________`

**☐ Conectado ao VPS**

---

## 9️⃣ INSTALAR DEPENDÊNCIAS (20 min)

### Copie e cole cada bloco no terminal do VPS:

**Bloco 1 - Atualizar sistema:**
```
apt update && apt upgrade -y
```

**Bloco 2 - Instalar programas:**
```
apt install -y nginx python3 python3-pip nodejs npm git curl ufw fail2ban mongodb-server
```

**Bloco 3 - Instalar PM2 e Yarn:**
```
npm install -g pm2 yarn
```

**Bloco 4 - Iniciar MongoDB:**
```
systemctl start mongodb
systemctl enable mongodb
```

**Bloco 5 - Configurar Firewall:**
```
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable
```

**Bloco 6 - Criar diretórios:**
```
mkdir -p /var/www/zurix/backend
mkdir -p /var/www/zurix/frontend
```

**☐ Dependências Instaladas**

---

## 🔟 COPIAR ARQUIVOS PARA VPS (10 min)

### Execute NO SEU COMPUTADOR (não no VPS):

⚠️ **VPN DEVE ESTAR LIGADA**

**Copiar Backend:**
```
scp -r /caminho/para/backend/* root@SEU_IP:/var/www/zurix/backend/
```

**Copiar Frontend:**
```
scp -r /caminho/para/frontend/* root@SEU_IP:/var/www/zurix/frontend/
```

**☐ Arquivos Copiados**

---

## 1️⃣1️⃣ CONFIGURAR BACKEND (10 min)

### Execute no VPS:

**Bloco 1 - Ir para pasta:**
```
cd /var/www/zurix/backend
```

**Bloco 2 - Criar arquivo .env:**
```
cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=zurix_db
CORS_ORIGINS=https://SEUDOMINIO.com
EOF
```
⚠️ **Substitua SEUDOMINIO.com pelo seu domínio real!**

**Bloco 3 - Instalar dependências:**
```
pip3 install -r requirements.txt
```

**Bloco 4 - Popular banco de dados:**
```
python3 seed_database.py
python3 seed_protocols.py
```

**Bloco 5 - Iniciar backend:**
```
pm2 start "uvicorn server:app --host 0.0.0.0 --port 8001" --name zurix-backend
pm2 save
pm2 startup
```

**☐ Backend Configurado**

---

## 1️⃣2️⃣ CONFIGURAR FRONTEND (10 min)

### Execute no VPS:

**Bloco 1 - Ir para pasta:**
```
cd /var/www/zurix/frontend
```

**Bloco 2 - Criar .env:**
```
echo "REACT_APP_BACKEND_URL=https://SEUDOMINIO.com" > .env
```
⚠️ **Substitua SEUDOMINIO.com pelo seu domínio real!**

**Bloco 3 - Instalar e buildar:**
```
yarn install
yarn build
```

**☐ Frontend Configurado**

---

# FASE 4: NGINX + SSL (20-30 min)

## 1️⃣3️⃣ CONFIGURAR NGINX (10 min)

### Execute no VPS (SUBSTITUA SEUDOMINIO.com):

```
cat > /etc/nginx/sites-available/zurix << 'EOF'
server {
    listen 80;
    server_name SEUDOMINIO.com www.SEUDOMINIO.com;
    
    location / {
        root /var/www/zurix/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

**Ativar site:**
```
ln -sf /etc/nginx/sites-available/zurix /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

**☐ Nginx Configurado**

---

## 1️⃣4️⃣ CONFIGURAR DNS (5 min)

### No site da Njalla:

| Passo | Ação |
|-------|------|
| 1 | Dashboard → Domains → Seu domínio |
| 2 | Clique em **DNS Settings** |
| 3 | Adicione os registros abaixo |

### Registro 1:
- **Tipo:** A
- **Nome:** @
- **Valor:** SEU_IP_DO_VPS

### Registro 2:
- **Tipo:** A
- **Nome:** www
- **Valor:** SEU_IP_DO_VPS

⏳ **Aguarde 5-15 minutos para propagar**

**☐ DNS Configurado**

---

## 1️⃣5️⃣ INSTALAR SSL/HTTPS (10 min)

### Execute no VPS:

**Bloco 1 - Instalar Certbot:**
```
apt install -y certbot python3-certbot-nginx
```

**Bloco 2 - Obter certificado:**
```
certbot --nginx -d SEUDOMINIO.com -d www.SEUDOMINIO.com
```
⚠️ **Substitua SEUDOMINIO.com pelo seu domínio real!**

- Quando pedir email, use o ProtonMail
- Escolha opção **2** (redirect para HTTPS)

**Bloco 3 - Reiniciar:**
```
systemctl restart nginx
pm2 restart all
```

**☐ SSL Instalado**

---

# FASE 5: TESTAR (10 min)

## 1️⃣6️⃣ TESTAR TUDO

### Teste 1 - Backend (no VPS):
```
curl https://SEUDOMINIO.com/api/
```

**Resultado esperado:**
```
{"message": "Zurix Science API", "version": "1.0.0"}
```

### Teste 2 - Frontend:
Abra no navegador: **https://SEUDOMINIO.com**

**☐ Site Funcionando**

---

# ✅ CHECKLIST FINAL

```
☐ VPN ligada durante todo processo
☐ VPS comprado com crypto
☐ Domínio comprado com crypto  
☐ DNS apontando para VPS
☐ Backend rodando (pm2 status)
☐ Frontend buildado
☐ Nginx configurado
☐ SSL instalado (HTTPS funciona)
☐ Site acessível
☐ Firewall ativo
```

---

# 🆘 COMANDOS DE EMERGÊNCIA

### Ver status dos serviços:
```
pm2 status
systemctl status nginx
systemctl status mongodb
```

### Ver logs de erro:
```
pm2 logs zurix-backend
tail -f /var/log/nginx/error.log
```

### Reiniciar tudo:
```
pm2 restart all
systemctl restart nginx
systemctl restart mongodb
```

---

# 📝 MINHAS ANOTAÇÕES

| Item | Valor |
|------|-------|
| **VPN Account** | |
| **Email ProtonMail** | |
| **Senha Email** | |
| **Conta Njalla** | |
| **Senha Njalla** | |
| **IP do VPS** | |
| **Senha Root VPS** | |
| **Meu Domínio** | |
| **Data de Renovação VPS** | |
| **Data de Renovação Domínio** | |

---

**Documento gerado em:** ___/___/______

**Zurix Science - Deployment Anônimo**
