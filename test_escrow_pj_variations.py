#!/usr/bin/env python3
"""
Teste variações específicas do schema PJ baseado na documentação
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_variation_1():
    """Variação 1: Exatamente como no exemplo da doc"""
    
    plugqi = PlugQi()
    
    payload = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "email@teste.com",
            "foundation_date": "2017-09-16",  # Data do exemplo
            "name": "Nome da Empresa"
        },
        "legal_representatives": [
            {
                "birthdate": "1963-07-23",  # Data do exemplo
                "name": "Don Corleone",     # Nome do exemplo
                "document_number": "03912394323",  # CPF do exemplo
                "documents": {
                    "national_registry_of_foreigners": {  # RNE como no exemplo
                        "ocr_front_key": str(uuid.uuid4()),
                        "ocr_back_key": str(uuid.uuid4())
                    }
                },
                "face": str(uuid.uuid4())
            },
            {
                "birthdate": "1996-03-10",  # Segundo representante
                "name": "John Doe",
                "document_number": "39113492093",
                "documents": {
                    "cnh": {
                        "ocr_key": str(uuid.uuid4())
                    }
                }
                # Sem face no segundo (como no exemplo)
            }
        ]
    }
    
    try:
        print("🧪 Variação 1: Exemplo exato da documentação...")
        response = plugqi.client.post("/account_request/escrow", payload)
        print("✅ SUCESSO Variação 1!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Variação 1 falhou: {str(e)[:150]}...")
        return False

def test_variation_2():
    """Variação 2: CNPJ com 14 dígitos"""
    
    plugqi = PlugQi()
    
    payload = {
        "account_owner": {
            "company_document_number": "99999999000199",  # 14 dígitos
            "email": "email@teste.com",
            "foundation_date": "2020-01-01",
            "name": "Nome da Empresa"
        },
        "legal_representatives": [
            {
                "birthdate": "1990-01-01",
                "name": "João Silva",
                "document_number": "12345678901",
                "documents": {
                    "rg": {  # RG em vez de CNH
                        "ocr_front_key": str(uuid.uuid4()),
                        "ocr_back_key": str(uuid.uuid4())
                    }
                },
                "face": str(uuid.uuid4())
            }
        ]
    }
    
    try:
        print("\n🧪 Variação 2: CNPJ 14 dígitos + RG...")
        response = plugqi.client.post("/account_request/escrow", payload)
        print("✅ SUCESSO Variação 2!")
        return True
        
    except Exception as e:
        print(f"❌ Variação 2 falhou: {str(e)[:150]}...")
        return False

def test_variation_3():
    """Variação 3: Sem documents, só face"""
    
    plugqi = PlugQi()
    
    payload = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "email@teste.com",
            "foundation_date": "2020-01-01",
            "name": "Nome da Empresa"
        },
        "legal_representatives": [
            {
                "birthdate": "1990-01-01",
                "name": "João Silva", 
                "document_number": "12345678901",
                "face": str(uuid.uuid4())
                # SEM documents
            }
        ]
    }
    
    try:
        print("\n🧪 Variação 3: Sem documents, só face...")
        response = plugqi.client.post("/account_request/escrow", payload)
        print("✅ SUCESSO Variação 3!")
        return True
        
    except Exception as e:
        print(f"❌ Variação 3 falhou: {str(e)[:150]}...")
        return False

def analyze_error_pattern():
    """Analisa padrão dos erros para identificar problema"""
    
    print("\n🔍 ANÁLISE DOS ERROS:")
    print("=" * 40)
    print("- Todos retornam 'not valid under any of the given schemas'")
    print("- PF funciona, PJ não funciona")
    print("- Pode ser que PJ tenha schema diferente ou endpoint diferente")
    print("\n💡 HIPÓTESES:")
    print("1. PJ pode precisar de endpoint diferente")
    print("2. PJ pode ter campos obrigatórios não documentados")
    print("3. PJ pode estar desabilitado no sandbox")

if __name__ == "__main__":
    print("🔬 VARIAÇÕES SCHEMA PJ ESCROW")
    print("=" * 50)
    
    success1 = test_variation_1()
    success2 = test_variation_2() 
    success3 = test_variation_3()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Exemplo exato doc: {'✅' if success1 else '❌'}")
    print(f"CNPJ 14 + RG: {'✅' if success2 else '❌'}")
    print(f"Só face: {'✅' if success3 else '❌'}")
    
    if not (success1 or success2 or success3):
        analyze_error_pattern()
        
        print("\n📋 RECOMENDAÇÃO:")
        print("- Confirmar com QiTech se PJ Escrow está habilitado")
        print("- Solicitar exemplo real de payload PJ funcionando")
        print("- Por enquanto, usar apenas PF Escrow que está funcionando")
