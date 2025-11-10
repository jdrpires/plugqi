#!/usr/bin/env python3
"""
Teste Integrado Avançado PlugQi
Tenta operações reais com tratamento adequado de erros
"""

import json
import uuid
from datetime import datetime, timedelta
from plugqi import PlugQi

def test_operacao(nome, funcao, *args, **kwargs):
    """Helper para testar operações com tratamento de erro"""
    try:
        resultado = funcao(*args, **kwargs)
        print(f"✅ {nome}: Sucesso")
        return {"status": "sucesso", "resultado": resultado}
    except Exception as e:
        error_msg = str(e)
        if "400" in error_msg:
            print(f"⚠️ {nome}: Erro 400 - Dados inválidos ou endpoint não disponível")
        elif "401" in error_msg:
            print(f"❌ {nome}: Erro 401 - Não autorizado")
        elif "404" in error_msg:
            print(f"⚠️ {nome}: Erro 404 - Endpoint não encontrado")
        else:
            print(f"❌ {nome}: {error_msg}")
        return {"status": "erro", "erro": error_msg}

def main():
    print("🚀 TESTE INTEGRADO AVANÇADO PLUGQI")
    print("=" * 60)
    
    # Inicializar PlugQi
    plugqi = PlugQi()
    
    # 1. Health Check
    print("\n1️⃣ VERIFICANDO CONECTIVIDADE...")
    if not plugqi.health_check():
        print("❌ Falha na conectividade com QiTech")
        return
    print("✅ Conectado à QiTech")
    
    # Usar conta PJ existente
    account_key = "bb67b08c-e8c0-4333-929a-1a64c0b0bfa6"
    requester_profile_key = account_key  # Assumindo que é o mesmo
    
    resultados = {}
    
    # 2. Testar Instituições Financeiras
    print("\n2️⃣ TESTANDO INSTITUIÇÕES FINANCEIRAS...")
    resultados["instituicoes"] = test_operacao(
        "Listar Instituições",
        plugqi.financial_institution.get_all_active
    )
    
    resultados["banco_brasil"] = test_operacao(
        "Buscar Banco do Brasil",
        plugqi.financial_institution.get_by_compe,
        "001"
    )
    
    # 3. Testar Criação de Boleto
    print("\n3️⃣ TESTANDO CRIAÇÃO DE BOLETO...")
    boleto_data = {
        "request_control_key": str(uuid.uuid4()),
        "amount": 100.0,
        "expiration": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "payer_data": {
            "name": "João Silva Teste",
            "document_number": "12345678901",
            "person_type": "natural"
        },
        "description": "Teste integrado PlugQi"
    }
    
    resultados["boleto"] = test_operacao(
        "Criar Boleto",
        plugqi.boleto.create_boleto,
        account_key,
        requester_profile_key,
        boleto_data
    )
    
    # 4. Testar BolePix
    print("\n4️⃣ TESTANDO BOLEPIX...")
    resultados["bolepix"] = test_operacao(
        "Criar BolePix",
        plugqi.boleto.create_bolepix,
        account_key,
        requester_profile_key,
        75.0,
        (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "Maria Silva",
        "98765432100"
    )
    
    # 5. Testar PIX
    print("\n5️⃣ TESTANDO PIX...")
    
    # Consultar chave PIX primeiro
    resultados["consulta_pix"] = test_operacao(
        "Consultar Chave PIX",
        plugqi.pix.consultar_chave_pix,
        "teste@email.com"
    )
    
    # Tentar enviar PIX
    resultados["envio_pix"] = test_operacao(
        "Enviar PIX",
        plugqi.pix.enviar_pix_chave,
        account_key,
        "teste@email.com",
        25.0,
        "E12345678901202411061030123456789",
        "PIX teste integrado"
    )
    
    # 6. Testar TED
    print("\n6️⃣ TESTANDO TED...")
    target_account = plugqi.ted.build_target_account(
        account_branch="0001",
        account_number="123456",
        account_digit="7",
        owner_document_number="12345678901",
        owner_name="Beneficiário TED",
        ispb="00000000"
    )
    
    resultados["ted"] = test_operacao(
        "Enviar TED",
        plugqi.ted.send_ted,
        account_key,
        str(uuid.uuid4()),
        target_account,
        150.0
    )
    
    # 7. Testar Agendamento TED
    print("\n7️⃣ TESTANDO AGENDAMENTO TED...")
    target_account_schedule = {
        "account_branch": "0001",
        "account_number": "654321",
        "account_digit": "0",
        "owner_document_number": "98765432100",
        "owner_name": "Beneficiário Agendado",
        "ispb": "60746948",
        "account_type": "checking_account"
    }
    
    schedule_payload = {
        "request_control_key": str(uuid.uuid4()),
        "target_account": target_account_schedule,
        "transaction_amount": 80.0,
        "schedule_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    }
    
    resultados["ted_agendado"] = test_operacao(
        "Agendar TED",
        plugqi.client.post,
        f"/account/{account_key}/ted_schedule",
        schedule_payload
    )
    
    # 8. Testar Transferências Automáticas
    print("\n8️⃣ TESTANDO TRANSFERÊNCIAS AUTOMÁTICAS...")
    destination = plugqi.automatic_transfer.build_destination(
        account_branch="0001",
        account_number="789012",
        account_digit="3",
        document_number="11122233344",
        name="Beneficiário Automático",
        financial_institutions_code_number="341"
    )
    
    resultados["transfer_auto"] = test_operacao(
        "Criar Regra Transferência",
        plugqi.automatic_transfer.create_single_beneficiary_rule,
        account_key,
        destination,
        "0 18 * * 1-5",  # Dias úteis às 18h
        50.0
    )
    
    # 9. Testar Upload de Documento
    print("\n9️⃣ TESTANDO UPLOAD DE DOCUMENTO...")
    # Criar arquivo temporário para teste
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Documento de teste para upload")
        temp_file = f.name
    
    resultados["upload_doc"] = test_operacao(
        "Upload Documento",
        plugqi.document_upload.upload_file,
        temp_file,
        "text/plain"
    )
    
    # 10. Análise dos Resultados
    print("\n🎯 ANÁLISE DOS RESULTADOS")
    print("=" * 60)
    
    sucessos = sum(1 for r in resultados.values() if r["status"] == "sucesso")
    total = len(resultados)
    
    print(f"📊 Sucessos: {sucessos}/{total} ({sucessos/total*100:.1f}%)")
    
    for nome, resultado in resultados.items():
        status_icon = "✅" if resultado["status"] == "sucesso" else "❌"
        print(f"{status_icon} {nome.replace('_', ' ').title()}")
    
    # 11. Relatório Detalhado
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "account_key": account_key,
        "total_testes": total,
        "sucessos": sucessos,
        "taxa_sucesso": f"{sucessos/total*100:.1f}%",
        "resultados_detalhados": resultados,
        "funcionalidades_funcionando": [
            nome for nome, resultado in resultados.items() 
            if resultado["status"] == "sucesso"
        ],
        "funcionalidades_com_erro": [
            nome for nome, resultado in resultados.items() 
            if resultado["status"] == "erro"
        ]
    }
    
    # Salvar relatório
    with open("relatorio_teste_integrado_avancado.json", "w") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 TESTE INTEGRADO AVANÇADO CONCLUÍDO!")
    print(f"📊 Taxa de sucesso: {sucessos/total*100:.1f}%")
    print(f"📄 Relatório: relatorio_teste_integrado_avancado.json")
    
    # Limpeza
    import os
    try:
        os.unlink(temp_file)
    except:
        pass

if __name__ == "__main__":
    main()
