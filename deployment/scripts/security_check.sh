#!/bin/bash
# ============================================
# NEXGEN SCIENCES - VERIFICAÇÃO DE SEGURANÇA
# Script para verificar configuração de segurança
# Executar DEPOIS do deployment
# ============================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     NEXGEN SCIENCES - VERIFICAÇÃO DE SEGURANÇA     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARN++))
}

echo -e "${BLUE}[1/8] Verificando Firewall (UFW)...${NC}"
if ufw status | grep -q "Status: active"; then
    check_pass "UFW está ativo"
    
    if ufw status | grep -q "22/tcp"; then
        check_warn "Porta SSH padrão (22) aberta - considere mudar"
    fi
    
    if ufw status | grep -q "80/tcp\|443/tcp"; then
        check_pass "Portas HTTP/HTTPS configuradas"
    fi
else
    check_fail "UFW não está ativo!"
fi

echo ""
echo -e "${BLUE}[2/8] Verificando Fail2Ban...${NC}"
if systemctl is-active --quiet fail2ban; then
    check_pass "Fail2Ban está ativo"
    
    BANNED=$(fail2ban-client status sshd 2>/dev/null | grep "Currently banned" | awk '{print $NF}')
    if [ ! -z "$BANNED" ] && [ "$BANNED" != "0" ]; then
        echo "   IPs banidos: $BANNED"
    fi
else
    check_fail "Fail2Ban não está instalado/ativo!"
fi

echo ""
echo -e "${BLUE}[3/8] Verificando SSH...${NC}"
SSH_PORT=$(grep "^Port" /etc/ssh/sshd_config 2>/dev/null | awk '{print $2}')
if [ "$SSH_PORT" = "22" ] || [ -z "$SSH_PORT" ]; then
    check_warn "SSH na porta padrão (22) - recomendado mudar"
else
    check_pass "SSH em porta customizada: $SSH_PORT"
fi

if grep -q "PermitRootLogin no\|PermitRootLogin prohibit-password" /etc/ssh/sshd_config 2>/dev/null; then
    check_pass "Login root com senha desabilitado"
else
    check_warn "Login root pode estar habilitado - verificar"
fi

if grep -q "PasswordAuthentication no" /etc/ssh/sshd_config 2>/dev/null; then
    check_pass "Autenticação por senha desabilitada"
else
    check_warn "Autenticação por senha habilitada - usar chaves SSH"
fi

echo ""
echo -e "${BLUE}[4/8] Verificando Nginx...${NC}"
if systemctl is-active --quiet nginx; then
    check_pass "Nginx está rodando"
    
    if nginx -t 2>&1 | grep -q "successful"; then
        check_pass "Configuração Nginx válida"
    else
        check_fail "Configuração Nginx com erros!"
    fi
    
    # Verificar SSL
    if [ -d "/etc/letsencrypt/live" ]; then
        check_pass "Certificado SSL instalado"
    else
        check_warn "SSL não configurado - executar certbot"
    fi
else
    check_fail "Nginx não está rodando!"
fi

echo ""
echo -e "${BLUE}[5/8] Verificando Backend (PM2)...${NC}"
if command -v pm2 &> /dev/null; then
    if pm2 list | grep -q "nexgen-backend"; then
        STATUS=$(pm2 list | grep "nexgen-backend" | awk '{print $10}')
        if [ "$STATUS" = "online" ]; then
            check_pass "Backend rodando via PM2"
        else
            check_fail "Backend não está online: $STATUS"
        fi
    else
        check_fail "Backend não configurado no PM2"
    fi
else
    check_fail "PM2 não instalado!"
fi

echo ""
echo -e "${BLUE}[6/8] Verificando MongoDB...${NC}"
if systemctl is-active --quiet mongod || systemctl is-active --quiet mongodb; then
    check_pass "MongoDB está rodando"
    
    # Verificar se bind apenas localhost
    if grep -q "bindIp: 127.0.0.1\|bind_ip = 127.0.0.1" /etc/mongod.conf 2>/dev/null; then
        check_pass "MongoDB apenas em localhost"
    else
        check_warn "MongoDB pode estar exposto - verificar bindIp"
    fi
else
    check_fail "MongoDB não está rodando!"
fi

echo ""
echo -e "${BLUE}[7/8] Verificando Logs...${NC}"
if [ -f "/var/log/nginx/nexgen_access.log" ]; then
    LOG_SIZE=$(du -k /var/log/nginx/nexgen_access.log 2>/dev/null | cut -f1)
    if [ "$LOG_SIZE" -gt 10240 ]; then
        check_warn "Logs Nginx grandes (${LOG_SIZE}KB) - considere limpar"
    else
        check_pass "Logs Nginx em tamanho normal"
    fi
fi

if grep -q "access_log off" /etc/nginx/sites-available/nexgen 2>/dev/null; then
    check_pass "Logs de acesso Nginx desabilitados (privacidade)"
else
    check_warn "Logs de acesso ativos - considere desabilitar para privacidade"
fi

echo ""
echo -e "${BLUE}[8/8] Verificando Atualizações...${NC}"
UPDATES=$(apt list --upgradable 2>/dev/null | grep -c upgradable || echo "0")
if [ "$UPDATES" -gt 10 ]; then
    check_warn "Existem $UPDATES atualizações pendentes"
else
    check_pass "Sistema relativamente atualizado"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Passou: $PASS${NC}  ${YELLOW}Avisos: $WARN${NC}  ${RED}Falhou: $FAIL${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}⚠️  Existem $FAIL problemas críticos que precisam ser resolvidos!${NC}"
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Existem $WARN avisos que devem ser verificados.${NC}"
    exit 0
else
    echo -e "${GREEN}✅ Todas as verificações passaram!${NC}"
    exit 0
fi
