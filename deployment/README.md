# 📦 Nexgen Sciences - Deployment Package

Este pacote contém tudo necessário para fazer o deployment anônimo do site Nexgen Sciences.

## 📁 Estrutura

```
deployment/
├── guides/
│   └── DEPLOYMENT_GUIDE.md    # Guia completo passo a passo
├── scripts/
│   ├── deploy.sh              # Script principal de deployment
│   ├── prepare_files.sh       # Prepara arquivos para transferência
│   └── security_check.sh      # Verifica segurança do servidor
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Leia o Guia Completo
```bash
# Abra e leia cuidadosamente:
guides/DEPLOYMENT_GUIDE.md
```

### 2. Prepare os Arquivos (Na máquina local)
```bash
chmod +x scripts/prepare_files.sh
./scripts/prepare_files.sh
```

### 3. Execute o Deployment (No VPS)
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Verifique a Segurança (No VPS)
```bash
chmod +x security_check.sh
./security_check.sh
```

## ⚠️ Ordem de Execução

1. ✅ Ler `DEPLOYMENT_GUIDE.md` completamente
2. ✅ Configurar VPN
3. ✅ Comprar VPS com crypto
4. ✅ Comprar domínio com crypto
5. ✅ Executar `prepare_files.sh` localmente
6. ✅ Copiar arquivos para VPS via SCP
7. ✅ Executar `deploy.sh` no VPS
8. ✅ Configurar DNS
9. ✅ Instalar SSL com Certbot
10. ✅ Executar `security_check.sh`
11. ✅ Testar site

## 📞 Suporte

Se tiver problemas durante o deployment, documente:
- Mensagens de erro
- Logs (`pm2 logs`, `/var/log/nginx/`)
- Passo onde falhou

---

**🔐 Mantenha-se seguro!**
