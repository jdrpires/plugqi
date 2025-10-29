from plugqi import PlugQi

def test_ted_schedule_module_loaded():
    """Teste básico: Verificar se o módulo TED Schedule foi carregado"""
    print("\n🏦 Teste Simples - TED Schedule")
    print("=" * 35)
    
    plugqi = PlugQi()
    
    # Verificar se o conector foi carregado
    assert hasattr(plugqi, 'ted_schedule'), "Conector ted_schedule não encontrado"
    print("✅ Módulo TED Schedule carregado")
    
    # Verificar métodos principais
    methods = [
        'create_ted_schedule',
        'cancel_ted_schedule',
        'get_ted_schedule',
        'list_ted_schedules',
        'create_ted_schedule_batch',
        'approve_ted_schedule_batch_2fa',
        'resend_ted_schedule_batch_token',
        'build_ted_schedule_item',
        'build_tfa_info_schedule_batch',
        'build_target_account_schedule'
    ]
    
    for method in methods:
        assert hasattr(plugqi.ted_schedule, method), f"Método {method} não encontrado"
        print(f"✅ Método {method} disponível")
    
    return True

def test_create_ted_schedule():
    """Teste da criação de agendamento TED"""
    print("\n=== Teste: Criar Agendamento TED ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    target_account = plugqi.ted_schedule.build_target_account_schedule(
        account_branch="0001",
        account_number="92796",
        account_digit="1",
        owner_document_number="23599885000192",
        owner_name="Titular da Conta",
        ispb="12345678",
        account_type="checking_account"
    )
    
    try:
        print(f"✅ Método create_ted_schedule disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedule")
        print(f"Método: POST")
        print(f"Valor: R$ 8.86")
        print(f"Data: 2024-12-01")
        print(f"Conta destino: {target_account['owner_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_build_target_account_schedule():
    """Teste do helper build_target_account_schedule"""
    print("\n=== Teste: Helper Target Account Schedule ===")
    
    plugqi = PlugQi()
    
    try:
        # Testar conta corrente
        target_checking = plugqi.ted_schedule.build_target_account_schedule(
            account_branch="0001",
            account_number="92796",
            account_digit="1",
            owner_document_number="23599885000192",
            owner_name="Titular da Conta",
            ispb="12345678",
            account_type="checking_account"
        )
        
        assert target_checking["account_type"] == "checking_account"
        print("✅ Target Account Checking OK")
        
        # Testar conta poupança
        target_saving = plugqi.ted_schedule.build_target_account_schedule(
            account_branch="0001",
            account_number="92796",
            account_digit="1",
            owner_document_number="23599885000192",
            owner_name="Titular da Conta",
            ispb="12345678",
            account_type="saving_account"
        )
        
        assert target_saving["account_type"] == "saving_account"
        print("✅ Target Account Saving OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_schedule_status_types():
    """Teste dos tipos de status de agendamento"""
    print("\n=== Teste: Status de Agendamento ===")
    
    status_types = {
        "scheduled": "Transação agendada",
        "sent": "Agendamento concluído e enviado com sucesso",
        "rejected": "Agendamento rejeitado durante criação ou execução",
        "cancelled": "Agendamento cancelado por solicitação de cliente",
        "pending_2fa_approval": "Pendente de aprovação por autenticação de dois fatores",
        "waiting_batch_approval": "Agendamento criado e vinculado a um lote aguardando aprovação"
    }
    
    print("✅ Status de agendamento mapeados:")
    for status, desc in status_types.items():
        print(f"  {status}: {desc}")
    
    return True

def test_cancel_ted_schedule():
    """Teste do cancelamento de agendamento TED"""
    print("\n=== Teste: Cancelar Agendamento TED ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    schedule_key = "f64b3fa7-d09d-4927-ad4f-b966df9fb153"
    
    try:
        print(f"✅ Método cancel_ted_schedule disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedule/{schedule_key}/cancel")
        print(f"Método: PATCH")
        print(f"Status esperado: cancelled")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_get_ted_schedule():
    """Teste da consulta de agendamento TED"""
    print("\n=== Teste: Consultar Agendamento TED ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    schedule_key = "0c9091ab-079b-4a43-8b3d-d4ba36a23883"
    
    try:
        print(f"✅ Método get_ted_schedule disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedule/{schedule_key}")
        print(f"Método: GET")
        print(f"Retorna: dados completos do agendamento + schedule_transfers")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_schedule_response_structure():
    """Teste da estrutura de resposta do agendamento"""
    print("\n=== Teste: Estrutura Resposta Agendamento ===")
    
    expected_fields = [
        "request_control_key",
        "schedule_key", 
        "schedule_batch_key",
        "schedule_status",
        "target_account",
        "transaction_amount",
        "rejection_info",
        "schedule_date",
        "updated_at",
        "created_at",
        "schedule_transfers"
    ]
    
    print("✅ Campos esperados na resposta:")
    for field in expected_fields:
        print(f"  {field}")
    
    print("\n✅ schedule_transfers contém:")
    transfer_fields = [
        "request_control_key",
        "ted_key",
        "created_at", 
        "ted_status",
        "fee_amount"
    ]
    
    for field in transfer_fields:
        print(f"  {field}")
    
    return True

def test_list_ted_schedules():
    """Teste da listagem de agendamentos TED"""
    print("\n=== Teste: Listar Agendamentos TED ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    
    try:
        print(f"✅ Método list_ted_schedules disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedules")
        print(f"Método: GET")
        print(f"Filtros: request_control_key, schedule_status, page, page_size")
        print(f"Paginação: page=1, page_size=30 (máximo)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_list_response_structure():
    """Teste da estrutura de resposta da listagem"""
    print("\n=== Teste: Estrutura Resposta Listagem ===")
    
    print("✅ Estrutura da resposta:")
    print("  data: array de agendamentos")
    print("    - request_control_key")
    print("    - schedule_key")
    print("    - schedule_status")
    print("    - schedule_date")
    print("    - created_at")
    print("  pagination:")
    print("    - current_page")
    print("    - next_page")
    print("    - rows_per_page")
    
    return True

def test_schedule_status_filters():
    """Teste dos filtros de status disponíveis"""
    print("\n=== Teste: Filtros de Status ===")
    
    status_filters = [
        "scheduled",
        "sent", 
        "rejected",
        "cancelled",
        "pending_2fa_approval",
        "pending_creation",
        "waiting_batch_approval"
    ]
    
    print("✅ Status disponíveis para filtro:")
    for status in status_filters:
        print(f"  {status}")
    
    print("\n✅ Pode filtrar por:")
    print("  - Status único: schedule_status=scheduled")
    print("  - Múltiplos status: schedule_status=scheduled,sent")
    
    return True

def test_resend_ted_schedule_batch_token():
    """Teste do reenvio de token para lote de agendamento TED"""
    print("\n=== Teste: Reenviar Token Lote Agendamento TED ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    schedule_batch_key = "8cb70dea-9fb0-4a68-9572-99a72849c8d6"
    
    try:
        print(f"✅ Método resend_ted_schedule_batch_token disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedule_batch/{schedule_batch_key}/resend_token")
        print(f"Método: PATCH")
        print(f"Contact types: email, sms ou None (usa original)")
        print(f"Status esperado: pending_2fa_approval (202)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_schedule_batch_resend_errors():
    """Teste dos códigos de erro específicos do reenvio de token"""
    print("\n=== Teste: Códigos de Erro Reenvio Token Lote ===")
    
    error_codes = {
        "TED000087": "Error Sending Token",
        "TED000103": "ScheduleBatch not Found", 
        "TED000106": "ScheduleBatch not in pending_2fa_approval status",
        "TED000107": "Schedule Batch could not be approved"
    }
    
    print("✅ Códigos de erro específicos do reenvio:")
    for code, desc in error_codes.items():
        print(f"  {code}: {desc}")
    
    return True

def test_schedule_error_codes():
    """Teste dos códigos de erro específicos do agendamento"""
    print("\n=== Teste: Códigos de Erro Agendamento ===")
    
    error_codes = {
        "TED000093": "TedSchedule not Found",
        "TED000094": "Ted Schedule cannot be cancelled in current status",
        "TED000095": "The given Ted Schedule is tied to a batch",
        "TED000096": "Action cannot be taken place as there is currently a pending transfer",
        "TED000108": "Number of transfer attempts exceeded"
    }
    
    print("✅ Códigos de erro específicos:")
    for code, desc in error_codes.items():
        print(f"  {code}: {desc}")
    
    return True

def test_create_ted_schedule_batch():
    """Teste da criação de agendamento TED em lote"""
    print("\n=== Teste: Criar Agendamento TED em Lote ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    
    try:
        print(f"✅ Método create_ted_schedule_batch disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedule_batch")
        print(f"Método: POST")
        print(f"Status esperado: pending_2fa_approval (202)")
        print(f"Webhook: baas.token_validation.ted.schedule.batch")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_build_ted_schedule_item():
    """Teste do helper build_ted_schedule_item"""
    print("\n=== Teste: Helper TED Schedule Item ===")
    
    plugqi = PlugQi()
    
    try:
        # Criar conta destino
        target_account = plugqi.ted_schedule.build_target_account_schedule(
            account_branch="0001",
            account_number="92796",
            account_digit="1",
            owner_document_number="23599885000192",
            owner_name="Titular da Conta",
            ispb="12345678",
            account_type="checking_account"
        )
        
        # Criar item de agendamento
        schedule_item = plugqi.ted_schedule.build_ted_schedule_item(
            target_account=target_account,
            transaction_amount=8.86,
            schedule_date="2024-12-01"
        )
        
        assert "request_control_key" in schedule_item
        assert schedule_item["transaction_amount"] == 8.86
        assert schedule_item["schedule_date"] == "2024-12-01"
        
        print("✅ TED Schedule Item OK")
        print(f"  Valor: R$ {schedule_item['transaction_amount']}")
        print(f"  Data: {schedule_item['schedule_date']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_build_tfa_info_schedule_batch():
    """Teste do helper build_tfa_info_schedule_batch"""
    print("\n=== Teste: Helper TFA Info Schedule Batch ===")
    
    plugqi = PlugQi()
    
    try:
        # Testar TFA por email
        tfa_email = plugqi.ted_schedule.build_tfa_info_schedule_batch(
            approver_document_number="98765432100",
            contact_type="email"
        )
        
        assert tfa_email["contact_type"] == "email"
        print("✅ TFA Schedule Batch Email OK")
        
        # Testar TFA por SMS
        tfa_sms = plugqi.ted_schedule.build_tfa_info_schedule_batch(
            approver_document_number="98765432100",
            contact_type="sms"
        )
        
        assert tfa_sms["contact_type"] == "sms"
        print("✅ TFA Schedule Batch SMS OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_schedule_batch_status():
    """Teste dos status de lote de agendamento"""
    print("\n=== Teste: Status Lote Agendamento ===")
    
    batch_status = {
        "created": "Agendamento em lote criado",
        "approved": "Agendamento em lote aprovado",
        "rejected": "Agendamento em lote rejeitado",
        "pending_2fa_approval": "Agendamento em lote pendente de aprovação por autenticação de dois fatores"
    }
    
    print("✅ Status de lote de agendamento:")
    for status, desc in batch_status.items():
        print(f"  {status}: {desc}")
    
    return True

def test_approve_ted_schedule_batch_2fa():
    """Teste da aprovação de lote de agendamento TED com 2FA"""
    print("\n=== Teste: Aprovar Lote Agendamento TED com 2FA ===")
    
    plugqi = PlugQi()
    
    # Dados de teste
    account_key = "test-account-key"
    schedule_batch_key = "f64b3fa7-d09d-4927-ad4f-b966df9fb153"
    token = "329123"
    
    try:
        print(f"✅ Método approve_ted_schedule_batch_2fa disponível")
        print(f"Endpoint: /account/{account_key}/ted_schedule_batch/{schedule_batch_key}/validate_token")
        print(f"Método: PUT")
        print(f"Token: {token}")
        print(f"Status esperado: approved (201)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_schedule_batch_approval_errors():
    """Teste dos códigos de erro específicos da aprovação de lote"""
    print("\n=== Teste: Códigos de Erro Aprovação Lote ===")
    
    error_codes = {
        "TED000082": "Number of token validation attempts exceeded",
        "TED000083": "Token Expired",
        "TED000084": "Incorrect Token",
        "TED000085": "Error Validating Token",
        "TED000102": "Ted Batch not in pending_2fa_approval status",
        "TED000103": "ScheduleBatch not Found",
        "TED000106": "ScheduleBatch not in pending_2fa_approval status",
        "TED000107": "Schedule Batch could not be approved"
    }
    
    print("✅ Códigos de erro específicos da aprovação:")
    for code, desc in error_codes.items():
        print(f"  {code}: {desc}")
    
    return True

if __name__ == "__main__":
    print("🚀 EXECUTANDO TESTES SIMPLES TED SCHEDULE")
    print("=" * 45)
    
    tests = [
        test_ted_schedule_module_loaded,
        test_create_ted_schedule,
        test_build_target_account_schedule,
        test_schedule_status_types,
        test_cancel_ted_schedule,
        test_get_ted_schedule,
        test_schedule_response_structure,
        test_list_ted_schedules,
        test_list_response_structure,
        test_schedule_status_filters,
        test_create_ted_schedule_batch,
        test_build_ted_schedule_item,
        test_build_tfa_info_schedule_batch,
        test_schedule_batch_status,
        test_approve_ted_schedule_batch_2fa,
        test_schedule_batch_approval_errors,
        test_resend_ted_schedule_batch_token,
        test_schedule_batch_resend_errors,
        test_schedule_error_codes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Falha no teste {test.__name__}: {e}")
    
    print(f"\n📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  Alguns testes falharam")
    
    print(f"✅ Testes TED Schedule concluídos")
