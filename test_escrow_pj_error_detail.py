#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
from qitech_client import QiTechError
import json

def test_escrow_pj_error_detail():
    """Capturar detalhes do erro Escrow PJ"""
    
    print("🔍 ANÁLISE DETALHADA DO ERRO - CNPJ 99060633000177")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    try:
        response = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number="99060633000177",
            email="jean.pires@plugz.com.br",
            foundation_date="2017-09-16",
            name="Teste Jean Escrow",
            legal_representatives=[
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
        )
        
        print("✅ Sucesso inesperado!")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
    except QiTechError as e:
        print(f"❌ QiTechError capturado:")
        print(f"📋 Status: {e.status}")
        print(f"📋 Mensagem: {str(e)}")
        print(f"📋 Payload do erro:")
        print(json.dumps(e.payload, indent=2, ensure_ascii=False))
        
        # Analisar o erro
        if e.status == 400:
            print("\n🔍 ANÁLISE DO ERRO 400:")
            if 'errors' in e.payload:
                for error in e.payload.get('errors', []):
                    print(f"  • {error}")
            elif 'message' in e.payload:
                print(f"  • {e.payload['message']}")
            else:
                print("  • Erro sem detalhes específicos")
        
    except Exception as e:
        print(f"❌ Erro não esperado: {e}")
        print(f"🔍 Tipo: {type(e)}")

if __name__ == "__main__":
    test_escrow_pj_error_detail()
