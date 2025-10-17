#!/usr/bin/env python3
"""
Script para testar o PlugQi de forma prática
"""
import subprocess
import sys

def run_unit_tests():
    """Executa testes unitários"""
    print("🧪 Executando testes unitários...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_smoke_test():
    """Executa smoke test básico"""
    print("\n🔥 Executando smoke test...")
    result = subprocess.run([
        sys.executable, "examples/smoke_test.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_integration_test():
    """Executa teste de integração"""
    print("\n🔗 Executando teste de integração...")
    result = subprocess.run([
        sys.executable, "test_integration.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Executa todos os tipos de teste"""
    print("🚀 Executando bateria completa de testes do PlugQi\n")
    
    tests = [
        ("Testes Unitários", run_unit_tests),
        ("Teste de Integração", run_integration_test),
        ("Smoke Test", run_smoke_test)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"📋 {name}")
        print('='*50)
        
        try:
            success = test_func()
            results.append((name, success))
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"\n{status}: {name}")
        except Exception as e:
            print(f"❌ ERRO em {name}: {e}")
            results.append((name, False))
    
    # Resumo final
    print(f"\n{'='*50}")
    print("📊 RESUMO FINAL")
    print('='*50)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n🎯 Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam - verifique configurações")
        return 1

if __name__ == "__main__":
    exit(main())
