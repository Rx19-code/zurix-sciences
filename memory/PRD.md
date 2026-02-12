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

### App Mobile (React Native/Expo)
- [x] Estrutura inicial criada
- [x] Navegacao basica
- [ ] Tela de Protocolos
- [ ] Tela de Historico de Verificacoes
- [ ] Sistema de pagamento crypto

### Deployment Anonimo
- [x] Scripts de deployment
- [x] Guias de seguranca
- [x] VPS configurado em zurixsciences.com (SSL, Nginx, MongoDB, PM2)

## Arquitetura

```
/app/
  backend/           # FastAPI + MongoDB (port 8001)
    server.py        # API routes
    seed_database.py # 49 products + 3 representatives
  frontend/          # React + Tailwind (port 3000)
    src/
      pages/         # Home, Products, ProductDetail, Calculator, Verify, Checkout, CheckoutSuccess, Representatives, Contact
      components/    # Navbar, Footer, CartDrawer, ProductCard, RegulatoryBanner
      context/       # CartContext
  mobile/            # React Native (Expo)
  deployment/        # Scripts e guias
```

## API Endpoints
- GET /api/products (filters: category, product_type, search, featured)
- GET /api/products/{id}
- GET /api/products/code/{verification_code}
- GET /api/categories
- GET /api/product-types
- GET /api/representatives
- POST /api/verify-product
- GET /api/protocols
- POST /api/verify-scan (mobile)
- GET /api/verification-history

## DB Schema
- products: {id, name, category, product_type, purity, dosage, description, price, verification_code, storage_info, batch_number, manufacturing_date, expiry_date, coa_url, featured}
- representatives: {id, country, region, name, whatsapp, flag_emoji}
- protocols: {id, title, description, category, price, duration_weeks, ...}

## Testing Status
- Backend: 100% pass (19/19 tests)
- Frontend: 100% pass (all pages and features)
- Test report: /app/test_reports/iteration_1.json

## Proximas Tarefas

### P0 - Urgente
- [ ] Deploy no VPS via GitHub (usuario quer usar git clone)

### P1 - Importante
- [ ] App mobile (telas restantes)
- [ ] Logo personalizada
- [ ] Sistema de pagamento crypto no app

### P2 - Backlog
- [ ] Autenticacao de usuario no app
- [ ] Dashboard administrativo
- [ ] Analytics anonimos
- [ ] Backend para formulario de contato (atualmente so console.log)

## Ultima Atualizacao
Dezembro 2025 - Site completo e testado (100% pass)
