#!/usr/bin/env python3
"""
Cria boleto REAL no sandbox QiTech
Usa suas credenciais do .env
"""
import uuid
import json
from datetime import datetime, timedelta
from plugqi import PlugQi
from qitech_client import QiTechError

def main():
    print("🎫 Criando BOLETO REAL no Sandbox QiTech\n")
    
    # Testa conectividade primeiro
    try:
        plugqi = PlugQi()
        health = plugqi.health_check()
        print(f"✅ Conectividade: {'OK' if health else 'FALHOU'}")
        
        if not health:
            print("❌ Verifique suas credenciais no .env")
            return 1
            
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return 1
    
    # Você precisa fornecer estas chaves:
    print("\n⚠️  VOCÊ PRECISA FORNECER:")
    account_key = input("Digite sua ACCOUNT_KEY: ").strip()
    profile_key = input("Digite sua REQUESTER_PROFILE_KEY: ").strip()
    
    if not account_key or not profile_key:
        print("❌ Chaves obrigatórias não fornecidas")
        return 1
    
    # Cria payload do boleto
    boleto_data = {
        "request_control_key": str(uuid.uuid4()),
        "amount": 100.50,
        "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "bank_teller_instructions": "Teste PlugQi - Boleto Real Sandbox",
        "payer_data": {
            "name": "João Silva Teste PlugQi",
            "document_number": "12345678901",
            "person_type": "natural"
        }
    }
    
    print(f"\n📤 Enviando boleto para QiTech...")
    print(f"💰 Valor: R$ {boleto_data['amount']:.2f}")
    print(f"📅 Vencimento: {boleto_data['expiration']}")
    print(f"👤 Pagador: {boleto_data['payer_data']['name']}")
    
    try:
        # Envia para API real
        response = plugqi.boleto.create_boleto(
            account_key=account_key,
            requester_profile_key=profile_key,
            boleto_data=boleto_data
        )
        
        print(f"\n🎉 BOLETO CRIADO COM SUCESSO!")
        print("="*60)
        
        # Dados retornados pela QiTech
        print(f"🔑 Bank Slip Key: {response.get('bank_slip_key')}")
        print(f"📊 Status: {response.get('bank_slip_status')}")
        print(f"🔢 Nosso Número: {response.get('our_number')}")
        
        if response.get('barcode'):
            print(f"📋 Código de Barras: {response['barcode']}")
        
        if response.get('digitable_line'):
            print(f"💳 Linha Digitável: {response['digitable_line']}")
        
        if response.get('qr_code_data'):
            qr_data = response['qr_code_data']
            print(f"📱 QR Code PIX: {qr_data.get('url', 'N/A')}")
        
        print(f"\n📄 RESPOSTA COMPLETA:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Salva resposta em arquivo
        with open("boleto_criado_response.json", "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resposta salva em: boleto_criado_response.json")
        
        return 0
        
    except QiTechError as e:
        print(f"\n❌ ERRO QITECH: {e.status}")
        print(f"📄 Detalhes: {json.dumps(e.payload, indent=2, ensure_ascii=False)}")
        return 1
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
