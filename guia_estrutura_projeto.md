# Guia de Estrutura do Projeto PlugQi

Este documento serve como mapa para navegar na estrutura do projeto PlugQi, detalhando onde cada componente está localizado e sua função.

## 📂 Estrutura de Pastas

```
plugqi/
├── api/                    # [NOVO] Camada de API REST (FastAPI)
│   ├── routers/            # Rotas da API separadas por contexto
│   │   ├── documents.py    # Endpoint de Upload
│   │   ├── risk.py         # Endpoint de Análise de Risco (PJ)
│   │   └── escrow.py       # Endpoint de Conta Escrow (PJ)
│   ├── main.py             # Ponto de entrada da aplicação (App FastAPI)
│   └── schemas.py          # Modelos de dados (Pydantic) para validação
│
├── connectors/             # Lógica de integração com a QiTech (SDK Interno)
│   ├── account_opening.py  # Conector de Abertura de Conta
│   ├── boleto.py           # Conector de Boletos
│   ├── document_upload.py  # Conector de Documentos
│   ├── pix.py              # Conector de PIX
│   ├── ted.py              # Conector de TED
│   └── risk_solution.py    # [MOVIDO] Cliente específico de Risco
│
├── tests/                  # Testes Automatizados
│   └── integration_test.py # Script de teste ponta-a-ponta da API
│
├── documentacao_tecnica_integracao.md # Documentação para o Cliente Final
├── plugqi_openapi.json     # Collection do Postman (Swagger exportado)
├── server.py               # (Legado) Servidor Flask antigo
└── plugqi.py               # Classe principal do SDK
```

---

## 🚀 Como Executar

### 1. API de Orquestração
A nova API roda na porta **8002**.

```bash
# Na pasta raiz (plugqi/)
python -m api.main
```

- **Swagger UI (Documentação Interativa):** `http://localhost:8002/docs` (Schemas ocultos para clareza)
- **Collection Postman:** Importe o arquivo `plugqi_openapi.json`.

### 2. Testes de Integração
Para validar se tudo está funcionando:

```bash
python tests/integration_test.py
```

---

## 🛠️ Detalhes dos Componentes

1.  **API (`api/`)**: É a "porta de entrada" para o mundo externo. Recebe as requisições do seu Frontend/Cliente, valida os dados (usando `schemas.py`) e chama os conectores.
2.  **Connectors (`connectors/`)**: É onde a mágica acontece. Eles sabem como conversar com a QiTech. Se a QiTech mudar a API dela, você só mexe aqui.
3.  **Routers (`api/routers/`)**: Organizam a API. Se precisar adicionar Renda Fixa no futuro, crie `api/routers/fixed_income.py`.


## 🔐 Gerenciando Chaves de Acesso

Para adicionar clientes sem alterar o código, usamos **Variáveis de Ambiente**.

### 1. Local (Desenvolvimento)
Crie ou edite o arquivo `.env` na raiz do projeto (`plugqi/.env`).
**Não commite este arquivo no Git!**

```ini
# Exemplo de arquivo .env
PLUGQI_API_KEY=minha_chave_mestra_local
PLUGQI_CLIENT_INTERNO=plg_int_123456
PLUGQI_CLIENT_PECA_RARA=plg_rare_789012
```

### 2. Produção (Servidor)
Não usamos arquivo `.env`. Cadastre as variáveis no painel da sua hospedagem (AWS Parameter Store, Heroku Config Vars, Railway Variables, etc.).

O sistema detectará automaticamente qualquer variável começando com `PLUGQI_CLIENT_`.
