#!/usr/bin/env python3
"""
Script Final - Gerar PDF da Documentação de Integração
"""

import os
import subprocess
import sys

def main():
    print("=== GERADOR DE PDF - DOCUMENTACAO DE INTEGRACAO ===")
    
    # Verificar se arquivo markdown existe
    if not os.path.exists('INTEGRACAO_FLUXO_COMPLETO.md'):
        print("ERRO: Arquivo INTEGRACAO_FLUXO_COMPLETO.md nao encontrado")
        return
    
    # Verificar se reportlab está instalado
    try:
        import reportlab
        print("✓ ReportLab encontrado")
    except ImportError:
        print("Instalando ReportLab...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'reportlab'], check=True)
    
    # Gerar PDF
    try:
        from generate_simple_pdf import generate_simple_pdf
        pdf_file = generate_simple_pdf()
        
        print(f"\n=== SUCESSO ===")
        print(f"PDF gerado: {pdf_file}")
        print(f"Caminho completo: {os.path.abspath(pdf_file)}")
        print(f"Tamanho: {os.path.getsize(pdf_file)} bytes")
        
        # Verificar se pode abrir o arquivo
        if os.path.exists(pdf_file):
            print("✓ Arquivo PDF criado com sucesso")
            print("\nO PDF está pronto para ser enviado ao desenvolvedor!")
        
    except Exception as e:
        print(f"ERRO ao gerar PDF: {e}")

if __name__ == "__main__":
    main()