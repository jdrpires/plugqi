# connectors/boleto_payment.py
from typing import Dict, Optional, Any
import uuid
from datetime import datetime

class BoletoPaymentConnector:
    def __init__(self, client):
        self.client = client

    def consultar_boleto_linha_digitavel(self, linha_digitavel: str, **kwargs) -> Dict[str, Any]:
        """Consulta boleto por linha digitável"""
        payload = {
            "digitable_line": linha_digitavel,
            **kwargs
        }
        return self.client.post("/bill_payment/consult", payload)

    def consultar_boleto_codigo_barras(self, codigo_barras: str, **kwargs) -> Dict[str, Any]:
        """Consulta boleto por código de barras"""
        payload = {
            "barcode": codigo_barras,
            **kwargs
        }
        return self.client.post("/bill_payment/consult", payload)

    def pagar_boleto_imediato(self, account_key: str, linha_digitavel: str, 
                             valor: float, request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Paga boleto imediatamente"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "digitable_line": linha_digitavel,
            "payment_amount": valor,
            "payment_date": datetime.now().strftime("%Y-%m-%d"),
            "payment_type": "immediate"
        }
        return self.client.post("/bill_payment/pay", payload)

    def agendar_pagamento_boleto(self, account_key: str, linha_digitavel: str, 
                                valor: float, data_pagamento: str, 
                                request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Agenda pagamento de boleto"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "digitable_line": linha_digitavel,
            "payment_amount": valor,
            "payment_date": data_pagamento,
            "payment_type": "scheduled"
        }
        return self.client.post("/bill_payment/schedule", payload)

    def consultar_status_pagamento(self, payment_key: str) -> Dict[str, Any]:
        """Consulta status de um pagamento"""
        return self.client.get(f"/bill_payment/{payment_key}")

    def cancelar_agendamento(self, payment_key: str, request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Cancela agendamento de pagamento"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4())
        }
        return self.client.delete(f"/bill_payment/{payment_key}", params=payload)

    def listar_pagamentos(self, account_key: str, **filters) -> Dict[str, Any]:
        """Lista pagamentos da conta"""
        params = {
            "account_key": account_key,
            **filters
        }
        return self.client.get("/bill_payment", params=params)

    # Helpers
    def validar_linha_digitavel(self, linha_digitavel: str) -> bool:
        """Valida formato da linha digitável"""
        # Remove espaços e pontos
        linha_limpa = linha_digitavel.replace(" ", "").replace(".", "")
        
        # Deve ter 47 dígitos para boleto bancário
        if len(linha_limpa) != 47:
            return False
        
        # Deve conter apenas números
        if not linha_limpa.isdigit():
            return False
        
        return True

    def validar_codigo_barras(self, codigo_barras: str) -> bool:
        """Valida formato do código de barras"""
        # Remove espaços
        codigo_limpo = codigo_barras.replace(" ", "")
        
        # Deve ter 44 dígitos
        if len(codigo_limpo) != 44:
            return False
        
        # Deve conter apenas números
        if not codigo_limpo.isdigit():
            return False
        
        return True

    def extrair_valor_linha_digitavel(self, linha_digitavel: str) -> float:
        """Extrai valor da linha digitável"""
        linha_limpa = linha_digitavel.replace(" ", "").replace(".", "")
        
        if len(linha_limpa) == 47:
            # Últimos 10 dígitos representam o valor em centavos
            valor_centavos = int(linha_limpa[-10:])
            return valor_centavos / 100.0
        
        return 0.0

    def build_pagamento_payload(self, account_key: str, linha_digitavel: str, 
                               valor: float, data_pagamento: str = None, 
                               request_control_key: str = None) -> Dict[str, Any]:
        """Helper para criar payload de pagamento"""
        return {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "digitable_line": linha_digitavel,
            "payment_amount": valor,
            "payment_date": data_pagamento or datetime.now().strftime("%Y-%m-%d"),
            "payment_type": "immediate" if not data_pagamento else "scheduled"
        }
