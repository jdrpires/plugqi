#!/usr/bin/env python3
"""
Gerador Final - Documentações PlugQi
Gera versão simples e técnica
"""

import os
import subprocess
import sys

def main():
    print("=== GERADOR DE DOCUMENTACOES PLUGQI ===")
    print()
    
    # Verificar arquivos markdown
    docs = {
        'Simples': 'INTEGRACAO_FLUXO_COMPLETO.md',
        'Tecnica': 'INTEGRACAO_TECNICA_COMPLETA.md'
    }
    
    for doc_type, filename in docs.items():
        if not os.path.exists(filename):
            print(f"ERRO: {filename} nao encontrado")
            return
        print(f"OK {doc_type}: {filename}")
    
    # Verificar reportlab
    try:
        import reportlab
        print("OK ReportLab disponivel")
    except ImportError:
        print("Instalando ReportLab...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'reportlab'], check=True)
    
    print("\n=== GERANDO PDFs ===")
    
    # Gerar PDF simples
    try:
        from generate_simple_pdf import generate_simple_pdf
        pdf_simples = generate_simple_pdf()
        print(f"OK PDF Simples: {pdf_simples}")
        print(f"  Tamanho: {os.path.getsize(pdf_simples)} bytes")
    except Exception as e:
        print(f"ERRO PDF Simples: {e}")
    
    # Gerar PDF técnico
    try:
        from generate_tech_pdf import generate_tech_pdf
        pdf_tecnico = generate_tech_pdf()
        print(f"OK PDF Tecnico: {pdf_tecnico}")
        print(f"  Tamanho: {os.path.getsize(pdf_tecnico)} bytes")
    except Exception as e:
        print(f"ERRO PDF Tecnico: {e}")
    
    print("\n=== RESUMO ===")
    print("Documentacoes disponiveis:")
    
    files = [
        'INTEGRACAO_FLUXO_COMPLETO.md',
        'INTEGRACAO_FLUXO_COMPLETO.pdf', 
        'INTEGRACAO_TECNICA_COMPLETA.md',
        'INTEGRACAO_TECNICA_COMPLETA.pdf'
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  OK {file} ({size} bytes)")
        else:
            print(f"  X {file} (nao encontrado)")
    
    print("\n=== RECOMENDACOES ===")
    print("• PDF Simples: Para desenvolvedores iniciantes")
    print("• PDF Tecnico: Para arquitetos e desenvolvedores senior")
    print("• Ambos incluem a URL: https://qi.homolog.plugz.com.br/")
    print("\nDocumentacoes prontas para envio!")

if __name__ == "__main__":
    main()