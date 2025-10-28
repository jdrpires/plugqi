#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
import json
import requests

def test_escrow_pj_debug():
    """Debug detalhado do erro Escrow PJ"""
    
    print("🔍 DEBUG ESCROW PJ - CNPJ 99060633000177")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    # Acessar o client interno para debug
    client = plugqi.account_opening.client
    
    payload = {
        "account_owner": {
            "company_document_number": "99060633000177",
            "email": "jean.pires@plugz.com.br",
            "foundation_date": "2017-09-16",
            "name": "Teste Jean Escrow"
        },
        "legal_representatives": [
            {
                "birthdate": "1963-07-23",
                "name": "Don Corleone",
                "document_number": "22203015837",
                "email": "Don@empresa.com",
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
                "email": "John@empresa.com",
                "documents": {
                    "cnh": {
                        "ocr_key": "beee557e-9240-4c5b-88f1-42812b195168"
                    }
                }
            }
        ]
    }
    
    print("📋 Payload enviado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        # Fazer chamada direta
        response = client.post("/account_request/escrow", payload)
        print("✅ Sucesso!")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTPError: {e}")
        print(f"📋 Status: {e.response.status_code}")
        print(f"📋 Resposta: {e.response.text}")
        
        try:
            error_json = e.response.json()
            print(f"📋 JSON do erro:")
            print(json.dumps(error_json, indent=2, ensure_ascii=False))
        except:
            pass
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print(f"🔍 Tipo: {type(e)}")

if __name__ == "__main__":
    test_escrow_pj_debug()
