#!/usr/bin/env python3
"""
Teste conta Escrow com payload corrigido conforme documentação QiTech
"""

import os
import sys
from datetime import datetime
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_escrow_minimal():
    """Teste com payload mínimo conforme documentação"""
    
    print("🔍 TESTE CONTA ESCROW - PAYLOAD CORRIGIDO")
    print("=" * 60)
    
    try:
        plugqi = PlugQi()
        
        # Payload mínimo conforme documentação QiTech
        minimal_payload = {
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
                "cnae_code": "6201501"
            }
        }
        
        print("✅ Payload mínimo construído")
        
        # Fazer chamada direta ao cliente
        response = plugqi.client.post("/account_request/escrow", minimal_payload)
        
        print("✅ Conta Escrow criada com sucesso!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        if hasattr(e, 'status'):
            print(f"Status: {e.status}")
        if hasattr(e, 'payload'):
            print(f"Payload erro: {e.payload}")
            
        return False

def test_escrow_step_by_step():
    """Teste passo a passo para identificar campo problemático"""
    
    print("\n🔍 TESTE PASSO A PASSO")
    print("=" * 40)
    
    try:
        plugqi = PlugQi()
        
        # Teste 1: Só dados básicos da empresa
        basic_payload = {
            "account_owner": {
                "person_type": "legal",
                "company_document_number": "12345678000195", 
                "name": "Empresa Teste LTDA",
                "email": "empresa@teste.com"
            }
        }
        
        print("1. Testando payload básico...")
        response = plugqi.client.post("/account_request/escrow", basic_payload)
        print("✅ Payload básico aceito!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no payload básico: {e}")
        
        # Teste 2: Adicionar campos obrigatórios um por vez
        try:
            print("2. Testando com telefone...")
            basic_payload["account_owner"]["phone"] = {
                "country_code": "55",
                "area_code": "11",
                "number": "999999999"
            }
            
            response = plugqi.client.post("/account_request/escrow", basic_payload)
            print("✅ Com telefone aceito!")
            
        except Exception as e2:
            print(f"❌ Erro com telefone: {e2}")
            
        return False

if __name__ == "__main__":
    print("🚀 TESTANDO CONTA ESCROW LIBERADA")
    print("=" * 50)
    
    # Teste 1: Payload mínimo
    success1 = test_escrow_minimal()
    
    if not success1:
        # Teste 2: Passo a passo
        test_escrow_step_by_step()
