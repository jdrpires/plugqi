#!/usr/bin/env python3
from flask import Flask, jsonify
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

if __name__ == '__main__':
    print("🚀 Servidor PlugQi iniciando...")
    app.run(host='0.0.0.0', port=5000, debug=True)
