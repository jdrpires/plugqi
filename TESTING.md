# 🧪 Guia de Testes - PlugQi

## Tipos de Teste Disponíveis

### 1. 🔧 Testes Unitários (Sempre Funcionam)
```bash
# Testa lógica interna sem API real
python3 -m pytest tests/ -v
```

**Status:** ✅ 8 testes passando
- Autenticação JWT ES512
- Connectors (Credit, Payment, Boleto)
- Helpers de boleto
- Configurações multi-ambiente

### 2. 🔗 Teste de Integração Local
```bash
# Testa conectores sem chamadas reais à API
python3 test_integration.py
```

**Status:** ✅ 3/4 testes passando
- ✅ Connectors carregados
- ✅ Helpers funcionando
- ✅ Health check básico
- ❌ Listagem de contas (precisa de credenciais válidas)

### 3. 🔥 Smoke Test com API Real
```bash
# Precisa de credenciais válidas no .env
python3 examples/smoke_test.py
```

**Requer:**
- `QITECH_CLIENT_KEY` válida
- `QITECH_PRIVATE_KEY_PATH` válida
- Conta ativa no sandbox QiTech

## Como Testar Cada Funcionalidade

### Boletos
```python
from plugqi import PlugQi
import uuid
from datetime import datetime, timedelta

plugqi = PlugQi()

# Teste básico (sem API)
boleto = plugqi.boleto.build_simple_boleto(
    request_control_key=str(uuid.uuid4()),
    amount=100.0,
    expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    payer_name="João Silva",
    payer_document="12345678901"
)
print("✅ Boleto criado:", boleto)
```

### Crédito
```python
# Teste de simulação
simulation = plugqi.credit.simulate_credit(
    amount=1000.0,
    installments=12
)
```

### Pagamentos
```python
# Teste PIX
pix = plugqi.payment.create_pix_payment(
    amount=100.0,
    recipient_key="chave-pix-destino"
)
```

## Configuração para Testes com API Real

1. **Configure o .env:**
```bash
QITECH_CLIENT_KEY=sua-chave-aqui
QITECH_PRIVATE_KEY_PATH=./keys/ec_p521_private.pem
QITECH_BASE_URL=https://api-auth.sandbox.qitech.app
```

2. **Coloque sua chave privada em:**
```
./keys/ec_p521_private.pem
```

3. **Execute teste completo:**
```bash
python3 run_tests.py
```

## Comandos Rápidos

```bash
# Só testes unitários (sempre funciona)
python3 -m pytest tests/ -v

# Teste específico
python3 -m pytest tests/test_boleto_connector.py -v

# Com cobertura
python3 -m pytest tests/ --cov=connectors --cov-report=html

# Teste de conectividade (precisa de .env)
python3 -c "from plugqi import PlugQi; print('✅ OK' if PlugQi().health_check() else '❌ FALHOU')"
```

## Status Atual dos Testes

| Tipo | Status | Descrição |
|------|--------|-----------|
| Unitários | ✅ 8/9 | Lógica interna funcionando |
| Integração | ⚠️ 3/4 | Connectors OK, API precisa de config |
| Smoke | ❌ | Precisa de credenciais válidas |

## Próximos Passos

1. Configure credenciais válidas no `.env`
2. Execute `python3 run_tests.py`
3. Todos os testes devem passar ✅
