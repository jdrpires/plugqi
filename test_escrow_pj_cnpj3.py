#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
from qitech_client import QiTechError
import json

def test_escrow_pj_cnpj3():
    """Teste conta Escrow PJ com CNPJ 98483046636326"""
    
    print("🏢 TESTE CONTA ESCROW PJ - CNPJ 98483046636326")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    try:
        response = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number="98483046636326",
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
        
        print("✅ Reserva realizada com sucesso!")
        print(f"📊 Resposta:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        with open('escrow_pj_cnpj3_response.json', 'w') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resposta salva em: escrow_pj_cnpj3_response.json")
        
    except QiTechError as e:
        print(f"❌ Erro QiTech:")
        print(f"📋 Status: {e.status}")
        print(f"📋 Detalhes:")
        print(json.dumps(e.payload, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_escrow_pj_cnpj3()
