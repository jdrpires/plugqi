#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
import json

def test_escrow_pj_cnpj2():
    """Teste conta Escrow PJ com CNPJ 99060633000177"""
    
    print("🏢 TESTE CONTA ESCROW PJ - CNPJ 99060633000177")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    if not plugqi.health_check():
        print("❌ Falha na conectividade")
        return False
    
    print("✅ Conectividade OK")
    
    try:
        print("🧪 Testando reserva de conta Escrow PJ...")
        
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
        
        print("✅ Reserva realizada com sucesso!")
        print(f"📊 Resposta:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        with open('escrow_pj_cnpj2_response.json', 'w') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resposta salva em: escrow_pj_cnpj2_response.json")
        return True
        
    except Exception as e:
        print(f"❌ Erro na reserva: {str(e)}")
        
        # Debug detalhado
        print(f"🔍 Tipo do erro: {type(e)}")
        
        if hasattr(e, 'response'):
            print(f"📋 Status Code: {e.response.status_code}")
            print(f"📋 Headers: {dict(e.response.headers)}")
            print(f"📋 Resposta completa: {e.response.text}")
            
            try:
                error_detail = json.loads(e.response.text)
                print(f"📋 JSON do erro:")
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                pass
        
        return False

if __name__ == "__main__":
    success = test_escrow_pj_cnpj2()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE ESCROW PJ CNPJ2: SUCESSO!")
    else:
        print("❌ TESTE ESCROW PJ CNPJ2: FALHOU")
    print("=" * 60)
