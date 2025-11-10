#!/usr/bin/env python3
"""
Testes de integração para cache de instituições financeiras
"""

import time
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi

def test_cache_performance():
    """Teste de performance do cache"""
    print("\n🚀 TESTE INTEGRAÇÃO - PERFORMANCE CACHE")
    print("=" * 45)
    
    plugqi = PlugQi()
    
    # Teste 1: Primeira consulta (sem cache)
    print("\n🧪 Teste 1: Primeira consulta ISPB (API)")
    start_time = time.time()
    result1 = plugqi.financial_institution.get_by_ispb_cached("00000000")
    first_call_time = time.time() - start_time
    print(f"⏱️  Tempo primeira consulta: {first_call_time:.3f}s")
    
    # Teste 2: Segunda consulta (com cache)
    print("\n🧪 Teste 2: Segunda consulta ISPB (cache)")
    start_time = time.time()
    result2 = plugqi.financial_institution.get_by_ispb_cached("00000000")
    second_call_time = time.time() - start_time
    print(f"⚡ Tempo segunda consulta: {second_call_time:.3f}s")
    
    # Verificar melhoria de performance
    if second_call_time < first_call_time:
        improvement = (first_call_time - second_call_time) / first_call_time * 100
        print(f"📈 Melhoria de performance: {improvement:.1f}%")
    
    # Verificar que os resultados são iguais
    assert result1 == result2, "Resultados do cache devem ser iguais"
    print("✅ Resultados consistentes entre API e cache")
    
    return first_call_time, second_call_time

def test_cache_functionality():
    """Teste de funcionalidade completa do cache"""
    print("\n🧪 TESTE INTEGRAÇÃO - FUNCIONALIDADE CACHE")
    print("=" * 45)
    
    plugqi = PlugQi()
    
    # Limpar cache para teste limpo
    plugqi.financial_institution.clear_cache()
    
    # Verificar cache vazio
    stats = plugqi.financial_institution.get_cache_stats()
    assert stats["cache_size"] == 0, "Cache deve estar vazio"
    assert not stats["cache_valid"], "Cache vazio deve ser inválido"
    print("✅ Cache inicializado vazio")
    
    # Teste ISPB
    print("\n🔍 Testando cache ISPB...")
    ispb_result = plugqi.financial_institution.get_by_ispb_cached("00000000")
    
    stats = plugqi.financial_institution.get_cache_stats()
    assert stats["cache_size"] == 1, "Cache deve ter 1 entrada"
    assert stats["cache_valid"], "Cache deve ser válido"
    print(f"✅ Cache ISPB: {stats['cache_size']} entrada(s)")
    
    # Teste COMPE
    print("\n🔍 Testando cache COMPE...")
    compe_result = plugqi.financial_institution.get_by_compe_cached("001")
    
    stats = plugqi.financial_institution.get_cache_stats()
    assert stats["cache_size"] == 2, "Cache deve ter 2 entradas"
    print(f"✅ Cache COMPE: {stats['cache_size']} entrada(s)")
    
    # Teste get_bank_info com cache
    print("\n🔍 Testando get_bank_info com cache...")
    bank_info = plugqi.financial_institution.get_bank_info("00000000")
    
    if bank_info:
        print(f"✅ Banco encontrado: {bank_info.get('name', 'N/A')}")
    else:
        print("⚠️  Banco não encontrado")
    
    # Verificar TTL
    print(f"\n📊 TTL configurado: {stats['ttl_seconds']:,}s (24 horas)")
    print(f"📊 Idade do cache: {stats['cache_age_seconds']:.1f}s")
    
    return True

def test_cache_expiration():
    """Teste de expiração do cache (simulado)"""
    print("\n🧪 TESTE INTEGRAÇÃO - EXPIRAÇÃO CACHE")
    print("=" * 45)
    
    plugqi = PlugQi()
    
    # Limpar cache primeiro
    plugqi.financial_institution.clear_cache()
    
    # Adicionar entrada no cache
    plugqi.financial_institution.get_by_ispb_cached("00000000")
    
    # Simular cache expirado
    plugqi.financial_institution._cache_timestamp = time.time() - 90000  # Mais de 24h
    
    stats = plugqi.financial_institution.get_cache_stats()
    assert not stats["cache_valid"], "Cache expirado deve ser inválido"
    print("✅ Cache expirado detectado corretamente")
    
    # Consulta deve ir para API novamente e renovar cache
    result = plugqi.financial_institution.get_by_ispb_cached("00000000")
    
    stats = plugqi.financial_institution.get_cache_stats()
    assert stats["cache_valid"], "Cache deve ser válido após renovação"
    assert stats["cache_age_seconds"] < 10, "Cache deve ser recente"
    print("✅ Cache renovado automaticamente")
    
    return True

def test_cache_clear():
    """Teste de limpeza manual do cache"""
    print("\n🧪 TESTE INTEGRAÇÃO - LIMPEZA CACHE")
    print("=" * 45)
    
    plugqi = PlugQi()
    
    # Adicionar dados ao cache
    plugqi.financial_institution.get_by_ispb_cached("00000000")
    
    stats_before = plugqi.financial_institution.get_cache_stats()
    print(f"📊 Cache antes: {stats_before['cache_size']} entrada(s)")
    
    # Limpar cache
    plugqi.financial_institution.clear_cache()
    
    stats_after = plugqi.financial_institution.get_cache_stats()
    assert stats_after["cache_size"] == 0, "Cache deve estar vazio após limpeza"
    assert not stats_after["cache_valid"], "Cache limpo deve ser inválido"
    print(f"✅ Cache limpo: {stats_after['cache_size']} entrada(s)")
    
    return True

def run_all_integration_tests():
    """Executa todos os testes de integração"""
    print("🧪 EXECUTANDO TESTES INTEGRAÇÃO - CACHE ISPB/COMPE")
    print("=" * 55)
    
    tests = [
        ("Performance", test_cache_performance),
        ("Funcionalidade", test_cache_functionality),
        ("Expiração", test_cache_expiration),
        ("Limpeza", test_cache_clear)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Executando: {test_name}")
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSOU")
        except Exception as e:
            print(f"❌ {test_name}: FALHOU - {e}")
    
    print(f"\n📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE INTEGRAÇÃO PASSARAM!")
        print("✅ Cache ISPB/COMPE totalmente funcional")
    else:
        print("⚠️  Alguns testes falharam")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_integration_tests()
    exit(0 if success else 1)
