#!/usr/bin/env python3
"""
Script principal para executar todos os tipos de teste do PlugQi
"""
import sys
import subprocess
import argparse
from datetime import datetime

def run_command(command, description):
    """Executa comando e retorna resultado"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FALHOU")
            if result.stderr:
                print(f"Erro: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False

def run_simple_tests():
    """Executa testes automatizados simples"""
    return run_command(
        "python3 test_automated_simple.py",
        "Testes Automatizados Simples (sem API)"
    )

def run_comprehensive_tests():
    """Executa testes completos com API"""
    return run_command(
        "python3 test_comprehensive_fixed.py",
        "Testes Completos com API Real"
    )

def run_unit_tests():
    """Executa testes unitários"""
    return run_command(
        "python3 -m pytest tests/ -v",
        "Testes Unitários"
    )

def generate_report():
    """Gera relatório completo"""
    return run_command(
        "python3 generate_comprehensive_report_fixed.py",
        "Geração de Relatório Completo"
    )

def run_integration_tests():
    """Executa testes de integração"""
    return run_command(
        "python3 test_integration_fixed.py",
        "Testes de Integração"
    )

def main():
    parser = argparse.ArgumentParser(description='Executa testes do PlugQi')
    parser.add_argument('--simple', action='store_true', help='Apenas testes simples')
    parser.add_argument('--unit', action='store_true', help='Apenas testes unitários')
    parser.add_argument('--comprehensive', action='store_true', help='Apenas testes completos')
    parser.add_argument('--report', action='store_true', help='Apenas gerar relatório')
    parser.add_argument('--integration', action='store_true', help='Apenas testes de integração')
    parser.add_argument('--all', action='store_true', help='Todos os testes (padrão)')
    
    args = parser.parse_args()
    
    print("🚀 PLUGQI - SISTEMA DE TESTES COMPLETO")
    print(f"📅 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = []
    
    # Se nenhuma opção específica, executa todos
    if not any([args.simple, args.unit, args.comprehensive, args.report, args.integration]):
        args.all = True
    
    if args.simple or args.all:
        results.append(("Testes Simples", run_simple_tests()))
    
    if args.unit or args.all:
        results.append(("Testes Unitários", run_unit_tests()))
    
    if args.integration or args.all:
        results.append(("Testes Integração", run_integration_tests()))
    
    if args.comprehensive or args.all:
        results.append(("Testes Completos", run_comprehensive_tests()))
    
    if args.report or args.all:
        results.append(("Relatório Completo", generate_report()))
    
    # Resumo final
    print("\n" + "="*80)
    print("📊 RESUMO FINAL DOS TESTES")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:.<50} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n🎯 RESULTADO GERAL: {passed}/{total} testes passaram ({success_rate:.1f}%)")
    print(f"📅 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"⚠️  {failed} TESTE(S) FALHARAM")
        return 1

if __name__ == "__main__":
    exit(main())
