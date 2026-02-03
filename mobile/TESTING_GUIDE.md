# 📱 GUIA COMPLETO - TESTAR APP NO EXPO GO

## 🚀 MÉTODO 1: Testar Localmente (Recomendado)

### PASSO 1: Instalar Expo Go
- **Android**: Google Play Store → "Expo Go"
- **iOS**: App Store → "Expo Go"

### PASSO 2: Conectar à mesma rede WiFi
⚠️ **IMPORTANTE**: Seu celular e computador devem estar na MESMA rede WiFi!

### PASSO 3: Iniciar o app
```bash
cd /app/mobile
npx expo start
```

### PASSO 4: Abrir no celular
**Opção A - QR Code:**
1. Terminal mostrará um QR Code
2. Abrir Expo Go no celular
3. Clicar em "Scan QR Code"
4. Escanear o QR Code
5. App abrirá automaticamente!

**Opção B - Link direto:**
1. Terminal mostrará: `exp://192.168.x.x:8081`
2. Copiar esse link
3. Abrir Expo Go
4. Colar o link
5. App abrirá!

---

## 🌐 MÉTODO 2: Testar via Tunnel (Redes diferentes)

Se celular e computador estiverem em redes diferentes:

```bash
cd /app/mobile
npx expo start --tunnel
```

Isso criará um link público que funciona de qualquer lugar!

---

## 🔧 CONFIGURAÇÃO DO BACKEND

⚠️ **PROBLEMA**: O app precisa acessar o backend!

### Solução para Android Emulator:
```javascript
// Em /app/mobile/src/constants/config.js
export const API_URL = 'http://10.0.2.2:8001/api';
```

### Solução para Dispositivo Físico:
1. Descobrir seu IP local:
```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

2. Atualizar config.js:
```javascript
export const API_URL = 'http://SEU_IP_LOCAL:8001/api';
// Exemplo: http://192.168.1.100:8001/api
```

3. Garantir que backend aceita conexões externas:
```bash
# Backend já está configurado para aceitar!
# CORS_ORIGINS='*' no .env
```

---

## 📝 COMANDOS ÚTEIS

### Iniciar app:
```bash
cd /app/mobile
npx expo start
```

### Limpar cache:
```bash
cd /app/mobile
npx expo start --clear
```

### Ver logs:
```bash
# Os logs aparecerão no terminal automaticamente
```

### Parar servidor:
```bash
# Pressionar Ctrl+C no terminal
```

---

## 🧪 TESTANDO FUNCIONALIDADES

### 1. Home Screen
✅ Deve mostrar estatísticas
✅ Cards de "Quick Actions"
✅ Banner regulatório

### 2. Scan Screen
✅ Câmera deve abrir
✅ Scanner QR Code
✅ Entrada manual funciona
✅ Teste com código: **CS-ZE101208**

### 3. Protocols (quando criado)
✅ Lista de 10 protocolos
✅ Filtro Basic/Advanced
✅ Preços $4.99 e $9.99

### 4. History (quando criado)
✅ Histórico de scans
✅ Estatísticas

### 5. Profile (quando criado)
✅ Info do dispositivo
✅ Protocolos comprados

---

## ⚠️ PROBLEMAS COMUNS

### "Unable to connect to Metro":
- Verificar se está na mesma WiFi
- Tentar reiniciar: Ctrl+C e npx expo start

### "Network Error" ao verificar produto:
- Verificar IP do backend no config.js
- Testar backend: curl http://SEU_IP:8001/api/

### "Camera permission denied":
- Nas configs do Expo Go, permitir câmera
- Reiniciar o app

### App não abre:
- Limpar cache: npx expo start --clear
- Reinstalar Expo Go
- Verificar versão do Node (usar Node 18+)

---

## 🎯 PRÓXIMOS PASSOS

Depois de testar:
1. ✅ Verificar se scanner funciona
2. ✅ Testar entrada manual de código
3. ✅ Ver resultado da verificação
4. 📝 Criar telas restantes (Protocols, History, Profile)
5. 💳 Adicionar sistema de pagamento cripto

---

## 💡 DICAS

- **Hot Reload**: Ao salvar código, app atualiza automaticamente!
- **Shake phone**: Menu de debug
- **Console logs**: Aparecem no terminal
- **Erros**: Mostrados no app e no terminal

---

Quer que eu crie as 3 telas restantes agora? 😊
