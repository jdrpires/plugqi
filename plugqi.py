from .connectors.credit import CreditConnector
from .connectors.payment import PaymentConnector

class PlugQi:
    def __init__(self):
        self.credit = CreditConnector()
        self.payment = PaymentConnector()
    
    def health_check(self):
        """Verifica se a API está funcionando"""
        try:
            response = self.credit._make_request('GET', '/health')
            return response.get('status') == 'ok'
        except Exception:
            return False
