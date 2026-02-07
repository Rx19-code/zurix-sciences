# Zurix Science - PRD

## Visão Geral
Site e-commerce para venda de peptídeos para pesquisa científica com sistema de verificação de autenticidade.

## Requisitos Funcionais

### Website (React + FastAPI)
- [x] Catálogo de 49 produtos com preços e informações
- [x] Calculadora de dosagem (mg, doses, ml)
- [x] Sistema de verificação de produtos (código único - prefixo ZX-)
- [x] Carrinho de compras
- [x] Checkout via WhatsApp (3 representantes regionais)
- [x] Banner regulatório dismissível
- [x] Background científico no hero
- [x] Logo genérica "Z" (temporária)
- [x] **Nome atualizado para "Zurix Science"**

### App Mobile (React Native/Expo)
- [x] Estrutura inicial criada
- [x] Navegação básica
- [ ] Tela de Protocolos
- [ ] Tela de Histórico de Verificações
- [ ] Sistema de pagamento crypto

### Deployment Anônimo
- [x] Script de deployment (`deploy.sh`)
- [x] Script de preparação (`prepare_files.sh`)
- [x] Script de verificação de segurança (`security_check.sh`)
- [x] **Guia completo de deployment anônimo** (`DEPLOYMENT_GUIDE.md`)
  - VPN e Tor setup
  - Email anônimo
  - Carteira crypto
  - Compra de VPS com Bitcoin
  - Configuração de servidor
  - SSL/HTTPS
  - Hardening de segurança
  - Checklist OPSEC

## Arquitetura

```
/app/
├── backend/           # FastAPI + MongoDB
├── frontend/          # React + Tailwind
├── mobile/            # React Native (Expo)
└── deployment/        # Scripts e guias
    ├── guides/
    │   └── DEPLOYMENT_GUIDE.md
    ├── scripts/
    │   ├── deploy.sh
    │   ├── prepare_files.sh
    │   └── security_check.sh
    └── README.md
```

## Próximas Tarefas

### P0 - Urgente
- [ ] Completar app mobile (telas restantes)

### P1 - Importante
- [ ] Sistema de pagamento crypto no app
- [ ] Backend para histórico de verificações
- [ ] Logo personalizada (aguardando arquivo)

### P2 - Backlog
- [ ] Autenticação de usuário no app
- [ ] Dashboard administrativo
- [ ] Analytics anônimos

## Status
- **Website:** ✅ Completo (Zurix Science)
- **Deployment Guide:** ✅ Completo
- **App Mobile:** 🔄 Em progresso (estrutura pronta)

## Última Atualização
Dezembro 2024 - Nome alterado para "Zurix Science"
