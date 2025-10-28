#!/usr/bin/env python3
"""
Teste simples do webhook listener
"""

import requests
import json

def test_webhook():
    """Testa webhook com dados da documentação"""
    
    # Webhook exato da documentação QiTech
    webhook_data = {
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
        print("🧪 Enviando webhook de teste...")
        
        response = requests.post(
            'http://localhost:5000/webhook/escrow',
            json=webhook_data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
            return True
        else:
            print("❌ Erro no webhook")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Webhook listener não está rodando!")
        print("Execute: python3 webhook_listener_escrow.py")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_result():
    """Verifica se webhook foi processado"""
    
    try:
        print("\n📊 Verificando resultado...")
        
        # Verificar lista geral
        response = requests.get('http://localhost:5000/webhooks')
        data = response.json()
        
        print(f"Total webhooks: {data['total_webhooks']}")
        print(f"Contas prontas: {data['accounts_ready']}")
        
        # Verificar conta específica
        account_key = "e8e9e118-45e7-4659-aaaa-0677c0e2e4dc"
        response = requests.get(f'http://localhost:5000/status/{account_key}')
        account_data = response.json()
        
        print(f"\nStatus da conta: {account_data['status']}")
        print(f"Pronta para confirmação: {account_data['ready_for_confirmation']}")
        
        return account_data['ready_for_confirmation']
        
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
        return False

if __name__ == "__main__":
    print("🔔 TESTE WEBHOOK ESCROW")
    print("=" * 30)
    
    # Testar webhook
    webhook_ok = test_webhook()
    
    if webhook_ok:
        # Verificar resultado
        ready = check_result()
        
        if ready:
            print("\n🎉 WEBHOOK FUNCIONANDO!")
            print("Conta marcada como pronta para confirmação")
        else:
            print("\n⚠️ Webhook recebido mas não processado corretamente")
    
    print("\n📋 Para testar:")
    print("1. Execute: python3 webhook_listener_escrow.py")
    print("2. Execute: python3 test_webhook_simple.py")
