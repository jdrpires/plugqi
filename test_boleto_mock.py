#!/usr/bin/env python3
"""
Teste de boleto com mock da API QiTech
"""
import uuid
from unittest.mock import Mock
from plugqi import PlugQi

def test_create_boleto_mock():
    """Testa criação de boleto com mock"""
    print("🎫 Testando criação de boleto (mock)...")
    
    # Mock do client
    mock_client = Mock()
    mock_client.post.return_value = {
        "request_control_key": "test-123",
        "bank_slip_key": "boleto-456",
        "bank_slip_status": "accepted",
        "our_number": 12345,
        "barcode": "12345678901234567890123456789012345678901234",
        "digitable_line": "12345.67890 12345.678901 23456.789012 3 45678901234"
    }
    
    # Cria PlugQi com mock
    plugqi = PlugQi(mock_client)
    
    # Dados do boleto
    boleto_data = plugqi.boleto.build_simple_boleto(
        request_control_key=str(uuid.uuid4()),
        amount=100.50,
        expiration="2024-12-31",
        payer_name="João Silva",
        payer_document="12345678901"
    )
    
    # Simula criação
    result = plugqi.boleto.create_boleto(
        account_key="account-123",
        requester_profile_key="profile-456", 
        boleto_data=boleto_data
    )
    
    # Verificações
    assert result["bank_slip_status"] == "accepted"
    assert result["our_number"] == 12345
    assert len(result["barcode"]) == 44
    
    print("✅ Boleto criado com sucesso!")
    print(f"✅ Status: {result['bank_slip_status']}")
    print(f"✅ Nosso número: {result['our_number']}")
    print(f"✅ Código de barras: {result['barcode'][:20]}...")
    
    return True

def test_list_boletos_mock():
    """Testa listagem de boletos com mock"""
    print("\n🔍 Testando listagem de boletos (mock)...")
    
    # Mock do client
    mock_client = Mock()
    mock_client.get.return_value = {
        "data": [
            {
                "bank_slip_key": "boleto-1",
                "bank_slip_status": "registered",
                "amount": 100.0,
                "expiration": "2024-12-31"
            },
            {
                "bank_slip_key": "boleto-2", 
                "bank_slip_status": "paid",
                "amount": 250.0,
                "expiration": "2024-11-30"
            }
        ],
        "pagination": {
            "current_page": 1,
            "rows_per_page": 10
        }
    }
    
    plugqi = PlugQi(mock_client)
    
    # Lista boletos
    result = plugqi.boleto.list_boletos("account-123")
    
    # Verificações
    assert len(result["data"]) == 2
    assert result["data"][0]["bank_slip_status"] == "registered"
    assert result["data"][1]["bank_slip_status"] == "paid"
    
    print(f"✅ {len(result['data'])} boletos encontrados")
    print(f"✅ Status: {[b['bank_slip_status'] for b in result['data']]}")
    
    return True

def test_get_boleto_mock():
    """Testa consulta de boleto específico"""
    print("\n🔍 Testando consulta de boleto (mock)...")
    
    mock_client = Mock()
    mock_client.get.return_value = {
        "bank_slip_key": "boleto-123",
        "bank_slip_status": "registered",
        "amount": 150.75,
        "expiration": "2024-12-31",
        "payer_data": {
            "name": "João Silva",
            "document_number": "12345678901"
        },
        "barcode": "12345678901234567890123456789012345678901234",
        "digitable_line": "12345.67890 12345.678901 23456.789012 3 45678901234"
    }
    
    plugqi = PlugQi(mock_client)
    
    # Consulta boleto
    result = plugqi.boleto.get_boleto("account-123", "boleto-123")
    
    # Verificações
    assert result["bank_slip_key"] == "boleto-123"
    assert result["amount"] == 150.75
    assert result["payer_data"]["name"] == "João Silva"
    
    print(f"✅ Boleto encontrado: {result['bank_slip_key']}")
    print(f"✅ Valor: R$ {result['amount']:.2f}")
    print(f"✅ Pagador: {result['payer_data']['name']}")
    
    return True

def main():
    """Executa testes com mock"""
    print("🎭 Iniciando testes de BOLETO com MOCK\n")
    
    tests = [
        test_create_boleto_mock,
        test_list_boletos_mock,
        test_get_boleto_mock
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Erro: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resumo Mock: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes com mock passaram!")
        return 0
    else:
        print("⚠️ Alguns testes falharam")
        return 1

if __name__ == "__main__":
    exit(main())
