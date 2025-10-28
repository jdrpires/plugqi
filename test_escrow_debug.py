#!/usr/bin/env python3
"""
Debug específico para conta Escrow - identificar erro exato
"""

import os
import sys
from datetime import datetime
import uuid

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugqi import PlugQi

def test_escrow_debug():
    """Teste focado para identificar erro específico da conta Escrow"""
    
    print("🔍 DEBUG CONTA ESCROW")
    print("=" * 50)
    
    try:
        # Inicializar PlugQi
        plugqi = PlugQi()
        
        # Verificar conectividade primeiro
        print("1. Testando conectividade...")
        if not plugqi.health_check():
            print("❌ Falha na conectividade")
            return False
        print("✅ Conectividade OK")
        
        # Construir payload mínimo para teste
        print("\n2. Construindo payload de teste...")
        
        # Dados básicos da empresa
        endereco = plugqi.account_opening.build_endereco(
            rua="Rua Teste",
            numero="123",
            bairro="Centro", 
            cidade="São Paulo",
            estado="SP",
            cep="01234567"
        )
        
        telefone = plugqi.account_opening.build_telefone("55", "11", "999999999")
        
        # Representante legal
        representante = plugqi.account_opening.build_company_representative(
            nome="João Silva",
            cpf="12345678901",
            nascimento="1990-01-01",
            endereco=endereco,
            email="joao@teste.com",
            telefone=telefone,
            nome_mae="Maria Silva"
        )
        
        # Account owner completo
        account_owner = plugqi.account_opening.build_account_owner_completo(
            cnpj="12345678000195",
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            email="empresa@teste.com",
            data_fundacao="2020-01-01",
            cnae="6201501",
            endereco=endereco,
            telefone=telefone,
            representantes=[representante]
        )
        
        # Assinatura
        assinatura = plugqi.account_opening.build_signature(
            nome="João Silva",
            email="joao@teste.com", 
            cpf="12345678901",
            telefone=telefone,
            timestamp=datetime.now().isoformat(),
            facial_recognition_key=str(uuid.uuid4()),
            session_id=str(uuid.uuid4())
        )
        
        # Contrato assinado
        signed_contract = plugqi.account_opening.build_signed_contract(
            document_key=str(uuid.uuid4()),
            assinaturas=[assinatura]
        )
        
        # Conta destino
        destination = plugqi.account_opening.build_destination_account(
            agencia="0001",
            conta="123456",
            digito="7",
            documento="12345678901",
            nome="João Silva",
            ispb="60746948",
            codigo_banco="341"
        )
        
        print("✅ Payload construído")
        
        # Tentar criar conta Escrow
        print("\n3. Tentando criar conta Escrow...")
        
        response = plugqi.account_opening.reservar_conta_pj(
            account_owner=account_owner,
            signed_contract=signed_contract,
            destinations=[destination]
        )
        
        print("✅ Conta Escrow criada com sucesso!")
        print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO IDENTIFICADO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        
        # Se for QiTechError, mostrar payload
        if hasattr(e, 'status'):
            print(f"Status Code: {e.status}")
        if hasattr(e, 'payload'):
            print(f"Payload de erro: {e.payload}")
            
        # Tentar acessar resposta diretamente
        if hasattr(e, 'response'):
            print(f"Response Status: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")
            
        return False

if __name__ == "__main__":
    test_escrow_debug()
