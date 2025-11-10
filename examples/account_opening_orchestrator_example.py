#!/usr/bin/env python3
"""
Exemplo de uso do Orquestrador de Abertura de Conta
Demonstra o fluxo completo automatizado
"""

import json
import tempfile
from plugqi import PlugQi


def create_sample_documents():
    """Cria documentos de exemplo para teste"""
    documents = {}
    
    # Criar arquivos temporários simulando documentos
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', delete=False) as f:
        f.write("RG Frente - Documento simulado")
        documents["rg_front"] = f.name
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', delete=False) as f:
        f.write("RG Verso - Documento simulado")
        documents["rg_back"] = f.name
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        f.write("Comprovante de Residência - Documento simulado")
        documents["proof_residence"] = f.name
        
    return documents


def exemplo_abertura_conta_pf():
    """Exemplo completo de abertura de conta PF"""
    print("🏦 EXEMPLO: ABERTURA DE CONTA PF COM ORQUESTRADOR")
    print("=" * 60)
    
    # Inicializar PlugQi
    plugqi = PlugQi()
    
    # Dados da pessoa
    person_data = plugqi.account_orchestrator.build_person_data(
        name="João Silva Santos",
        document="12345678901",
        email="joao.silva@email.com",
        birthdate="1990-05-15"
    )
    
    # Documentos necessários
    documents_paths = create_sample_documents()
    
    print("📋 Dados da pessoa:")
    print(f"   Nome: {person_data['name']}")
    print(f"   CPF: {person_data['document_number']}")
    print(f"   Email: {person_data['email']}")
    
    print(f"\n📄 Documentos preparados: {len(documents_paths)} arquivos")
    
    # Executar fluxo completo
    print("\n🚀 Iniciando fluxo orquestrado...")
    
    try:
        result = plugqi.account_orchestrator.create_account_pf_complete(
            person_data=person_data,
            documents_paths=documents_paths
        )
        
        print(f"\n✅ Workflow ID: {result['workflow_id']}")
        print(f"📊 Status Final: {result['status']}")
        print(f"🏦 Account Key: {result.get('account_request_key', 'N/A')}")
        
        print(f"\n📋 Etapas executadas:")
        for step in result['steps']:
            status_icon = "✅" if step['status'] == 'completed' else "⏳"
            print(f"   {status_icon} {step['step']}: {step['status']}")
            
        if result['errors']:
            print(f"\n❌ Erros encontrados:")
            for error in result['errors']:
                print(f"   • {error}")
                
        # Salvar resultado
        with open("resultado_abertura_pf.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Resultado salvo em: resultado_abertura_pf.json")
        
    except Exception as e:
        print(f"\n❌ Erro no fluxo: {e}")
    
    # Limpeza
    import os
    for file_path in documents_paths.values():
        try:
            os.unlink(file_path)
        except:
            pass


def exemplo_abertura_conta_pj():
    """Exemplo completo de abertura de conta PJ"""
    print("\n🏢 EXEMPLO: ABERTURA DE CONTA PJ COM ORQUESTRADOR")
    print("=" * 60)
    
    # Inicializar PlugQi
    plugqi = PlugQi()
    
    # Dados da empresa
    company_data = plugqi.account_orchestrator.build_company_data(
        name="Empresa Exemplo LTDA",
        document="12345678000195",
        email="contato@empresaexemplo.com",
        foundation_date="2020-01-15"
    )
    
    # Representante legal
    legal_rep = plugqi.account_orchestrator.build_legal_representative(
        name="Maria Silva Santos",
        document="98765432100",
        email="maria.silva@empresaexemplo.com",
        birthdate="1985-03-20"
    )
    
    # Documentos da empresa
    documents_paths = {
        "company_statute": tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False).name,
        "cnpj_certificate": tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False).name
    }
    
    print("📋 Dados da empresa:")
    print(f"   Razão Social: {company_data['name']}")
    print(f"   CNPJ: {company_data['document_number']}")
    print(f"   Email: {company_data['email']}")
    print(f"   Representante: {legal_rep['name']}")
    
    # Executar fluxo completo
    print("\n🚀 Iniciando fluxo orquestrado PJ...")
    
    try:
        result = plugqi.account_orchestrator.create_account_pj_complete(
            company_data=company_data,
            legal_representatives=[legal_rep],
            documents_paths=documents_paths
        )
        
        print(f"\n✅ Workflow ID: {result['workflow_id']}")
        print(f"📊 Status Final: {result['status']}")
        print(f"🏦 Account Key: {result.get('account_request_key', 'N/A')}")
        
        # Salvar resultado
        with open("resultado_abertura_pj.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Resultado salvo em: resultado_abertura_pj.json")
        
    except Exception as e:
        print(f"\n❌ Erro no fluxo: {e}")


def exemplo_monitoramento():
    """Exemplo de monitoramento de workflow"""
    print("\n📊 EXEMPLO: MONITORAMENTO DE WORKFLOW")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    # Simular consulta de workflow
    workflow_id = "exemplo-workflow-123"
    
    try:
        status = plugqi.account_orchestrator.get_workflow_status(workflow_id)
        print(f"Status do workflow {workflow_id}:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")


def main():
    """Executa todos os exemplos"""
    print("🎯 EXEMPLOS DO ORQUESTRADOR DE ABERTURA DE CONTA")
    print("=" * 70)
    
    # Exemplo PF
    exemplo_abertura_conta_pf()
    
    # Exemplo PJ
    exemplo_abertura_conta_pj()
    
    # Exemplo monitoramento
    exemplo_monitoramento()
    
    print(f"\n🎉 EXEMPLOS CONCLUÍDOS!")
    print("📁 Arquivos gerados:")
    print("   • resultado_abertura_pf.json")
    print("   • resultado_abertura_pj.json")


if __name__ == "__main__":
    main()
