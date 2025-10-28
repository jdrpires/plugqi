#!/usr/bin/env python3
"""
Sistema de testes atualizado do PlugQi
Executa diferentes tipos de teste conforme necessidade
"""
import sys
import subprocess
import os
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔄 {title}")
    print(f"{'='*60}")

def run_test_file(filename, description):
    """Executa arquivo de teste específico"""
    if not os.path.exists(filename):
        print(f"❌ Arquivo {filename} não encontrado")
        return False
    
    print_header(description)
    try:
        result = subprocess.run([sys.executable, filename], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FALHOU")
            if result.stderr:
                print(f"Erro: {result.stderr}")
            if result.stdout:
                print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar {filename}: {e}")
        return False

def main():
    print("🚀 PLUGQI - SISTEMA DE TESTES INTEGRADO")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Lista de testes disponíveis
    tests = [
        ("test_automated_simple.py", "Testes Automatizados Simples"),
        ("test_integration.py", "Testes de Integração"),
        ("test_comprehensive.py", "Testes Completos com API"),
        ("generate_comprehensive_report.py", "Relatório Completo")
    ]
    
    results = []
    
    # Executa cada teste
    for filename, description in tests:
        success = run_test_file(filename, description)
        results.append((description, success))
    
    # Executa testes unitários com pytest
    print_header("Testes Unitários (pytest)")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Testes Unitários - SUCESSO")
            print(result.stdout)
            results.append(("Testes Unitários", True))
        else:
            print("❌ Testes Unitários - FALHOU")
            if result.stderr:
                print(f"Erro: {result.stderr}")
            results.append(("Testes Unitários", False))
    except Exception as e:
        print(f"❌ Erro ao executar pytest: {e}")
        results.append(("Testes Unitários", False))
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO FINAL")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:.<50} {status}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"⚠️  {total - passed} TESTE(S) FALHARAM")
        return 1

if __name__ == "__main__":
    exit(main())
