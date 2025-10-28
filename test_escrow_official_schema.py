#!/usr/bin/env python3
"""
Teste com payload baseado na documentação oficial QiTech para conta Escrow
"""

import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_official_schema():
    """Teste com schema baseado na documentação oficial QiTech"""
    
    plugqi = PlugQi()
    
    # Payload baseado na documentação oficial QiTech
    official_payload = {
        "account_owner": {
            "person_type": "legal",
            "company_document_number": "12345678000195",
            "name": "Empresa Teste LTDA",
            "trading_name": "Empresa Teste",
            "email": "empresa@teste.com",
            "phone": {
                "country_code": "55",
                "area_code": "11",
                "number": "999999999"
            },
            "address": {
                "street": "Rua Teste",
                "number": "123",
                "neighborhood": "Centro",
                "city": "São Paulo",
                "state": "SP",
                "postal_code": "01234567"
            },
            "company_type": "ltda",
            "foundation_date": "2020-01-01",
            "cnae_code": "6201501",
            "company_representatives": [
                {
                    "name": "João Silva",
                    "individual_document_number": "12345678901",
                    "person_type": "natural",
                    "birth_date": "1990-01-01",
                    "mother_name": "Maria Silva",
                    "email": "joao@teste.com",
                    "phone": {
                        "country_code": "55",
                        "area_code": "11",
                        "number": "999999999"
                    },
                    "address": {
                        "street": "Rua Teste",
                        "number": "123",
                        "neighborhood": "Centro",
                        "city": "São Paulo",
                        "state": "SP",
                        "postal_code": "01234567"
                    },
                    "nationality": "Brasileira",
                    "marital_status": "single",
                    "is_pep": False
                }
            ]
        },
        "signed_contract": {
            "document_key": str(uuid.uuid4()),
            "signatures": [
                {
                    "signer": {
                        "name": "João Silva",
                        "email": "joao@teste.com",
                        "document_number": "12345678901",
                        "phone": {
                            "country_code": "55",
                            "area_code": "11",
                            "number": "999999999"
                        }
                    },
                    "authenticity": {
                        "timestamp": datetime.now().isoformat(),
                        "facial_recognition_key": str(uuid.uuid4()),
                        "session_id": str(uuid.uuid4())
                    },
                    "authentication_type": "opt-in"
                }
            ]
        },
        "destinations": [
            {
                "name": "João Silva",
                "document_number": "12345678901",
                "account_branch": "0001",
                "account_number": "123456",
                "account_digit": "7",
                "financial_institution_code_number": "341",
                "ispb_number": "60746948"
            }
        ]
    }
    
    try:
        print("🧪 Testando payload oficial completo...")
        print("Enviando requisição...")
        
        response = plugqi.client.post("/account_request/escrow", official_payload)
        
        print("✅ SUCESSO! Conta Escrow criada!")
        print(f"Response: {response}")
        
        # Salvar response para análise
        with open('escrow_success_response.json', 'w') as f:
            import json
            json.dump(response, f, indent=2)
            
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        
        if hasattr(e, 'payload') and e.payload:
            print(f"Payload de erro: {e.payload}")
            
            # Tentar extrair informações específicas do erro
            error_data = e.payload.get('data', '')
            if 'required' in error_data.lower():
                print("🔍 Campos obrigatórios detectados no erro")
            if 'invalid' in error_data.lower():
                print("🔍 Campos inválidos detectados no erro")
                
        return False

def test_without_optional_fields():
    """Teste removendo campos opcionais um por vez"""
    
    plugqi = PlugQi()
    
    # Payload sem campos opcionais
    minimal_required = {
        "account_owner": {
            "person_type": "legal",
            "company_document_number": "12345678000195",
            "name": "Empresa Teste LTDA",
            "email": "empresa@teste.com",
            "company_representatives": [
                {
                    "name": "João Silva",
                    "individual_document_number": "12345678901",
                    "person_type": "natural",
                    "birth_date": "1990-01-01",
                    "mother_name": "Maria Silva"
                }
            ]
        },
        "signed_contract": {
            "document_key": str(uuid.uuid4()),
            "signatures": []
        },
        "destinations": []
    }
    
    try:
        print("\n🧪 Testando payload mínimo obrigatório...")
        response = plugqi.client.post("/account_request/escrow", minimal_required)
        print("✅ Payload mínimo funcionou!")
        return True
        
    except Exception as e:
        print(f"❌ Payload mínimo falhou: {str(e)[:200]}...")
        return False

if __name__ == "__main__":
    print("📋 TESTE SCHEMA OFICIAL - CONTA ESCROW")
    print("=" * 50)
    
    # Teste 1: Schema oficial completo
    success = test_official_schema()
    
    if not success:
        # Teste 2: Schema mínimo
        test_without_optional_fields()
