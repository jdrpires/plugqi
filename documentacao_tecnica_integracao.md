# Documentação Técnica de Integração - PlugQi API

**URL Base (Homologação):** `http://localhost:8002`  
**URL Base (Produção):** `https://api.plugqi.com.br`

---

## Visão Geral

A API PlugQi oferece uma camada de orquestração que abstrai a complexidade da integração com a QiTech, fornecendo endpoints REST simplificados para:

1.  **Orquestração de Documentos** - Upload de arquivos
2.  **Risk Solution** - Análise de risco para PF e PJ
3.  **Contas Escrow** - Abertura de contas
4.  **Monitoramento** - Health check e Status

---

## Autenticação

A API utiliza autenticação básica ou via API Key (configuração pendente).
Para os testes locais, os endpoints estão abertos.

---

## Endpoints

Todas as rotas são prefixadas com `/api/v1`.

### 1. Health Check
**Endpoint:** `/health`
**Método:** `GET`
**Descrição:** Verifica se a API está online.

---

### 2. Documentos

#### Upload de Arquivo
**Endpoint:** `/api/v1/documents/upload`
**Método:** `POST`
**Tipo:** `multipart/form-data`

**Parâmetros:**
*   `file`: Arquivo a ser enviado.

**Response:**
```json
{
  "document_key": "uuid-do-documento",
  "document_md5": "hash-md5",
  "filename": "arquivo.pdf",
  "file_type": "application/pdf",
  "size": 1024
}
```

---

### 3. Risk Solution (Análise de Risco)

Este módulo realiza a análise de crédito e risco (Know Your Customer/Business).


**Endpoint:** `/api/v1/risk/legal-person`
**Método:** `POST`
**Descrição:** Envia dados de **Pessoa Jurídica (PJ)** para análise.

**Payload Exemplo:**
```json
{
  "legal_name": "Empresa LTDA",
  "document_number": "12.345.678/0001-90",
  "foundation_date": "2020-01-01",
  "annual_revenues": 100000000,
  "partners": [...]
  // ... outros campos conforme schema RiskLegalPersonRequest
}
```

---

### 4. Contas Escrow

#### Reservar Conta Escrow (PJ)
**Endpoint:** `/api/v1/accounts/escrow/pj`
**Método:** `POST`
**Descrição:** Inicia o processo de abertura de conta Escrow para Pessoa Jurídica.

**Payload Exemplo:**
```json
{
  "company_document_number": "12.345.678/0001-90",
  "name": "Empresa LTDA",
  "email": "contato@empresa.com",
  "foundation_date": "2020-01-01",
  "legal_representatives": [
    {
      "name": "Sócio Representante",
      "individual_document_number": "123.456.789-00",
      "email": "socio@empresa.com",
      "person_type": "natural"
      // ... endereço e telefone
    }
  ]
}
```

---

## Mapeamento de Conceitos

Para evitar dúvidas:

| Termo QiTech / API | Significado | Tipo de Pessoa |
|-------------------|-------------|----------------|
| **Natural Person** | Pessoa Natural | **PF (Pessoa Física)** |
| **Legal Person** | Pessoa Legal/Jurídica | **PJ (Pessoa Jurídica)** |

---

## Executando Localmente

1.  Certifique-se de estar na raiz do projeto.
2.  Execute: `python -m api.main`
3.  Acesse a documentação interativa (Swagger UI): `http://localhost:8002/docs`
