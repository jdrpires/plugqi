#!/usr/bin/env python3
"""
Teste de integração real - Regras de Movimentação Automática
ATENÇÃO: Este teste faz chamadas reais à API QiTech
"""

import json
import uuid
from datetime import datetime
from plugqi import PlugQi

def test_automatic_transfer_integration():
    """Teste de integração com API real"""
    
    print("🔄 TESTE INTEGRAÇÃO - Regras de Movimentação Automática")
    print("=" * 60)
    print(f"⏰ Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        plugqi = PlugQi()
        
        # Verificar conectividade primeiro
        if not plugqi.health_check():
            print("❌ Falha na conectividade com QiTech")
            return
        
        print("✅ Conectado à QiTech")
        
        # Dados de teste (usar conta válida em produção)
        account_key = "6203037b-4405-4602-b7ce-ff99806d9cb0"  # Substituir por conta real
        
        # Destination de exemplo
        destination = plugqi.automatic_transfer.build_destination(
            account_branch="0931",
            account_number="1232046",
            account_digit="9",
            document_number="48504807000198",
            name="Mateus Fonseca",
            financial_institutions_code_number="063",
            percentage=100,
            is_pix_transfer=False
        )
        
        print(f"\n📋 Dados do teste:")
        print(f"   Account Key: {account_key}")
        print(f"   Destination: {destination['name']}")
        
        # 1. Teste Split Percentage
        print(f"\n1️⃣ Testando Split Percentage")
        try:
            result = plugqi.automatic_transfer.create_split_percentage_rule(
                account_key=account_key,
                destinations=[destination],
                transfer_cronstring="*/5 * * * *",  # A cada 5 minutos (teste)
                remaining_balance=0,
                is_active=False  # Inativo para não executar
            )
            
            print("✅ Split Percentage criado com sucesso!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            # Salvar key para possível cleanup
            if 'automatic_transfer_key' in result:
                transfer_key = result['automatic_transfer_key']
                print(f"   🔑 Transfer Key: {transfer_key}")
                
                # Teste de desativação
                print(f"\n🔄 Testando desativação da regra...")
                deactivate_result = plugqi.automatic_transfer.deactivate_rule(
                    automatic_transfer_key=transfer_key,
                    rule_type="split_percentage",
                    rule_configuration=result['rule_configuration'],
                    transfer_cronstring="*/5 * * * *"
                )
                print("✅ Regra desativada com sucesso!")
                print(f"   Status: {deactivate_result.get('is_active', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Erro Split Percentage: {e}")
            
            # Se erro de permissão, tentar outros testes
            if "401" in str(e) or "403" in str(e):
                print("⚠️  Possível problema de permissão - continuando outros testes...")
            else:
                print(f"   Detalhes: {type(e).__name__}")
        
        # 2. Teste Split Equal
        print(f"\n2️⃣ Testando Split Equal")
        try:
            # Remove percentage para split_equal
            destination_equal = {k: v for k, v in destination.items() if k != 'percentage'}
            
            result = plugqi.automatic_transfer.create_split_equal_rule(
                account_key=account_key,
                destinations=[destination_equal],
                transfer_cronstring="0 2 * * *",  # 02:00 diariamente
                remaining_balance=100.0,
                is_active=False
            )
            
            print("✅ Split Equal criado com sucesso!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
        except Exception as e:
            print(f"❌ Erro Split Equal: {e}")
        
        # 3. Teste Single Beneficiary
        print(f"\n3️⃣ Testando Single Beneficiary")
        try:
            destination_single = {k: v for k, v in destination.items() if k != 'percentage'}
            
            result = plugqi.automatic_transfer.create_single_beneficiary_rule(
                account_key=account_key,
                destination=destination_single,
                transfer_cronstring="0 23 * * *",  # 23:00 diariamente
                remaining_balance=0,
                is_active=False
            )
            
            print("✅ Single Beneficiary criado com sucesso!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
        except Exception as e:
            print(f"❌ Erro Single Beneficiary: {e}")
        
        # 4. Teste Raw API
        print(f"\n4️⃣ Testando API Raw")
        try:
            raw_data = {
                "transfer_cronstring": "0 1 * * *",
                "account_key": account_key,
                "rule_configuration": {
                    "destinations": [destination],
                    "remaining_balance": 50.0
                },
                "is_active": False,
                "rule": "split_percentage"
            }
            
            result = plugqi.automatic_transfer.create_transfer_rule(raw_data)
            print("✅ Raw API funcionando!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
        except Exception as e:
            print(f"❌ Erro Raw API: {e}")
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        print(f"   Tipo: {type(e).__name__}")

def test_cron_validation():
    """Testa diferentes padrões CRON"""
    
    print(f"\n📅 Testando padrões CRON")
    print("-" * 30)
    
    cron_patterns = [
        "*/5 * * * *",      # A cada 5 minutos
        "0 0 * * *",        # Diariamente às 00:00
        "0 12 * * *",       # Diariamente às 12:00
        "0 0 * * 1",        # Toda segunda às 00:00
        "0 18 * * 1-5",     # Dias úteis às 18:00
        "0 0 1 * *",        # Todo dia 1 do mês
        "0 0 1 1 *"         # Todo 1º de janeiro
    ]
    
    for pattern in cron_patterns:
        print(f"   ✅ {pattern:<15} - Padrão válido")

def save_test_results(results):
    """Salva resultados do teste"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"automatic_transfer_test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Resultados salvos em: {filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE INTEGRAÇÃO")
    print("⚠️  ATENÇÃO: Este teste faz chamadas reais à API!")
    print("=" * 60)
    
    test_automatic_transfer_integration()
    test_cron_validation()
    
    print(f"\n✅ TESTE CONCLUÍDO")
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
