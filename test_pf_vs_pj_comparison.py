#!/usr/bin/env python3
"""
Comparação direta PF vs PJ para identificar diferença
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_pf_working():
    """PF que sabemos que funciona"""
    
    plugqi = PlugQi()
    
    pf_payload = {
        "account_owner": {
            "document_number": "99999999999",
            "email": "joao@teste.com",
            "birthdate": "1990-01-01",
            "name": "João Silva",
            "documents": {
                "cnh": {
                    "ocr_key": str(uuid.uuid4())
                }
            },
            "face": str(uuid.uuid4())
        }
    }
    
    try:
        print("✅ Testando PF (sabemos que funciona)...")
        response = plugqi.client.post("/account_request/escrow", pf_payload)
        print(f"✅ PF SUCESSO: {response['account_request_key']}")
        return True
        
    except Exception as e:
        print(f"❌ PF falhou: {e}")
        return False

def test_pj_minimal():
    """PJ mais simples possível"""
    
    plugqi = PlugQi()
    
    pj_minimal = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "empresa@teste.com",
            "foundation_date": "2020-01-01", 
            "name": "Empresa Teste"
        }
    }
    
    try:
        print("\n🧪 Testando PJ mínimo...")
        response = plugqi.client.post("/account_request/escrow", pj_minimal)
        print(f"✅ PJ MÍNIMO SUCESSO: {response['account_request_key']}")
        return True
        
    except Exception as e:
        print(f"❌ PJ mínimo falhou: {str(e)[:100]}...")
        return False

def test_different_endpoint():
    """Teste se PJ usa endpoint diferente"""
    
    plugqi = PlugQi()
    
    pj_payload = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "empresa@teste.com",
            "foundation_date": "2020-01-01",
            "name": "Empresa Teste"
        }
    }
    
    endpoints = [
        "/account_request/escrow/legal",
        "/account_request/escrow/company", 
        "/account_request/company",
        "/account_request/legal_entity"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🧪 Testando endpoint: {endpoint}")
            response = plugqi.client.post(endpoint, pj_payload)
            print(f"✅ SUCESSO no endpoint: {endpoint}")
            print(f"Response: {response}")
            return True
            
        except Exception as e:
            status = getattr(e, 'status', 'unknown')
            if status == 404:
                print(f"   {endpoint}: Não existe")
            elif status == 400:
                print(f"   {endpoint}: Schema inválido")
            elif status == 401:
                print(f"   {endpoint}: Não autorizado")
            else:
                print(f"   {endpoint}: Erro {status}")
    
    return False

def analyze_difference():
    """Analisa diferenças entre PF e PJ"""
    
    print("\n🔍 ANÁLISE PF vs PJ:")
    print("=" * 40)
    print("PF FUNCIONA:")
    print("- document_number (CPF)")
    print("- birthdate")
    print("- Estrutura simples")
    print()
    print("PJ NÃO FUNCIONA:")
    print("- company_document_number (CNPJ)")
    print("- foundation_date")
    print("- legal_representatives")
    print()
    print("💡 HIPÓTESES:")
    print("1. PJ pode estar desabilitado no sandbox")
    print("2. PJ pode precisar de endpoint específico")
    print("3. Documentação pode estar desatualizada")

if __name__ == "__main__":
    print("🔬 COMPARAÇÃO PF vs PJ")
    print("=" * 50)
    
    pf_works = test_pf_working()
    pj_minimal_works = test_pj_minimal()
    endpoint_works = test_different_endpoint()
    
    print(f"\n📊 RESULTADOS:")
    print(f"PF funciona: {'✅' if pf_works else '❌'}")
    print(f"PJ mínimo: {'✅' if pj_minimal_works else '❌'}")
    print(f"Endpoints alternativos: {'✅' if endpoint_works else '❌'}")
    
    if not (pj_minimal_works or endpoint_works):
        analyze_difference()
        
        print("\n📋 CONCLUSÃO:")
        print("- PF Escrow: FUNCIONANDO ✅")
        print("- PJ Escrow: PROBLEMA NO SCHEMA ❌")
        print("- Recomendação: Confirmar com QiTech se PJ está habilitado")
