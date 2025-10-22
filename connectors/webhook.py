# connectors/webhook.py
from typing import Dict, Any, Optional, Callable
import json
from datetime import datetime

class WebhookConnector:
    def __init__(self, client):
        self.client = client
        self.handlers = {}
        
    # Configuração de Webhooks
    def configurar_webhook(self, account_key: str, webhook_url: str, 
                          eventos: list, request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Configura webhook na QiTech"""
        import uuid
        
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "webhook_url": webhook_url,
            "events": eventos,
            "enabled": True
        }
        return self.client.post("/webhooks", payload)
    
    def listar_webhooks(self, account_key: str) -> Dict[str, Any]:
        """Lista webhooks configurados"""
        return self.client.get("/webhooks", params={"account_key": account_key})
    
    def atualizar_webhook(self, webhook_key: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza configuração de webhook"""
        return self.client.patch(f"/webhooks/{webhook_key}", dados)
    
    def deletar_webhook(self, webhook_key: str) -> Dict[str, Any]:
        """Remove webhook"""
        return self.client.delete(f"/webhooks/{webhook_key}")
    
    # Processamento de Webhooks Recebidos
    def processar_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa webhook recebido da QiTech"""
        webhook_type = payload.get("webhook_type")
        
        if webhook_type in self.handlers:
            return self.handlers[webhook_type](payload)
        else:
            return self.processar_webhook_generico(payload)
    
    def processar_webhook_generico(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processamento genérico de webhook"""
        return {
            "processed": True,
            "webhook_type": payload.get("webhook_type"),
            "timestamp": datetime.now().isoformat(),
            "data": payload
        }
    
    # Handlers Específicos
    def registrar_handler(self, webhook_type: str, handler_func: Callable):
        """Registra handler para tipo específico de webhook"""
        self.handlers[webhook_type] = handler_func
    
    def handler_boleto_liquidacao(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para liquidação de boletos"""
        data = payload.get("data", {})
        
        return {
            "processed": True,
            "type": "bank_slip_payment",
            "bank_slip_key": data.get("bank_slip_key"),
            "status": data.get("bank_slip_status"),
            "payment_amount": data.get("payment_amount"),
            "payment_date": data.get("payment_date"),
            "processed_at": datetime.now().isoformat()
        }
    
    def handler_pix_recebido(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para PIX recebido"""
        data = payload.get("data", {})
        
        return {
            "processed": True,
            "type": "pix_received",
            "transaction_id": data.get("transaction_id"),
            "amount": data.get("amount"),
            "sender_name": data.get("sender_name"),
            "end_to_end_id": data.get("end_to_end_id"),
            "processed_at": datetime.now().isoformat()
        }
    
    def handler_abertura_conta(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para mudança de status de abertura de conta"""
        data = payload.get("data", {})
        
        return {
            "processed": True,
            "type": "account_request_status_change",
            "account_request_key": data.get("account_request_key"),
            "status": payload.get("status"),
            "account_key": data.get("account_key"),
            "processed_at": datetime.now().isoformat()
        }
    
    # Validações
    def validar_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Valida assinatura do webhook"""
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def validar_webhook_payload(self, payload: Dict[str, Any]) -> bool:
        """Valida estrutura do payload do webhook"""
        campos_obrigatorios = ["webhook_type", "event_datetime", "key"]
        
        for campo in campos_obrigatorios:
            if campo not in payload:
                return False
        
        return True
    
    # Helpers
    def get_tipos_webhook_suportados(self) -> Dict[str, str]:
        """Retorna tipos de webhook suportados"""
        return {
            "bank_slip.status_change": "Mudança de status do boleto",
            "bank_slip.payment": "Pagamento de boleto",
            "pix.received": "PIX recebido",
            "pix.sent": "PIX enviado",
            "pix.failed": "PIX falhou",
            "account_request.status_change": "Mudança de status de abertura de conta",
            "payment.confirmation": "Confirmação de pagamento",
            "payment.failed": "Falha de pagamento"
        }
    
    def criar_resposta_webhook(self, sucesso: bool = True, mensagem: str = "OK") -> Dict[str, Any]:
        """Cria resposta padrão para webhook"""
        return {
            "success": sucesso,
            "message": mensagem,
            "timestamp": datetime.now().isoformat()
        }
    
    def log_webhook(self, payload: Dict[str, Any], response: Dict[str, Any]):
        """Log do webhook processado"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "webhook_type": payload.get("webhook_type"),
            "key": payload.get("key"),
            "processed": response.get("processed", False),
            "payload": payload,
            "response": response
        }
        
        # Salva log (em produção, usar sistema de log adequado)
        try:
            with open("webhook_logs.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Falha silenciosa no log
        
        return log_entry
