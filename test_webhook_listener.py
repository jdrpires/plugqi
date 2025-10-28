#!/usr/bin/env python3
"""
Teste do webhook listener com dados mock
"""

import requests
import json
from datetime import datetime

def test_webhook_pending():
    """Testa webhook com status pending_additional_data"""
    
    # Webhook mock conforme documentação
    webhook_mock = {
        "key": "e8e9e118-45e7-4659-aaaa-0677c0e2e4dc",
        "data": {
            "account_info": {
                "account_digit": "7",
                "account_branch": "0001",
                "account_number": "6694401"
            },
            "account_request_key": "e8e9e118-45e7-4659-aaaa-0677c0e2e4dc"
        },
        "status": "pending_additional_data",
        "webhook_type": "account_request.status_change",
        "event_datetime": "2025-01-19T14:18:25.409670"
    }
    
    try:
        print("🧪 Testando webhook pending_additional_data...")
        
        response = requests.post(
            'http://localhost:5000/webhook/escrow',
            json=webhook_mock,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_webhook_rejected():
    """Testa webhook com status rejected"""
    
    webhook_mock = {
        "key": "e8e9e118-45e7-4659-aaaa-0677c0e2e4dc",
        "data": {
            "account_info": {
                "account_digit": "1",
                "account_branch": "0001",
                "account_number": "4456617"
            },
            "account_request_key": "e8e9e118-45e7-4659-aaaa-0677c0e2e4dc"
        },
        "status": "rejected",
        "webhook_type": "account_request.status_change",
        "event_datetime": "2025-01-19T14:18:25.409670"
    }
    
    try:
        print("\n🧪 Testando webhook rejected...")
        
        response = requests.post(
            'http://localhost:5000/webhook/escrow',
            json=webhook_mock,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def check_webhook_status():
    """Verifica status dos webhooks"""
    
    try:
        print("\n📊 Verificando status dos webhooks...")
        
        response = requests.get('http://localhost:5000/webhooks')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total webhooks: {data['total_webhooks']}")
            print(f"Contas prontas: {data['accounts_ready']}")
            print(f"Contas rejeitadas: {data['accounts_rejected']}")
            
            if data['ready_accounts']:
                print("\n✅ Contas prontas para confirmação:")
                for key, account in data['ready_accounts'].items():
                    print(f"  - {key}: {account['account_info']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return False

def check_specific_account():
    """Verifica conta específica"""
    
    account_key = "e8e9e118-45e7-4659-aaaa-0677c0e2e4dc"
    
    try:
        print(f"\n🔍 Verificando conta: {account_key}")
        
        response = requests.get(f'http://localhost:5000/status/{account_key}')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data['status']}")
            print(f"Pronta para confirmação: {data['ready_for_confirmation']}")
            
            if data.get('account_info'):
                info = data['account_info']
                print(f"Conta: {info['account_branch']}-{info['account_number']}-{info['account_digit']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar conta: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE WEBHOOK LISTENER ESCROW")
    print("=" * 50)
    print("IMPORTANTE: Execute 'python3 webhook_listener_escrow.py' em outro terminal primeiro!")
    print("=" * 50)
    
    input("Pressione Enter quando o webhook listener estiver rodando...")
    
    # Executar testes
    test1 = test_webhook_pending()
    test2 = test_webhook_rejected()
    
    # Verificar resultados
    check_webhook_status()
    check_specific_account()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Webhook pending: {'✅' if test1 else '❌'}")
    print(f"Webhook rejected: {'✅' if test2 else '❌'}")
    
    if test1 and test2:
        print("\n🎉 WEBHOOK LISTENER FUNCIONANDO!")
    else:
        print("\n❌ Problemas no webhook listener")
