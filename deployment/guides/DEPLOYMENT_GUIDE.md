# 🔐 GUIA COMPLETO - DEPLOYMENT ANÔNIMO
## Nexgen Sciences Research

---

## 📋 FASE 1: PREPARAÇÃO (Antes de começar)

### 1. Comprar VPS Anônimo

**Recomendações por prioridade:**

**🥇 NJALLA (Melhor para anonimato)**
- Site: https://njal.la
- Preço: ~$15/mês
- Aceita: Bitcoin, Monero, PayPal
- Localização: Suécia
- KYC: NÃO requer
- **Setup:** Domínio + VPS juntos
- ✅ WHOIS proxy incluído (você não aparece)

**🥈 1984 HOSTING**
- Site: https://1984.hosting
- Preço: ~$10/mês
- Aceita: Bitcoin
- Localização: Islândia
- KYC: NÃO requer
- Forte privacidade

**🥉 FLOKINET**
- Site: https://flokinet.is
- Preço: ~$12/mês
- Aceita: Bitcoin, Litecoin
- Localização: Islândia/Romênia
- KYC: NÃO requer
- Offshore hosting

**Especificações mínimas VPS:**
```
- CPU: 2 cores
- RAM: 4GB
- Storage: 40GB SSD
- Bandwidth: 2TB/mês
- OS: Ubuntu 22.04 LTS
```

---

### 2. Comprar Domínio Anônimo

**Opções:**

**A) Via Njalla (Recomendado)**
- Proxy de domínio (você não aparece no WHOIS)
- Aceita crypto
- $15/ano

**B) Via Namecheap**
- WHOIS privacy incluído
- Aceita Bitcoin
- ~$10/ano
- Extensões: .com, .net, .to

**C) Via Porkbun**
- Privacy incluído
- Aceita crypto
- Barato (~$8/ano)

**Extensões recomendadas:**
- `.com` - Mais profissional
- `.to` - Tonga, popular para privacidade
- `.is` - Islândia
- `.ch` - Suíça

---

### 3. Ferramentas Necessárias

**No seu computador:**
```bash
# Linux/Mac
- Terminal (já tem)
- SSH client (já tem)

# Windows
- PuTTY (SSH client)
- WinSCP (transferir arquivos)
```

**VPN/Tor:**
- ProtonVPN (grátis/pago)
- Mullvad VPN (aceita crypto)
- Tor Browser

---

## 🚀 FASE 2: DEPLOYMENT

### Passo 1: Conectar ao VPS

```bash
# Sempre via VPN/Tor primeiro!

# Conectar via SSH
ssh root@SEU_VPS_IP

# Trocar senha root imediatamente
passwd
```

---

### Passo 2: Preparar VPS

```bash
# 1. Baixar script de deploy
wget https://SEU_LINK/deploy.sh
# OU copiar manualmente o arquivo deploy.sh

chmod +x deploy.sh

# 2. Editar configurações
nano deploy.sh

# Alterar estas linhas:
# DOMAIN="seu-dominio.com"     ← SEU DOMÍNIO AQUI
# BACKEND_PORT=8001
# FRONTEND_PORT=3000

# 3. Executar script
./deploy.sh
```

---

### Passo 3: Copiar Arquivos do Site

**Do seu computador (Emergent):**

```bash
# 1. Fazer download dos arquivos
# No Emergent, salvar projeto localmente

# 2. Copiar para VPS via SCP
scp -r /path/to/app/backend root@SEU_VPS_IP:/var/www/nexgen/
scp -r /path/to/app/frontend root@SEU_VPS_IP:/var/www/nexgen/

# OU via SFTP (mais fácil no Windows)
# Usar WinSCP ou FileZilla
```

---

### Passo 4: Configurar DNS

**No seu registrador de domínio:**

```
Tipo: A
Nome: @
Valor: SEU_VPS_IP
TTL: 300

Tipo: A  
Nome: www
Valor: SEU_VPS_IP
TTL: 300
```

**Aguardar 5-30 minutos para propagar**

---

### Passo 5: Instalar SSL (HTTPS)

```bash
# No VPS
certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Seguir instruções
# Escolher opção 2 (redirect HTTP para HTTPS)

# Reiniciar serviços
systemctl restart nginx
pm2 restart all
```

