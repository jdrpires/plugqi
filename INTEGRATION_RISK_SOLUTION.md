# Documentação de Integração — Risk Solution (QiTech)
## Endpoint de Recebimento (Webhook)
  - `Content-Type: application/json`
  - `Signature: <hmac-sha1-hex>` — HMAC-SHA1 sobre `(endpoint + method + payload)` usando `QITECH_WEBHOOK_SECRET`.

Comportamento do listener (arquivo `examples/qitech_webhook_db.py`):

*** Begin Technical Integration Guide for Developers ***

Title: Technical Integration Guide — Risk Solution (QiTech)

Purpose
- Provide a concise, developer-focused integration guide so another developer can implement webhook handling, verify signatures, persist events and trigger Escrow account reservation.

Quick Start (what you need)
- Repo files to use: `risk_solution.py`, `examples/qitech_webhook_db.py`, `examples/qitech_webhook_test.py`, `test_fluxo_integrado_simples.py`.
- Env vars (minimum): `DATABASE_URL`, `QITECH_WEBHOOK_SECRET`, `QITECH_API_KEY`, and `URL_APLICACAO` (`https://qi.homolog.plugz.com.br/`).
- Install: `pip install -r requirements.txt`

1) Webhook Receiver — specification
- Endpoint (our public app): `POST https://qi.homolog.plugz.com.br/webhooks/qitech/onboarding`
- Required headers:
  - `Content-Type: application/json`
  - `Signature: <hex-hmac-sha1>`

Signature algorithm (exact)
- Compute HMAC-SHA1 hex over the string: `(path + method + payload)`
- Use the secret from `QITECH_WEBHOOK_SECRET`.
- Example Python (use existing helper):

```python
from risk_solution import RiskSolutionClient
sig = RiskSolutionClient.compute_webhook_signature('/webhooks/qitech/onboarding', 'POST', payload_text, os.environ['QITECH_WEBHOOK_SECRET'])
```

Receiver behavior (implementation notes)
- Persist full payload and headers to `webhook_qitech` for audit (see SQL file `create_webhook_qitech_ptbr.sql`).
- Compare incoming `Signature` header with computed signature using `hmac.compare_digest`.
- If invalid signature: return `403` but keep the persisted record with `assinatura_ok=false` (this helps debugging). If you prefer to drop invalid events, change order.
- If signature valid and `analysis_status` indicates approval (`APPROVED`,`OK`), call `create_escrow_reservation_from_payload(payload)` to request Escrow reservation.

2) Webhook payloads (examples)
- Approved example (minimal):

```json
{
  "registration_id": "reg-12345",
  "analysis_status": "APPROVED",
  "event_date": "2026-01-08T12:34:56Z",
  "reason": "Análise OK",
  "cpf": "12345678901",
  "email": "cliente@example.com",
  "name": "Fulano de Tal"
}
```

- Rejected example:

```json
{
  "registration_id": "reg-12346",
  "analysis_status": "REJECTED",
  "reason": "Documento inválido"
}
```

3) Database — table (exact)
- File: `create_webhook_qitech_ptbr.sql` (in repo). Core columns:
  - `id` UUID PK
  - `id_registro` varchar
  - `tipo_pessoa` varchar
  - `id_pessoa` varchar
  - `status_analise` varchar
  - `data_evento` timestamptz
  - `motivo` text
  - `conteudo` jsonb
  - `cabecalhos` jsonb
  - `assinatura` varchar
  - `assinatura_ok` boolean
  - `recebido_em` timestamptz

4) Escrow reservation (what we POST)
- Function: `create_escrow_reservation_from_payload(payload)` in `examples/qitech_webhook_db.py`.
- For natural person, send to `/account_request/escrow` with body:

```json
{ "account_owner": { "document_number": "<cpf>", "email":"<email>", "name":"<name>", "birthdate":"YYYY-MM-DD" } }
```

- For legal person, send to `/account_request/escrow/legal` with body:

```json
{ "account_owner": { "company_document_number": "<cnpj>", "email":"<email>", "name":"<company_name>" } }
```

5) Testing — local quick commands
- Run listener:

```powershell
python examples/qitech_webhook_db.py
```

- Send signed test webhook:

```powershell
QITECH_WEBHOOK_SECRET=change-me python examples/qitech_webhook_test.py
```

- Check status:

```bash
curl "http://localhost:8000/webhooks/qitech/status?id_registro=reg-12345" | jq .
```

