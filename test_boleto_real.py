#!/usr/bin/env python3
"""
Teste REAL de boleto no sandbox QiTech
Envia payload e retorna código de barras + linha digitável
"""
import uuid
import json
from datetime import datetime, timedelta
from plugqi import PlugQi
from qitech_client import QiTechError

def test_create_real_boleto():
    """Cria boleto real no sandbox QiTech"""
    print("🎫 Criando boleto REAL no sandbox QiTech...\n")
    
    try:
        # Inicializa PlugQi (usa credenciais do .env)
        plugqi = PlugQi()
        
        # SUBSTITUA ESTAS CHAVES PELAS SUAS:
        account_key = "SUA_ACCOUNT_KEY_AQUI"  # Substitua pela sua account_key
        requester_profile_key = "SUA_PROFILE_KEY_AQUI"  # Substitua pela sua profile_key
        
        # Cria payload do boleto
        boleto_data = plugqi.boleto.build_simple_boleto(
            request_control_key=str(uuid.uuid4()),
            amount=100.50,
            expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            payer_name="João Silva Teste",
            payer_document="12345678901",
            bank_teller_instructions="Teste de integração PlugQi - Sandbox"
        )
        
        print("📤 Enviando payload para QiTech:")
        print(json.dumps(boleto_data, indent=2, ensure_ascii=False))
        print("\n" + "="*50)
        
        # Envia para API real
        response = plugqi.boleto.create_boleto(
            account_key=account_key,
            requester_profile_key=requester_profile_key,
            boleto_data=boleto_data
        )
        
        print("📥 RESPOSTA DA QITECH:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        
        # Extrai dados importantes
        if "bank_slip_key" in response:
            print(f"\n✅ Boleto criado com sucesso!")
            print(f"🔑 Chave do boleto: {response['bank_slip_key']}")
            print(f"📊 Status: {response.get('bank_slip_status', 'N/A')}")
            print(f"🔢 Nosso número: {response.get('our_number', 'N/A')}")
            
            if "barcode" in response:
                print(f"📋 Código de barras: {response['barcode']}")
            
            if "digitable_line" in response:
                print(f"💳 Linha digitável: {response['digitable_line']}")
            
            # Se tem QR Code (bolePix)
            if "qr_code_data" in response:
                qr_data = response["qr_code_data"]
                print(f"📱 QR Code PIX: {qr_data.get('url', 'N/A')}")
        
        return response
        
    except QiTechError as e:
        print(f"❌ Erro QiTech: {e.status}")
        print(f"📄 Detalhes: {e.payload}")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def test_get_boleto_details(account_key, bank_slip_key):
    """Consulta detalhes do boleto criado"""
    print(f"\n🔍 Consultando boleto: {bank_slip_key}")
    
    try:
        plugqi = PlugQi()
        
        details = plugqi.boleto.get_boleto(account_key, bank_slip_key)
        
        print("📋 DETALHES DO BOLETO:")
        print(json.dumps(details, indent=2, ensure_ascii=False))
        
        return details
        
    except Exception as e:
        print(f"❌ Erro ao consultar: {e}")
        return None

def main():
    """Executa teste completo"""
    print("🚀 TESTE REAL - Boleto no Sandbox QiTech\n")
    
    # Verifica se tem credenciais
    try:
        plugqi = PlugQi()
        health = plugqi.health_check()
        if not health:
            print("❌ Falha no health check - verifique credenciais no .env")
            return 1
        print("✅ Conectividade OK\n")
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        print("💡 Configure QITECH_CLIENT_KEY e QITECH_PRIVATE_KEY_PATH no .env")
        return 1
    
    # IMPORTANTE: Configure suas chaves aqui
    print("⚠️  ATENÇÃO: Configure suas chaves no código:")
    print("   - account_key = 'SUA_ACCOUNT_KEY'")
    print("   - requester_profile_key = 'SUA_PROFILE_KEY'")
    print()
    
    # Cria boleto
    response = test_create_real_boleto()
    
    if response and "bank_slip_key" in response:
        # Consulta detalhes (opcional)
        account_key = "SUA_ACCOUNT_KEY_AQUI"  # Mesma chave usada acima
        test_get_boleto_details(account_key, response["bank_slip_key"])
    
    return 0 if response else 1

if __name__ == "__main__":
    exit(main())
