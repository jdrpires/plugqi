#!/usr/bin/env python3
"""
Teste específico do BoletoConnector
"""
import uuid
from datetime import datetime, timedelta
from plugqi import PlugQi

def test_boleto_helpers():
    """Testa helpers do boleto"""
    print("🔍 Testando helpers de boleto...")
    
    plugqi = PlugQi()
    
    # 1. Teste build_payer_data
    payer = plugqi.boleto.build_payer_data(
        name="João Silva",
        document="12345678901",
        person_type="natural",
        email="joao@teste.com"
    )
    
    assert payer["name"] == "João Silva"
    assert payer["document_number"] == "12345678901"
    assert payer["contact"]["email"] == "joao@teste.com"
    print("✅ build_payer_data: OK")
    
    # 2. Teste build_simple_boleto
    boleto = plugqi.boleto.build_simple_boleto(
        request_control_key=str(uuid.uuid4()),
        amount=150.75,
        expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        payer_name="Maria Santos",
        payer_document="98765432100",
        bank_teller_instructions="Pagamento da fatura 123"
    )
    
    assert boleto["amount"] == 150.75
    assert boleto["payer_data"]["name"] == "Maria Santos"
    assert boleto["bank_teller_instructions"] == "Pagamento da fatura 123"
    print("✅ build_simple_boleto: OK")
    
    return True

def test_boleto_methods():
    """Testa se métodos do boleto existem"""
    print("\n🔍 Testando métodos do BoletoConnector...")
    
    plugqi = PlugQi()
    
    methods = [
        'create_boleto',
        'create_boleto_instant', 
        'create_boletos_batch',
        'get_boleto',
        'list_boletos',
        'list_requester_profiles',
        'create_requester_profile',
        'build_payer_data',
        'build_simple_boleto'
    ]
    
    for method in methods:
        if hasattr(plugqi.boleto, method):
            print(f"✅ {method}: OK")
        else:
            print(f"❌ {method}: AUSENTE")
            return False
    
    return True

def test_boleto_payload():
    """Testa criação de payload completo"""
    print("\n🔍 Testando payload completo de boleto...")
    
    plugqi = PlugQi()
    
    # Payload completo
    boleto_data = {
        "request_control_key": str(uuid.uuid4()),
        "amount": 250.00,
        "expiration": "2024-12-31",
        "bank_teller_instructions": "Não receber após vencimento",
        "payer_data": plugqi.boleto.build_payer_data(
            name="Empresa XYZ Ltda",
            document="12345678000195",
            person_type="legal",
            email="financeiro@empresa.com"
        ),
        "fine_data": {
            "fine_type": "percentage",
            "fine_percentage": 2,
            "days_to_fine": 1
        },
        "interest_data": {
            "interest_type": "calendar_days_monthly_percentage", 
            "interest_percentage": 1,
            "days_to_interest": 1
        }
    }
    
    # Validações básicas
    assert boleto_data["amount"] > 0
    assert boleto_data["payer_data"]["person_type"] == "legal"
    assert boleto_data["fine_data"]["fine_percentage"] == 2
    
    print("✅ Payload completo: OK")
    print(f"✅ Valor: R$ {boleto_data['amount']:.2f}")
    print(f"✅ Pagador: {boleto_data['payer_data']['name']}")
    
    return True

def main():
    """Executa todos os testes de boleto"""
    print("🎫 Iniciando testes específicos de BOLETO\n")
    
    tests = [
        test_boleto_methods,
        test_boleto_helpers, 
        test_boleto_payload
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            results.append(False)
    
    # Resumo
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resumo Boletos: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes de boleto passaram!")
        return 0
    else:
        print("⚠️ Alguns testes falharam")
        return 1

if __name__ == "__main__":
    exit(main())
