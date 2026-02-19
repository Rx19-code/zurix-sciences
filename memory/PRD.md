# Zurix Sciences - PRD

## Problema Original
Site e-commerce para venda de produtos de pesquisa de peptideos, deploy anonimo, e app mobile companion.

## Requisitos Funcionais

### Website (React + FastAPI + MongoDB)
- [x] Catalogo de 49 produtos com precos e informacoes completas
- [x] 4 categorias: GLP-1 Analogs, Research Peptides, Cognitive Enhancers, Coenzymes
- [x] Busca e filtros avancados (categoria, tipo, ordenacao)
- [x] Calculadora de dosagem (concentracao, ml por dose, total de doses)
- [x] Sistema de verificacao de produtos (codigo unico - prefixo ZX-)
- [x] Carrinho de compras com drawer lateral
- [x] Checkout via WhatsApp (3 representantes regionais: Paraguay, USA, Hong Kong)
- [x] Banner regulatorio dismissivel
- [x] Pagina de contato
- [x] Pagina de representantes com botoes WhatsApp
- [x] Pagina de detalhe do produto com info de lote e armazenamento
- [x] Logo "Z" (temporaria)
- [x] Navbar responsiva com menu mobile

### Sistema de Verificacao Avancado (NOVO - Fev 2026)
- [x] Codigos unicos por unidade de produto (formato: ZX-XXXXXX-XXXX-X-XXXXXX)
- [x] Contador de verificacoes por codigo unico
- [x] Avisos de risco: 1a verificacao (verde), 2a (amarelo/caution), 3+ (vermelho/danger)
- [x] Painel Admin em /admin para importar codigos
- [x] Login admin com senha
- [x] Visualizacao de lotes importados
- [x] Logs de verificacao com timestamps
- [x] Endpoint /api/verify-product para website
- [x] Endpoint /api/verify-scan para app mobile

### App Mobile (React Native/Expo)
- [x] Estrutura com 5 abas (Home, Shop, Verify, Protocols, Profile)
- [x] Tela Home com estatisticas e acoes rapidas
- [x] Tela Shop com produtos, carrinho e checkout via WhatsApp
- [x] Modal de termos e disclaimer legal
- [x] Tela Verify com scanner QR e entrada manual
- [x] Tela Protocols com paywall crypto (BTC, USDT, XMR, SOL)
- [x] Tela Profile com historico de verificacoes
- [ ] Integracao com novo sistema de verificacao (ZX- codes)
- [ ] Teste de conectividade de rede

### Deployment Anonimo
- [x] Scripts de deployment
- [x] Guias de seguranca
- [x] VPS configurado em zurixsciences.com (SSL, Nginx, MongoDB, PM2)

## Arquitetura

```
/app/
  backend/           # FastAPI + MongoDB (port 8001)
    server.py        # API routes (admin, verify, products, protocols)
    seed_database.py # 49 products + 3 representatives
  frontend/          # React + Tailwind (port 3000)
    src/
      pages/         # Home, Products, ProductDetail, Calculator, Verify, Admin, Checkout, CheckoutSuccess, Representatives, Contact
      components/    # Navbar, Footer, CartDrawer, ProductCard, RegulatoryBanner
      context/       # CartContext
  mobile/            # React Native (Expo)
    App.js           # Arquivo monolitico (2000+ linhas) - precisa refatoracao
  deployment/        # Scripts e guias
```

## API Endpoints
- GET /api/products (filters: category, product_type, search, featured)
- GET /api/products/{id}
- GET /api/products/code/{verification_code}
- GET /api/categories
- GET /api/product-types
- GET /api/representatives
- POST /api/verify-product (website - novo sistema com unique codes)
- POST /api/verify-scan (mobile - atualizado para suportar ZX- codes)
- GET /api/protocols
- GET /api/verification-history
- POST /api/admin/login
- POST /api/admin/import-codes
- GET /api/admin/codes
- GET /api/admin/batches
- GET /api/admin/verification-logs
- DELETE /api/admin/batch/{batch_number}

## DB Schema
- products: {id, name, category, product_type, purity, dosage, description, price, verification_code, storage_info, batch_number, manufacturing_date, expiry_date, coa_url, featured}
- representatives: {id, country, region, name, whatsapp, flag_emoji}
- protocols: {id, title, description, category, price, duration_weeks, ...}
- unique_codes: {id, code, batch_number, product_id, product_name, verification_count, first_verified_at, last_verified_at, created_at}
- verification_logs: {id, code, batch_number, product_name, timestamp, verification_number, device_id}

## Credenciais Admin
- URL: /admin
- Password: Rx050217!

## Testing Status
- Backend: 100% pass (verificacao, admin, products)
- Frontend Web: 100% pass (todas as paginas)
- App Mobile: PENDENTE - problemas de conectividade de rede

## Proximas Tarefas

### P0 - Urgente
- [ ] Resolver erro de rede no app mobile (usuario precisa fazer diagnostico)
- [ ] Testar app mobile com novo sistema de verificacao

### P1 - Importante
- [ ] Corrigir link "Visit Website" no app mobile
- [ ] Refatorar mobile/App.js (arquivo monolitico de 2000+ linhas)
- [ ] Logo personalizada

### P2 - Backlog
- [ ] Autenticacao de usuario no app mobile
- [ ] Dashboard administrativo mais completo
- [ ] Analytics anonimos
- [ ] Backend para formulario de contato (atualmente so console.log)

## Problemas Conhecidos no App Mobile
1. **Erro de Rede**: O usuario reportou "Network request failed" ao carregar produtos. Isso pode ser problema de rede local (VPN no PC, WiFi diferente no celular). Usuario precisa testar acessando https://www.zurixsciences.com/api/products diretamente no navegador do celular.
2. **Link Website**: O botao "Visit Website" foi reportado como nao funcionando.
3. **Icones**: Aviso de icone invalido foi reportado mas o codigo parece correto (shield-checkmark).

## Ultima Atualizacao
Fevereiro 2026 - Sistema de verificacao avancado completo e testado
