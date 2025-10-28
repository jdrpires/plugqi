#!/usr/bin/env python3
"""
Teste PJ Escrow com schema EXATO da documentação QiTech
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_pj_exact_schema():
    """Teste com schema EXATO da documentação"""
    
    plugqi = PlugQi()
    
    # Schema EXATO da documentação QiTech
    exact_payload = {
        "account_owner": {
            "company_document_number": "99999999999",  # Mock aprovação
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
                    "cnh": {
                        "ocr_key": str(uuid.uuid4())
                    }
                },
                "face": str(uuid.uuid4())
            }
        ]
    }
    
    try:
        print("🧪 Testando PJ com schema EXATO da documentação...")
        print(f"Payload: {exact_payload}")
        
        response = plugqi.client.post("/account_request/escrow", exact_payload)
        
        print("✅ SUCESSO! PJ Escrow criada!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        if hasattr(e, 'payload'):
            error_detail = e.payload.get('description', '')
            print(f"Erro detalhado: {error_detail}")
            
            # Analisar erro específico
            if 'required' in error_detail.lower():
                print("🔍 Campo obrigatório faltando")
            if 'invalid' in error_detail.lower():
                print("🔍 Campo com valor inválido")
                
        return False

def test_without_face():
    """Teste sem campo face (opcional na doc)"""
    
    plugqi = PlugQi()
    
    payload_no_face = {
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
                "documents": {
                    "cnh": {
                        "ocr_key": str(uuid.uuid4())
                    }
                }
                # SEM campo face
            }
        ]
    }
    
    try:
        print("\n🧪 Testando PJ sem campo 'face'...")
        response = plugqi.client.post("/account_request/escrow", payload_no_face)
        print("✅ SUCESSO sem face!")
        return True
        
    except Exception as e:
        print(f"❌ Falhou sem face: {str(e)[:100]}...")
        return False

def test_minimal_pj():
    """Teste PJ sem legal_representatives"""
    
    plugqi = PlugQi()
    
    minimal_pj = {
        "account_owner": {
            "company_document_number": "99999999999",
            "email": "email@teste.com",
            "foundation_date": "2020-01-01", 
            "name": "Nome da Empresa"
        }
        # SEM legal_representatives
    }
    
    try:
        print("\n🧪 Testando PJ sem legal_representatives...")
        response = plugqi.client.post("/account_request/escrow", minimal_pj)
        print("✅ SUCESSO PJ mínimo!")
        return True
        
    except Exception as e:
        print(f"❌ PJ mínimo falhou: {str(e)[:100]}...")
        return False

if __name__ == "__main__":
    print("🔧 AJUSTE ESCROW PJ - SCHEMA EXATO")
    print("=" * 50)
    
    # Teste 1: Schema exato
    success1 = test_pj_exact_schema()
    
    # Teste 2: Sem face
    success2 = test_without_face()
    
    # Teste 3: Mínimo
    success3 = test_minimal_pj()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Schema exato: {'✅' if success1 else '❌'}")
    print(f"Sem face: {'✅' if success2 else '❌'}")
    print(f"PJ mínimo: {'✅' if success3 else '❌'}")
    
    if success1 or success2 or success3:
        print("\n🎉 ENCONTRAMOS O SCHEMA CORRETO!")
    else:
        print("\n🔍 Ainda precisamos ajustar o schema")
