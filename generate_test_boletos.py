#!/usr/bin/env python3
"""
Gerador de Boletos de Teste para QA
Gera diferentes cenários de boletos para testes
"""
import uuid
import json
from datetime import datetime, timedelta
from plugqi import PlugQi

def generate_boleto_pessoa_fisica():
    """Boleto para pessoa física - cenário básico"""
    plugqi = PlugQi()
    
    return plugqi.boleto.build_simple_boleto(
        request_control_key=str(uuid.uuid4()),
        amount=150.75,
        expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        payer_name="João Silva Santos",
        payer_document="12345678901",
        bank_teller_instructions="Pagamento da fatura 001 - Não receber após vencimento"
    )

def generate_boleto_pessoa_juridica():
    """Boleto para pessoa jurídica com multa e juros"""
    plugqi = PlugQi()
    
    payer_data = plugqi.boleto.build_payer_data(
        name="Empresa XYZ Tecnologia Ltda",
        document="12345678000195",
        person_type="legal",
        email="financeiro@empresa.com"
    )
    
    return {
        "request_control_key": str(uuid.uuid4()),
        "amount": 2500.00,
        "expiration": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        "bank_teller_instructions": "Pagamento de serviços de consultoria - Ref: Contrato 2024/001",
        "payer_data": payer_data,
        "fine_data": {
            "fine_type": "percentage",
            "fine_percentage": 2,
            "days_to_fine": 1
        },
        "interest_data": {
            "interest_type": "calendar_days_monthly_percentage",
            "interest_percentage": 1,
            "days_to_interest": 1
        }
    }

def generate_boleto_com_desconto():
    """Boleto com desconto por antecipação"""
    plugqi = PlugQi()
    
    return {
        "request_control_key": str(uuid.uuid4()),
        "amount": 1000.00,
        "expiration": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        "bank_teller_instructions": "Pagamento com desconto para antecipação",
        "payer_data": plugqi.boleto.build_payer_data(
            name="Maria Oliveira Costa",
            document="98765432100",
            email="maria@email.com"
        ),
        "discounts_data": [
            {
                "discount_number": 1,
                "discount_type": "percentage",
                "discount_percentage": 5.0,
                "discount_limit_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            }
        ]
    }

def generate_boleto_valor_alto():
    """Boleto de valor alto para testes de limite"""
    plugqi = PlugQi()
    
    return {
        "request_control_key": str(uuid.uuid4()),
        "amount": 50000.00,
        "expiration": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "bank_teller_instructions": "Pagamento de equipamentos - Pedido 12345",
        "payer_data": plugqi.boleto.build_payer_data(
            name="Indústria ABC S.A.",
            document="11222333000144",
            person_type="legal"
        ),
        "protest_data": {
            "days_to_protest": 10
        }
    }

def generate_boleto_vencimento_curto():
    """Boleto com vencimento em 7 dias"""
    plugqi = PlugQi()
    
    return plugqi.boleto.build_simple_boleto(
        request_control_key=str(uuid.uuid4()),
        amount=89.90,
        expiration=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        payer_name="Carlos Eduardo Lima",
        payer_document="55566677788",
        bank_teller_instructions="Pagamento urgente - Vence em 7 dias"
    )

def generate_boleto_cartao_credito():
    """Boleto tipo cartão de crédito (pagamento parcial)"""
    plugqi = PlugQi()
    
    return {
        "request_control_key": str(uuid.uuid4()),
        "amount": 0.00,  # Cartão de crédito pode ter valor zero
        "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "financial_instrument_type": "credit_card",
        "bank_teller_instructions": "Fatura do cartão de crédito",
        "payer_data": plugqi.boleto.build_payer_data(
            name="Ana Paula Ferreira",
            document="11122233344"
        ),
        "partial_payment_data": {
            "partial_payment_minimum_type": "percentage",
            "partial_payment_minimum_percentage": 10.0,
            "partial_payment_maximum_type": "percentage", 
            "partial_payment_maximum_percentage": 100.0,
            "partial_payment_quantity": 12
        }
    }

def main():
    """Gera todos os boletos de teste"""
    print("🎫 Gerando Boletos de Teste para QA\n")
    
    test_cases = [
        ("Pessoa Física Básico", generate_boleto_pessoa_fisica),
        ("Pessoa Jurídica c/ Multa/Juros", generate_boleto_pessoa_juridica),
        ("Com Desconto", generate_boleto_com_desconto),
        ("Valor Alto", generate_boleto_valor_alto),
        ("Vencimento Curto", generate_boleto_vencimento_curto),
        ("Cartão de Crédito", generate_boleto_cartao_credito)
    ]
    
    boletos = {}
    
    for name, generator in test_cases:
        try:
            boleto = generator()
            boletos[name] = boleto
            
            # Info resumida
            amount = boleto.get("amount", 0)
            payer = boleto.get("payer_data", {}).get("name", "N/A")
            expiration = boleto.get("expiration", "N/A")
            
            print(f"✅ {name}")
            print(f"   💰 Valor: R$ {amount:.2f}")
            print(f"   👤 Pagador: {payer}")
            print(f"   📅 Vencimento: {expiration}")
            print()
            
        except Exception as e:
            print(f"❌ Erro em {name}: {e}")
    
    # Salva em arquivo JSON
    with open("boletos_teste_qa.json", "w", encoding="utf-8") as f:
        json.dump(boletos, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Arquivo gerado: boletos_teste_qa.json")
    print(f"📊 Total: {len(boletos)} cenários de teste")
    
    # Resumo para QA
    print("\n" + "="*50)
    print("📋 RESUMO PARA QA")
    print("="*50)
    print("Cenários de teste disponíveis:")
    for i, (name, _) in enumerate(test_cases, 1):
        print(f"{i}. {name}")
    
    print(f"\n🔧 Como usar:")
    print(f"1. Carregue o arquivo: boletos_teste_qa.json")
    print(f"2. Use os payloads para testar a API")
    print(f"3. Substitua account_key e requester_profile_key")
    
    return boletos

if __name__ == "__main__":
    boletos = main()
