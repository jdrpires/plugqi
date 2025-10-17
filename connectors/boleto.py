# connectors/boleto.py
from typing import Dict, List, Optional, Any

class BoletoConnector:
    def __init__(self, client):
        self.client = client

    # Carteiras de cobrança
    def list_requester_profiles(self, account_key: str, **params) -> Dict[str, Any]:
        """Lista carteiras de cobrança da conta"""
        return self.client.get(f"/account/{account_key}/requester_profiles", params=params)

    def create_requester_profile(self, account_key: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova carteira de cobrança"""
        return self.client.post(f"/account/{account_key}/requester_profile", profile_data)

    # Boletos únicos
    def create_boleto(self, account_key: str, requester_profile_key: str, boleto_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria boleto único (padrão - assíncrono)"""
        return self.client.post(f"/account/{account_key}/requester_profile/{requester_profile_key}/bank_slip", boleto_data)

    def create_boleto_instant(self, account_key: str, requester_profile_key: str, boleto_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria boleto único (instantâneo - síncrono)"""
        return self.client.post(f"/account/{account_key}/requester_profile/{requester_profile_key}/bank_slip/instant", boleto_data)

    def create_boletos_batch(self, account_key: str, requester_profile_key: str, boletos_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria boletos em lote"""
        return self.client.post(f"/account/{account_key}/requester_profile/{requester_profile_key}/bank_slip/batch", boletos_data)

    # Consultas
    def get_boleto(self, account_key: str, bank_slip_key: str) -> Dict[str, Any]:
        """Consulta boleto por chave"""
        return self.client.get(f"/account/{account_key}/bank_slip/{bank_slip_key}")

    def list_boletos(self, account_key: str, **params) -> Dict[str, Any]:
        """Lista boletos da conta"""
        return self.client.get(f"/account/{account_key}/bank_slip", params=params)

    # Helpers para criar payloads
    def build_payer_data(self, name: str, document: str, person_type: str = "natural", 
                        email: Optional[str] = None, phone: Optional[Dict] = None, 
                        address: Optional[Dict] = None) -> Dict[str, Any]:
        """Helper para criar dados do pagador"""
        payer = {
            "name": name,
            "document_number": document,
            "person_type": person_type
        }
        if email or phone:
            payer["contact"] = {}
            if email:
                payer["contact"]["email"] = email
            if phone:
                payer["contact"]["phone"] = phone
        if address:
            payer["address"] = address
        return payer

    def build_simple_boleto(self, request_control_key: str, amount: float, expiration: str, 
                           payer_name: str, payer_document: str, **kwargs) -> Dict[str, Any]:
        """Helper para criar boleto simples"""
        return {
            "request_control_key": request_control_key,
            "amount": amount,
            "expiration": expiration,
            "payer_data": self.build_payer_data(payer_name, payer_document),
            **kwargs
        }
