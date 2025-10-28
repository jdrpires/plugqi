#!/usr/bin/env python3
"""
Debug do endpoint de instituições financeiras
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def debug_endpoint():
    """Debug específico do endpoint"""
    
    plugqi = PlugQi()
    
    print("🔍 DEBUG ENDPOINT /financial_institution")
    print("=" * 50)
    
    # Testar health check primeiro
    print("1. Testando conectividade...")
    if plugqi.health_check():
        print("✅ Health check OK")
    else:
        print("❌ Health check falhou")
        return
    
    # Testar endpoint sem parâmetros
    print("\n2. Testando endpoint básico...")
    try:
        response = plugqi.client.get("/financial_institution")
        print("✅ Endpoint acessível!")
        print(f"Response type: {type(response)}")
        
        if isinstance(response, dict):
            if 'data' in response:
                print(f"Formato paginado - {len(response['data'])} itens")
            else:
                print(f"Formato direto - {len(response)} itens")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no endpoint: {e}")
        
        if hasattr(e, 'status'):
            print(f"Status code: {e.status}")
        if hasattr(e, 'payload'):
            print(f"Payload erro: {e.payload}")
        
        return False

def test_different_approaches():
    """Testa diferentes abordagens"""
    
    plugqi = PlugQi()
    
    print("\n3. Testando abordagens alternativas...")
    
    # Testar com parâmetros mínimos
    approaches = [
        ("Sem parâmetros", {}),
        ("Com page_size", {"page_size": 1}),
        ("Com page_number", {"page_number": 1}),
        ("Com ISPB conhecido", {"ispb_number": "60746948"}),
        ("Com COMPE conhecido", {"compe_number": "341"})
    ]
    
    for name, params in approaches:
        try:
            print(f"\n   Testando {name}...")
            response = plugqi.client.get("/financial_institution", params=params)
            print(f"   ✅ {name}: Sucesso!")
            
            if isinstance(response, dict):
                if 'data' in response:
                    print(f"   📊 {len(response['data'])} instituições encontradas")
                else:
                    print(f"   📊 {len(response)} instituições encontradas")
            
            return True
            
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:100]}...")
    
    return False

if __name__ == "__main__":
    success1 = debug_endpoint()
    
    if not success1:
        success2 = test_different_approaches()
        
        if not success2:
            print("\n📋 DIAGNÓSTICO:")
            print("❌ Endpoint /financial_institution não acessível")
            print("💡 Possíveis soluções:")
            print("1. Verificar se endpoint está liberado no sandbox")
            print("2. Confirmar com QiTech se requer permissões especiais")
            print("3. Testar em ambiente de produção")
    else:
        print("\n🎉 ENDPOINT FUNCIONANDO!")
        print("✅ Consulta de instituições financeiras disponível")