6) Postman
- Use `postman_collection_full_project.json` and `postman_env_full_project.json`. Set `webhook_url`, `webhook_secret`, `base_url`.

7) Integration steps for another developer (concrete)
- 1) Pull repo and create virtualenv, install `pip install -r requirements.txt`.
- 2) Set env vars: `DATABASE_URL`, `QITECH_WEBHOOK_SECRET`, `URL_APLICACAO`.
- 3) Run DB migration: execute `create_webhook_qitech_ptbr.sql` on the target Postgres.
- 4) Run the Flask listener on a reachable URL (or use ngrok when testing locally).
- 5) Verify signature computation using `RiskSolutionClient.compute_webhook_signature` against the test script `examples/qitech_webhook_test.py`.
- 6) Confirm that after an `APPROVED` webhook the Escrow reservation endpoint is called and returns an `account_key`.

8) Acceptance tests (what to verify)
- With valid signature and `analysis_status=APPROVED`:
  - DB `webhook_qitech` has a new record with `assinatura_ok=true` and `status_analise=APPROVED`.
  - Escrow reservation POST is called and returns `account_key`.
- With invalid signature:
  - Endpoint returns `403` and DB has the record with `assinatura_ok=false`.

9) Security & operational notes
- Store `QITECH_WEBHOOK_SECRET` securely (secrets manager). Do not commit to Git.
- Use `hmac.compare_digest` when comparing signatures to avoid timing attacks.
- Log failures with enough detail for debugging but avoid logging full secrets.

Contacts / next steps
- If you want, I can also:
  - generate a PDF of this guide,
  - add Postman pre-request script to compute `Signature` automatically,
  - add unit tests that mock QiTech webhooks and assert DB + Escrow calls.

*** End Technical Integration Guide ***
# Documentação de Integração — Risk Solution (QiTech)

Versão: 1.0

Status: implementação disponível no repositório — o cliente `RiskSolutionClient`, listener de webhooks, endpoint de consulta e scripts de teste foram adicionados.

## Arquivos principais (locais)

- `risk_solution.py` — client para endpoints de Risk Solution.
- `examples/qitech_webhook_db.py` — Flask listener que valida assinatura HMAC-SHA1 e persiste webhooks em `webhook_qitech` (Postgres). Também registra em `logs`.
- `examples/qitech_webhook_test.py` — script que cria payload de teste, calcula assinatura e executa POST/GET local.
- `test_fluxo_integrado_simples.py` — teste integrado que inclui bloco Risk Solution e pode opcionalmente executar o webhook test (set `RUN_WEBHOOK_TEST=true`).
- `postman_collection_full_project.json` — coleção Postman completa para este projeto.
- `postman_env_full_project.json` — ambiente do Postman (variáveis usadas na collection).
- `INTEGRATION_RISK_SOLUTION.md` — este arquivo (markdown editável).

## Sumário rápido

- Fluxo: Envio → RiskSolution → Webhook assinado → Persistência → (opcional) criação de reserva Escrow → Confirmação.
- Assinatura: HMAC-SHA1 sobre `(endpoint + method + payload)` com chave `QITECH_WEBHOOK_SECRET`.
- Tabela alvo: `webhook_qitech` (colunas em PT-BR). O SQL está disponível em `create_webhook_qitech_ptbr.sql`.

## Requisitos de ambiente

- Python 3.10+ recomendado
- Dependências: instalar com `pip install -r requirements.txt` (inclui `requests`, `flask`, `psycopg2-binary`, `reportlab` etc.)
- Variáveis de ambiente essenciais (arquivo `.env`):
  - `DATABASE_URL` — conexão Postgres
  - `QITECH_WEBHOOK_SECRET` — segredo HMAC para validar webhooks
  - `QITECH_API_KEY` — chave para chamadas ao Risk Solution (sandbox/prod)

- `URL_APLICACAO` — URL pública da aplicação (ex.: https://qi.homolog.plugz.com.br/)

1) Variáveis de ambiente

- `DATABASE_URL` — string de conexão Postgres
- `QITECH_WEBHOOK_SECRET` — segredo HMAC compartilhado para validação de webhooks
- `QITECH_API_KEY` — chave para chamadas Risk Solution (usado em `test_fluxo_integrado_simples.py`)

2) Endpoints implementados

