#!/usr/bin/env python3
"""
Webhook Listener para conta Escrow - Conforme documentação QiTech
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Armazenar webhooks e status
webhooks_log = []
accounts_ready = {}

@app.route('/webhook/escrow', methods=['POST'])
def escrow_webhook():
    """Handler para webhooks de conta Escrow"""
    
    try:
        webhook_data = request.get_json()
        timestamp = datetime.now().isoformat()
        
        # Log do webhook
        log_entry = {
            'received_at': timestamp,
            'webhook': webhook_data
        }
        webhooks_log.append(log_entry)
        
        # Extrair dados do webhook
        webhook_type = webhook_data.get('webhook_type')
        status = webhook_data.get('status')
        key = webhook_data.get('key')
        data = webhook_data.get('data', {})
        account_request_key = data.get('account_request_key')
        account_info = data.get('account_info', {})
        
        print(f"\n🔔 WEBHOOK ESCROW RECEBIDO")
        print(f"Timestamp: {timestamp}")
        print(f"Type: {webhook_type}")
        print(f"Status: {status}")
        print(f"Key: {key}")
        print(f"Account Request Key: {account_request_key}")
        
        # Processar conforme status
        if webhook_type == 'account_request.status_change':
            
            if status == 'pending_additional_data':
                print(f"✅ CONTA PRONTA PARA CONFIRMAÇÃO!")
                print(f"Agência: {account_info.get('account_branch')}")
                print(f"Conta: {account_info.get('account_number')}")
                print(f"Dígito: {account_info.get('account_digit')}")
                
                # Marcar como pronta para confirmação
                accounts_ready[account_request_key] = {
                    'status': 'ready_for_confirmation',
                    'account_info': account_info,
                    'received_at': timestamp,
                    'webhook_data': webhook_data
                }
                
                # Salvar para processamento posterior
                save_ready_account(account_request_key, accounts_ready[account_request_key])
                
            elif status == 'rejected':
                print(f"❌ CONTA REJEITADA!")
                print(f"Account Request Key: {account_request_key}")
                
                # Marcar como rejeitada
                accounts_ready[account_request_key] = {
                    'status': 'rejected',
                    'account_info': account_info,
                    'received_at': timestamp,
                    'webhook_data': webhook_data
                }
            
            else:
                print(f"ℹ️ Status não processado: {status}")
        
        # Salvar webhook completo
        save_webhook_log(log_entry)
        
        return jsonify({
            'status': 'received',
            'timestamp': timestamp,
            'processed': True
        }), 200
        
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/status/<account_request_key>', methods=['GET'])
def check_account_status(account_request_key):
    """Verifica se conta está pronta para confirmação"""
    
    if account_request_key in accounts_ready:
        account_data = accounts_ready[account_request_key]
        
        return jsonify({
            'account_request_key': account_request_key,
            'status': account_data['status'],
            'ready_for_confirmation': account_data['status'] == 'ready_for_confirmation',
            'account_info': account_data.get('account_info'),
            'received_at': account_data['received_at']
        })
    else:
        return jsonify({
            'account_request_key': account_request_key,
            'status': 'waiting_webhook',
            'ready_for_confirmation': False,
            'message': 'Aguardando webhook pending_additional_data'
        })

@app.route('/webhooks', methods=['GET'])
def list_webhooks():
    """Lista todos os webhooks recebidos"""
    
    return jsonify({
        'total_webhooks': len(webhooks_log),
        'accounts_ready': len([k for k, v in accounts_ready.items() if v['status'] == 'ready_for_confirmation']),
        'accounts_rejected': len([k for k, v in accounts_ready.items() if v['status'] == 'rejected']),
        'recent_webhooks': webhooks_log[-5:],  # Últimos 5
        'ready_accounts': {k: v for k, v in accounts_ready.items() if v['status'] == 'ready_for_confirmation'}
    })

def save_webhook_log(log_entry):
    """Salva webhook em arquivo de log"""
    
    filename = f"webhook_escrow_log_{datetime.now().strftime('%Y%m%d')}.json"
    
    try:
        # Carregar logs existentes
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_logs = json.load(f)
        else:
            existing_logs = []
        
        # Adicionar novo log
        existing_logs.append(log_entry)
        
        # Salvar arquivo
        with open(filename, 'w') as f:
            json.dump(existing_logs, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Erro ao salvar log: {e}")

def save_ready_account(account_request_key, account_data):
    """Salva conta pronta para confirmação"""
    
    filename = "accounts_ready_for_confirmation.json"
    
    try:
        # Carregar contas existentes
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                ready_accounts = json.load(f)
        else:
            ready_accounts = {}
        
        # Adicionar nova conta
        ready_accounts[account_request_key] = account_data
        
        # Salvar arquivo
        with open(filename, 'w') as f:
            json.dump(ready_accounts, f, indent=2)
            
        print(f"💾 Conta salva para confirmação: {account_request_key}")
            
    except Exception as e:
        print(f"⚠️ Erro ao salvar conta: {e}")

if __name__ == "__main__":
    print("🚀 WEBHOOK LISTENER ESCROW")
    print("=" * 40)
    print("URL do webhook: http://localhost:5000/webhook/escrow")
    print("Status das contas: http://localhost:5000/webhooks")
    print("Verificar conta: http://localhost:5000/status/{account_request_key}")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
