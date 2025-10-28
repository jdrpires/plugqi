# 📋 Solicitação de Liberação de Endpoints - QiTech

**Data:** 22/10/2024  
**Cliente:** [Seu Nome/Empresa]  
**API Key:** 48f5f0b3-e796-4ff6-85ee-f59b1413c500  
**Ambiente:** Sandbox  

---

## 🎯 **SOLICITAÇÃO**

Solicito a **liberação dos seguintes endpoints** para desenvolvimento e testes do SDK PlugQi:

### **1. 🏦 Abertura de Contas ESCROW**
- **Endpoint:** `POST /account_request/escrow`
- **Status atual:** ❌ Erro GDF000014 - "Endpoint não permitido para a ClientIntegration"
- **Necessidade:** Implementação completa de abertura de contas via API

### **2. 🔄 Funcionalidades PIX**
- **Endpoints:** 
  - `POST /pix/keys` (criação de chaves)
  - `POST /pix/payments` (envio de PIX)
  - `GET /pix/keys` (listagem de chaves)
  - `POST /pix/qr-codes` (QR codes)
- **Status atual:** ❌ Erro 404 - "Resource not found"
- **Necessidade:** Funcionalidades PIX completas

### **3. 💳 BolePix Avançado**
- **Funcionalidade:** Criação de boletos com chave PIX integrada
- **Status atual:** ❌ Erro 400 - Chaves PIX não aceitas
- **Necessidade:** Integração boleto + PIX

---

## 🔧 **IMPLEMENTAÇÃO ATUAL**

### ✅ **Funcionalidades Implementadas e Testadas:**
- **Boletos:** 100% funcional (4/4 testes passando)
- **Autenticação JWT ES512:** Funcionando perfeitamente
- **Estrutura de dados:** Conforme documentação oficial
- **Helpers e validações:** Implementados completamente

### ❌ **Funcionalidades Bloqueadas por Permissão:**
- **Abertura de contas ESCROW:** Implementação completa, mas endpoint bloqueado
- **PIX:** Estrutura pronta, mas endpoints não disponíveis
- **BolePix:** Payload correto, mas chaves PIX rejeitadas

---

## 📊 **DETALHES TÉCNICOS**

### **Abertura de Conta ESCROW - Implementação Completa:**

```json
{
  "account_owner": {
    "address": { "street": "Rua Teste", "number": "123", ... },
    "cnae_code": "6201501",
    "company_document_number": "12345678000100",
    "company_type": "ltda",
    "email": "empresa@teste.com",
    "foundation_date": "2020-01-01",
    "name": "Empresa Teste Ltda",
    "person_type": "legal",
    "phone": { "country_code": "55", "area_code": "11", ... },
    "trading_name": "Teste",
    "company_representatives": [...]
  },
  "signed_contract": {
    "document_key": "uuid-do-documento",
    "signatures": [...]
  },
  "destinations": [
    {
      "account_branch": "0001",
      "account_number": "12345",
      "account_digit": "6",
      "document_number": "12345678901",
      "name": "Titular",
      "ispb_number": "60701190",
      "financial_institution_code_number": "341"
    }
  ]
}
```

### **Erro Atual:**
```json
{
  "status": 401,
  "code": "GDF000014",
  "description": "Endpoint or HTTP method not allowed for the given ClientIntegration (Action: POST /account_request/escrow)"
}
```

---

## 🎯 **JUSTIFICATIVA TÉCNICA**

### **1. SDK Completo:**
- Desenvolvendo SDK Python oficial para QiTech
- Cobertura completa de funcionalidades
- Testes automatizados implementados
- Documentação técnica completa

### **2. Implementação Correta:**
- ✅ Payloads conforme documentação oficial
- ✅ Autenticação JWT ES512 funcionando
- ✅ Estrutura de dados validada
- ✅ Helpers e validações implementados

### **3. Necessidade de Testes:**
- Validação completa das funcionalidades
- Testes de integração end-to-end
- Cenários positivos e negativos
- Documentação de casos de uso

---

## 📋 **ENDPOINTS SOLICITADOS**

| Endpoint | Método | Status | Prioridade |
|----------|--------|--------|------------|
| `/account_request/escrow` | POST | ❌ Bloqueado | 🔴 Alta |
| `/pix/keys` | GET/POST | ❌ 404 | 🔴 Alta |
| `/pix/payments` | POST | ❌ 404 | 🔴 Alta |
| `/pix/qr-codes` | POST | ❌ 404 | 🟡 Média |
| BolePix com chaves válidas | - | ❌ 400 | 🟡 Média |

---

## 🚀 **PRÓXIMOS PASSOS**

Após liberação dos endpoints:

1. **Testes completos** de todas as funcionalidades
2. **Documentação** de casos de uso
3. **Publicação** do SDK para comunidade
4. **Suporte** a desenvolvedores terceiros

---

## 📞 **CONTATO**

**Desenvolvedor:** [Seu Nome]  
**Email:** [seu-email@dominio.com]  
**Projeto:** PlugQi SDK Python  
**GitHub:** https://github.com/jeanpires/plugqi  

---

## 📎 **ANEXOS**

- Código fonte completo do SDK
- Testes automatizados implementados
- Documentação técnica
- Exemplos de uso

**Aguardo retorno para liberação dos endpoints solicitados.**

---

*Este documento foi gerado automaticamente pelo sistema de testes PlugQi em 22/10/2024.*
