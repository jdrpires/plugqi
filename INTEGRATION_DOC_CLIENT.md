# Documentação de Integração — Cliente

> Documentação focada na experiência do desenvolvedor externo que consome a API.

## Visão Geral

Esta documentação resume os endpoints usados no teste `test_fluxo_integrado_simples.py` e nos módulos `qitech_client` e `risk_solution`. Ela cobre duas superfícies principais:

- Risk Solution (onboarding): endpoints para envio/consulta de pessoas naturais e jurídicas.
- QiTech API (serviços bancários): endpoints protegidos por JWT (`AUTHORIZATION`) + `API-CLIENT-KEY` para operações de conta, PIX, TED, boletos e consulta de instituições.

Utilize as URLs abaixo como placeholders; substitua `https://api.empresa.com/v1` pelo host fornecido (ex.: sandbox ou produção).

---

## Autenticação

- Risk Solution (onboarding):
  - Header: `Authorization: <API_KEY>` (o client `RiskSolutionClient` envia a chave diretamente no header `Authorization`).
  - Content-Type: `application/json`.

- QiTech API (core):
  - Headers obrigatórios:
    - `AUTHORIZATION: <JWT ES512>` — JWT assinado com chave privada ES512. O JWT contém `payload_md5`, `timestamp`, `method` e `uri`.
    - `API-CLIENT-KEY: <CLIENT_API_KEY>` — chave pública do cliente.
  - Para requests com body JSON: `Content-Type: application/json`.
  - Observação: para gerar o `AUTHORIZATION` corretamente, é necessário calcular o MD5 exato do payload (ou `{}` para GET/DELETE) e assinar o URI relativo (path + query) — o SDK fornece `auth_headers_for()` para facilitar.

---

## Referência de Endpoints (principais)

Notas:
- As URLs abaixo usam o placeholder `https://api.empresa.com/v1` — substitua pelo `base_url` da sua integração.
- Em `Path` indique `:param` para path params.

- **Health Check**
  - Método / URL: `POST https://api.empresa.com/v1/test`
  - Descrição: Verifica conectividade e autenticação do cliente.
  - Parâmetros: body JSON simples `{ "name": "QI Tech" }` (opcional).
  - Example Request:

```bash
curl -X POST "https://api.empresa.com/v1/test" \
  -H "AUTHORIZATION: <JWT>" \
  -H "API-CLIENT-KEY: <API_CLIENT_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"name":"QI Tech"}'
```

  - Responses:
    - 200: `{ "ok": true }` (exemplo)
    - 401: erro de autenticação (token inválido)

- **Consultar Instituições Financeiras**
  - Método / URL: `GET https://api.empresa.com/v1/financial_institution`
  - Descrição: Lista instituições; suporta filtros por `ispb_number`, `name`, `compe_number`, paginação.
  - Query params:

| Nome | Tipo | Obrigatório | Observações |
|------|------|------------:|------------|
| ispb_number | string | não | filtro por ISPB (8 dígitos)
| name | string | não | busca por nome
| compe_number | string | não | código COMPE (ex.: "001")
| page_number | int | não | paginação
| page_size | int | não | paginação

  - Example Request:

```bash
curl -G "https://api.empresa.com/v1/financial_institution" \
  -H "AUTHORIZATION: <JWT>" \
  -H "API-CLIENT-KEY: <API-CLIENT-KEY>" \
  --data-urlencode "compe_number=001"
```

  - Response 200 (sucesso):

```json
{
  "data": [
    {"ispb_number":"00000000","compe_number":"001","name":"Banco Exemplo","is_active":true}
  ],
  "pagination": {"page":1,"page_size":30}
}
```

  - Erros: 401 (autenticação), 400 (parâmetro inválido).

- **PIX — Consultar chave**
  - Método / URL: `GET https://api.empresa.com/v1/pix_key/:pix_key`
  - Descrição: Retorna dados públicos da chave PIX (ex.: `end_to_end_id`) para uso em transferências.
  - Path params: `:pix_key` (string)
  - Exemplo cURL:

