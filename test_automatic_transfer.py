#!/usr/bin/env python3
"""
Teste das regras de movimentação automática
"""

import json
from plugqi import PlugQi

def test_automatic_transfer_rules():
    """Testa criação de regras de movimentação automática"""
    
    plugqi = PlugQi()
    
    # Dados de exemplo para testes
    account_key = "6203037b-4405-4602-b7ce-ff99806d9cb0"
    
    # Destination de exemplo
    destination_data = {
        "account_branch": "0931",
        "account_number": "1232046", 
        "account_digit": "9",
        "document_number": "48504807000198",
        "name": "Mateus Fonseca",
        "financial_institutions_code_number": "063"
    }
    
    print("🔄 Testando Regras de Movimentação Automática")
    print("=" * 50)
    
    # 1. Teste Split Percentage
    print("\n1️⃣ Testando Split Percentage")
    try:
        # Adiciona percentage para split_percentage
        destination_percentage = destination_data.copy()
        destination_percentage["percentage"] = 100
        destination_percentage["is_pix_transfer"] = False
        
        result = plugqi.automatic_transfer.create_split_percentage_rule(
            account_key=account_key,
            destinations=[destination_percentage],
            transfer_cronstring="*/5 * * * *",  # A cada 5 minutos
            remaining_balance=0,
            is_active=True
        )
        print(f"✅ Split Percentage: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erro Split Percentage: {e}")
    
    # 2. Teste Split Equal
    print("\n2️⃣ Testando Split Equal")
    try:
        result = plugqi.automatic_transfer.create_split_equal_rule(
            account_key=account_key,
            destinations=[destination_data],
            transfer_cronstring="*/5 * * * *",
            remaining_balance=0,
            is_active=True
        )
        print(f"✅ Split Equal: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erro Split Equal: {e}")
    
    # 3. Teste Single Beneficiary
    print("\n3️⃣ Testando Single Beneficiary")
    try:
        result = plugqi.automatic_transfer.create_single_beneficiary_rule(
            account_key=account_key,
            destination=destination_data,
            transfer_cronstring="*/5 * * * *",
            remaining_balance=0,
            is_active=False  # Inativo por padrão
        )
        print(f"✅ Single Beneficiary: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erro Single Beneficiary: {e}")
    
    # 4. Teste Helper build_destination
    print("\n4️⃣ Testando Helper build_destination")
    try:
        destination = plugqi.automatic_transfer.build_destination(
            account_branch="0931",
            account_number="1232046",
            account_digit="9", 
            document_number="48504807000198",
            name="Mateus Fonseca",
            financial_institutions_code_number="063",
            percentage=50,
            is_pix_transfer=True
        )
        print(f"✅ Destination Helper: {json.dumps(destination, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erro Destination Helper: {e}")
    
    # 5. Teste Raw API
    print("\n5️⃣ Testando API Raw")
    try:
        raw_data = {
            "transfer_cronstring": "*/5 * * * *",
            "account_key": account_key,
            "rule_configuration": {
                "destinations": [destination_percentage],
                "remaining_balance": 0
            },
            "is_active": True,
            "rule": "split_percentage"
        }
        
        result = plugqi.automatic_transfer.create_transfer_rule(raw_data)
        print(f"✅ Raw API: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erro Raw API: {e}")

def test_cron_examples():
    """Exemplos de CRON strings"""
    
    print("\n📅 Exemplos de CRON Strings")
    print("=" * 30)
    
    cron_examples = {
        "*/5 * * * *": "A cada 5 minutos",
        "0 0 * * *": "Diariamente às 00:00",
        "0 12 * * *": "Diariamente às 12:00", 
        "0 0 * * 1": "Toda segunda-feira às 00:00",
        "0 0 1 * *": "Todo dia 1 do mês às 00:00",
        "0 18 * * 1-5": "Dias úteis às 18:00"
    }
    
    for cron, description in cron_examples.items():
        print(f"  {cron:<12} → {description}")

if __name__ == "__main__":
    test_automatic_transfer_rules()
    test_cron_examples()
