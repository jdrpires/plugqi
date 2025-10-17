# 🧪 Guia de Testes QA - Boletos PlugQi

## 📋 Cenários de Teste Gerados

### 1. **Pessoa Física Básico**
- **Valor:** R$ 150,75
- **Pagador:** João Silva Santos (CPF)
- **Vencimento:** 30 dias
- **Características:** Boleto simples, sem multa/juros

### 2. **Pessoa Jurídica c/ Multa/Juros**
- **Valor:** R$ 2.500,00
- **Pagador:** Empresa XYZ Tecnologia Ltda (CNPJ)
- **Vencimento:** 45 dias
- **Características:** Multa 2% + Juros 1% a.m.

### 3. **Com Desconto**
- **Valor:** R$ 1.000,00
- **Pagador:** Maria Oliveira Costa (CPF)
- **Vencimento:** 60 dias
- **Características:** Desconto 5% se pago em 15 dias

### 4. **Valor Alto**
- **Valor:** R$ 50.000,00
- **Pagador:** Indústria ABC S.A. (CNPJ)
- **Vencimento:** 90 dias
- **Características:** Protesto em 10 dias

### 5. **Vencimento Curto**
- **Valor:** R$ 89,90
- **Pagador:** Carlos Eduardo Lima (CPF)
- **Vencimento:** 7 dias
- **Características:** Urgente

### 6. **Cartão de Crédito**
- **Valor:** R$ 0,00
- **Pagador:** Ana Paula Ferreira (CPF)
- **Vencimento:** 30 dias
- **Características:** Pagamento parcial permitido

## 🔧 Como Testar

### Endpoints para Testar:

```bash
# Criar boleto padrão (assíncrono)
POST /account/{account_key}/requester_profile/{profile_key}/bank_slip

# Criar boleto instantâneo (síncrono)
POST /account/{account_key}/requester_profile/{profile_key}/bank_slip/instant

# Consultar boleto
GET /account/{account_key}/bank_slip/{bank_slip_key}

# Listar boletos
GET /account/{account_key}/bank_slip
```

### Usando os Payloads:

1. **Carregue o arquivo:** `boletos_teste_qa.json`
2. **Substitua as chaves:**
   - `{account_key}` → sua chave de conta
   - `{profile_key}` → sua chave de carteira
3. **Envie o payload** no body da requisição

### Exemplo de Uso:

```python
import json

# Carrega os boletos de teste
with open('boletos_teste_qa.json', 'r') as f:
    boletos = json.load(f)

# Pega o boleto de pessoa física
boleto_pf = boletos["Pessoa Física Básico"]

# Envia para API
# POST /account/SUA_ACCOUNT_KEY/requester_profile/SUA_PROFILE_KEY/bank_slip
# Body: boleto_pf
```

## ✅ Casos de Teste Sugeridos

### Testes Funcionais:
- [ ] Criar boleto pessoa física
- [ ] Criar boleto pessoa jurídica
- [ ] Boleto com multa e juros
- [ ] Boleto com desconto
- [ ] Boleto de valor alto
- [ ] Boleto cartão de crédito
- [ ] Consultar boleto criado
- [ ] Listar boletos da conta

### Testes de Validação:
- [ ] CPF/CNPJ inválidos
- [ ] Valor negativo
- [ ] Data de vencimento no passado
- [ ] Campos obrigatórios ausentes
- [ ] Desconto maior que valor
- [ ] Multa/juros inválidos

### Testes de Limite:
- [ ] Valor máximo permitido
- [ ] Vencimento máximo (3650 dias)
- [ ] Múltiplos descontos
- [ ] Caracteres especiais em instruções

### Respostas Esperadas:

**Sucesso (202):**
```json
{
  "request_control_key": "uuid",
  "bank_slip_key": "uuid", 
  "bank_slip_status": "accepted",
  "our_number": 12345,
  "barcode": "44 dígitos",
  "digitable_line": "47 dígitos"
}
```

**Erro (400):**
```json
{
  "status": 400,
  "code": "BKS000001",
  "title": "Bad Request",
  "description": "Descrição do erro"
}
```

## 🚀 Automação

Para automatizar os testes:

```bash
# Gerar novos boletos
python3 generate_test_boletos.py

# Testar funcionalidades
python3 test_boleto.py

# Testar com mock
python3 test_boleto_mock.py
```

## 📊 Métricas de Teste

- **6 cenários** diferentes
- **3 tipos** de pessoa (PF, PJ, Cartão)
- **4 configurações** especiais (multa, juros, desconto, protesto)
- **Cobertura completa** dos campos da API

---
**Arquivo gerado em:** `boletos_teste_qa.json`  
**Última atualização:** 2025-10-17
