#!/usr/bin/env python3
"""
Teste de integração completo do PlugQi
Execute: python3 test_integration.py
"""
import os
import json
from plugqi import PlugQi
from qitech_client import QiTechError

def test_health_check():
    """Testa conectividade básica"""
    print("🔍 Testando conectividade...")
    
    try:
        plugqi = PlugQi()
        result = plugqi.health_check()
        print(f"✅ Health check: {'OK' if result else 'FALHOU'}")
        return result
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_account_list():
    """Testa listagem de contas"""
    print("\n🔍 Testando listagem de contas...")
    
    try:
        plugqi = PlugQi()
        
        # Usa dados do .env ou valores padrão
        doc_number = os.getenv("QI_OWNER_DOCUMENT_NUMBER", "22203015837")
        account_number = os.getenv("QI_ACCOUNT_NUMBER", "68670834")
        
        accounts = plugqi.client.get("/account", params={
            "owner_document_number": doc_number,
            "account_number": account_number
        })
        
        print(f"✅ Contas encontradas: {len(accounts.get('data', []))}")
        return True
        
    except QiTechError as e:
        print(f"❌ Erro QiTech: {e.status} - {e}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_connectors():
    """Testa se todos os connectors estão funcionando"""
    print("\n🔍 Testando connectors...")
    
    try:
        plugqi = PlugQi()
        
        # Testa se connectors existem
        connectors = ['credit', 'payment', 'boleto']
        for connector in connectors:
            if hasattr(plugqi, connector):
                print(f"✅ {connector.capitalize()}Connector: OK")
            else:
                print(f"❌ {connector.capitalize()}Connector: AUSENTE")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos connectors: {e}")
        return False

def test_boleto_helpers():
    """Testa helpers do BoletoConnector"""
    print("\n🔍 Testando helpers de boleto...")
    
    try:
        plugqi = PlugQi()
        
        # Testa build_payer_data
        payer = plugqi.boleto.build_payer_data(
            name="João Teste",
            document="12345678901",
            email="joao@teste.com"
        )
        
        assert payer["name"] == "João Teste"
        assert payer["document_number"] == "12345678901"
        print("✅ build_payer_data: OK")
        
        # Testa build_simple_boleto
        boleto = plugqi.boleto.build_simple_boleto(
            request_control_key="test-123",
            amount=100.0,
            expiration="2024-12-31",
            payer_name="João Teste",
            payer_document="12345678901"
        )
        
        assert boleto["amount"] == 100.0
        assert boleto["payer_data"]["name"] == "João Teste"
        print("✅ build_simple_boleto: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos helpers: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes de integração do PlugQi\n")
    
    tests = [
        test_connectors,
        test_boleto_helpers,
        test_health_check,
        test_account_list
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Resumo
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resumo: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam")
        return 1

if __name__ == "__main__":
    exit(main())
