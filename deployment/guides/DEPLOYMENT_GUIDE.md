# 🔐 GUIA COMPLETO - DEPLOYMENT ANÔNIMO
## Nexgen Sciences Research

**Última atualização:** Dezembro 2024  
**Nível de Anonimato:** Máximo

---

> ⚠️ **AVISO IMPORTANTE:** Este guia é para fins educacionais e proteção de privacidade. Certifique-se de cumprir as leis do seu país.

---

## 🛡️ FASE 0: PREPARAÇÃO DE OPSEC (CRÍTICO)

### 1. Configurar VPN ANTES de Qualquer Coisa

**NÃO faça nenhum passo deste guia sem VPN ativada!**

**VPNs Recomendadas (aceitam crypto):**

| VPN | Preço | Crypto | Logs | Site |
|-----|-------|--------|------|------|
| **Mullvad** | €5/mês | ✅ BTC, XMR | No-logs | mullvad.net |
| **ProtonVPN** | Grátis/Pago | ✅ BTC | No-logs | protonvpn.com |
| **IVPN** | $6/mês | ✅ BTC, XMR | No-logs | ivpn.net |

**Setup Mullvad (Recomendado):**
```bash
# 1. Acesse: mullvad.net (via Tor Browser)
# 2. Clique "Generate account" (não precisa email!)
# 3. Você recebe um número de conta
# 4. Pague com Bitcoin/Monero
# 5. Baixe o app e conecte

# Verificar IP mudou:
curl ifconfig.me
```

---

### 2. Criar Email Anônimo

**Opções:**

**A) ProtonMail (Recomendado)**
```
1. Via Tor Browser: https://proton.me
2. Criar conta (não precisa telefone)
3. Usar VPN durante criação
4. Email: seunome@proton.me
```

**B) Tutanota**
```
1. https://tutanota.com
2. Grátis, sem telefone
3. Forte criptografia
```

**C) Guerrilla Mail (Temporário)**
```
1. https://guerrillamail.com
2. Email descartável
3. Bom para confirmações rápidas
```

---

### 3. Carteira de Crypto Anônima

**Para Bitcoin:**
```bash
# Opção 1: Electrum (Desktop)
# - Baixe: electrum.org
# - Não requer KYC
# - Use via Tor: electrum --proxy socks5:localhost:9050

# Opção 2: Samourai Wallet (Android)
# - Foco em privacidade
# - Suporta CoinJoin
```

**Para Monero (Máximo anonimato):**
```bash
# Monero GUI Wallet
# - Baixe: getmonero.org
# - Completamente anônimo
# - Sem blockchain tracking
```

**Comprar Crypto sem KYC:**
- **Bisq** - Exchange P2P descentralizada
- **LocalMonero** - P2P para Monero
- **Robosats** - Via Lightning Network (Tor)
- **Bitcoin ATMs** - Com dinheiro (sem ID em alguns)

---

### 4. Tor Browser Setup

```bash
# Baixar: https://www.torproject.org
# Use para:
# - Criar contas
# - Pesquisar provedores
# - Pagamentos

# Verificar Tor funcionando:
# Acesse: https://check.torproject.org
```

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

---

## 🔒 APÊNDICE A: ANONIMIZAÇÃO DO MONGODB

### Configurar MongoDB sem Logs Sensíveis

```bash
# Editar configuração MongoDB
nano /etc/mongod.conf

# Adicionar/modificar:
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  # Nível mínimo de log
  verbosity: 0
  
# Desabilitar profiling (queries logging)
operationProfiling:
  mode: off

# Reiniciar
systemctl restart mongod
```

### Limpar Logs Periodicamente

```bash
# Adicionar ao cron (crontab -e):
0 0 * * * echo "" > /var/log/mongodb/mongod.log
0 0 * * * echo "" > /var/log/nginx/nexgen_access.log
```

---

## 🔒 APÊNDICE B: HARDENING DO SERVIDOR

### 1. Mudar Porta SSH (Dificulta Scanners)

```bash
# Editar SSH config
nano /etc/ssh/sshd_config

# Mudar linha:
Port 22
# Para (exemplo):
Port 2222

# Atualizar firewall
ufw allow 2222/tcp
ufw delete allow 22/tcp

# Reiniciar SSH
systemctl restart sshd

# IMPORTANTE: Conectar agora via:
ssh -p 2222 root@SEU_VPS_IP
```

### 2. Desabilitar Login Root com Senha

```bash
# Criar novo usuário
adduser nexgenadmin
usermod -aG sudo nexgenadmin

# Copiar chave SSH para novo usuário
mkdir -p /home/nexgenadmin/.ssh
cp ~/.ssh/authorized_keys /home/nexgenadmin/.ssh/
chown -R nexgenadmin:nexgenadmin /home/nexgenadmin/.ssh

# Desabilitar root password login
nano /etc/ssh/sshd_config
# Mudar para:
PermitRootLogin prohibit-password
PasswordAuthentication no

systemctl restart sshd
```

