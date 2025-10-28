# 📮 Guia da Collection Postman - PlugQi QiTech

## 🎯 Visão Geral

Collection completa para testes QA do SDK PlugQi com API QiTech, baseada nos testes automatizados do sistema.

## 📁 Arquivos da Collection

- `PlugQi_QiTech_Complete_Collection.json` - Collection principal completa
- `postman_collection_plugqi_part1.json` - Parte 1: Health Check
- `postman_collection_boletos.json` - Parte 2: Boletos
- `postman_collection_pix.json` - Parte 3: PIX
- `postman_collection_escrow_negative.json` - Parte 4: Escrow e Testes Negativos

## 🚀 Como Importar

1. Abra o Postman
2. Clique em "Import"
3. Selecione `PlugQi_QiTech_Complete_Collection.json`
4. A collection será importada com todas as pastas e testes

## ⚙️ Configuração Inicial

### 1. Variáveis de Ambiente

Crie um Environment no Postman com as seguintes variáveis:

```
QITECH_CLIENT_KEY = sua-chave-cliente-qitech
ACCOUNT_KEY = sua-chave-conta-teste
REQUESTER_PROFILE_KEY = sua-chave-perfil-solicitante
```

### 2. JWT Token

**IMPORTANTE:** O JWT token deve ser gerado manualmente ou via script:

```javascript
// Exemplo de geração JWT (implementar conforme sua lógica)
pm.collectionVariables.set('jwt_token', 'seu-jwt-token-aqui');
```

## 📋 Estrutura da Collection

### 🔧 Health Check & Auth
- **Health Check** - Verifica conectividade com API QiTech

### 💰 Boletos
- **Criar Boleto Simples** - Cria boleto básico
- **Consultar Boleto** - Consulta boleto criado
- **Criar BolePix** - Cria boleto com PIX integrado

### 🔄 PIX
- **Enviar PIX por Chave** - Transferência PIX
- **Validar Chave PIX** - Valida chave PIX

### 🏦 Conta Escrow (BLOQUEADO)
- **Reservar Conta PJ** - Teste do erro GDF000014 (esperado)

### ❌ Testes Negativos
- **Boleto - Dados Inválidos** - Testa validação de dados
- **Autenticação - Token Inválido** - Testa autenticação

## 🎯 Ordem de Execução Recomendada

1. **Health Check** - Sempre primeiro
2. **Criar Boleto Simples** - Gera boleto para testes
3. **Consultar Boleto** - Usa boleto criado
4. **Criar BolePix** - Testa integração PIX
5. **Enviar PIX** - Testa transferência
6. **Validar Chave PIX** - Testa validação
7. **Testes Negativos** - Valida tratamento de erros
8. **Conta Escrow** - Confirma bloqueio esperado

## 📊 Resultados Esperados

### ✅ Sucessos Esperados
- Health Check: 100%
- Boletos: ~90% (dependendo da configuração)
- PIX: ~80% (algumas chaves podem falhar)
- Testes Negativos: 100% (erros são esperados)

### ❌ Falhas Esperadas
- **Conta Escrow**: Erro 401 GDF000014 (endpoint bloqueado)
- **PIX com chaves inválidas**: Erro 400/422
- **Dados inválidos**: Erro 400/422

## 🔄 Variáveis Dinâmicas

A collection gera automaticamente:

- **UUIDs únicos** para request_control_key
- **Datas futuras** para vencimentos
- **End-to-end IDs** para PIX
- **Chaves PIX válidas** do mock data

## 🧪 Scripts de Teste

Cada request inclui:

### Pre-request Scripts
```javascript
// Gera dados únicos
pm.collectionVariables.set('request_control_key', pm.variables.replaceIn('{{$guid}}'));

// Calcula datas
var dueDate = new Date();
dueDate.setDate(dueDate.getDate() + 30);
pm.collectionVariables.set('due_date', dueDate.toISOString().split('T')[0]);
```

### Test Scripts
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('boleto_key');
});
```

## 📈 Métricas e Relatórios

### Executar Collection Completa
1. Clique em "Run Collection"
2. Selecione todas as requests
3. Configure iterations (recomendado: 1)
4. Execute

### Relatório Esperado
```
✅ Health Check: 1/1 passed
✅ Boletos: 3/3 passed
✅ PIX: 2/2 passed
❌ Conta Escrow: 0/1 passed (esperado)
✅ Testes Negativos: 2/2 passed

Total: 8/9 passed (88.9%)
```

## 🔧 Troubleshooting

### Erro de Autenticação
- Verifique se jwt_token está configurado
- Confirme se as chaves estão corretas
- Teste Health Check primeiro

### Erro 401 GDF000014
- **Normal para Conta Escrow** - endpoint bloqueado
- Para outros endpoints: verifique permissões

### Erro de Timeout
- Aumente timeout no Postman (Settings > General)
- Verifique conectividade de rede

### PIX Falhas
- Algumas chaves mock podem não existir
- Use chave padrão: `183466bd-6383-4517-96f2-48f4f1488692`

## 🔄 Atualizações Futuras

Esta collection será atualizada quando:

1. **Novos endpoints** forem liberados
2. **Conta Escrow** for desbloqueada
3. **Novas funcionalidades** forem implementadas
4. **Testes adicionais** forem necessários

## 📞 Suporte

Para dúvidas sobre a collection:
1. Consulte este guia
2. Verifique logs do console no Postman
3. Compare com testes automatizados do PlugQi
4. Consulte documentação QiTech oficial

---

**Versão:** 1.0  
**Data:** 2024-10-23  
**Compatível com:** Postman v10+  
**Baseado em:** PlugQi Test Suite v1.0
