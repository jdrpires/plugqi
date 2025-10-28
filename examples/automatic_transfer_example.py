#!/usr/bin/env python3
"""
Exemplo prático de uso das regras de movimentação automática
"""

from plugqi import PlugQi

def exemplo_split_percentage():
    """Exemplo: Dividir 80% entre 2 contas, deixar 20% na origem"""
    
    plugqi = PlugQi()
    
    # Conta origem
    account_key = "sua-conta-key-aqui"
    
    # Destinos com percentuais
    destinations = [
        plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="123456",
            account_digit="7",
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001",  # Banco do Brasil
            percentage=50  # 50%
        ),
        plugqi.automatic_transfer.build_destination(
            account_branch="0001", 
            account_number="654321",
            account_digit="8",
            document_number="98765432100",
            name="Maria Santos",
            financial_institutions_code_number="341",  # Itaú
            percentage=30  # 30%
        )
    ]
    # Total: 80% transferido, 20% fica na conta origem
    
    try:
        result = plugqi.automatic_transfer.create_split_percentage_rule(
            account_key=account_key,
            destinations=destinations,
            transfer_cronstring="0 18 * * 1-5",  # Dias úteis às 18h
            remaining_balance=100.0,  # Manter R$ 100 sempre na conta
            is_active=True
        )
        print("✅ Regra Split Percentage criada:", result)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exemplo_split_equal():
    """Exemplo: Dividir igualmente entre 3 contas"""
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    
    # 3 destinos - será dividido igualmente (33.33% cada)
    destinations = [
        plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="111111",
            account_digit="1",
            document_number="11111111111",
            name="Conta 1",
            financial_institutions_code_number="001"
        ),
        plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="222222", 
            account_digit="2",
            document_number="22222222222",
            name="Conta 2",
            financial_institutions_code_number="237"  # Bradesco
        ),
        plugqi.automatic_transfer.build_destination(
            account_branch="0001",
            account_number="333333",
            account_digit="3", 
            document_number="33333333333",
            name="Conta 3",
            financial_institutions_code_number="104"  # Caixa
        )
    ]
    
    try:
        result = plugqi.automatic_transfer.create_split_equal_rule(
            account_key=account_key,
            destinations=destinations,
            transfer_cronstring="0 0 * * *",  # Diariamente à meia-noite
            remaining_balance=50.0,  # Manter R$ 50 na conta
            is_active=True
        )
        print("✅ Regra Split Equal criada:", result)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exemplo_single_beneficiary():
    """Exemplo: Transferir tudo para uma única conta"""
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    
    # Um único beneficiário
    destination = plugqi.automatic_transfer.build_destination(
        account_branch="0932",
        account_number="987654",
        account_digit="0",
        document_number="12345678000199",
        name="Empresa Principal LTDA",
        financial_institutions_code_number="033"  # Santander
    )
    
    try:
        result = plugqi.automatic_transfer.create_single_beneficiary_rule(
            account_key=account_key,
            destination=destination,
            transfer_cronstring="0 23 * * *",  # Diariamente às 23h
            remaining_balance=0,  # Transferir tudo
            is_active=True
        )
        print("✅ Regra Single Beneficiary criada:", result)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def exemplo_desativar_regra():
    """Exemplo: Desativar uma regra existente"""
    
    plugqi = PlugQi()
    
    # Key da regra a ser desativada (obtida na criação)
    automatic_transfer_key = "967c40ea-ba35-4445-89b1-fa35bd0749a4"
    
    # Configuração atual da regra (deve ser a mesma)
    rule_configuration = {
        "destination": {
            "account_branch": "0931",
            "account_digit": "9", 
            "account_number": "1232046",
            "document_number": "48504807000198",
            "financial_institutions_code_number": "063",
            "name": "Mateus Fonseca"
        },
        "remaining_balance": 0
    }
    
    try:
        result = plugqi.automatic_transfer.deactivate_rule(
            automatic_transfer_key=automatic_transfer_key,
            rule_type="single_beneficiary",
            rule_configuration=rule_configuration,
            transfer_cronstring="*/5 * * * *"
        )
        print("✅ Regra desativada:", result)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🔄 Exemplos de Regras de Movimentação Automática")
    print("=" * 50)
    
    print("\n1️⃣ Split Percentage (80% dividido, 20% fica)")
    exemplo_split_percentage()
    
    print("\n2️⃣ Split Equal (divisão igualitária entre 3 contas)")
    exemplo_split_equal()
    
    print("\n3️⃣ Single Beneficiary (tudo para uma conta)")
    exemplo_single_beneficiary()
    
    print("\n4️⃣ Desativar regra existente")
    exemplo_desativar_regra()
