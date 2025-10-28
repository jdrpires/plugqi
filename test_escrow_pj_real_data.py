#!/usr/bin/env python3
"""
Teste PJ Escrow com dados reais fornecidos
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_pj_real_data():
    """Teste com payload real fornecido"""
    
    plugqi = PlugQi()
    
    # Payload com dados reais fornecidos
    real_payload = {
        "account_owner": {
            "company_document_number": "29060633000177",
            "email": "jean.pires@plugz.com.br",
            "foundation_date": "2017-09-16",
            "name": "Teste Jean Escrow"
        },
        "legal_representatives": [
            {
                "birthdate": "1963-07-23",
                "name": "Don Corleone",
                "document_number": "22203015837",
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
                "document_number": "33588385878",
                "documents": {
                    "cnh": {
                        "ocr_key": "beee557e-9240-4c5b-88f1-42812b195168"
                    }
                }
            }
        ]
    }
    
    try:
        print("🧪 Testando PJ com dados reais...")
        print(f"CNPJ: {real_payload['account_owner']['company_document_number']}")
        print(f"Email: {real_payload['account_owner']['email']}")
        
        response = plugqi.client.post("/account_request/escrow", real_payload)
        
        print("✅ SUCESSO! PJ Escrow criada com dados reais!")
        print(f"Account Request Key: {response['account_request_key']}")
        print(f"Conta: {response['account_info']['account_branch']}-{response['account_info']['account_number']}-{response['account_info']['account_digit']}")
        print(f"Status: {response['account_request_status']}")
        
        # Salvar resultado
        with open('escrow_pj_success.json', 'w') as f:
            import json
            json.dump(response, f, indent=2)
            
        return True
        
    except Exception as e:
        print(f"❌ Erro com dados reais: {str(e)}")
        if hasattr(e, 'payload'):
            print(f"Detalhes do erro: {e.payload}")
        return False

if __name__ == "__main__":
    print("🎯 TESTE PJ ESCROW - DADOS REAIS")
    print("=" * 50)
    
    success = test_pj_real_data()
    
    if success:
        print("\n🎉 PJ ESCROW FUNCIONANDO COM DADOS REAIS!")
        print("✅ Problema resolvido!")
    else:
        print("\n❌ Ainda há problema mesmo com dados reais")
        print("📋 Confirmar com QiTech se PJ está habilitado")
