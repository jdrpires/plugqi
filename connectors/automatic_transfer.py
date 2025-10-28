class AutomaticTransferConnector:
    def __init__(self, client):
        self.client = client
        self.base_path = "/baas/automatic_transfer"

    def create_transfer_rule(self, rule_data):
        """
        Criar regra de movimentação automática
        
        Args:
            rule_data (dict): Dados da regra com campos obrigatórios:
                - transfer_cronstring: Frequência CRON
                - account_key: UUID da conta origem
                - rule: "split_percentage", "split_equal" ou "single_beneficiary"
                - rule_configuration: Configuração da regra
                - is_active: True/False
        """
        endpoint = f"{self.base_path}/transfer_configuration"
        return self.client.post(endpoint, rule_data)

    def update_transfer_rule(self, rule_data):
        """
        Atualizar regra de movimentação automática
        
        Args:
            rule_data (dict): Dados da regra incluindo automatic_transfer_key
        """
        endpoint = f"{self.base_path}/transfer_configuration"
        return self.client.put(endpoint, rule_data)

    def create_split_percentage_rule(self, account_key, destinations, transfer_cronstring="0 0 * * *", remaining_balance=0, is_active=True):
        """
        Criar regra de divisão percentual
        
        Args:
            account_key (str): UUID da conta origem
            destinations (list): Lista de destinos com percentage
            transfer_cronstring (str): Frequência CRON (padrão: diário às 00:00)
            remaining_balance (float): Saldo que permanece na conta
            is_active (bool): Se a regra está ativa
        """
        rule_data = {
            "transfer_cronstring": transfer_cronstring,
            "account_key": account_key,
            "rule_configuration": {
                "destinations": destinations,
                "remaining_balance": remaining_balance
            },
            "is_active": is_active,
            "rule": "split_percentage"
        }
        return self.create_transfer_rule(rule_data)

    def create_split_equal_rule(self, account_key, destinations, transfer_cronstring="0 0 * * *", remaining_balance=0, is_active=True):
        """
        Criar regra de divisão igualitária
        
        Args:
            account_key (str): UUID da conta origem
            destinations (list): Lista de destinos (sem percentage)
            transfer_cronstring (str): Frequência CRON (padrão: diário às 00:00)
            remaining_balance (float): Saldo que permanece na conta
            is_active (bool): Se a regra está ativa
        """
        rule_data = {
            "transfer_cronstring": transfer_cronstring,
            "account_key": account_key,
            "rule_configuration": {
                "destinations": destinations,
                "remaining_balance": remaining_balance
            },
            "is_active": is_active,
            "rule": "split_equal"
        }
        return self.create_transfer_rule(rule_data)

    def create_single_beneficiary_rule(self, account_key, destination, transfer_cronstring="0 0 * * *", remaining_balance=0, is_active=True):
        """
        Criar regra de beneficiário único
        
        Args:
            account_key (str): UUID da conta origem
            destination (dict): Dados do beneficiário único
            transfer_cronstring (str): Frequência CRON (padrão: diário às 00:00)
            remaining_balance (float): Saldo que permanece na conta
            is_active (bool): Se a regra está ativa
        """
        rule_data = {
            "transfer_cronstring": transfer_cronstring,
            "account_key": account_key,
            "rule_configuration": {
                "destination": destination,
                "remaining_balance": remaining_balance
            },
            "is_active": is_active,
            "rule": "single_beneficiary"
        }
        return self.create_transfer_rule(rule_data)

    def deactivate_rule(self, automatic_transfer_key, rule_type, rule_configuration, transfer_cronstring="0 0 * * *"):
        """
        Desativar regra de movimentação automática
        
        Args:
            automatic_transfer_key (str): UUID da regra a ser desativada
            rule_type (str): Tipo da regra
            rule_configuration (dict): Configuração atual da regra
            transfer_cronstring (str): Frequência CRON
        """
        rule_data = {
            "transfer_cronstring": transfer_cronstring,
            "automatic_transfer_key": automatic_transfer_key,
            "rule_configuration": rule_configuration,
            "is_active": False,
            "rule": rule_type
        }
        return self.update_transfer_rule(rule_data)

    def build_destination(self, account_branch, account_number, account_digit, document_number, name, financial_institutions_code_number, percentage=None, is_pix_transfer=False):
        """
        Helper para construir objeto destination
        
        Args:
            account_branch (str): Agência
            account_number (str): Número da conta
            account_digit (str): Dígito da conta
            document_number (str): CPF/CNPJ
            name (str): Nome/Razão social
            financial_institutions_code_number (str): Código COMPE
            percentage (int): Percentual (apenas para split_percentage)
            is_pix_transfer (bool): Se é transferência PIX
        """
        destination = {
            "account_branch": account_branch,
            "account_number": account_number,
            "account_digit": account_digit,
            "document_number": document_number,
            "name": name,
            "financial_institutions_code_number": financial_institutions_code_number
        }
        
        if percentage is not None:
            destination["percentage"] = percentage
            
        if is_pix_transfer:
            destination["is_pix_transfer"] = is_pix_transfer
            
        return destination
