#!/usr/bin/env python3
"""
Confirmação PF Escrow com schema correto da documentação
"""

import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_complete_pf_flow():
    """Fluxo completo: Reserva + Confirmação PF"""
    
    plugqi = PlugQi()
    
    # ETAPA 1: Reserva (POST)
    print("🔄 ETAPA 1: Reservando conta PF...")
    
    pf_reserva = {
        "account_owner": {
            "document_number": "99999999999",
            "email": "teste@gmail.com",
            "birthdate": "1990-05-06",
            "name": "Nome do Titular da Conta",
            "documents": {
                "cnh": {
                    "ocr_key": str(uuid.uuid4())
                }
            },
            "face": str(uuid.uuid4())
        }
    }
    
    try:
        response_reserva = plugqi.client.post("/account_request/escrow", pf_reserva)
        
        account_request_key = response_reserva['account_request_key']
        print(f"✅ Reserva criada: {account_request_key}")
        print(f"Status: {response_reserva['account_request_status']}")
        
    except Exception as e:
        print(f"❌ Falha na reserva: {e}")
        return False
    
    # ETAPA 2: Confirmação (PATCH) - Schema EXATO da documentação
    print(f"\n🔄 ETAPA 2: Confirmando conta PF...")
    
    # Payload EXATO da documentação PF
    pf_confirmacao = {
        "account_owner": {
            "address": {
                "street": "Av. Brigadeiro Faria Lima",
                "state": "SP",
                "city": "São Paulo",
                "neighborhood": "Jardim Paulistano",
                "number": "2391",
                "postal_code": "01452905",
                "complement": "Complemento"
            },
            "birth_date": "1990-05-06",
            "document_identification": str(uuid.uuid4()),
            "email": "teste@gmail.com",
            "individual_document_number": "99999999999",
            "is_pep": False,
            "mother_name": "Dona Maria Mariane",
            "name": "Nome do Titular da Conta",
            "nationality": "Brasileira",
            "person_type": "natural",
            "phone": {
                "country_code": "055",
                "area_code": "11",
                "number": "999999999"
            },
            "proof_of_residence": str(uuid.uuid4())
        },
        "signed_contract": {
            "document_key": str(uuid.uuid4()),
            "signatures": [
                {
                    "authenticity": {
                        "timestamp": datetime.now().isoformat() + "Z",
                        "facial_recognition_key": str(uuid.uuid4()),
                        "lang": "-35.8916627",
                        "lat": "-7.2226067",
                        "ip_address": "177.51.1.186",
                        "session_id": "jdifj329842"
                    },
                    "signer": {
                        "name": "Nome do Titular da Conta",
                        "email": "teste@gmail.com",
                        "phone": {
                            "country_code": "055",
                            "area_code": "11",
                            "number": "999999999"
                        },
                        "document_number": "99999999999"
                    },
                    "authentication_type": "opt-in"
                }
            ]
        },
        "destinations": [
            {
                "account_branch": "0001",
                "account_number": "1234567",
                "account_digit": "1",
                "document_number": "04252012000123",
                "name": "Conta do FIDC",
                "ispb_number": "32402502",
                "financial_institution_code_number": "329"
            }
        ],
        "additional_documents": [str(uuid.uuid4())]
    }
    
    try:
        endpoint_patch = f"/account_request/{account_request_key}/escrow"
        response_confirmacao = plugqi.client.patch(endpoint_patch, pf_confirmacao)
        
        print("✅ CONFIRMAÇÃO REALIZADA COM SUCESSO!")
        print(f"Account Key final: {response_confirmacao.get('account_key')}")
        print(f"Response completa: {response_confirmacao}")
        
        return True
        
    except Exception as e:
        print(f"❌ Falha na confirmação: {e}")
        if hasattr(e, 'payload'):
            print(f"Detalhes do erro: {e.payload}")
        return False

if __name__ == "__main__":
    print("🏦 FLUXO COMPLETO PF ESCROW")
    print("=" * 50)
    
    success = test_complete_pf_flow()
    
    if success:
        print("\n🎉 CONTA PF ESCROW COMPLETAMENTE CRIADA!")
        print("✅ Reserva (POST) + Confirmação (PATCH) = SUCESSO")
    else:
        print("\n❌ Problema no fluxo completo")
        print("📋 Verificar documentação ou aguardar webhook")
