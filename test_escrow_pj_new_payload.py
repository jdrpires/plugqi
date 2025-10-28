#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
import json

def test_escrow_pj_new_payload():
    """Teste conta Escrow PJ com payload fornecido"""
    
    print("🏢 TESTE CONTA ESCROW PJ - NOVO PAYLOAD")
    print("=" * 60)
    
    # Inicializar PlugQi
    plugqi = PlugQi()
    
    # Verificar conectividade
    if not plugqi.health_check():
        print("❌ Falha na conectividade")
        return False
    
    print("✅ Conectividade OK")
    
    # Payload fornecido
    payload = {
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
    
    print(f"📋 Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        print("🧪 Testando reserva de conta Escrow PJ...")
        
        # Tentar reservar conta com argumentos separados
        response = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number=payload["account_owner"]["company_document_number"],
            email=payload["account_owner"]["email"],
            foundation_date=payload["account_owner"]["foundation_date"],
            name=payload["account_owner"]["name"],
            legal_representatives=payload["legal_representatives"]
        )
        
        print("✅ Reserva realizada com sucesso!")
        print(f"📊 Resposta:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Salvar resposta
        with open('escrow_pj_response_new.json', 'w') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resposta salva em: escrow_pj_response_new.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na reserva: {str(e)}")
        
        # Tentar extrair detalhes do erro
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            try:
                error_detail = json.loads(e.response.text)
                print(f"📋 Detalhes do erro:")
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print(f"📋 Resposta bruta: {e.response.text}")
        
        return False

if __name__ == "__main__":
    success = test_escrow_pj_new_payload()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE ESCROW PJ: SUCESSO!")
    else:
        print("❌ TESTE ESCROW PJ: FALHOU")
    print("=" * 60)