### 3. Instalar Monitoramento de Intrusão

```bash
# OSSEC (detecção de intrusão)
apt install ossec-hids-server

# Verificar status
/var/ossec/bin/ossec-control status
```

---

## 🔒 APÊNDICE C: PASSO A PASSO - COMPRAR VPS COM CRYPTO

### Exemplo: Njalla com Bitcoin

```
PASSO 1: PREPARAÇÃO
☐ VPN ligada
☐ Tor Browser aberto
☐ Carteira Bitcoin com saldo

PASSO 2: CRIAR CONTA NJALLA
1. Acesse: https://njal.la (via Tor)
2. Clique "Sign Up"
3. Use email ProtonMail
4. Senha forte (gerada)
5. Confirmar email

PASSO 3: COMPRAR VPS
1. Dashboard → "VPS"
2. Escolher plano (~$15/mês)
3. Localização: Suécia
4. OS: Ubuntu 22.04
5. Checkout → Bitcoin
6. Copiar endereço BTC
7. Enviar da sua carteira
8. Aguardar confirmação (~30 min)

PASSO 4: COMPRAR DOMÍNIO
1. Dashboard → "Domains"
2. Buscar domínio desejado
3. Checkout → Bitcoin
4. Aguardar confirmação

PASSO 5: CONFIGURAR DNS
1. Domains → Seu domínio
2. DNS Settings
3. Adicionar registros A (ver Fase 2)

PASSO 6: ACESSAR VPS
1. Dashboard → VPS
2. Copiar IP e senha root
3. ssh root@IP (via VPN!)
```

---

## 🔒 APÊNDICE D: CHECKLIST COMPLETO DE OPSEC

### Antes de Começar:
```
☐ VPN ligada e testada (curl ifconfig.me)
☐ Tor Browser instalado
☐ Email anônimo criado (ProtonMail)
☐ Carteira crypto configurada
☐ Crypto comprada (sem KYC)
☐ Nenhuma conta pessoal logada no navegador
```

### Durante Compras:
```
☐ Sempre via VPN + Tor
☐ Não usar cartão de crédito
☐ Não usar email pessoal
☐ Não usar nome real
☐ Não usar telefone pessoal
```

### Durante Configuração:
```
☐ SSH apenas via VPN
☐ Senhas geradas (não pessoais)
☐ Chaves SSH (não senhas)
☐ Porta SSH alterada
☐ Fail2ban ativo
```

### Após Deployment:
```
☐ Logs minimizados/desabilitados
☐ Cloudflare proxy ativo (esconde IP)
☐ Backups em local separado
☐ Testar acesso via Tor
☐ Não compartilhar IP real do servidor
```

### Manutenção:
```
☐ Acessar VPS apenas via VPN
☐ Renovar domínio/VPS com crypto
☐ Verificar logs periodicamente
☐ Atualizar sistema mensalmente
☐ Manter backups atualizados
```

---

## 🔒 APÊNDICE E: SCRIPT DE LIMPEZA DE LOGS

Criar arquivo `/root/clean_logs.sh`:

```bash
#!/bin/bash
# Script para limpar logs sensíveis

echo "🧹 Limpando logs..."

# Nginx
echo "" > /var/log/nginx/access.log
echo "" > /var/log/nginx/error.log
echo "" > /var/log/nginx/nexgen_access.log 2>/dev/null
echo "" > /var/log/nginx/nexgen_error.log 2>/dev/null

# MongoDB
echo "" > /var/log/mongodb/mongod.log

# Sistema
echo "" > /var/log/auth.log
echo "" > /var/log/syslog
journalctl --rotate
journalctl --vacuum-time=1d

# PM2
pm2 flush

echo "✅ Logs limpos!"
```

```bash
# Tornar executável
chmod +x /root/clean_logs.sh

# Agendar limpeza diária
crontab -e
# Adicionar:
0 4 * * * /root/clean_logs.sh
```

---

## 📚 RECURSOS ADICIONAIS

### Links Úteis:
- **Mullvad VPN:** https://mullvad.net
- **ProtonMail:** https://proton.me
- **Njalla:** https://njal.la
- **Bisq Exchange:** https://bisq.network
- **Tor Project:** https://www.torproject.org

### Ferramentas de Privacidade:
- **Have I Been Pwned:** https://haveibeenpwned.com
- **DNS Leak Test:** https://dnsleaktest.com
- **IP Leak Test:** https://ipleak.net

---

## ⚠️ DISCLAIMER

Este guia é fornecido apenas para fins educacionais sobre privacidade digital. O usuário é responsável por:
- Cumprir todas as leis locais e internacionais
- Usar as informações de forma ética e legal
- Qualquer uso indevido das técnicas descritas

A privacidade é um direito, mas a responsabilidade é sua.

---

**🔐 Mantenha-se seguro e privado!**
