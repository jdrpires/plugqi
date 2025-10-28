# 🔌 PlugQi - SDK Python para QiTech

SDK Python simplificado para integração com a API da QiTech, oferecendo funcionalidades bancárias e financeiras completas.

## 🚀 Funcionalidades

- **🏦 Abertura de Contas** - Contas PJ com fluxo completo
- **💰 Boletos** - Criação, consulta e BolePix
- **🔄 PIX** - Chaves, pagamentos e QR codes
- **💳 Pagamentos** - Boletos e transferências
- **💸 Crédito** - Simulações e análises
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

## 🧪 Testes

```bash
# Testes unitários
python -m pytest tests/ -v

# Teste de integração
python test_integration.py

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
│   └── credit.py         # Crédito
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