#!/usr/bin/env python3
"""
Fluxo completo Escrow: Reserva -> Webhook -> Confirmação
"""

import os
import sys
import uuid
import time
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def create_escrow_reservation():
    """Cria reserva de conta Escrow PF"""
    
    plugqi = PlugQi()
    
    pf_payload = {
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
        print("🔄 ETAPA 1: Criando reserva de conta...")
        
        response = plugqi.client.post("/account_request/escrow", pf_payload)
        
        account_request_key = response['account_request_key']
        print(f"✅ Reserva criada: {account_request_key}")
        print(f"Status: {response['account_request_status']}")
        
        return account_request_key
        
    except Exception as e:
        print(f"❌ Erro na reserva: {e}")
        return None

def wait_for_webhook(account_request_key, timeout=300):
    """Aguarda webhook de confirmação"""
    
    print(f"\n⏳ ETAPA 2: Aguardando webhook para {account_request_key}...")
    print("(Simulando webhook - em produção viria da QiTech)")
    
    # Simular webhook após 5 segundos
    time.sleep(5)
    
    # Enviar webhook mock para o listener
    webhook_mock = {
        "key": account_request_key,
        "data": {
            "account_info": {
                "account_digit": "7",
                "account_branch": "0001",
                "account_number": "6694401"
            },
            "account_request_key": account_request_key
        },
        "status": "pending_additional_data",
        "webhook_type": "account_request.status_change",
        "event_datetime": datetime.now().isoformat()
    }
    
    try:
        # Enviar webhook mock
        response = requests.post(
            'http://localhost:5000/webhook/escrow',
            json=webhook_mock,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Webhook recebido pelo listener!")
            return True
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ Webhook listener não disponível: {e}")
        print("Continuando sem webhook listener...")
        return True

def confirm_escrow_account(account_request_key):
    """Confirma abertura da conta Escrow"""
    
    plugqi = PlugQi()
    
    confirmation_payload = {
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
        print(f"\n🔄 ETAPA 3: Confirmando conta {account_request_key}...")
        
        endpoint = f"/account_request/{account_request_key}/escrow"
        response = plugqi.client.patch(endpoint, confirmation_payload)
        
        print("✅ CONTA CONFIRMADA COM SUCESSO!")
        print(f"Account Key final: {response.get('account_key')}")
        
        return response.get('account_key')
        
    except Exception as e:
        print(f"❌ Erro na confirmação: {e}")
        if hasattr(e, 'payload'):
            error_code = e.payload.get('code', 'N/A')
            if error_code == 'ACR000042':
                print("⚠️ Conta ainda não está pronta para confirmação")
                print("Aguarde o webhook pending_additional_data da QiTech")
        return None

def complete_escrow_flow():
    """Executa fluxo completo de conta Escrow"""
    
    print("🏦 FLUXO COMPLETO CONTA ESCROW")
    print("=" * 50)
    
    # Etapa 1: Reserva
    account_request_key = create_escrow_reservation()
    if not account_request_key:
        return False
    
    # Etapa 2: Webhook (simulado)
    webhook_received = wait_for_webhook(account_request_key)
    if not webhook_received:
        print("⚠️ Continuando sem webhook...")
    
    # Etapa 3: Confirmação
    account_key = confirm_escrow_account(account_request_key)
    
    if account_key:
        print(f"\n🎉 CONTA ESCROW CRIADA COM SUCESSO!")
        print(f"Account Request Key: {account_request_key}")
        print(f"Account Key: {account_key}")
        return True
    else:
        print(f"\n⏳ CONTA RESERVADA, AGUARDANDO WEBHOOK REAL")
        print(f"Account Request Key: {account_request_key}")
        print("Execute novamente após receber webhook da QiTech")
        return False

if __name__ == "__main__":
    complete_escrow_flow()
