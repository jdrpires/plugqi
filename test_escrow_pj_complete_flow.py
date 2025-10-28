#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
from qitech_client import QiTechError
import json
import time

def test_escrow_pj_complete_flow():
    """Teste completo: Reserva + Confirmação de conta Escrow PJ"""
    
    print("🏢 TESTE COMPLETO ESCROW PJ - CNPJ 97115705024702")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    # ETAPA 1: RESERVAR CONTA
    print("📋 ETAPA 1: RESERVAR CONTA")
    try:
        response_reserva = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number="97115705024702",
            email="jean.pires@plugz.com.br",
            foundation_date="2017-09-16",
            name="Empresa Teste Escrow",
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
                }
            ]
        )
        
        print("✅ Reserva realizada!")
        print(json.dumps(response_reserva, indent=2, ensure_ascii=False))
        
        account_request_key = response_reserva["account_request_key"]
        print(f"\n🔑 Account Request Key: {account_request_key}")
        
    except QiTechError as e:
        print(f"❌ Erro na reserva: {e.status}")
        print(json.dumps(e.payload, indent=2, ensure_ascii=False))
        return False
    
    # ETAPA 2: CONFIRMAR ABERTURA
    print("\n📋 ETAPA 2: CONFIRMAR ABERTURA")
    
    # Payload de confirmação
    account_owner = {
        "address": {
            "city": "São Paulo",
            "complement": "Sala 101",
            "neighborhood": "Centro",
            "number": "100",
            "postal_code": "01310100",
            "state": "SP",
            "street": "Rua da Consolação"
        },
        "cnae_code": "4721-1/02",
        "company_document_number": "97115705024702",
        "company_statute": "8b0d8c33-01c9-4cf5-a0fa-1d2a96f4b34d",
        "company_type": "ltda",
        "email": "jean.pires@plugz.com.br",
        "foundation_date": "2017-09-16",
        "name": "Empresa Teste Escrow",
        "person_type": "legal",
        "phone": {
            "area_code": "11",
            "country_code": "055",
            "number": "988888888"
        },
        "trading_name": "Teste Escrow Ltda",
        "company_representatives": [
            {
                "name": "Don Corleone",
                "address": {
                    "city": "São Paulo",
                    "complement": None,
                    "neighborhood": "Centro",
                    "number": "100",
                    "postal_code": "01310100",
                    "state": "SP",
                    "street": "Rua da Consolação"
                },
                "email": "Don@empresa.com",
                "birth_date": "1963-07-23",
                "individual_document_number": "22203015837",
                "document_identification": "8b0d8c33-01c9-4cf5-a0fa-1d2a96f4b34d",
                "document_identification_number": "339122924",
                "is_pep": False,
                "marital_status": "single",
                "mother_name": "Maria Corleone",
                "nationality": "Brasileira",
                "person_type": "natural",
                "phone": {
                    "area_code": "11",
                    "country_code": "055",
                    "number": "999999999"
                }
            }
        ]
    }
    
    signed_contract = {
        "document_key": "4d7f4e29-4b58-4905-9a69-b1f9215263f5",
        "signatures": [
            {
                "authenticity": {
                    "timestamp": "2024-10-23T22:00:00.000Z",
                    "facial_recognition_key": "79003de0-2590-455d-9b73-426b8ca284eb",
                    "lang": "-46.6333094",
                    "lat": "-23.5505199",
                    "ip_address": "177.51.1.186",
                    "session_id": "session123456"
                },
                "signer": {
                    "name": "Don Corleone",
                    "email": "Don@empresa.com",
                    "phone": {
                        "country_code": "055",
                        "area_code": "11",
                        "number": "999999999"
                    },
                    "document_number": "22203015837"
                },
                "authentication_type": "opt-in"
            }
        ]
    }
    
    destinations = [
        {
            "account_branch": "0001",
            "account_number": "1234567",
            "account_digit": "1",
            "document_number": "04252012000123",
            "name": "Conta Destino Teste",
            "ispb_number": "32402502",
            "financial_institution_code_number": "329"
        }
    ]
    
    try:
        print("🧪 Enviando confirmação...")
        
        response_confirmacao = plugqi.account_opening.confirmar_abertura_conta_escrow_pj(
            account_request_key=account_request_key,
            account_owner=account_owner,
            signed_contract=signed_contract,
            destinations=destinations,
            additional_documents=["b12c8807-8f3f-4083-9cb1-7cce641f3786"]
        )
        
        print("✅ Confirmação realizada!")
        print(json.dumps(response_confirmacao, indent=2, ensure_ascii=False))
        
        # Salvar resultados
        resultado = {
            "reserva": response_reserva,
            "confirmacao": response_confirmacao,
            "account_request_key": account_request_key
        }
        
        with open('escrow_pj_complete_flow.json', 'w') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultado completo salvo em: escrow_pj_complete_flow.json")
        return True
        
    except QiTechError as e:
        print(f"❌ Erro na confirmação: {e.status}")
        print(json.dumps(e.payload, indent=2, ensure_ascii=False))
        return False

if __name__ == "__main__":
    success = test_escrow_pj_complete_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 FLUXO COMPLETO ESCROW PJ: SUCESSO!")
    else:
        print("❌ FLUXO COMPLETO ESCROW PJ: FALHOU")
    print("=" * 60)
