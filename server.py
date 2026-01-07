#!/usr/bin/env python3
from flask import Flask, jsonify, request
from plugqi import PlugQi

app = Flask(__name__)
plugqi = PlugQi()

@app.route('/health')
def health():
    return jsonify({"status": "ok", "qitech_connected": plugqi.health_check()})

@app.route('/boleto/create', methods=['POST'])
def create_boleto():
    # Implementar criação de boleto
    return jsonify({"message": "Endpoint para criar boleto"})


@app.route('/__generate_auth', methods=['POST'])
def generate_auth():
    """Gerar headers AUTHORIZATION + API-CLIENT-KEY para uso em Postman/local.

    Payload esperado (JSON): {"method": "POST", "endpoint": "/account/{account_key}/boleto/{profile}", "body": {...}}
    Retorna: {"headers": {"AUTHORIZATION": "...", "API-CLIENT-KEY": "...", ...}}
    """
    try:
        payload = request.get_json(silent=True) or {}
        method = payload.get('method', 'GET')
        endpoint = payload.get('endpoint', '/')
        body = payload.get('body')
        params = payload.get('params')

        headers = plugqi.client.auth_headers_for(method, endpoint, json_body=body, params=params)
        return jsonify({"headers": headers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Servidor PlugQi iniciando...")
    app.run(host='0.0.0.0', port=5000, debug=True)
