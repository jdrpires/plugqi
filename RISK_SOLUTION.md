**Risk Solution**: integração com endpoints de Onboarding da QI Tech (3.1.1–3.1.12)

- **O que implementei**: módulo `risk_solution.py` com client HTTP para os endpoints principais: `natural_person`, `legal_person`, atualizações (`PUT`), consultas (`GET`) e recuperação de PDF. Inclui validações básicas de formato para CPF/CNPJ, e função utilitária `compute_webhook_signature` para validar webhooks HMAC.

- **Como usar**:
  - Instale dependências (se necessário): `pip install requests pytest`
  - Exemplo de uso:

```python
from risk_solution import RiskSolutionClient
client = RiskSolutionClient(api_key='SUA_API_KEY')
payload = {'id': 'abc', 'document_number': '123.456.789-12', 'registration_date': '2024-01-01T00:00:00Z'}
resp = client.send_natural_person(payload)
print(resp.status_code, resp.text)
```

- **Tests**: adicionei `tests/test_risk_solution.py` com testes unitários baseados em `pytest` que mockam `requests`.

- **Collections Postman**: inclui uma collection mínima `postman_collection_risk_solution.json` (arquivo criado no repositório) com chamadas de exemplo.

- **Pontos importantes e limitações**:
  - Validações implementadas cobrem apenas formatos (regex). Regras de negócio complexas da QI Tech devem ser seguidas conforme documentação.
  - Integração com webhook assume cálculo HMAC SHA1 exatamente como descrito na documentação.

- **Próximos passos sugeridos**:
  - Integrar com os secrets/variáveis de ambiente do projeto (por exemplo `sandbox_keys.json`).
  - Expandir cobertura de testes para cenários de erro e comportamentos assíncronos (PDF gerado asincronamente).