```bash
curl -H "AUTHORIZATION: <JWT>" -H "API-CLIENT-KEY: <API_CLIENT_KEY>" \
  "https://api.empresa.com/v1/pix_key/abcd-1234"
```

  - Response 200:

```json
{ "pix_key": "abcd-1234", "end_to_end_id": "E2E-0001", "owner_name": "Fulano" }
```

  - Erros comuns: 404 (chave não encontrada), 401.

- **PIX — Enviar PIX por chave**
  - Método / URL: `POST https://api.empresa.com/v1/account/:account_key/pix_transfer`
  - Descrição: Envia PIX (key/manual/static_qr_code/dynamic_qr_code) a partir de `account_key`.
  - Path params: `:account_key` (UUID)
  - Body (JSON):

| Campo | Tipo | Obrigatório | Observações |
|-------|------|-----------:|------------|
| request_control_key | string | não | UUID v4 para idempotência (o SDK gera se omitido)
| pix_transfer_type | string | sim | `key`/`manual`/`static_qr_code`/`dynamic_qr_code`
| target_pix_key | string | condicional | para `key` / `static_qr_code` / `dynamic_qr_code`
| target_account | object | condicional | para `manual`
| transaction_amount | number | sim | valor em unidades (ex.: 50.0)
| end_to_end_id | string | condicional | recomendado para `key` transfers
| pix_message | string | não | descrição

  - Exemplo request:

```bash
curl -X POST "https://api.empresa.com/v1/account/ACCOUNT_KEY/pix_transfer" \
  -H "AUTHORIZATION: <JWT>" \
  -H "API-CLIENT-KEY: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "pix_transfer_type":"key",
    "target_pix_key":"destino@email.com",
    "transaction_amount":50.0,
    "end_to_end_id":"E2E-123"
  }'
```

  - Response 201/200: resumo da transferência (keys, status)
  - Erros: 400 (payload inválido), 401, 422 (saldo insuficiente / validação bancária).

- **TED — Enviar TED**
  - Método / URL: `POST https://api.empresa.com/v1/account/:account_key/ted`
  - Descrição: Executa uma transferência TED.
  - Body (JSON):

| Campo | Tipo | Obrigatório |
|-------|------|-----------:|
| request_control_key | string | sim |
| target_account | object | sim | objeto com `account_branch`, `account_number`, `account_digit`, `owner_document_number`, `owner_name`, `ispb` |
| transaction_amount | number | sim |
| tfa_info | object | não | para fluxos com 2FA

  - Exemplo:

```bash
curl -X POST "https://api.empresa.com/v1/account/ACCOUNT_KEY/ted" \
  -H "AUTHORIZATION: <JWT>" \
  -H "API-CLIENT-KEY: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "request_control_key":"<uuid>",
    "target_account":{ "account_branch":"0001","account_number":"123456","account_digit":"7","owner_document_number":"12345678901","owner_name":"Teste","ispb":"00000000" },
    "transaction_amount":200.0
  }'
```

  - Response 201: confirmação / chave da TED
  - Erros: 400, 401, 422 (2FA exigido ou saldo insuficiente)

- **Boletos — Criar boleto**
  - Método / URL: `POST https://api.empresa.com/v1/account/:account_key/requester_profile/:requester_profile_key/bank_slip`
  - Descrição: Cria boleto (assíncrono) ou use `/bank_slip/instant` para operação síncrona.
  - Body resumido:

| Campo | Tipo | Obrigatório |
|-------|------|-----------:|
| request_control_key | string | não |
| amount | number | sim |
| expiration | string | sim | formato `YYYY-MM-DD`
| payer_data | object | sim | `name`, `document_number`, `person_type` |

  - Exemplo de request:

```bash
curl -X POST "https://api.empresa.com/v1/account/ACCOUNT_KEY/requester_profile/RP_KEY/bank_slip" \
  -H "AUTHORIZATION: <JWT>" \
  -H "API-CLIENT-KEY: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount":150.0,
    "expiration":"2026-02-07",
    "payer_data":{ "name":"João Silva","document_number":"12345678901","person_type":"natural" }
  }'
```

  - Response 201: chave do boleto, instruções de pagamento

