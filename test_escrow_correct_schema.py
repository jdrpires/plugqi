#!/usr/bin/env python3
"""
Teste conta Escrow com schema correto da documentação QiTech
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_escrow_pj_correct():
    """Teste PJ com schema correto da documentação"""
    
    plugqi = PlugQi()
    
    # Payload correto para PJ conforme documentação
    correct_payload = {
        "account_owner": {
            "company_document_number": "99999999999",  # Mock para aprovação automática
            "email": "empresa@teste.com",
            "foundation_date": "2020-01-01",
            "name": "Empresa Teste LTDA"
        },
        "legal_representatives": [
            {
                "birthdate": "1990-01-01",
                "name": "João Silva",
                "document_number": "12345678901",
                "documents": {
                    "cnh": {
                        "ocr_key": str(uuid.uuid4())
                    }
                },
                "face": str(uuid.uuid4())
            }
        ]
    }
    
    try:
        print("🧪 Testando conta Escrow PJ com schema correto...")
        print(f"Payload: {correct_payload}")
        
        response = plugqi.client.post("/account_request/escrow", correct_payload)
        
        print("✅ SUCESSO! Conta Escrow PJ criada!")
        print(f"Response: {response}")
        
        # Salvar dados importantes
        if 'account_request_key' in response:
            print(f"🔑 Account Request Key: {response['account_request_key']}")
            
        if 'account_info' in response:
            account_info = response['account_info']
            print(f"🏦 Conta criada: {account_info['account_branch']}-{account_info['account_number']}-{account_info['account_digit']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        if hasattr(e, 'payload'):
            print(f"Payload erro: {e.payload}")
        return False

def test_escrow_pf_correct():
    """Teste PF com schema correto da documentação"""
    
    plugqi = PlugQi()
    
    # Payload correto para PF conforme documentação
    correct_payload = {
        "account_owner": {
            "document_number": "99999999999",  # Mock para aprovação automática
            "email": "joao@teste.com",
            "birthdate": "1990-01-01",
            "name": "João Silva",
            "documents": {
                "cnh": {
                    "ocr_key": str(uuid.uuid4())
                }
            },
            "face": str(uuid.uuid4())
        }
    }
    
    try:
        print("\n🧪 Testando conta Escrow PF com schema correto...")
        print(f"Payload: {correct_payload}")
        
        response = plugqi.client.post("/account_request/escrow", correct_payload)
        
        print("✅ SUCESSO! Conta Escrow PF criada!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        if hasattr(e, 'payload'):
            print(f"Payload erro: {e.payload}")
        return False

def test_minimal_pj():
    """Teste PJ mínimo sem documentos opcionais"""
    
    plugqi = PlugQi()
    
    minimal_payload = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "empresa@teste.com", 
            "foundation_date": "2020-01-01",
            "name": "Empresa Teste LTDA"
        }
    }
    
    try:
        print("\n🧪 Testando PJ mínimo (sem legal_representatives)...")
        
        response = plugqi.client.post("/account_request/escrow", minimal_payload)
        
        print("✅ SUCESSO! PJ mínimo funcionou!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ PJ mínimo falhou: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 TESTE CONTA ESCROW - SCHEMA OFICIAL")
    print("=" * 50)
    
    # Teste 1: PJ completo
    success_pj = test_escrow_pj_correct()
    
    # Teste 2: PF completo  
    success_pf = test_escrow_pf_correct()
    
    # Teste 3: PJ mínimo
    success_minimal = test_minimal_pj()
    
    print("\n📊 RESULTADOS:")
    print(f"PJ Completo: {'✅' if success_pj else '❌'}")
    print(f"PF Completo: {'✅' if success_pf else '❌'}")
    print(f"PJ Mínimo: {'✅' if success_minimal else '❌'}")
    
    if success_pj or success_pf or success_minimal:
        print("\n🎉 CONTA ESCROW FUNCIONANDO!")
    else:
        print("\n🔍 Ainda há problemas no schema")
