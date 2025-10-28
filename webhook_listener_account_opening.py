#!/usr/bin/env python3

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Armazenar webhooks recebidos
webhooks_received = []

@app.route('/webhook/account_opening', methods=['POST'])
def handle_account_opening_webhook():
    """Receber webhooks de abertura de conta"""
    
    try:
        webhook_data = request.get_json()
        
        # Log do webhook recebido
        timestamp = datetime.now().isoformat()
        webhook_entry = {
            "timestamp": timestamp,
            "data": webhook_data
        }
        
        webhooks_received.append(webhook_entry)
        
        print(f"\n🔔 WEBHOOK RECEBIDO - {timestamp}")
        print("=" * 50)
        print(json.dumps(webhook_data, indent=2, ensure_ascii=False))
        
        # Verificar se é o webhook que esperamos
        if webhook_data.get('webhook_type') == 'account_request.status_change':
            status = webhook_data.get('status')
            account_request_key = webhook_data.get('data', {}).get('account_request_key')
            
            print(f"\n📊 STATUS: {status}")
            print(f"🔑 ACCOUNT_REQUEST_KEY: {account_request_key}")
            
            if status == 'pending_additional_data':
                print("✅ PRONTO PARA CONFIRMAÇÃO!")
                
                # Salvar dados para confirmação
                confirmation_data = {
                    "account_request_key": account_request_key,
                    "account_info": webhook_data.get('data', {}).get('account_info'),
                    "ready_for_confirmation": True,
                    "timestamp": timestamp
                }
                
                with open('account_ready_for_confirmation.json', 'w') as f:
                    json.dump(confirmation_data, f, indent=2, ensure_ascii=False)
                
                print("💾 Dados salvos em: account_ready_for_confirmation.json")
            
            elif status == 'rejected':
                print("❌ CONTA REJEITADA!")
        
        # Salvar histórico completo
        with open('webhooks_account_opening.json', 'w') as f:
            json.dump(webhooks_received, f, indent=2, ensure_ascii=False)
        
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    """Status dos webhooks recebidos"""
    return jsonify({
        "total_webhooks": len(webhooks_received),
        "last_webhook": webhooks_received[-1] if webhooks_received else None
    })

@app.route('/webhook/clear', methods=['POST'])
def clear_webhooks():
    """Limpar histórico de webhooks"""
    global webhooks_received
    webhooks_received = []
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    print("🔔 WEBHOOK LISTENER - ABERTURA DE CONTA")
    print("=" * 50)
    print("📡 Endpoint: http://localhost:5000/webhook/account_opening")
    print("📊 Status: http://localhost:5000/webhook/status")
    print("🧹 Clear: POST http://localhost:5000/webhook/clear")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
