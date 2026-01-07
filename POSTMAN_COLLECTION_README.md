# Postman Collection - PlugQi

Este README mostra como usar a collection Postman já presente (`PlugQi_QiTech_Complete_Collection.json`) localmente, incluindo um helper para gerar o JWT necessário para autenticação.

**Resumo:**
- A collection já existe em `PlugQi_QiTech_Complete_Collection.json` e cobre Boletos, PIX, testes negativos e health check.
- Para facilitar uso no Postman, adicionei um endpoint local em `server.py` que gera os headers de autenticação: `POST /__generate_auth`.
- Também inclui um arquivo de ambiente `postman_env_plugqi.json` com variáveis básicas.

## Passo a passo (rápido)

1. Rode o servidor localmente:

```powershell
python server.py
```

2. No Postman, importe a collection `PlugQi_QiTech_Complete_Collection.json` (File > Import).
3. Importe o ambiente `postman_env_plugqi.json` (File > Import) e selecione o ambiente `PlugQi - Local`.
4. Preencha as variáveis do ambiente: `QITECH_CLIENT_KEY`, `ACCOUNT_KEY`, `REQUESTER_PROFILE_KEY`.

## Gerar o JWT automaticamente (opção recomendada)

A collection usa `{{jwt_token}}` para o header `Authorization`. Para não ter que gerar o JWT manualmente, há duas opções:

### A) Manual — chamar o endpoint local de geração e copiar o token

- Faça uma requisição POST para `http://localhost:5000/__generate_auth` com body JSON, por exemplo:

```json
{
  "method": "GET",
  "endpoint": "/health"
}
```

- A resposta terá `{ "headers": { "AUTHORIZATION": "<token>", "API-CLIENT-KEY": "<key>" } }`.
- Copie o valor de `AUTHORIZATION` para a variável `jwt_token` no ambiente do Postman.

### B) Semi-automático — pré-request script (exemplo)

Você pode adicionar este trecho como `Pre-request Script` em cada request (ou no nível da collection) para chamar o helper local e popular `jwt_token` antes da execução:

```javascript
// Pré-request: busca headers no proxy local e popula a variável jwt_token
if (pm.environment.get('use_local_proxy') === 'true') {
  var endpoint = pm.request.url.getPath();
  // Se existirem query params, append manualmente (opcional)
  pm.sendRequest({
    url: pm.environment.get('local_proxy_url') + '/__generate_auth',
    method: 'POST',
    header: { 'Content-Type': 'application/json' },
    body: {
      mode: 'raw',
      raw: JSON.stringify({
        method: pm.request.method,
        endpoint: endpoint,
        body: (pm.request.body && pm.request.body.raw) ? JSON.parse(pm.request.body.raw) : {}
      })
    }
  }, function (err, res) {
    if (err) { console.log('Erro ao gerar auth:', err); return; }
    var hdrs = (res && res.json && res.json().headers) ? res.json().headers : {};
    if (hdrs.AUTHORIZATION) pm.environment.set('jwt_token', hdrs.AUTHORIZATION);
    if (hdrs['API-CLIENT-KEY']) pm.environment.set('QITECH_CLIENT_KEY', hdrs['API-CLIENT-KEY']);
  });
}
```

Observação: dependendo da URL do request no Postman, `pm.request.url.getPath()` pode retornar apenas o caminho; se a sua request inclui querystring que impacta a assinatura, ajuste o `endpoint` manualmente (ex.: `/account/{{ACCOUNT_KEY}}/boleto/{{REQUESTER_PROFILE_KEY}}`).

## Fluxo recomendado de execução

1. Executar `Health Check` (verifica conectividade).
2. Criar Boleto Simples.
3. Consultar o boleto criado usando `last_boleto_key` (variável criada automaticamente pela collection).
4. Criar BolePix (Boleto + PIX).
5. Executar transfers PIX e validação de chaves.
6. Executar testes negativos e validar respostas.

## Observações finais

- A geração do JWT exige a `QITECH_PRIVATE_KEY` configurada no ambiente do servidor (variável `QITECH_PRIVATE_KEY_PATH` ou PEM inline) — isso é usado pelo `QiTechClient` localizado no projeto.
- Se preferir não rodar o servidor local, gere o JWT por script Python local e cole em `jwt_token`.

Se quiser, eu posso:
- Exportar a collection final com o pre-request script embutido que chama o proxy local.
- Gerar um pequeno helper CLI para gerar o token e preencher o arquivo de ambiente automaticamente.