- **Risk Solution — Enviar Pessoa Natural**
  - Método / URL: `POST https://onboarding.empresa.com/v1/natural_person` (placeholder)
  - Descrição: envia dados de pessoa física para análise/onboarding.
  - Headers: `Authorization: <API_KEY>`, `Content-Type: application/json`.
  - Parâmetros de body (principais obrigatórios): `id`, `registration_id`, `registration_date` (ISO8601), `client_category`=`individual`, `name`, `document_number` (CPF formatado `###.###.###-##`), `birthdate` (`YYYY-MM-DD`).

  - Exemplo:

```bash
curl -X POST "https://onboarding.empresa.com/v1/natural_person?analyze=false" \
  -H "Authorization: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"id":"<uuid>","name":"Fulano","document_number":"123.456.789-12","birthdate":"1990-05-20"}'
```

  - Resposta 200: objeto com `id` e status
  - Erros: 400 (CPF mal formatado), 401 (chave inválida)

- **Risk Solution — Enviar Pessoa Jurídica**
  - Método / URL: `POST https://onboarding.empresa.com/v1/legal_person`
  - Observações: `document_number` deve estar no formato CNPJ `##.###.###/####-##`.

---

## Dicas de Integração / Gotchas

- JWT & MD5: para a QiTech API, o `AUTHORIZATION` é um JWT ES512 que inclui o `payload_md5`. Para `GET` e `DELETE`, o cliente usa o MD5 de `b"{}"` — isso é crítico: se você calcular MD5 de `''` ou de um JSON com espaços, o token será inválido.
- URI relativa: a assinatura inclui o path exato e a query ordenada. Use a função `auth_headers_for()` do SDK para gerar headers reproduzíveis em ferramentas como Postman.
- Formatos de documento:
  - CPF esperado pela Risk Solution: `###.###.###-##`.
  - CNPJ esperado: `##.###.###/####-##`.
- Datas: use ISO8601 (`YYYY-MM-DD` ou `YYYY-MM-DDTHH:MM:SSZ`) conforme o exemplo nos testes.
- Idempotência: prefira enviar `request_control_key` (UUID v4) para operações financeiras e lotes.
- Limites: `page_size` costuma ter máximo (ex.: 30 em alguns endpoints). Verifique a paginação quando listar grandes volumes.

---

## Exemplos Rápidos (Resumo)

- Gerar headers (exemplo simplificado):

```bash
# QiTech (exemplo):
curl -H "AUTHORIZATION: eyJhbGciOiJFUzUxMi..." -H "API-CLIENT-KEY: your-client-key" \
  -H "Content-Type: application/json" \
  -d '{"foo":"bar"}' https://api.empresa.com/v1/account/...

# Risk Solution (exemplo):
curl -H "Authorization: EXAMPLE-OF-API-KEY" -H "Content-Type: application/json" \
  -d '{"name":"Fulano","document_number":"123.456.789-12"}' \
  "https://onboarding.empresa.com/v1/natural_person?analyze=false"
```

---

## Onde procurar no SDK

- `qitech_client.QiTechClient` — geração de JWT, `auth_headers_for()`, `_request()` (lógica MD5 / assinatura).
- `connectors/financial_institution.py` — `GET /financial_institution`.
- `connectors/pix.py` — endpoints `GET /pix_key/:pix_key` e `POST /account/:account_key/pix_transfer`.
- `connectors/ted.py` — endpoints para `/account/:account_key/ted`, `/account/:account_key/ted_batch`, e endpoints de aprovação/resend.
- `connectors/boleto.py` — endpoints de boletos e helpers (`/account/:account_key/requester_profile/.../bank_slip`).
- `risk_solution.RiskSolutionClient` — endpoints de onboarding `/natural_person`, `/legal_person`, etc.

---

Se você quiser, eu posso:
- Gerar exemplos de Postman (collection) prontos usando `auth_headers_for()`;
- Adicionar exemplos de resposta de erro extraídos do sandbox real (se você fornecer respostas reais);
- Converter esta documentação em um README mais formal com links para cada método do SDK.

Arquivo gerado a partir da análise de `test_fluxo_integrado_simples.py` e dos módulos do SDK.
