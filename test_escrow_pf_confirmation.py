#!/usr/bin/env python3
"""
Confirmação da conta PF Escrow - Segunda etapa (PATCH)
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_pf_confirmation():
    """Teste completo: Reserva + Confirmação PF"""
    
    plugqi = PlugQi()
    
    # Etapa 1: Reserva (POST)
    print("🔄 ETAPA 1: Reservando conta PF...")
    
    pf_payload = {
        "account_owner": {
            "document_number": "99999999999",
            "email": "teste@teste.com",
            "birthdate": "1990-01-01",
            "name": "Teste PF Confirmação",
            "documents": {
                "cnh": {
                    "ocr_key": str(uuid.uuid4())
                }
            },
            "face": str(uuid.uuid4())
        }
    }
    
    try:
        response_reserva = plugqi.client.post("/account_request/escrow", pf_payload)
        
        account_request_key = response_reserva['account_request_key']
        print(f"✅ Reserva criada: {account_request_key}")
        print(f"Status: {response_reserva['account_request_status']}")
        
    except Exception as e:
        print(f"❌ Falha na reserva: {e}")
        return False
    
    # Etapa 2: Confirmação (PATCH)
    print(f"\n🔄 ETAPA 2: Confirmando conta PF...")
    print(f"Account Request Key: {account_request_key}")
    
    # Payload de confirmação (baseado na documentação PJ, adaptado para PF)
    confirmation_payload = {
        "account_owner": {
            "address": {
                "city": "São Paulo",
                "complement": "Apto 101",
                "neighborhood": "Centro",
                "number": "123",
                "postal_code": "01234567",
                "state": "SP",
                "street": "Rua Teste"
            },
            "document_number": "99999999999",
            "email": "teste@teste.com",
            "birthdate": "1990-01-01",
            "name": "Teste PF Confirmação",
            "person_type": "natural",
            "phone": {
                "area_code": "11",
                "country_code": "055",
                "number": "999999999"
            }
        },
        "signed_contract": {
            "document_key": str(uuid.uuid4()),
            "signatures": [
                {
                    "authenticity": {
                        "timestamp": "2024-10-23T16:17:00Z",
                        "facial_recognition_key": str(uuid.uuid4()),
                        "session_id": str(uuid.uuid4())
                    },
                    "signer": {
                        "name": "Teste PF Confirmação",
                        "email": "teste@teste.com",
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
                "account_number": "123456",
                "account_digit": "7",
                "document_number": "99999999999",
                "name": "Teste PF Confirmação",
                "ispb_number": "60746948",
                "financial_institution_code_number": "341"
            }
        ]
    }
    
    try:
        endpoint_confirmation = f"/account_request/{account_request_key}/escrow"
        response_confirmation = plugqi.client.patch(endpoint_confirmation, confirmation_payload)
        
        print("✅ CONFIRMAÇÃO REALIZADA COM SUCESSO!")
        print(f"Account Key final: {response_confirmation.get('account_key', 'N/A')}")
        print(f"Response: {response_confirmation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Falha na confirmação: {e}")
        if hasattr(e, 'payload'):
            print(f"Detalhes: {e.payload}")
        return False

if __name__ == "__main__":
    print("🏦 CONFIRMAÇÃO CONTA PF ESCROW")
    print("=" * 50)
    
    success = test_pf_confirmation()
    
    if success:
        print("\n🎉 CONTA PF ESCROW TOTALMENTE CRIADA!")
        print("✅ Reserva + Confirmação completas")
    else:
        print("\n❌ Problema na confirmação")
        print("📋 Verificar payload de confirmação")