---

### Passo 6: Testar

```bash
# Testar backend
curl https://seu-dominio.com/api/

# Testar frontend
# Abrir no navegador: https://seu-dominio.com

# Verificar logs
pm2 logs nexgen-backend
tail -f /var/log/nginx/nexgen_error.log
```

---

## 🔐 FASE 3: SEGURANÇA E ANONIMATO

### 1. Cloudflare (OPCIONAL mas recomendado)

**Vantagens:**
- Esconde IP real do servidor
- DDoS protection
- SSL grátis
- Cache (site mais rápido)

**Setup:**
1. Criar conta Cloudflare (email anônimo)
2. Adicionar domínio
3. Mudar nameservers no registrador
4. Ativar "Proxy" (nuvem laranja)
5. SSL/TLS: Full (strict)

---

### 2. Configurar Fail2Ban

```bash
# Proteção contra brute force SSH
apt install fail2ban

cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
```

---

### 3. Desabilitar Logs Sensíveis

```bash
# Nginx - logs mínimos
# Editar /etc/nginx/sites-available/nexgen

# Substituir:
access_log /var/log/nginx/nexgen_access.log;
# Por:
access_log off;
# OU logs anônimos:
log_format anonymous '$remote_addr anonymized $request';
access_log /var/log/nginx/access.log anonymous;
```

---

### 4. Configurar Backups Automáticos

```bash
# Criar script de backup
cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --out $BACKUP_DIR/mongo_$DATE

# Backup arquivos
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/nexgen

# Manter apenas últimos 7 dias
find $BACKUP_DIR -mtime +7 -delete
EOF

chmod +x /root/backup.sh

# Agendar diariamente (cron)
crontab -e
# Adicionar: 0 3 * * * /root/backup.sh
```

---

## 📊 FASE 4: MONITORAMENTO

### Comandos Úteis

```bash
# Status dos serviços
pm2 status
systemctl status nginx
systemctl status mongodb

# Ver logs
pm2 logs nexgen-backend
tail -f /var/log/nginx/nexgen_error.log

# Uso de recursos
htop
df -h  # disco
free -m  # RAM

# Reiniciar serviços
pm2 restart all
systemctl restart nginx
systemctl restart mongodb
```

---

## 🆘 TROUBLESHOOTING

### Site não carrega:

```bash
# 1. Verificar Nginx
nginx -t
systemctl status nginx

# 2. Verificar backend
pm2 status
pm2 logs nexgen-backend

# 3. Verificar DNS
ping seu-dominio.com
nslookup seu-dominio.com

# 4. Verificar firewall
ufw status
```

### Erro 502 Bad Gateway:

```bash
# Backend não está rodando
pm2 restart nexgen-backend
pm2 logs
```

### SSL não funciona:

```bash
# Reinstalar certificado
certbot delete
certbot --nginx -d seu-dominio.com
systemctl restart nginx
```

---

## 💰 CUSTOS ESTIMADOS

**Mensal:**
- VPS: $10-15
- Domínio: $1-2 (anual/12)
- VPN: $0-10 (opcional)
- **Total: ~$15-30/mês**

**Anual:**
- VPS: $120-180
- Domínio: $10-20
- VPN: $0-120
- **Total: ~$150-350/ano**

---

## ✅ CHECKLIST FINAL

### Antes de ir ao ar:
```
☐ VPS comprado e acessível
☐ Domínio registrado com privacy
☐ DNS apontando para VPS
☐ Script de deploy executado
☐ Arquivos copiados
☐ SSL instalado (HTTPS)
☐ Site acessível
☐ Backend funcionando
☐ Produtos visíveis
☐ Verificação funcionando
☐ Firewall configurado
☐ Fail2ban instalado
☐ Backups configurados
☐ Cloudflare configurado (opcional)
☐ Testado via VPN/Tor
☐ WhatsApp dos representantes atualizados
```

---

## 📞 SUPORTE

Se precisar de ajuda:
1. Documentar o erro
2. Ver logs: `pm2 logs` e `/var/log/nginx/`
3. Me chamar com detalhes
4. Posso ajudar a debugar!

---

**Boa sorte com o deployment! 🚀🔐**
