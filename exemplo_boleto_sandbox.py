#!/usr/bin/env python3
"""
EXEMPLO PRÁTICO - Como criar boleto no sandbox
SUBSTITUA AS CHAVES PELAS SUAS ANTES DE EXECUTAR
"""
import uuid
import json
from datetime import datetime, timedelta
from plugqi import PlugQi

# ⚠️ SUBSTITUA ESTAS CHAVES PELAS SUAS:
ACCOUNT_KEY = "12345678-1234-1234-1234-123456789012"  # Sua account_key
PROFILE_KEY = "87654321-4321-4321-4321-210987654321"  # Sua requester_profile_key

def criar_boleto_sandbox():
    """Cria boleto real no sandbox"""
    print("🎫 Criando boleto no sandbox QiTech...")
    
    # Inicializa PlugQi
    plugqi = PlugQi()
    
    # Payload do boleto
    boleto_payload = {
        "request_control_key": str(uuid.uuid4()),
        "amount": 150.75,
        "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "bank_teller_instructions": "Pagamento teste PlugQi - Sandbox",
        "payer_data": {
            "name": "João Silva Teste",
            "document_number": "12345678901",
            "person_type": "natural"
        }
    }
    
    print("📤 Payload enviado:")
    print(json.dumps(boleto_payload, indent=2, ensure_ascii=False))
    print("\n" + "="*60)
    
    try:
        # Chama API real
        response = plugqi.boleto.create_boleto(
            account_key=ACCOUNT_KEY,
            requester_profile_key=PROFILE_KEY,
            boleto_data=boleto_payload
        )
        
        print("📥 RESPOSTA DA QITECH:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Dados do boleto criado
        print(f"\n🎉 BOLETO CRIADO!")
        print(f"🔑 Bank Slip Key: {response.get('bank_slip_key')}")
        print(f"📊 Status: {response.get('bank_slip_status')}")
        print(f"🔢 Nosso Número: {response.get('our_number')}")
        print(f"📋 Código de Barras: {response.get('barcode')}")
        print(f"💳 Linha Digitável: {response.get('digitable_line')}")
        
        return response
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

if __name__ == "__main__":
    print("🚀 EXEMPLO - Boleto Real no Sandbox\n")
    print("⚠️  ANTES DE EXECUTAR:")
    print("1. Configure suas credenciais no .env")
    print("2. Substitua ACCOUNT_KEY e PROFILE_KEY no código")
    print("3. Execute: python3 exemplo_boleto_sandbox.py\n")
    
    # Verifica se as chaves foram alteradas
    if "12345678-1234" in ACCOUNT_KEY:
        print("❌ ERRO: Substitua ACCOUNT_KEY pela sua chave real!")
        print("❌ ERRO: Substitua PROFILE_KEY pela sua chave real!")
        exit(1)
    
    criar_boleto_sandbox()
