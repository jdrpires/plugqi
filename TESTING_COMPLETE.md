# 🧪 Sistema Completo de Testes - PlugQi

## 📋 Visão Geral

O PlugQi possui um sistema completo de testes em **4 níveis**:

1. **🔧 Testes Simples Automatizados** - Validação rápida sem API
2. **🧪 Testes Unitários** - Lógica interna com pytest
3. **🔗 Testes Completos** - Cenários reais com API
4. **📊 Relatório de Stress** - Massa de dados e performance

## 🚀 Como Executar

### Execução Rápida (Recomendado)
```bash
# Executa todos os testes
python run_all_tests.py

# Apenas testes simples (sem API)
python run_all_tests.py --simple

# Apenas testes unitários
python run_all_tests.py --unit

# Apenas testes completos (precisa credenciais)
python run_all_tests.py --comprehensive

# Apenas relatório completo
python run_all_tests.py --report
```

### Execução Individual
```bash
# Testes simples (sempre funcionam)
python test_automated_simple.py

# Testes completos (precisam credenciais)
python test_comprehensive.py

# Relatório com massa de dados
python generate_comprehensive_report.py

# Testes unitários
python -m pytest tests/ -v
```

## 📁 Arquivos do Sistema de Testes

### Testes Principais
- `test_automated_simple.py` - Testes rápidos sem API
- `test_comprehensive.py` - Testes completos com cenários positivos/negativos
- `generate_comprehensive_report.py` - Gerador de relatório com massa de dados
- `run_all_tests.py` - Script principal para executar todos os testes
- `run_tests.py` - Script integrado (compatibilidade)

### Dados de Teste
- `pix_keys_mock.json` - Chaves PIX mockadas para testes
- `test_results_*.json` - Resultados dos testes (gerados automaticamente)
- `comprehensive_report_*.json` - Relatórios completos (gerados automaticamente)

### Testes Unitários (pasta tests/)
- `test_auth_es512.py` - Autenticação JWT
- `test_boleto_connector.py` - Funcionalidades de boleto
- `test_signed_client_methods.py` - Cliente HTTP
- `conftest.py` - Configurações pytest

## 🎯 Tipos de Teste

### 1. 🔧 Testes Simples Automatizados
**Arquivo:** `test_automated_simple.py`
**Objetivo:** Validação rápida da estrutura e lógica interna
**Execução:** Sem credenciais, sempre funciona

**Testa:**
- ✅ Helpers de boleto (build_payer_data, build_simple_boleto)
- ✅ Validação de chaves PIX
- ✅ Métodos de abertura de conta
- ✅ Carregamento de chaves PIX mockadas
- ✅ Estrutura dos conectores

### 2. 🧪 Testes Unitários
**Pasta:** `tests/`
**Objetivo:** Testa lógica interna com mocks
**Execução:** `python -m pytest tests/ -v`

**Testa:**
- ✅ Autenticação JWT ES512
- ✅ Assinatura de requisições
- ✅ Conectores individuais
- ✅ Helpers e utilitários

### 3. 🔗 Testes Completos
**Arquivo:** `test_comprehensive.py`
**Objetivo:** Cenários reais com API QiTech
**Execução:** Precisa credenciais válidas no `.env`

**Testa:**
- 🏦 **Abertura de Contas:** 3 contas escrow
- 💰 **Boletos:** 5 tipos diferentes
- 💳 **BolePix:** 5 boletos com PIX
- 🔄 **PIX:** 10 transações com valores aleatórios
- ❌ **Cenários Negativos:** CPF inválido, valores negativos
- 🔍 **Cenários Exploratórios:** Caracteres especiais, limites

### 4. 📊 Relatório de Stress
**Arquivo:** `generate_comprehensive_report.py`
**Objetivo:** Massa de dados e testes de performance
**Execução:** Gera relatório JSON completo

**Gera:**
- 🏦 **3 contas escrow** com dados completos
- 💰 **5 tipos de boletos** (PF, PJ, valores diversos)
- 💳 **5 BolePix** com chaves PIX aleatórias
- 🔄 **10 transações PIX** com valores em centavos
- ⚡ **Testes de stress** (velocidade, throughput)
- 📈 **Métricas de performance** (taxa sucesso, distribuição valores)

## 🔑 Chaves PIX Mockadas

