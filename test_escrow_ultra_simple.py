#!/usr/bin/env python3
"""
Teste ultra-simples para identificar o schema correto da conta Escrow
"""

import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_minimal_schemas():
    """Testa diferentes schemas mínimos"""
    
    plugqi = PlugQi()
    
    # Schema 1: Apenas account_owner básico
    schema1 = {
        "account_owner": {
            "company_document_number": "12345678000195",
            "name": "Empresa Teste LTDA"
        }
    }
    
    # Schema 2: Com signed_contract vazio
    schema2 = {
        "account_owner": {
            "company_document_number": "12345678000195", 
            "name": "Empresa Teste LTDA"
        },
        "signed_contract": {}
    }
    
    # Schema 3: Com destinations vazio
    schema3 = {
        "account_owner": {
            "company_document_number": "12345678000195",
            "name": "Empresa Teste LTDA"
        },
        "signed_contract": {},
        "destinations": []
    }
    
    # Schema 4: Baseado em outros endpoints QiTech
    schema4 = {
        "requester_profile_key": str(uuid.uuid4()),
        "account_owner": {
            "company_document_number": "12345678000195",
            "name": "Empresa Teste LTDA",
            "person_type": "legal"
        }
    }
    
    schemas = [
        ("Schema 1 - Básico", schema1),
        ("Schema 2 - Com signed_contract", schema2), 
        ("Schema 3 - Com destinations", schema3),
        ("Schema 4 - Com requester_profile_key", schema4)
    ]
    
    for name, schema in schemas:
        try:
            print(f"\n🧪 Testando {name}...")
            print(f"Payload: {schema}")
            
            response = plugqi.client.post("/account_request/escrow", schema)
            print(f"✅ {name} - SUCESSO!")
            print(f"Response: {response}")
            return True
            
        except Exception as e:
            print(f"❌ {name} - Erro: {str(e)[:200]}...")
            if hasattr(e, 'payload') and e.payload:
                error_msg = e.payload.get('description', '')
                if 'required' in error_msg.lower():
                    print(f"   Campo obrigatório detectado!")
    
    return False

def test_get_schema_info():
    """Tenta obter informações do schema via outros endpoints"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🔍 Tentando GET no endpoint para ver schema...")
        response = plugqi.client.get("/account_request/escrow")
        print(f"GET Response: {response}")
        
    except Exception as e:
        print(f"GET Error: {e}")
        
    try:
        print("\n🔍 Tentando listar account_requests...")
        response = plugqi.client.get("/account_request")
        print(f"List Response: {response}")
        
    except Exception as e:
        print(f"List Error: {e}")

if __name__ == "__main__":
    print("🔬 ANÁLISE DE SCHEMA - CONTA ESCROW")
    print("=" * 50)
    
    # Teste schemas
    success = test_minimal_schemas()
    
    if not success:
        # Tenta obter info do schema
        test_get_schema_info()
