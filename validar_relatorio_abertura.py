#!/usr/bin/env python3
"""
Validador do Relatório de Abertura de Contas
Verifica se todos os arquivos e dados estão corretos
"""
import json
import os
from datetime import datetime

def validar_relatorio_abertura():
    """Valida relatório completo de abertura de contas"""
    print("🔍 Validando Relatório de Abertura de Contas\n")
    
    erros = []
    avisos = []
    
    # 1. Verifica arquivo principal
    try:
        with open("relatorio_abertura_contas.json", "r", encoding="utf-8") as f:
            relatorio = json.load(f)
        
        print("✅ Arquivo principal encontrado")
        
        # Valida campos obrigatórios
        campos_obrigatorios = ["timestamp", "total_testes", "testes_passaram", "taxa_sucesso", "resultados"]
        for campo in campos_obrigatorios:
            if campo not in relatorio:
                erros.append(f"Campo obrigatório ausente: {campo}")
        
        # Valida taxa de sucesso
        if relatorio.get("taxa_sucesso") == "100.0%":
            print("✅ Taxa de sucesso: 100%")
        else:
            avisos.append(f"Taxa de sucesso não é 100%: {relatorio.get('taxa_sucesso')}")
        
        # Valida resultados
        total_testes = relatorio.get("total_testes", 0)
        testes_passaram = relatorio.get("testes_passaram", 0)
        
        if total_testes == 6:
            print("✅ Total de testes: 6")
        else:
            erros.append(f"Esperado 6 testes, encontrado: {total_testes}")
        
        if testes_passaram == total_testes:
            print("✅ Todos os testes passaram")
        else:
            erros.append(f"Nem todos os testes passaram: {testes_passaram}/{total_testes}")
            
    except FileNotFoundError:
        erros.append("Arquivo relatorio_abertura_contas.json não encontrado")
    except json.JSONDecodeError:
        erros.append("Arquivo relatorio_abertura_contas.json com JSON inválido")
    
    # 2. Verifica webhooks
    try:
        with open("relatorio_webhooks_abertura.json", "r", encoding="utf-8") as f:
            webhooks = json.load(f)
        
        print("✅ Arquivo de webhooks encontrado")
        
        # Valida tipos de webhook
        tipos_esperados = ["pending_additional_data", "approved", "rejected"]
        for tipo in tipos_esperados:
            if tipo in webhooks:
                webhook = webhooks[tipo]
                if webhook.get("webhook_type") == "account_request.status_change":
                    print(f"✅ Webhook {tipo}: OK")
                else:
                    erros.append(f"Webhook {tipo} com tipo incorreto")
            else:
                erros.append(f"Webhook {tipo} ausente")
                
    except FileNotFoundError:
        erros.append("Arquivo relatorio_webhooks_abertura.json não encontrado")
    except json.JSONDecodeError:
        erros.append("Arquivo relatorio_webhooks_abertura.json com JSON inválido")
    
    # 3. Verifica cenários de mock
    try:
        with open("relatorio_cenarios_mock.json", "r", encoding="utf-8") as f:
            cenarios = json.load(f)
        
        print("✅ Arquivo de cenários encontrado")
        
        # Valida cenários
        if len(cenarios) == 3:
            print("✅ 3 cenários de mock")
        else:
            erros.append(f"Esperado 3 cenários, encontrado: {len(cenarios)}")
        
        # Valida cada cenário
        status_esperados = ["automatic_approval", "automatic_rejection", "manual_analysis"]
        digitos_esperados = ["9", "8", "5"]
        
        for i, cenario in enumerate(cenarios):
            if i < len(status_esperados):
                if cenario.get("status_esperado") == status_esperados[i]:
                    print(f"✅ Cenário {i+1}: {cenario.get('cenario')}")
                else:
                    erros.append(f"Cenário {i+1} com status incorreto")
                    
    except FileNotFoundError:
        erros.append("Arquivo relatorio_cenarios_mock.json não encontrado")
    except json.JSONDecodeError:
        erros.append("Arquivo relatorio_cenarios_mock.json com JSON inválido")
    
    # 4. Verifica funcionalidades testadas
    funcionalidades_esperadas = [
        "Validações de CPF/CNPJ",
        "Sistema de mock por primeiro dígito", 
        "Helpers de construção de payload",
        "Fluxo duas etapas (POST + PATCH)",
        "Webhooks de status change",
        "Cenários de aprovação/rejeição"
    ]
    
    if 'relatorio' in locals():
        funcionalidades = relatorio.get("funcionalidades_testadas", [])
        for func in funcionalidades_esperadas:
            if func in funcionalidades:
                print(f"✅ Funcionalidade: {func}")
            else:
                erros.append(f"Funcionalidade ausente: {func}")
    
    # 5. Resumo da validação
    print("\n" + "="*50)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("="*50)
    
    if erros:
        print("❌ ERROS ENCONTRADOS:")
        for erro in erros:
            print(f"  • {erro}")
    
    if avisos:
        print("\n⚠️ AVISOS:")
        for aviso in avisos:
            print(f"  • {aviso}")
    
    if not erros and not avisos:
        print("🎉 RELATÓRIO VÁLIDO - Todos os critérios atendidos!")
        
        # Estatísticas finais
        print(f"\n📈 Estatísticas:")
        print(f"• Arquivos gerados: 3")
        print(f"• Testes executados: 6")
        print(f"• Taxa de sucesso: 100%")
        print(f"• Funcionalidades: {len(funcionalidades_esperadas)}")
        print(f"• Cenários de mock: 3")
        print(f"• Tipos de webhook: 3")
        
        return True
    else:
        print(f"\n⚠️ Validação falhou: {len(erros)} erro(s), {len(avisos)} aviso(s)")
        return False

if __name__ == "__main__":
    success = validar_relatorio_abertura()
    exit(0 if success else 1)
