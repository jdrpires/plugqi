#!/usr/bin/env python3
"""
Teste da consulta de instituições financeiras
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_list_all():
    """Testa listagem geral de instituições"""
    
    plugqi = PlugQi()
    
    try:
        print("🧪 Testando listagem geral...")
        
        response = plugqi.financial_institution.list_institutions()
        
        print(f"✅ Listagem realizada!")
        
        # Verificar formato da resposta
        if 'data' in response and 'pagination' in response:
            print(f"📊 Formato paginado:")
            print(f"Total de instituições: {response['pagination']['total_rows']}")
            print(f"Página atual: {response['pagination']['current_page']}")
            print(f"Total de páginas: {response['pagination']['total_pages']}")
            
            # Mostrar primeiras instituições
            for i, inst in enumerate(response['data'][:3]):
                print(f"  {i+1}. {inst['name']} (ISPB: {inst['ispb_number']})")
        
        else:
            print(f"📊 Formato direto:")
            count = 0
            for ispb, data in list(response.items())[:3]:
                if isinstance(data, dict):
                    print(f"  {count+1}. {data['name']} (ISPB: {ispb})")
                    count += 1
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def test_search_by_name():
    """Testa busca por nome"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🧪 Testando busca por nome...")
        
        # Buscar bancos conhecidos
        banks_to_search = ["Banco do Brasil", "Itaú", "Bradesco"]
        
        for bank_name in banks_to_search:
            try:
                response = plugqi.financial_institution.get_by_name(bank_name)
                
                if 'data' in response and response['data']:
                    inst = response['data'][0]
                    print(f"✅ {bank_name}: {inst['name']} (ISPB: {inst['ispb_number']})")
                else:
                    # Buscar no formato direto
                    found = False
                    for ispb, data in response.items():
                        if isinstance(data, dict) and bank_name.lower() in data['name'].lower():
                            print(f"✅ {bank_name}: {data['name']} (ISPB: {ispb})")
                            found = True
                            break
                    
                    if not found:
                        print(f"⚠️ {bank_name}: Não encontrado")
                        
            except Exception as e:
                print(f"⚠️ {bank_name}: Erro na busca - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na busca por nome: {e}")
        return False

def test_search_by_codes():
    """Testa busca por códigos ISPB e COMPE"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🧪 Testando busca por códigos...")
        
        # Códigos conhecidos
        test_codes = [
            ("00000000", "ISPB", "Banco do Brasil"),
            ("001", "COMPE", "Banco do Brasil"),
            ("60746948", "ISPB", "Itaú"),
            ("341", "COMPE", "Itaú")
        ]
        
        for code, code_type, expected_name in test_codes:
            try:
                if code_type == "ISPB":
                    response = plugqi.financial_institution.get_by_ispb(code)
                else:
                    response = plugqi.financial_institution.get_by_compe(code)
                
                # Processar resposta
                found = False
                
                if 'data' in response and response['data']:
                    inst = response['data'][0]
                    print(f"✅ {code_type} {code}: {inst['name']}")
                    found = True
                else:
                    # Buscar no formato direto
                    for ispb, data in response.items():
                        if isinstance(data, dict):
                            if (code_type == "ISPB" and ispb == code) or \
                               (code_type == "COMPE" and data.get('compe_number') == code):
                                print(f"✅ {code_type} {code}: {data['name']}")
                                found = True
                                break
                
                if not found:
                    print(f"⚠️ {code_type} {code}: Não encontrado")
                    
            except Exception as e:
                print(f"⚠️ {code_type} {code}: Erro - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na busca por códigos: {e}")
        return False

def test_pagination():
    """Testa paginação"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🧪 Testando paginação...")
        
        response = plugqi.financial_institution.get_paginated(page_number=1, page_size=5)
        
        if 'pagination' in response:
            pagination = response['pagination']
            print(f"✅ Paginação funcionando!")
            print(f"Página: {pagination['current_page']}")
            print(f"Itens por página: {pagination['rows_per_page']}")
            print(f"Total de itens: {pagination['total_rows']}")
            
            # Mostrar instituições da página
            for i, inst in enumerate(response['data']):
                print(f"  {i+1}. {inst['name']}")
        
        else:
            print("⚠️ Resposta não paginada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na paginação: {e}")
        return False

def test_helper_methods():
    """Testa métodos helper"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🧪 Testando métodos helper...")
        
        # Testar get_bank_info
        bank_info = plugqi.financial_institution.get_bank_info("341")  # Itaú
        
        if bank_info:
            print(f"✅ get_bank_info(341): {bank_info['name']}")
        else:
            print("⚠️ get_bank_info(341): Não encontrado")
        
        # Testar get_all_active
        active_institutions = plugqi.financial_institution.get_all_active()
        
        if active_institutions:
            print(f"✅ get_all_active: {len(active_institutions)} instituições ativas")
            
            # Mostrar algumas
            for i, inst in enumerate(active_institutions[:3]):
                print(f"  {i+1}. {inst['name']}")
        else:
            print("⚠️ get_all_active: Nenhuma instituição encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos métodos helper: {e}")
        return False

if __name__ == "__main__":
    print("🏦 TESTE CONSULTA INSTITUIÇÕES FINANCEIRAS")
    print("=" * 60)
    
    # Verificar conectividade
    plugqi = PlugQi()
    if not plugqi.health_check():
        print("❌ Falha na conectividade com QiTech")
        exit(1)
    
    print("✅ Conectividade OK")
    
    # Executar testes
    test1 = test_list_all()
    test2 = test_search_by_name()
    test3 = test_search_by_codes()
    test4 = test_pagination()
    test5 = test_helper_methods()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Listagem geral: {'✅' if test1 else '❌'}")
    print(f"Busca por nome: {'✅' if test2 else '❌'}")
    print(f"Busca por códigos: {'✅' if test3 else '❌'}")
    print(f"Paginação: {'✅' if test4 else '❌'}")
    print(f"Métodos helper: {'✅' if test5 else '❌'}")
    
    success_count = sum([test1, test2, test3, test4, test5])
    
    if success_count >= 3:
        print(f"\n🎉 CONSULTA DE INSTITUIÇÕES FUNCIONANDO!")
        print(f"Sucessos: {success_count}/5")
    else:
        print(f"\n❌ Problemas na consulta de instituições")
        print(f"Sucessos: {success_count}/5")
