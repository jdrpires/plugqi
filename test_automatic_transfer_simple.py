#!/usr/bin/env python3
"""
Teste simples - Regras de Movimentação Automática
Executa validações básicas sem necessidade de credenciais
"""

import json
from plugqi import PlugQi

def test_automatic_transfer_module_loaded():
    """Testa se o módulo foi carregado corretamente"""
    
    print("🔄 Teste Simples - Transferências Automáticas")
    print("=" * 45)
    
    try:
        plugqi = PlugQi()
        
        # Verifica se o módulo foi carregado
        assert hasattr(plugqi, 'automatic_transfer'), "Módulo automatic_transfer não encontrado"
        print("✅ Módulo automatic_transfer carregado")
        
        # Verifica métodos principais
        methods = [
            'create_transfer_rule',
            'update_transfer_rule', 
            'create_split_percentage_rule',
            'create_split_equal_rule',
            'create_single_beneficiary_rule',
            'deactivate_rule',
            'build_destination'
        ]
        
        for method in methods:
            assert hasattr(plugqi.automatic_transfer, method), f"Método {method} não encontrado"
            print(f"✅ Método {method} disponível")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_build_destination_helper():
    """Testa o helper build_destination"""
    
    print("\n🔧 Testando Helper build_destination")
    print("-" * 35)
    
    try:
        plugqi = PlugQi()
        
        # Teste básico
        destination = plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="123456",
            account_digit="7",
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001"
        )
        
        required_fields = [
            "account_branch", "account_number", "account_digit",
            "document_number", "name", "financial_institutions_code_number"
        ]
        
        for field in required_fields:
            assert field in destination, f"Campo {field} não encontrado"
        
        print("✅ Campos obrigatórios presentes")
        
        # Teste com percentage
        destination_pct = plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="123456", 
            account_digit="7",
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001",
            percentage=50
        )
        
        assert destination_pct["percentage"] == 50, "Percentage não definido corretamente"
        print("✅ Percentage funcionando")
        
        # Teste com PIX
        destination_pix = plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="123456",
            account_digit="7", 
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001",
            is_pix_transfer=True
        )
        
        assert destination_pix["is_pix_transfer"] is True, "PIX transfer não definido"
        print("✅ PIX transfer funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_rule_data_structure():
    """Testa estrutura de dados das regras"""
    
    print("\n📋 Testando Estruturas de Dados")
    print("-" * 30)
    
    try:
        plugqi = PlugQi()
        
        # Mock client para não fazer chamadas reais
        class MockClient:
            def post(self, endpoint, data):
                return {"mock": "response", "data": data}
            def put(self, endpoint, data):
                return {"mock": "response", "data": data}
        
        plugqi.automatic_transfer.client = MockClient()
        
        # Teste Split Percentage
        destinations = [{
            "account_branch": "0001",
            "account_number": "123456",
            "account_digit": "7",
            "document_number": "12345678901", 
            "name": "João Silva",
            "financial_institutions_code_number": "001",
            "percentage": 100
        }]
        
        result = plugqi.automatic_transfer.create_split_percentage_rule(
            account_key="test-key",
            destinations=destinations,
            transfer_cronstring="0 0 * * *"
        )
        
        # Verifica estrutura da requisição
        request_data = result["data"]
        assert request_data["rule"] == "split_percentage", "Rule type incorreto"
        assert request_data["account_key"] == "test-key", "Account key incorreto"
        assert "rule_configuration" in request_data, "Rule configuration ausente"
        
        print("✅ Split Percentage - estrutura OK")
        
        # Teste Split Equal
        destinations_equal = [{
            "account_branch": "0001",
            "account_number": "123456",
            "account_digit": "7",
            "document_number": "12345678901",
            "name": "João Silva", 
            "financial_institutions_code_number": "001"
        }]
        
        result = plugqi.automatic_transfer.create_split_equal_rule(
            account_key="test-key",
            destinations=destinations_equal
        )
        
        request_data = result["data"]
        assert request_data["rule"] == "split_equal", "Rule type incorreto"
        print("✅ Split Equal - estrutura OK")
        
        # Teste Single Beneficiary
        destination_single = {
            "account_branch": "0001",
            "account_number": "123456",
            "account_digit": "7",
            "document_number": "12345678901",
            "name": "João Silva",
            "financial_institutions_code_number": "001"
        }
        
        result = plugqi.automatic_transfer.create_single_beneficiary_rule(
            account_key="test-key",
            destination=destination_single
        )
        
        request_data = result["data"]
        assert request_data["rule"] == "single_beneficiary", "Rule type incorreto"
        assert "destination" in request_data["rule_configuration"], "Destination ausente"
        print("✅ Single Beneficiary - estrutura OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_cron_patterns():
    """Testa padrões CRON comuns"""
    
    print("\n📅 Validando Padrões CRON")
    print("-" * 25)
    
    valid_patterns = [
        ("*/5 * * * *", "A cada 5 minutos"),
        ("0 0 * * *", "Diariamente às 00:00"),
        ("0 12 * * *", "Diariamente às 12:00"),
        ("0 0 * * 1", "Toda segunda às 00:00"),
        ("0 18 * * 1-5", "Dias úteis às 18:00"),
        ("0 0 1 * *", "Todo dia 1 do mês"),
        ("0 0 1 1 *", "Todo 1º de janeiro")
    ]
    
    for pattern, description in valid_patterns:
        # Validação básica de formato CRON (5 campos)
        parts = pattern.split()
        assert len(parts) == 5, f"CRON inválido: {pattern}"
        print(f"✅ {pattern:<15} - {description}")
    
    return True

if __name__ == "__main__":
    print("🚀 EXECUTANDO TESTES SIMPLES")
    print("=" * 40)
    
    tests = [
        test_automatic_transfer_module_loaded,
        test_build_destination_helper,
        test_rule_data_structure,
        test_cron_patterns
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Falha no teste {test.__name__}: {e}")
    
    print(f"\n📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  Alguns testes falharam")
    
    print(f"✅ Testes simples concluídos")
