#!/usr/bin/env python3
"""
Exemplo prático de uso do serviço TED completo
"""

import uuid
from plugqi import PlugQi

def exemplo_fluxo_completo_ted_2fa():
    """Exemplo do fluxo completo TED com 2FA"""
    
    print("🔄 Fluxo Completo TED com 2FA")
    print("-" * 30)
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    
    # Passo 1: Enviar TED com 2FA
    request_control_key = str(uuid.uuid4())
    
    target_account = plugqi.ted.build_target_account(
        account_branch="0001",
        account_number="92796",
        account_digit="1",
        owner_document_number="23599885000192",
        owner_name="João Silva",
        ispb="00000000",
        account_type="checking_account"
    )
    
    try:
        # Enviar TED
        ted_result = plugqi.ted.send_ted_with_2fa(
            account_key=account_key,
            request_control_key=request_control_key,
            target_account=target_account,
            transaction_amount=500.00,
            approver_document_number="98765432100",
            contact_type="email"
        )
        
        print("✅ Passo 1: TED enviado")
        print(f"   Status: {ted_result.get('ted_status')}")
        print(f"   TED Key: {ted_result.get('ted_key')}")
        print("   📧 Token enviado por email")
        
        # Passo 2: Aprovar com token (simulado)
        ted_key = ted_result.get('ted_key')
        token = "329123"  # Token recebido por email
        
        approval_result = plugqi.ted.approve_ted_email_sms(
            account_key=account_key,
            ted_key=ted_key,
            token=token
        )
        
        print("✅ Passo 2: TED aprovado")
        print(f"   Status: {approval_result.get('ted_status')}")
        print(f"   Valor: R$ {approval_result.get('transaction_amount')}")
        print(f"   Taxa: R$ {approval_result.get('fee_amount', 0)}")
        
    except Exception as e:
        print(f"❌ Erro no fluxo: {e}")

def exemplo_aprovacao_email_sms():
    """Exemplo de aprovação via email/SMS"""
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    ted_key = "8cb70dea-9fb0-4a68-9572-99a72849c8d6"  # Obtido do envio
    token = "329123"  # Token recebido
    
    try:
        result = plugqi.ted.approve_ted_email_sms(
            account_key=account_key,
            ted_key=ted_key,
            token=token
        )
        
        print("✅ TED aprovado via Email/SMS!")
        print(f"   Status: {result.get('ted_status')}")
        print(f"   Transaction Key: {result.get('transaction_key')}")
        
    except Exception as e:
        print(f"❌ Erro aprovação Email/SMS: {e}")

def exemplo_aprovacao_device():
    """Exemplo de aprovação via dispositivo"""
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    ted_key = "8cb70dea-9fb0-4a68-9572-99a72849c8d6"
    
    try:
        result = plugqi.ted.approve_ted_device(
            account_key=account_key,
            ted_key=ted_key
        )
        
        print("✅ TED aprovado via Device!")
        print(f"   Status: {result.get('ted_status')}")
        print("   📱 Aprovação automática por dispositivo")
        
    except Exception as e:
        print(f"❌ Erro aprovação Device: {e}")

def exemplo_ted_basico():
    """Exemplo básico de TED sem 2FA"""
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    request_control_key = str(uuid.uuid4())
    
    target_account = plugqi.ted.build_target_account(
        account_branch="0932",
        account_number="123456",
        account_digit="7",
        owner_document_number="12345678901",
        owner_name="Maria Santos",
        ispb="60746948",
        account_type="checking_account"
    )
    
    try:
        result = plugqi.ted.send_ted(
            account_key=account_key,
            request_control_key=request_control_key,
            target_account=target_account,
            transaction_amount=100.50
        )
        
        print("✅ TED básico enviado!")
        print(f"   Status: {result.get('ted_status')}")
        print(f"   TED Key: {result.get('ted_key')}")
        
    except Exception as e:
        print(f"❌ Erro TED básico: {e}")

def exemplo_diferentes_aprovacoes():
    """Exemplo com diferentes métodos de aprovação"""
    
    plugqi = PlugQi()
    
    account_key = "sua-conta-key-aqui"
    ted_key = "test-ted-key"
    
    print("\n🔐 Diferentes Métodos de Aprovação")
    print("-" * 35)
    
    # Método 1: Aprovação genérica com token
    try:
        result1 = plugqi.ted.approve_ted_2fa(
            account_key=account_key,
            ted_key=ted_key,
            token="123456"
        )
        print("✅ Método 1: approve_ted_2fa com token")
        
    except Exception as e:
        print(f"❌ Método 1: {e}")
    
    # Método 2: Aprovação específica email/sms
    try:
        result2 = plugqi.ted.approve_ted_email_sms(
            account_key=account_key,
            ted_key=ted_key,
            token="654321"
        )
        print("✅ Método 2: approve_ted_email_sms")
        
    except Exception as e:
        print(f"❌ Método 2: {e}")
    
    # Método 3: Aprovação device (sem token)
    try:
        result3 = plugqi.ted.approve_ted_device(
            account_key=account_key,
            ted_key=ted_key
        )
        print("✅ Método 3: approve_ted_device")
        
    except Exception as e:
        print(f"❌ Método 3: {e}")

def exemplo_tratamento_erros():
    """Exemplo de tratamento de erros comuns"""
    
    print("\n⚠️  Tratamento de Erros Comuns")
    print("-" * 30)
    
    erros_comuns = [
        ("TED000020", "TED não encontrada"),
        ("TED000086", "TED não está pending_2fa_approval"),
        ("TED000082", "Máximo de tentativas excedido"),
        ("TED000084", "Token incorreto"),
        ("TED000083", "Token expirado"),
        ("TED000110", "Token obrigatório para SMS/email")
    ]
    
    for codigo, descricao in erros_comuns:
        print(f"   {codigo}: {descricao}")

def exemplo_status_resposta():
    """Exemplo dos diferentes status de resposta"""
    
    print("\n📊 Status de Resposta TED")
    print("-" * 25)
    
    status_responses = [
        ("pending_2fa_approval", "202", "Aguardando token de aprovação"),
        ("sent", "201", "Transferência enviada com sucesso"),
        ("pending", "202", "Transferência pendente no sistema"),
        ("rejected", "4xx", "Transferência rejeitada")
    ]
    
    for status, http_code, descricao in status_responses:
        print(f"   {status:<20} ({http_code}) - {descricao}")

if __name__ == "__main__":
    print("🏦 EXEMPLOS COMPLETOS - SERVIÇO TED")
    print("=" * 45)
    
    print("\n1️⃣ Fluxo Completo TED com 2FA")
    exemplo_fluxo_completo_ted_2fa()
    
    print("\n2️⃣ TED Básico (sem 2FA)")
    exemplo_ted_basico()
    
    print("\n3️⃣ Aprovação via Email/SMS")
    exemplo_aprovacao_email_sms()
    
    print("\n4️⃣ Aprovação via Device")
    exemplo_aprovacao_device()
    
    exemplo_diferentes_aprovacoes()
    exemplo_tratamento_erros()
    exemplo_status_resposta()
    
    print(f"\n✅ Exemplos TED Completo concluídos")
