# 🔌 PlugQi - SDK Python para QiTech

SDK Python simplificado para integração com a API da QiTech, oferecendo funcionalidades bancárias e financeiras completas.

## 🚀 Funcionalidades

- **🏦 Abertura de Contas** - Contas PJ com fluxo completo
- **💰 Boletos** - Criação, consulta e BolePix
- **🔄 PIX** - Chaves, pagamentos e QR codes
- **💳 Pagamentos** - Boletos e transferências
- **💸 Crédito** - Simulações e análises
- **🔄 Transferências Automáticas** - Regras de movimentação programada
- **🔐 Autenticação** - JWT ES512 automática

## 📦 Instalação

```bash
git clone https://github.com/jeanpires/plugqi.git
cd plugqi
pip install -r requirements.txt
```

## ⚙️ Configuração

Crie um arquivo `.env`:

```env
QITECH_CLIENT_KEY=sua-api-key
QITECH_PRIVATE_KEY_PATH=./keys/ec_p521_private.pem
QITECH_BASE_URL=https://api-auth.sandbox.qitech.app
```

## 🔧 Uso Básico

```python
from plugqi import PlugQi

# Inicializar
plugqi = PlugQi()

# Verificar conectividade
if plugqi.health_check():
    print("✅ Conectado à QiTech")

# Criar boleto
boleto = plugqi.boleto.create_boleto(
    account_key="sua-conta",
    requester_profile_key="sua-carteira",
    boleto_data={
        "request_control_key": "uuid-unico",
        "amount": 100.0,
        "expiration": "2024-12-31",
        "payer_data": {
            "name": "João Silva",
            "document_number": "12345678901"
        }
    }
)

# Enviar PIX
pix = plugqi.pix.enviar_pix_chave(
    account_key="sua-conta",
    pix_key="joao@email.com",
    valor=50.0
)

# Criar regra de transferência automática
regra = plugqi.automatic_transfer.create_split_percentage_rule(
    account_key="sua-conta",
    destinations=[{
        "account_branch": "0001",
        "account_number": "123456",
        "account_digit": "7",
        "document_number": "12345678901",
        "name": "João Silva",
        "financial_institutions_code_number": "001",
        "percentage": 80
    }],
    transfer_cronstring="0 18 * * 1-5",  # Dias úteis às 18h
    remaining_balance=100.0
)
```

## 📚 Módulos Disponíveis

### Boletos (`plugqi.boleto`)
- `create_boleto()` - Criar boleto
- `create_bolepix()` - Boleto + PIX
- `get_boleto()` - Consultar boleto
- `list_boletos()` - Listar boletos

### PIX (`plugqi.pix`)
- `criar_chave_pix()` - Criar chave
- `enviar_pix_chave()` - Enviar por chave
- `criar_qr_code_estatico()` - QR Code
- `listar_transacoes_pix()` - Histórico

### Contas (`plugqi.account_opening`)
- `reservar_conta_pj()` - Reservar conta
- `confirmar_abertura_conta()` - Confirmar abertura
- `consultar_status_abertura()` - Status

### Pagamentos (`plugqi.payment`)
- Pagamento de boletos
- Transferências bancárias

### Crédito (`plugqi.credit`)
- Simulações de empréstimo

### Transferências Automáticas (`plugqi.automatic_transfer`)
- `create_split_percentage_rule()` - Divisão percentual
- `create_split_equal_rule()` - Divisão igualitária  
- `create_single_beneficiary_rule()` - Beneficiário único
- `update_transfer_rule()` - Atualizar regra
- `deactivate_rule()` - Desativar regra
- `build_destination()` - Helper para destinos

#### Tipos de Regras de Transferência

**Split Percentage** - Divide percentualmente:
```python
# 80% dividido entre contas, 20% fica na origem
destinations = [
    {"percentage": 50, ...},  # 50%
    {"percentage": 30, ...}   # 30%
]
plugqi.automatic_transfer.create_split_percentage_rule(
    account_key="conta-origem",
    destinations=destinations,
    transfer_cronstring="0 18 * * 1-5"  # Dias úteis 18h
)
```

**Split Equal** - Divide igualmente:
```python
# Divide igualmente entre todas as contas destino
plugqi.automatic_transfer.create_split_equal_rule(
    account_key="conta-origem", 
    destinations=[conta1, conta2, conta3],
    remaining_balance=100.0  # Manter R$ 100 na origem
)
```

**Single Beneficiary** - Um único destino:
```python
# Transfere tudo para uma conta
plugqi.automatic_transfer.create_single_beneficiary_rule(
    account_key="conta-origem",
    destination=conta_destino,
    transfer_cronstring="0 0 * * *"  # Diariamente à meia-noite
)
```

#### Exemplos de CRON
- `"*/5 * * * *"` - A cada 5 minutos
- `"0 0 * * *"` - Diariamente às 00:00
- `"0 18 * * 1-5"` - Dias úteis às 18:00
- `"0 0 1 * *"` - Todo dia 1 do mês

## 🧪 Testes

```bash
# Testes unitários
python -m pytest tests/ -v

# Teste de integração
python test_integration.py

# Teste transferências automáticas
python test_automatic_transfer.py

# Smoke test (precisa de credenciais)
python examples/smoke_test.py
```

## 📁 Estrutura

```
plugqi/
├── plugqi.py              # Classe principal
├── qitech_client.py       # Cliente HTTP + JWT
├── connectors/            # Módulos especializados
│   ├── boleto.py         # Boletos
│   ├── pix.py            # PIX
│   ├── account_opening.py # Contas
│   ├── payment.py        # Pagamentos
│   ├── credit.py         # Crédito
│   └── automatic_transfer.py # Transferências automáticas
├── tests/                # Testes
├── examples/             # Exemplos
└── keys/                 # Chaves privadas
```

## 🔑 Autenticação

O PlugQi usa autenticação JWT ES512 com chaves criptográficas. Coloque sua chave privada em `./keys/ec_p521_private.pem` ou configure o caminho no `.env`.

## 📖 Documentação

- [Guia de Testes](TESTING.md)
- [Guia QA](QA_TEST_GUIDE.md)
- [Exemplos](examples/)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🆘 Suporte

Para dúvidas sobre a API QiTech, consulte a [documentação oficial](https://qitech.com.br/docs).