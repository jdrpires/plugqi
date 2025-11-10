# 🎯 Guia da Collection Postman - Orquestrador PlugQi

## 📋 Visão Geral

A **PlugQi Orchestrator Collection** é uma collection Postman especializada para testar o Orquestrador de Abertura de Conta do PlugQi.

## 📦 Arquivos da Collection

- `PlugQi_Orchestrator_Collection.json` - Collection principal do orquestrador
- `PlugQi_QiTech_Complete_Collection.json` - Collection completa original (mantida)

## 🚀 Como Importar

### 1. No Postman
1. Abra o Postman
2. Clique em **Import**
3. Selecione o arquivo `PlugQi_Orchestrator_Collection.json`
4. Clique em **Import**

### 2. Configurar Variáveis
Após importar, configure as variáveis de ambiente:

```
QITECH_BASE_URL = https://api-auth.sandbox.qitech.app
QITECH_CLIENT_KEY = sua-chave-aqui
```

## 📊 Requests Disponíveis

### 🔧 **Health Check**
- **Método**: POST
- **Endpoint**: `/test`
- **Propósito**: Verificar conectividade com a API QiTech
- **Status Esperado**: 200 OK

### 🏦 **Orquestrador - Abertura Conta PF**
- **Método**: POST
- **Endpoint**: `/orchestrator/account/pf`
- **Propósito**: Iniciar fluxo completo de abertura de conta Pessoa Física
- **Dados**: Nome, CPF, email, documentos, endereço
- **Variáveis Geradas**: `workflow_id`, `account_request_key`

### 🏢 **Orquestrador - Abertura Conta PJ**
- **Método**: POST
- **Endpoint**: `/orchestrator/account/pj`
- **Propósito**: Iniciar fluxo completo de abertura de conta Pessoa Jurídica
- **Dados**: Empresa, CNPJ, representantes legais, documentos
- **Variáveis Geradas**: `workflow_id_pj`

### 📊 **Consultar Status Workflow**
- **Método**: GET
- **Endpoint**: `/orchestrator/workflow/{workflow_id}/status`
- **Propósito**: Consultar status de um workflow específico
- **Usa**: `workflow_id` gerado nos requests anteriores

### 🔄 **Retomar Workflow**
- **Método**: POST
- **Endpoint**: `/orchestrator/workflow/resume`
- **Propósito**: Retomar um workflow interrompido
- **Parâmetros**: `workflow_id`, `resume_from_step`

### 🏦 **Consultar Instituições Financeiras**
- **Método**: GET
- **Endpoint**: `/financial_institution`
- **Propósito**: Listar instituições financeiras disponíveis
- **Resultado**: Lista com 230+ bancos

### 📄 **Upload Documento**
- **Método**: POST
- **Endpoint**: `/document`
- **Propósito**: Fazer upload de documentos
- **Tipo**: Multipart/form-data
- **Campos**: `file`, `document_type`

## 🎯 Ordem de Execução Recomendada

### 📋 **Fluxo Básico**
1. **Health Check** - Verificar conectividade
2. **Consultar Instituições** - Validar API funcionando
3. **Abertura Conta PF** - Testar fluxo pessoa física
4. **Consultar Status** - Verificar progresso do workflow
5. **Abertura Conta PJ** - Testar fluxo pessoa jurídica

### 🔄 **Fluxo Avançado**
1. Executar fluxo básico
2. **Upload Documento** - Testar upload individual
3. **Retomar Workflow** - Testar recuperação de workflow
4. **Consultar Status** - Verificar estado final

## 📊 Scripts de Teste Automático

### ✅ **Validações Implementadas**
- Status codes esperados (200, 400, 401, 404)
- Estrutura de resposta JSON
- Presença de campos obrigatórios
- Geração automática de dados únicos
- Logs detalhados no console

### 🔧 **Pre-request Scripts**
- Geração de emails únicos com timestamp
- Configuração de variáveis dinâmicas
- Logs de início de operação

### 📋 **Test Scripts**
- Validação de status HTTP
- Extração de dados de resposta
- Configuração de variáveis para próximos requests
- Logs de resultado

## 🎨 Variáveis Dinâmicas

### 🔄 **Geradas Automaticamente**
- `test_email_pf` - Email único para PF
- `test_email_pj` - Email único para PJ
- `workflow_id` - ID do workflow PF
- `workflow_id_pj` - ID do workflow PJ
- `account_request_key` - Chave da conta criada
- `document_key` - Chave do documento enviado

### ⚙️ **Configuráveis**
- `QITECH_BASE_URL` - URL base da API
- `QITECH_CLIENT_KEY` - Chave do cliente

## 📈 Resultados Esperados

### ✅ **Cenários de Sucesso**
- Health Check: 200 OK
- Instituições Financeiras: 200 OK com lista de bancos
- Workflows: Podem retornar 200 (sucesso) ou 400 (falha esperada)

### ⚠️ **Cenários de Falha (Esperados)**
- Orquestrador PF/PJ: 400/401 (configurações sandbox)
- Upload Documento: 400 (formato/permissões)
- Status Workflow: 404 (workflow não encontrado)

## 🔍 Troubleshooting

### ❌ **Problemas Comuns**

#### 1. **401 Unauthorized**
- Verificar `QITECH_CLIENT_KEY`
- Confirmar autenticação JWT
- Validar permissões da chave

#### 2. **400 Bad Request**
- Dados inválidos no payload
- Formato de documento incorreto
- Campos obrigatórios ausentes

#### 3. **404 Not Found**
- Endpoint não existe
- Workflow ID inválido
- Recurso não encontrado

### ✅ **Soluções**
1. Verificar variáveis de ambiente
2. Conferir logs do console
3. Validar formato dos dados
4. Testar Health Check primeiro

## 📊 Métricas de Teste

### 🎯 **Taxa de Sucesso Esperada**
- Health Check: 100%
- Instituições Financeiras: 100%
- Orquestrador: 20% (limitações sandbox)
- Upload Documento: 20% (limitações sandbox)

### 📈 **KPIs Monitorados**
- Tempo de resposta
- Status codes
- Estrutura de dados
- Geração de IDs únicos
- Logs de execução

## 🎉 Conclusão

A collection está otimizada para testar o **Orquestrador de Abertura de Conta** com:
- ✅ Testes automatizados
- ✅ Geração de dados dinâmicos
- ✅ Validações robustas
- ✅ Logs detalhados
- ✅ Fluxos completos

**Pronta para uso em ambiente de desenvolvimento e testes!**
