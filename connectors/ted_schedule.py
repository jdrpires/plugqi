import uuid
from datetime import datetime

class TedScheduleConnector:
    def __init__(self, client):
        self.client = client
    
    def create_ted_schedule(self, account_key, target_account, transaction_amount, schedule_date, request_control_key=None):
        """
        Solicitar Agendamento de Transação TED
        
        Args:
            account_key (str): Chave da conta origem
            target_account (dict): Dados da conta destino
            transaction_amount (float): Valor da transferência
            schedule_date (str): Data do agendamento (YYYY-MM-DD)
            request_control_key (str, optional): Chave de controle (UUID v4)
        """
        endpoint = f"/account/{account_key}/ted_schedule"
        
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "target_account": target_account,
            "transaction_amount": transaction_amount,
            "schedule_date": schedule_date
        }
        
        return self.client.make_request("POST", endpoint, payload)
    
    def cancel_ted_schedule(self, account_key, schedule_key):
        """
        Cancelar Agendamento de Transação TED
        
        Args:
            account_key (str): Chave da conta
            schedule_key (str): Chave do agendamento
        """
        endpoint = f"/account/{account_key}/ted_schedule/{schedule_key}/cancel"
        
        return self.client.make_request("PATCH", endpoint, {})
    
    def get_ted_schedule(self, account_key, schedule_key):
        """
        Consultar Agendamento de Transação TED
        
        Args:
            account_key (str): Chave da conta
            schedule_key (str): Chave do agendamento
        """
        endpoint = f"/account/{account_key}/ted_schedule/{schedule_key}"
        
        return self.client.make_request("GET", endpoint)
    
    def list_ted_schedules(self, account_key, request_control_key=None, schedule_status=None, page=1, page_size=30):
        """
        Listar Agendamentos de Transação TED de uma conta
        
        Args:
            account_key (str): Chave da conta
            request_control_key (str, optional): Filtrar por chave de controle
            schedule_status (str or list, optional): Filtrar por status
            page (int): Número da página (padrão: 1)
            page_size (int): Tamanho da página (padrão: 30, máximo: 30)
        """
        endpoint = f"/account/{account_key}/ted_schedules"
        
        params = {
            "page": page,
            "page_size": min(page_size, 30)
        }
        
        if request_control_key:
            params["request_control_key"] = request_control_key
            
        if schedule_status:
            if isinstance(schedule_status, list):
                params["schedule_status"] = ",".join(schedule_status)
            else:
                params["schedule_status"] = schedule_status
        
        return self.client.make_request("GET", endpoint, params=params)
    
    def create_ted_schedule_batch(self, account_key, ted_schedules, tfa_info, request_control_key=None):
        """
        Solicitar Agendamento de Transação TED em Lote
        
        Args:
            account_key (str): Chave da conta origem
            ted_schedules (list): Lista de agendamentos TED
            tfa_info (dict): Informações do aprovador (approver_document_number, contact_type)
            request_control_key (str, optional): Chave de controle (UUID v4)
        """
        endpoint = f"/account/{account_key}/ted_schedule_batch"
        
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "ted_schedules": ted_schedules,
            "tfa_info": tfa_info
        }
        
        return self.client.make_request("POST", endpoint, payload)
    
    def approve_ted_schedule_batch_2fa(self, account_key, schedule_batch_key, token):
        """
        Aprovar Agendamento de Transação TED em Lote com Autenticação de Dois Fatores
        
        Args:
            account_key (str): Chave da conta
            schedule_batch_key (str): Chave do lote de agendamento
            token (str): Código de autenticação (6 dígitos)
        """
        endpoint = f"/account/{account_key}/ted_schedule_batch/{schedule_batch_key}/validate_token"
        
        payload = {
            "token": token
        }
        
        return self.client.make_request("PUT", endpoint, payload)
    
    def resend_ted_schedule_batch_token(self, account_key, schedule_batch_key, contact_type=None):
        """
        Solicitar Reenvio de Token para um Agendamento de Transação TED em Lote
        
        Args:
            account_key (str): Chave da conta
            schedule_batch_key (str): Chave do lote de agendamento
            contact_type (str, optional): "email" ou "sms". Se não informado, usa o original
        """
        endpoint = f"/account/{account_key}/ted_schedule_batch/{schedule_batch_key}/resend_token"
        
        payload = {}
        if contact_type:
            payload["contact_type"] = contact_type
        
        return self.client.make_request("PATCH", endpoint, payload)
    
    def build_ted_schedule_item(self, target_account, transaction_amount, schedule_date, request_control_key=None):
        """
        Helper para construir item de agendamento TED para lote
        
        Args:
            target_account (dict): Dados da conta destino
            transaction_amount (float): Valor da transferência
            schedule_date (str): Data do agendamento (YYYY-MM-DD)
            request_control_key (str, optional): Chave de controle (UUID v4)
        """
        return {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "target_account": target_account,
            "transaction_amount": transaction_amount,
            "schedule_date": schedule_date
        }
    
    def build_tfa_info_schedule_batch(self, approver_document_number, contact_type):
        """
        Helper para construir objeto tfa_info para lote de agendamentos
        
        Args:
            approver_document_number (str): CPF do aprovador (11 dígitos)
            contact_type (str): "email" ou "sms"
        """
        return {
            "approver_document_number": approver_document_number,
            "contact_type": contact_type
        }
    
    def build_target_account_schedule(self, account_branch, account_number, account_digit, 
                                    owner_document_number, owner_name, ispb, account_type="checking_account"):
        """
        Helper para construir objeto target_account para agendamento
        
        Args:
            account_branch (str): Agência (4 dígitos)
            account_number (str): Número da conta (até 20 dígitos)
            account_digit (str): Dígito da conta (1 dígito)
            owner_document_number (str): CPF/CNPJ do titular (apenas números)
            owner_name (str): Nome do titular (até 50 caracteres)
            ispb (str): ISPB da instituição (8 dígitos)
            account_type (str): Tipo da conta (padrão: checking_account)
        """
        return {
            "account_branch": account_branch,
            "account_number": account_number,
            "account_digit": account_digit,
            "owner_document_number": owner_document_number,
            "owner_name": owner_name,
            "ispb": ispb,
            "account_type": account_type
        }