O arquivo `pix_keys_mock.json` contém **60+ chaves PIX** de diferentes bancos:

- **🏦 Caixa Econômica Federal** (104)
- **🏦 Itaú Unibanco** (341)
- **🏦 Bradesco** (237)
- **🏦 Santander** (33)
- **🏦 Banco Inter** (77)
- **🏦 Nubank** (260)
- **🏦 C6 Bank** (336)
- **🏦 Safra** (422)

**Tipos de chave:**
- 📧 Email (pix01@pix01.com, pix02@pix02.com...)
- 📱 Telefone (+5568911106520, +5568970000000...)
- 🆔 CPF/CNPJ (65322181032, 40008675000100...)
- 🔀 Aleatória (UUID v4)

## 📊 Relatórios Gerados

### Estrutura do Relatório JSON
```json
{
  "execution_info": {
    "start_time": "2024-10-22T16:00:00",
    "duration_seconds": 45.2,
    "total_operations": 23,
    "success_rate": 95.7
  },
  "accounts": {
    "created": [...],
    "failed": [...],
    "total": 3
  },
  "boletos": {
    "created": [...],
    "failed": [...],
    "total": 5
  },
  "performance_metrics": {
    "amount_distribution": {
      "total": 53847.23,
      "avg": 2342.49,
      "min": 0.01,
      "max": 50000.00
    }
  },
  "stress_test_results": {
    "boleto_creation_speed": {
      "rate_per_second": 15.3
    }
  }
}
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```env
QITECH_CLIENT_KEY=sua-api-key
QITECH_PRIVATE_KEY_PATH=./keys/ec_p521_private.pem
QITECH_BASE_URL=https://api-auth.sandbox.qitech.app
```

### Dependências
```bash
pip install -r requirements.txt
```

## 🎯 Cenários de Teste Cobertos

### ✅ Cenários Positivos
- Criação de boletos PF e PJ
- BolePix com diferentes chaves
- Transações PIX com valores variados
- Abertura de contas escrow
- Validação de documentos

### ❌ Cenários Negativos
- CPF/CNPJ inválidos
- Valores negativos
- Datas no passado
- Campos obrigatórios ausentes
- Chaves PIX malformadas

### 🔍 Cenários Exploratórios
- Caracteres especiais em nomes
- Valores com muitas casas decimais
- UUIDs duplicados
- Limites de campo
- Performance sob carga

## 📈 Métricas Coletadas

- **Taxa de sucesso** por funcionalidade
- **Tempo de execução** de cada operação
- **Distribuição de valores** (min, max, média)
- **Velocidade de criação** (ops/segundo)
- **Análise de erros** por categoria
- **Cobertura de cenários** (positivos/negativos)

## 🚨 Troubleshooting

### Erro: "Arquivo pix_keys_mock.json não encontrado"
```bash
# Execute primeiro o sistema de testes para gerar o arquivo
python test_automated_simple.py
```

### Erro: "QiTech Error 401 - Unauthorized"
```bash
# Configure credenciais válidas no .env
# Para testes simples, use:
python test_automated_simple.py --simple
```

### Erro: "pytest não encontrado"
```bash
pip install pytest
```

## 🎉 Exemplo de Execução Completa

```bash
# 1. Testes rápidos (sempre funcionam)
python test_automated_simple.py
# ✅ 15/15 testes passaram

# 2. Testes unitários
python -m pytest tests/ -v
# ✅ 8/8 testes passaram

# 3. Testes completos (com credenciais)
python test_comprehensive.py
# ✅ 25/28 testes passaram (3 falhas de auth esperadas)

# 4. Relatório completo
python generate_comprehensive_report.py
# 📊 Relatório salvo em comprehensive_report_20241022_160000.json

# 5. Todos juntos
python run_all_tests.py
# 🎯 RESULTADO: 68/71 testes passaram (95.8%)
```

## 📝 Próximos Passos

1. **Configure credenciais** válidas no `.env`
2. **Execute testes simples** para validar estrutura
3. **Execute testes completos** para validar API
4. **Gere relatório** para análise de performance
5. **Analise resultados** e ajuste conforme necessário

---

**💡 Dica:** Execute `python run_all_tests.py --simple` primeiro para validar que tudo está funcionando antes de tentar os testes com API real.
