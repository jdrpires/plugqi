class TedConnector:
    def __init__(self, client):
        self.client = client

    def send_ted(self, account_key, request_control_key, target_account, transaction_amount, tfa_info=None):
        """
        Realizar TED
        
        Args:
            account_key (str): Chave da conta origem
            request_control_key (str): UUID v4 único da requisição
            target_account (dict): Dados da conta destino
            transaction_amount (float): Valor da transferência
            tfa_info (dict, optional): Informações de autenticação 2FA
        """
        endpoint = f"/account/{account_key}/ted"
        
        ted_data = {
            "request_control_key": request_control_key,
            "target_account": target_account,
            "transaction_amount": transaction_amount
        }
        
        if tfa_info:
            ted_data["tfa_info"] = tfa_info
        
        return self.client.post(endpoint, ted_data)

    def send_ted_batch(self, account_key, request_control_key, teds, tfa_info=None):
        """
        Realizar TED em lote
        
        Args:
            account_key (str): Chave da conta origem
            request_control_key (str): UUID v4 único do lote
            teds (list): Lista de objetos TED
            tfa_info (dict, optional): Informações de autenticação 2FA
        """
        endpoint = f"/account/{account_key}/ted_batch"
        
        batch_data = {
            "request_control_key": request_control_key,
            "teds": teds
        }
        
        if tfa_info:
            batch_data["tfa_info"] = tfa_info
        
        return self.client.post(endpoint, batch_data)

    def send_ted_batch_with_2fa(self, account_key, request_control_key, teds, 
                               approver_document_number, contact_type):
        """
        Realizar TED em lote com autenticação de dois fatores
        
        Args:
            account_key (str): Chave da conta origem
            request_control_key (str): UUID v4 único do lote
            teds (list): Lista de objetos TED
            approver_document_number (str): CPF do aprovador
            contact_type (str): "email" ou "sms"
        """
        tfa_info = self.build_tfa_info_batch(approver_document_number, contact_type)
        
        return self.send_ted_batch(
            account_key=account_key,
            request_control_key=request_control_key,
            teds=teds,
            tfa_info=tfa_info
        )

    def approve_ted_batch_2fa(self, account_key, ted_batch_key, token):
        """
        Aprovar lote TED com token 2FA
        
        Args:
            account_key (str): Chave da conta origem
            ted_batch_key (str): Chave do lote TED
            token (str): Token de 6 dígitos
        """
        endpoint = f"/account/{account_key}/ted_batch/{ted_batch_key}/validate_token"
        
        payload = {"token": token}
        
        return self.client.put(endpoint, payload)

    def list_ted_batches(self, account_key, request_control_key=None, ted_batch_status=None, 
                        date_from=None, date_to=None, page=None, page_size=None):
        """
        Listar transações em lote de uma conta
        
        Args:
            account_key (str): Chave da conta origem
            request_control_key (str, optional): UUID do lote específico
            ted_batch_status (str, optional): Status do lote
            date_from (str, optional): Data inicial (YYYY-MM-DD)
            date_to (str, optional): Data final (YYYY-MM-DD)
            page (int, optional): Número da página (padrão: 1)
            page_size (int, optional): Tamanho da página (padrão: 30, máximo: 30)
        """
        endpoint = f"/account/{account_key}/ted_batches"
        
        params = {}
        if request_control_key:
            params["request_control_key"] = request_control_key
        if ted_batch_status:
            params["ted_batch_status"] = ted_batch_status
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
        
        return self.client.get(endpoint, params=params)

    def list_batch_teds(self, account_key, ted_batch_key, request_control_key=None, ted_status=None,
                       date_from=None, date_to=None, page=None, page_size=None):
        """
        Listar transações TED de um lote específico
        
        Args:
            account_key (str): Chave da conta origem
            ted_batch_key (str): Chave do lote TED
            request_control_key (str, optional): UUID da transação específica
            ted_status (str, optional): Status da transação TED
            date_from (str, optional): Data inicial (YYYY-MM-DD)
            date_to (str, optional): Data final (YYYY-MM-DD)
            page (int, optional): Número da página (padrão: 1)
            page_size (int, optional): Tamanho da página (padrão: 30, máximo: 30)
        """
        endpoint = f"/account/{account_key}/ted_batch/{ted_batch_key}/teds"
        
        params = {}
        if request_control_key:
            params["request_control_key"] = request_control_key
        if ted_status:
            params["ted_status"] = ted_status
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
        
        return self.client.get(endpoint, params=params)

    def send_ted_with_2fa(self, account_key, request_control_key, target_account, 
                         transaction_amount, approver_document_number, contact_type, session_id=None):
        """
        Realizar TED com autenticação de dois fatores
        
        Args:
            account_key (str): Chave da conta origem
            request_control_key (str): UUID v4 único da requisição
            target_account (dict): Dados da conta destino
            transaction_amount (float): Valor da transferência
            approver_document_number (str): CPF do aprovador
            contact_type (str): "email", "sms" ou "device"
            session_id (str, optional): UUID da sessão (obrigatório para device)
        """
        tfa_info = self.build_tfa_info(approver_document_number, contact_type, session_id)
        
        return self.send_ted(
            account_key=account_key,
            request_control_key=request_control_key,
            target_account=target_account,
            transaction_amount=transaction_amount,
            tfa_info=tfa_info
        )

    def approve_ted_2fa(self, account_key, ted_key, token=None):
        """
        Aprovar TED com token 2FA
        
        Args:
            account_key (str): Chave da conta origem
            ted_key (str): Chave da transferência TED
            token (str, optional): Token de 6 dígitos (obrigatório para email/sms)
        """
        endpoint = f"/account/{account_key}/ted/{ted_key}/validate_token"
        
        payload = {}
        if token:
            payload["token"] = token
        
        return self.client.put(endpoint, payload)

    def approve_ted_email_sms(self, account_key, ted_key, token):
        """
        Aprovar TED via email ou SMS com token
        
        Args:
            account_key (str): Chave da conta origem
            ted_key (str): Chave da transferência TED
            token (str): Token de 6 dígitos
        """
        return self.approve_ted_2fa(account_key, ted_key, token)

    def approve_ted_device(self, account_key, ted_key):
        """
        Aprovar TED via dispositivo (sem token)
        
        Args:
            account_key (str): Chave da conta origem
            ted_key (str): Chave da transferência TED
        """
        return self.approve_ted_2fa(account_key, ted_key)

    def resend_ted_token(self, account_key, ted_key, contact_type=None):
        """
        Solicitar reenvio de token para TED
        
        Args:
            account_key (str): Chave da conta origem
            ted_key (str): Chave da transferência TED
            contact_type (str, optional): "email" ou "sms" (se não informado, usa o original)
        """
        endpoint = f"/account/{account_key}/ted/{ted_key}/resend_token"
        
        payload = {}
        if contact_type:
            payload["contact_type"] = contact_type
        
        return self.client.patch(endpoint, payload)

    def resend_ted_token_email(self, account_key, ted_key):
        """
        Reenviar token TED por email
        
        Args:
            account_key (str): Chave da conta origem
            ted_key (str): Chave da transferência TED
        """
        return self.resend_ted_token(account_key, ted_key, "email")

    def resend_ted_token_sms(self, account_key, ted_key):
        """
        Reenviar token TED por SMS
        
        Args:
            account_key (str): Chave da conta origem
            ted_key (str): Chave da transferência TED
        """
        return self.resend_ted_token(account_key, ted_key, "sms")

    def build_target_account(self, account_branch, account_number, account_digit, 
                           owner_document_number, owner_name, ispb, account_type="checking_account"):
        """
        Helper para construir objeto target_account
        
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

    def build_ted_item(self, request_control_key, target_account, transaction_amount):
        """
        Helper para construir item TED para lote
        
        Args:
            request_control_key (str): UUID v4 único da transação
            target_account (dict): Dados da conta destino
            transaction_amount (float): Valor da transferência
        """
        return {
            "request_control_key": request_control_key,
            "target_account": target_account,
            "transaction_amount": transaction_amount
        }

    def build_tfa_info(self, approver_document_number, contact_type, session_id=None):
        """
        Helper para construir objeto tfa_info
        
        Args:
            approver_document_number (str): CPF do aprovador (11 dígitos)
            contact_type (str): "email", "sms" ou "device"
            session_id (str, optional): UUID da sessão (obrigatório para device)
        """
        tfa_info = {
            "approver_document_number": approver_document_number,
            "contact_type": contact_type
        }
        
        if session_id:
            tfa_info["session_id"] = session_id
        
        return tfa_info

    def build_tfa_info_batch(self, approver_document_number, contact_type):
        """
        Helper para construir objeto tfa_info para lote (sem session_id)
        
        Args:
            approver_document_number (str): CPF do aprovador (11 dígitos)
            contact_type (str): "email" ou "sms"
        """
        return {
            "approver_document_number": approver_document_number,
            "contact_type": contact_type
        }
    
    def approve_ted_batch_2fa(self, account_key, ted_batch_key, token):
        """
        Fase 9: Aprovar Transação em Lote com Autenticação de Dois Fatores
        
        Args:
            account_key (str): Chave da conta
            ted_batch_key (str): Chave do lote TED
            token (str): Código de autenticação (6 dígitos)
        """
        endpoint = f"/account/{account_key}/ted_batch/{ted_batch_key}/validate_token"
        
        payload = {
            "token": token
        }
        
        return self.client.make_request("PUT", endpoint, payload)
    
    def resend_ted_batch_token(self, account_key, ted_batch_key, contact_type=None):
        """
        Fase 10: Solicitar Reenvio de Token para uma Transação TED em Lote
        
        Args:
            account_key (str): Chave da conta
            ted_batch_key (str): Chave do lote TED
            contact_type (str, optional): "email" ou "sms". Se não informado, usa o original
        """
        endpoint = f"/account/{account_key}/ted_batch/{ted_batch_key}/resend_token"
        
        payload = {}
        if contact_type:
            payload["contact_type"] = contact_type
        
        return self.client.make_request("PATCH", endpoint, payload)
    
    def get_ted(self, account_key, ted_key, ted_direction):
        """
        Fase 18: Consultar TED
        
        Args:
            account_key (str): Chave da conta
            ted_key (str): Chave da TED
            ted_direction (str): "incoming" (entrada) ou "outgoing" (saída)
        """
        endpoint = f"/account/{account_key}/ted/{ted_key}/{ted_direction}"
        
        return self.client.make_request("GET", endpoint)
    
    def list_teds(self, account_key, ted_direction="outgoing", request_control_key=None, 
                  date_from=None, date_to=None, page=1, page_size=30):
        """
        Fase 19: Listar TEDs
        
        Args:
            account_key (str): Chave da conta
            ted_direction (str): "incoming" ou "outgoing" (padrão: outgoing)
            request_control_key (str, optional): Filtrar por chave de controle
            date_from (str, optional): Data inicial (YYYY-MM-DD)
            date_to (str, optional): Data final (YYYY-MM-DD)
            page (int): Número da página (padrão: 1)
            page_size (int): Tamanho da página (padrão: 30, máximo: 30)
        """
        endpoint = f"/account/{account_key}/teds"
        
        params = {
            "ted_direction": ted_direction,
            "page": page,
            "page_size": min(page_size, 30)
        }
        
        if request_control_key:
            params["request_control_key"] = request_control_key
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        
        return self.client.make_request("GET", endpoint, params=params)
    
    # Webhook Helpers - Fase 20
    def parse_ted_webhook(self, webhook_data):
        """
        Fase 20: Parser para webhooks TED
        
        Args:
            webhook_data (dict): Dados do webhook recebido
            
        Returns:
            dict: Dados parseados do webhook
        """
        webhook_type = webhook_data.get("webhook_type")
        
        if webhook_type == "baas.ted.outgoing_ted":
            return self._parse_outgoing_ted_webhook(webhook_data)
        elif webhook_type == "baas.ted.incoming_ted":
            return self._parse_incoming_ted_webhook(webhook_data)
        else:
            return {"error": "Tipo de webhook TED não reconhecido"}
    
    def _parse_outgoing_ted_webhook(self, webhook_data):
        """Parser para webhook de TED enviada"""
        data = webhook_data.get("data", {})
        return {
            "webhook_type": "outgoing_ted",
            "webhook_datetime": webhook_data.get("webhook_datetime"),
            "ted_key": data.get("ted_key"),
            "account_key": data.get("account_key"),
            "ted_status": data.get("ted_status"),
            "transaction_amount": data.get("transaction_amount"),
            "fee_amount": data.get("fee_amount"),
            "target_account": data.get("target_account"),
            "refusal_reason": data.get("refusal_reason", {})
        }
    
    def _parse_incoming_ted_webhook(self, webhook_data):
        """Parser para webhook de TED recebida"""
        data = webhook_data.get("data", {})
        return {
            "webhook_type": "incoming_ted",
            "webhook_datetime": webhook_data.get("webhook_datetime"),
            "ted_key": data.get("ted_key"),
            "account_key": data.get("account_key"),
            "ted_status": data.get("ted_status"),
            "transaction_amount": data.get("transaction_amount"),
            "fee_amount": data.get("fee_amount"),
            "source_account": data.get("source_account"),
            "refusal_reason": data.get("refusal_reason", {})
        }
