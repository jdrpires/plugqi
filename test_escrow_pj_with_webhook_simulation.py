#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
from qitech_client import QiTechError
import json
import time

def simulate_webhook_pending_additional_data(account_request_key: str, account_info: dict):
    """Simular webhook pending_additional_data"""
    
    webhook_data = {
        "key": account_request_key,
        "data": {
            "account_info": account_info,
            "account_request_key": account_request_key
        },
        "status": "pending_additional_data",
        "webhook_type": "account_request.status_change",
        "event_datetime": "2024-10-23T22:15:00.000000",
        "request_control_key": "simulated-webhook-123"
    }
    
    print("🔔 SIMULANDO WEBHOOK pending_additional_data")
    print(json.dumps(webhook_data, indent=2, ensure_ascii=False))
    
    # Salvar como se fosse um webhook real
    with open('simulated_webhook_pending.json', 'w') as f:
        json.dump(webhook_data, f, indent=2, ensure_ascii=False)
    
    return webhook_data

def test_escrow_pj_with_webhook():
    """Teste Escrow PJ simulando o fluxo completo com webhook"""
    
    print("🏢 TESTE ESCROW PJ COM SIMULAÇÃO DE WEBHOOK")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    # Usar uma conta já criada para testar confirmação
    # (Vamos usar a conta criada anteriormente)
    account_request_key = "218d7204-5341-405f-a8d3-30b7bc6c8634"
    account_info = {
        "account_branch": "0001",
        "account_digit": "5",
        "account_number": "2690192"
    }
    
    print(f"🔑 Usando Account Request Key: {account_request_key}")
    
    # Simular webhook
    webhook_data = simulate_webhook_pending_additional_data(account_request_key, account_info)
    
    print("\n📋 TENTANDO CONFIRMAÇÃO APÓS WEBHOOK SIMULADO")
    
    # Payload de confirmação simplificado
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
                    "complement": "",
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
        print("🧪 Tentando confirmação...")
        
        response = plugqi.account_opening.confirmar_abertura_conta_escrow_pj(
            account_request_key=account_request_key,
            account_owner=account_owner,
            signed_contract=signed_contract,
            destinations=destinations
        )
        
        print("✅ Confirmação realizada!")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        with open('escrow_pj_confirmation_success.json', 'w') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        return True
        
    except QiTechError as e:
        print(f"❌ Erro na confirmação: {e.status}")
        print(f"📋 Código: {e.payload.get('code', 'N/A')}")
        print(f"📋 Descrição: {e.payload.get('description', 'N/A')}")
        print(f"📋 Tradução: {e.payload.get('translation', 'N/A')}")
        
        # Analisar o erro
        if e.payload.get('code') == 'ACR000042':
            print("\n🔍 ANÁLISE: Conta ainda não está no status correto")
            print("💡 SOLUÇÃO: Aguardar webhook real 'pending_additional_data'")
        
        return False

if __name__ == "__main__":
    success = test_escrow_pj_with_webhook()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CONFIRMAÇÃO ESCROW PJ: SUCESSO!")
    else:
        print("❌ CONFIRMAÇÃO ESCROW PJ: Aguardando webhook real")
    print("=" * 60)
