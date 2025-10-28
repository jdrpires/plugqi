#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi
from qitech_client import QiTechError
import json

def test_escrow_pj_status():
    """Verificar status das contas Escrow PJ criadas"""
    
    print("🔍 VERIFICAÇÃO DE STATUS - CONTAS ESCROW PJ")
    print("=" * 60)
    
    plugqi = PlugQi()
    
    # Contas criadas anteriormente
    contas = [
        {
            "cnpj": "29060633000177",
            "account_request_key": "bb67b08c-e8c0-4333-929a-1a64c0b0bfa6",
            "conta": "5493907-8"
        },
        {
            "cnpj": "98483046636326", 
            "account_request_key": "5e5e3076-2fb0-4430-833f-acdf0f7ad3cf",
            "conta": "1262010-9"
        },
        {
            "cnpj": "97115705024702",
            "account_request_key": "218d7204-5341-405f-a8d3-30b7bc6c8634", 
            "conta": "2690192-5"
        }
    ]
    
    resultados = []
    
    for i, conta in enumerate(contas, 1):
        print(f"\n📋 CONTA {i}: {conta['cnpj']}")
        print(f"🔑 Key: {conta['account_request_key']}")
        print(f"💳 Conta: {conta['conta']}")
        
        try:
            # Tentar consultar status (se houver endpoint)
            # Por enquanto, vamos tentar a confirmação para ver o erro
            
            # Payload mínimo para teste
            test_payload = {
                "account_owner": {
                    "address": {
                        "city": "São Paulo",
                        "complement": "",
                        "neighborhood": "Centro", 
                        "number": "100",
                        "postal_code": "01310100",
                        "state": "SP",
                        "street": "Rua Teste"
                    },
                    "cnae_code": "4721-1/02",
                    "company_document_number": conta['cnpj'],
                    "company_statute": "8b0d8c33-01c9-4cf5-a0fa-1d2a96f4b34d",
                    "company_type": "ltda",
                    "email": "jean.pires@plugz.com.br",
                    "foundation_date": "2017-09-16",
                    "name": "Empresa Teste",
                    "person_type": "legal",
                    "phone": {
                        "area_code": "11",
                        "country_code": "055", 
                        "number": "988888888"
                    },
                    "trading_name": "Teste Ltda",
                    "company_representatives": []
                },
                "signed_contract": {
                    "document_key": "4d7f4e29-4b58-4905-9a69-b1f9215263f5",
                    "signatures": []
                },
                "destinations": [
                    {
                        "account_branch": "0001",
                        "account_number": "1234567",
                        "account_digit": "1", 
                        "document_number": "04252012000123",
                        "name": "Conta Teste",
                        "ispb_number": "32402502",
                        "financial_institution_code_number": "329"
                    }
                ]
            }
            
            response = plugqi.account_opening.confirmar_abertura_conta_escrow_pj(
                account_request_key=conta['account_request_key'],
                account_owner=test_payload['account_owner'],
                signed_contract=test_payload['signed_contract'],
                destinations=test_payload['destinations']
            )
            
            print("✅ Confirmação aceita!")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            
            resultados.append({
                "conta": conta,
                "status": "confirmacao_aceita",
                "response": response
            })
            
        except QiTechError as e:
            print(f"📋 Status Code: {e.status}")
            print(f"📋 Código QiTech: {e.payload.get('code', 'N/A')}")
            print(f"📋 Descrição: {e.payload.get('description', 'N/A')}")
            print(f"📋 Tradução: {e.payload.get('translation', 'N/A')}")
            
            # Interpretar erros
            code = e.payload.get('code', '')
            if code == 'ACR000042':
                status_interpretado = "Aguardando webhook pending_additional_data"
            elif code == 'OBD000085':
                status_interpretado = "Funcionalidade não liberada para sandbox"
            elif code == 'QIT000404':
                status_interpretado = "Conta não encontrada"
            else:
                status_interpretado = f"Erro: {code}"
            
            print(f"🔍 Status interpretado: {status_interpretado}")
            
            resultados.append({
                "conta": conta,
                "status": status_interpretado,
                "error": e.payload
            })
    
    # Salvar resultados
    with open('escrow_pj_status_check.json', 'w') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: escrow_pj_status_check.json")
    
    # Resumo
    print(f"\n📊 RESUMO:")
    for resultado in resultados:
        conta_info = resultado['conta']
        print(f"  • {conta_info['cnpj']}: {resultado['status']}")

if __name__ == "__main__":
    test_escrow_pj_status()
