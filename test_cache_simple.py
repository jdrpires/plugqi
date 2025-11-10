#!/usr/bin/env python3
"""
Teste simples e robusto para cache de instituições financeiras
"""

import time
from plugqi import PlugQi

def test_cache_basic_functionality():
    """Teste básico de funcionalidade do cache"""
    print("🧪 TESTE CACHE BÁSICO - ISPB/COMPE")
    print("=" * 40)
    
    plugqi = PlugQi()
    
    # Limpar cache
    plugqi.financial_institution.clear_cache()
    print("✅ Cache limpo")
    
    # Verificar cache vazio
    stats = plugqi.financial_institution.get_cache_stats()
    assert stats["cache_size"] == 0
    print(f"✅ Cache vazio: {stats['cache_size']} entradas")
    
    # Primeira consulta (API)
    print("\n🔍 Primeira consulta ISPB (API)...")
    start = time.time()
    result1 = plugqi.financial_institution.get_by_ispb_cached("00000000")
    time1 = time.time() - start
    print(f"⏱️  Tempo: {time1:.3f}s")
    
    # Verificar cache populado
    stats = plugqi.financial_institution.get_cache_stats()
    assert stats["cache_size"] == 1
    print(f"✅ Cache populado: {stats['cache_size']} entrada(s)")
    
    # Segunda consulta (cache)
    print("\n⚡ Segunda consulta ISPB (cache)...")
    start = time.time()
    result2 = plugqi.financial_institution.get_by_ispb_cached("00000000")
    time2 = time.time() - start
    print(f"⚡ Tempo: {time2:.3f}s")
    
    # Verificar resultados iguais
    assert result1 == result2
    print("✅ Resultados consistentes")
    
    # Verificar melhoria de performance
    if time2 < time1:
        improvement = ((time1 - time2) / time1) * 100
        print(f"📈 Melhoria: {improvement:.1f}%")
    
    # Teste COMPE
    print("\n🔍 Teste COMPE com cache...")
    compe_result = plugqi.financial_institution.get_by_compe_cached("001")
    
    stats = plugqi.financial_institution.get_cache_stats()
    print(f"✅ Cache final: {stats['cache_size']} entrada(s)")
    
    # Teste get_bank_info
    print("\n🏦 Teste get_bank_info...")
    bank_info = plugqi.financial_institution.get_bank_info("00000000")
    if bank_info:
        print(f"✅ Banco: {bank_info.get('name', 'N/A')}")
    
    return True

def test_cache_stats():
    """Teste das estatísticas do cache"""
    print("\n📊 TESTE ESTATÍSTICAS CACHE")
    print("=" * 35)
    
    plugqi = PlugQi()
    
    # Obter estatísticas
    stats = plugqi.financial_institution.get_cache_stats()
    
    print(f"Cache size: {stats['cache_size']}")
    print(f"Cache válido: {stats['cache_valid']}")
    print(f"TTL: {stats['ttl_seconds']:,}s")
    print(f"Idade: {stats['cache_age_seconds']:.1f}s")
    
    # Verificar estrutura
    required_keys = ["cache_size", "cache_valid", "ttl_seconds", "cache_age_seconds"]
    for key in required_keys:
        assert key in stats, f"Chave {key} deve estar presente"
    
    print("✅ Estatísticas completas")
    return True

def run_simple_tests():
    """Executa testes simples"""
    print("🚀 TESTES SIMPLES - CACHE ISPB/COMPE")
    print("=" * 45)
    
    tests = [
        ("Funcionalidade Básica", test_cache_basic_functionality),
        ("Estatísticas", test_cache_stats)
    ]
    
    passed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n🔄 {name}...")
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSOU")
        except Exception as e:
            print(f"❌ {name}: FALHOU - {e}")
    
    print(f"\n📊 RESULTADO: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Cache ISPB/COMPE funcionando perfeitamente")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)
