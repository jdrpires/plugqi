#!/usr/bin/env python3
"""
Teste PJ com payload EXATO da documentação enviada
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_exact_documentation():
    """Payload EXATO da documentação"""
    
    plugqi = PlugQi()
    
    # Payload EXATO da documentação
    exact_payload = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "email@teste.com",
            "foundation_date": "2017-09-16",
            "name": "Nome da Empresa"
        },
        "legal_representatives": [
            {
                "birthdate": "1963-07-23",
                "name": "Don Corleone",
                "document_number": "03912394323",
                "documents": {
                    "national_registry_of_foreigners": {
                        "ocr_front_key": "0aa8a4ca-5873-49bd-851c-1f2c71a1cc28",
                        "ocr_back_key": "29f6e346-7fae-4dcb-9ea1-2a3e4ef593ea"
                    }
                },
                "face": "68da08f1-6cf4-4dce-a297-7b2f09311784"
            },
            {
                "birthdate": "1996-03-10",
                "name": "John Doe",
                "document_number": "39113492093",
                "documents": {
                    "cnh": {
                        "ocr_key": "beee557e-9240-4c5b-88f1-42812b195168"
                    }
                }
            }
        ]
    }
    
    try:
        print("🧪 Testando payload EXATO da documentação...")
        response = plugqi.client.post("/account_request/escrow", exact_payload)
        
        print("✅ SUCESSO! PJ Escrow funcionando!")
        print(f"Account Request Key: {response['account_request_key']}")
        print(f"Conta: {response['account_info']['account_branch']}-{response['account_info']['account_number']}-{response['account_info']['account_digit']}")
        print(f"Status: {response['account_request_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        if hasattr(e, 'payload'):
            print(f"Detalhes: {e.payload}")
        return False

def test_with_valid_uuids():
    """Teste com UUIDs válidos gerados"""
    
    plugqi = PlugQi()
    
    payload_valid_uuids = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "email@teste.com", 
            "foundation_date": "2017-09-16",
            "name": "Nome da Empresa"
        },
        "legal_representatives": [
            {
                "birthdate": "1963-07-23",
                "name": "Don Corleone",
                "document_number": "03912394323",
                "documents": {
                    "national_registry_of_foreigners": {
                        "ocr_front_key": str(uuid.uuid4()),
                        "ocr_back_key": str(uuid.uuid4())
                    }
                },
                "face": str(uuid.uuid4())
            },
            {
                "birthdate": "1996-03-10",
                "name": "John Doe", 
                "document_number": "39113492093",
                "documents": {
                    "cnh": {
                        "ocr_key": str(uuid.uuid4())
                    }
                }
            }
        ]
    }
    
    try:
        print("\n🧪 Testando com UUIDs válidos gerados...")
        response = plugqi.client.post("/account_request/escrow", payload_valid_uuids)
        
        print("✅ SUCESSO com UUIDs válidos!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Falhou com UUIDs válidos: {str(e)}")
        return False

if __name__ == "__main__":
    print("📋 TESTE PJ - DOCUMENTAÇÃO EXATA")
    print("=" * 50)
    
    success1 = test_exact_documentation()
    success2 = test_with_valid_uuids()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Payload exato doc: {'✅' if success1 else '❌'}")
    print(f"UUIDs válidos: {'✅' if success2 else '❌'}")
    
    if success1 or success2:
        print("\n🎉 PJ ESCROW FUNCIONANDO!")
    else:
        print("\n❌ PJ ainda com problemas")