- POST `/webhooks/qitech/onboarding` — recebe webhooks do Risk Solution, valida assinatura (HMAC-SHA1) e persiste. Campos persistidos (PT-BR): `id_registro`, `tipo_pessoa`, `id_pessoa`, `status_analise`, `data_evento`, `motivo`, `conteudo`, `cabecalhos`, `assinatura`, `assinatura_ok`, `recebido_em`.
- GET  `/webhooks/qitech/status` — consulta o último webhook por query param `id_registro` ou `id_pessoa` (opcional `tipo_pessoa`). Retorna resumo com `status_analise`, `data_evento`, `motivo`, `conteudo`.

3) Assinatura de Webhook (HMAC-SHA1)

O cálculo usado é: HMAC-SHA1 sobre a string `(endpoint + method + payload)` com a chave `QITECH_WEBHOOK_SECRET`. No cliente, a função utilitária `RiskSolutionClient.compute_webhook_signature(endpoint, method, payload, signature_key)` gera a hash hex.

Exemplo em Python (cURL equivalente está na collection do Postman):

```python
from risk_solution import RiskSolutionClient
sig = RiskSolutionClient.compute_webhook_signature('/webhooks/qitech/onboarding', 'POST', payload_text, 'seu_segredo')
```

4) Banco de dados — tabela `webhook_qitech` (PT-BR)

Estrutura recomendada (já forneci o SQL em `create_webhook_qitech_ptbr.sql`):
- `id` UUID PK
- `id_registro` varchar(100)
- `tipo_pessoa` varchar(50)
- `id_pessoa` varchar(100)
- `status_analise` varchar(50)
- `data_evento` timestamptz
- `motivo` text
- `conteudo` jsonb
- `cabecalhos` jsonb
- `assinatura` varchar(200)
- `assinatura_ok` boolean
- `recebido_em` timestamptz

5) Fluxo completo (simplificado)

1. Cliente envia dados para Risk Solution (via `risk_solution.py` or directly to QiTech sandbox).
2. QiTech (Risk Solution) processa e envia webhook para nosso endpoint `/webhooks/qitech/onboarding` contendo `registration_id` e `analysis_status`.
3. Nosso listener valida assinatura e persiste o payload completo em `webhook_qitech` (logs completos).
4. Se `status_analise` indicar aprovação, o listener tenta criar reserva Escrow via `PlugQi` automaticamente.
5. Utilitário `GET /webhooks/qitech/status?id_registro=...` permite verificar o último status e prosseguir na criação/confirmação da conta Escrow.

6) Testes e automação

- `examples/qitech_webhook_test.py` — script que:
  - monta payload de exemplo (campo `registration_id: reg-12345`)
  - calcula assinatura usando `RiskSolutionClient.compute_webhook_signature`
  - POST para `POST /webhooks/qitech/onboarding`
  - GET para `GET /webhooks/qitech/status?id_registro=reg-12345`

- `test_fluxo_integrado_simples.py` — teste integrado que já contém bloco Risk Solution (envio simulado quando chave é placeholder) e demais validações de conectividade e helpers. Mantenha esse arquivo como referência para o cliente executar verificação local.

7) Postman

- Coleção: `postman_collection_risk_solution.json` (incluída no repositório).
- Ambiente sugerido (arquivo environment fornecido abaixo): `postman_env_risk_solution.json` — configure `api_key`, `base_url`, `webhook_url`, `webhook_secret`.

8) Gerar PDF explicativo

- Incluí um script utilitário `tools/generate_integration_pdf.py` que converte este Markdown em um PDF simples (utiliza `reportlab`). Para gerar o PDF localmente:

```powershell
pip install -r requirements.txt
python tools/generate_integration_pdf.py INTEGRATION_RISK_SOLUTION.md integration_risk_solution.pdf
```

9) Próximos passos e recomendações

- Revisar os campos do payload do Risk Solution e mapear exatamente `cpf/cnpj`, `email`, `name`, `birthdate` usados na criação de reserva Escrow; posso ajustar o mapeamento automaticamente.
- Decidir política: criação automática de reserva Escrow (hoje: tentativa automática se status aprovado). Se preferir, alterar para criação manual por operador.
- Gerar documentação final em PDF após sua revisão — posso aplicar alterações e gerar nova versão.

---

Se quiser, eu gero agora o PDF e a collection de Postman com exemplos mais completos (cURL, exemplos de headers, environment). Diga se prefere que eu gere o PDF agora com o conteúdo atual.
