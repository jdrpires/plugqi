# Integração: Abertura de Conta Escrow (com Risk Solution)

## Visão geral
Este documento descreve o fluxo de integração para abertura de contas Escrow, considerando que os dados passam pelo serviço de Risk Solution antes da reserva/abertura final na plataforma QiTech/PlugQi.

Fluxo resumido:
1. Enviar dados ao Risk Solution (Natural ou Legal).
2. Aguardar análise (automatic_approval / manual_analysis / automatic_rejection).
3. Se aprovado/pendente, criar reserva de conta Escrow (POST /account_request/escrow).
4. Aguardar webhook de atualização de status (ex.: `pending_additional_data`, `pending_bacen_validation`).
5. Enviar confirmação (PATCH /account_request/{account_request_key}/escrow) com dados completos.

Criar reserva - Método: POST /account_request/escrow - Objetivo: iniciar solicitação; retorno contém account_request_key e account_request_status.

Exemplo (request PF)

```
{
 "account_owner": {
   "document_number": "99999999999",
   "email": "teste@gmail.com",
   "birthdate": "1990-05-06",
   "name": "Nome do Titular da Conta",
   "documents": { "cnh": { "ocr_key": "<uuid>" } },
   "face": "<uuid>"
 }
}
```

Exemplo (resposta)

```
{
 "account_info": { "account_branch": "0001", "account_digit": "2", "account_number": "2797627" },
 "account_request_key": "fee89de6-e62e-4e88-b77d-457ebb439555",
 "account_request_status": "pending_bacen_validation"
}
```

Consultar status - Método: GET /account_request/{account_request_key} - Uso: verificar current status antes de tentar confirmar.

Confirmar abertura - Método: PATCH /account_request/{account_request_key}/escrow - Objetivo: enviar dados completos para concluir a abertura.

Exemplo (PATCH resumo)

```
{
 "account_owner": {
   "address": { "street": "Av. Brigadeiro Faria Lima", "number": "2391", "city": "São Paulo", "state": "SP", "postal_code": "01452905" },
   "birth_date": "1990-05-06",
   "individual_document_number": "99999999999",
   "email": "teste@gmail.com",
   "name": "Nome do Titular da Conta",
   "phone": { "country_code": "055", "area_code": "11", "number": "999999999" },
   "proof_of_residence": "<uuid>"
 },
 "signed_contract": { "document_key": "<uuid>", "signatures": [ /* ... */ ] },
 "destinations": [ /* ... */ ],
 "additional_documents": [ "<uuid>" ]
}
```

Webhook (exemplo mínimo) - Tipo: account_request.status_change

```
{
 "key": "fee89de6-e62e-4e88-b77d-457ebb439555",
 "data": { "account_info": { "account_digit": "7", "account_branch": "0001", "account_number": "6694401" }, "account_request_key": "fee89de6-e62e-4e88-b77d-457ebb439555" },
 "status": "pending_additional_data",
 "webhook_type": "account_request.status_change",
 "event_datetime": "2025-01-01T12:00:00"
}
```

Risk Solution (resumo)

POST /natural_person?analyze=true (PF) — Envia CPF formatado `###.###.###-##`. Retorno: id, status (automatic_approval/manual_analysis/automatic_rejection) e score.

Exemplo (request PF)

```
{
 "document_number": "123.456.789-10",
 "name": "Fulano da Silva",
 "birth_date": "1990-05-06",
 "email": "fulano@example.com"
}
```

Exemplo (resposta resumo)

```
{
 "id": "rs_abc123",
 "status": "automatic_approval",
 "score": 85
}
```

Erros importantes: `ACR000042` — conta não pronta para confirmação (aguardar webhook `pending_additional_data`).

Fim.
``` 
    "email": "fulano@example.com"
  }'
```

PJ (Legal Person):

```bash
curl -X POST "https://api.sandbox.caas.qitech.app/onboarding/legal_person?analyze=true" \
  -H "Authorization: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_number": "12.345.678/0001-90",
    "name": "Empresa Exemplo LTDA",
    "foundation_date": "2010-01-01",
    "email": "contato@empresa.com"
  }'
```

### Exemplos CURL — PlugQi Escrow

Criar reserva (POST):

```bash
curl -X POST "https://{plugqi-host}/account_request/escrow" \
  -H "Content-Type: application/json" \
  -d '{
    "account_owner": { "document_number": "99999999999", "email": "teste@gmail.com", "birthdate": "1990-05-06", "name": "Nome do Titular da Conta" }
  }'
```

Consultar status (GET):

```bash
curl -X GET "https://{plugqi-host}/account_request/{account_request_key}" \
  -H "Content-Type: application/json"
```

Confirmar abertura (PATCH):

```bash
curl -X PATCH "https://{plugqi-host}/account_request/{account_request_key}/escrow" \
  -H "Content-Type: application/json" \
  -d '{ /* payload de confirmação completo */ }'
```

### Respostas de erro comuns

Exemplo — conta não pronta (ACR000042):

```json
{
  "error": "Account not ready",
  "code": "ACR000042",
  "message": "Account request still in status pending_additional_data"
}
```

Exemplo — rejeição automática no Risk Solution:

```json
{
  "id": "rs_abc123",
  "status": "automatic_rejection",
  "score": 12,
  "details": { "reason": "high_risk_document" }
}
```

### Verificação de assinatura HMAC (exemplo Python)

O repositório contém a função `compute_webhook_signature(endpoint, method, payload, signature_key)` em `risk_solution.py`.

Exemplo de verificação para uso no listener:

```python
import hmac
import hashlib

def verify_webhook(endpoint: str, method: str, payload_str: str, header_signature: str, signature_key: str) -> bool:
    message = (endpoint + method + payload_str).encode('utf-8')
    expected = hmac.new(signature_key.encode('utf-8'), message, hashlib.sha1).hexdigest()
    return hmac.compare_digest(expected, header_signature)

# uso:
# verify_webhook('/webhook/escrow', 'POST', received_body_string, header_signature_value, 'your_signature_key')
```

---

Se quiser que eu gere o PDF automaticamente, autorize instalar dependências (`markdown`, `weasyprint` ou `pandoc`) ou me diga qual ferramenta prefere.

