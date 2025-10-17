# connectors/pix.py
from typing import Dict, Optional, Any, List
import uuid
from datetime import datetime

class PixConnector:
    def __init__(self, client):
        self.client = client

    # Gestão de Chaves PIX
    def criar_chave_pix(self, account_key: str, tipo_chave: str, valor_chave: str, 
                       request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Cria nova chave PIX"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "pix_key_type": tipo_chave,
            "pix_key_value": valor_chave
        }
        return self.client.post("/pix/keys", payload)

    def listar_chaves_pix(self, account_key: str) -> Dict[str, Any]:
        """Lista chaves PIX da conta"""
        return self.client.get(f"/pix/keys", params={"account_key": account_key})

    def deletar_chave_pix(self, pix_key: str, request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Deleta chave PIX"""
        payload = {"request_control_key": request_control_key or str(uuid.uuid4())}
        return self.client.delete(f"/pix/keys/{pix_key}", params=payload)

    # Claim e Portabilidade
    def claim_chave_pix(self, account_key: str, pix_key: str, tipo_claim: str,
                       request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Faz claim de chave PIX"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "pix_key": pix_key,
            "claim_type": tipo_claim
        }
        return self.client.post("/pix/keys/claim", payload)

    def portabilidade_chave_pix(self, account_key: str, pix_key: str, tipo_portabilidade: str,
                               request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Solicita portabilidade de chave PIX"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "pix_key": pix_key,
            "portability_type": tipo_portabilidade
        }
        return self.client.post("/pix/keys/portability", payload)

    # Envios PIX
    def enviar_pix_chave(self, account_key: str, pix_key: str, valor: float, 
                        descricao: str = "", request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia PIX por chave"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "pix_key": pix_key,
            "amount": valor,
            "description": descricao
        }
        return self.client.post("/pix/payments", payload)

    def enviar_pix_dados(self, account_key: str, dados_destinatario: Dict[str, Any], 
                        valor: float, descricao: str = "", 
                        request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia PIX por dados bancários"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "recipient_data": dados_destinatario,
            "amount": valor,
            "description": descricao
        }
        return self.client.post("/pix/payments", payload)

    # QR Code PIX
    def criar_qr_code_estatico(self, account_key: str, pix_key: str, valor: float,
                              descricao: str = "", request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Cria QR Code PIX estático"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "pix_key": pix_key,
            "amount": valor,
            "description": descricao,
            "qr_type": "static"
        }
        return self.client.post("/pix/qr-codes", payload)

    def criar_qr_code_dinamico(self, account_key: str, pix_key: str, valor: float,
                              descricao: str = "", expiracao: Optional[str] = None,
                              request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Cria QR Code PIX dinâmico"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            "pix_key": pix_key,
            "amount": valor,
            "description": descricao,
            "qr_type": "dynamic",
            "expiration_date": expiracao
        }
        return self.client.post("/pix/qr-codes", payload)

    def consultar_qr_code(self, qr_code_key: str) -> Dict[str, Any]:
        """Consulta QR Code PIX"""
        return self.client.get(f"/pix/qr-codes/{qr_code_key}")

    # Limites PIX
    def consultar_limites_pix(self, account_key: str) -> Dict[str, Any]:
        """Consulta limites PIX da conta"""
        return self.client.get(f"/pix/limits", params={"account_key": account_key})

    def configurar_limites_pix(self, account_key: str, limites: Dict[str, float],
                              request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Configura limites PIX"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "account_key": account_key,
            **limites
        }
        return self.client.post("/pix/limits", payload)

    # Consultas e Histórico
    def consultar_transacao_pix(self, transaction_id: str) -> Dict[str, Any]:
        """Consulta transação PIX por ID"""
        return self.client.get(f"/pix/transactions/{transaction_id}")

    def listar_transacoes_pix(self, account_key: str, **filters) -> Dict[str, Any]:
        """Lista transações PIX da conta"""
        params = {"account_key": account_key, **filters}
        return self.client.get("/pix/transactions", params=params)

    def gerar_comprovante_pix(self, transaction_id: str) -> Dict[str, Any]:
        """Gera comprovante de transação PIX"""
        return self.client.get(f"/pix/transactions/{transaction_id}/receipt")

    # Helpers
    def validar_chave_pix(self, tipo: str, valor: str) -> bool:
        """Valida formato de chave PIX"""
        import re
        
        if tipo == "cpf":
            # Remove formatação e valida 11 dígitos
            cpf = re.sub(r'[^0-9]', '', valor)
            return len(cpf) == 11 and cpf.isdigit()
        
        elif tipo == "cnpj":
            # Remove formatação e valida 14 dígitos
            cnpj = re.sub(r'[^0-9]', '', valor)
            return len(cnpj) == 14 and cnpj.isdigit()
        
        elif tipo == "email":
            # Validação básica de email
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, valor))
        
        elif tipo == "telefone":
            # Formato +5511999887766
            phone_pattern = r'^\+55\d{10,11}$'
            return bool(re.match(phone_pattern, valor))
        
        elif tipo == "aleatoria":
            # UUID v4
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
            return bool(re.match(uuid_pattern, valor, re.IGNORECASE))
        
        return False

    def build_dados_destinatario(self, nome: str, documento: str, banco: str, 
                                agencia: str, conta: str, tipo_conta: str = "checking") -> Dict[str, Any]:
        """Helper para criar dados do destinatário"""
        return {
            "name": nome,
            "document": documento,
            "bank_code": banco,
            "branch": agencia,
            "account": conta,
            "account_type": tipo_conta
        }

    def extrair_end_to_end_id(self, response: Dict[str, Any]) -> Optional[str]:
        """Extrai End-to-End ID da resposta"""
        return response.get("end_to_end_id")

    def get_tabela_erros_pix(self) -> Dict[str, Any]:
        """Retorna tabela de erros PIX BACEN/SPB/MED"""
        return {
            "bacen": {
                "AB03": "Liquidação da transação interrompida devido a timeout no SPI",
                "AC03": "Conta do recebedor inválida ou inexistente", 
                "AG03": "Falha na validação do CPF/CNPJ",
                "AM04": "Saldo insuficiente",
                "BE08": "Chave PIX não encontrada",
                "CH16": "Chave PIX bloqueada",
                "DS04": "Ordem rejeitada pelo participante recebedor"
            },
            "spb": {
                "DS04": "Ordem rejeitada pelo participante recebedor",
                "FF01": "Transação inválida ou malformada",
                "RR04": "Regulamentação não permite a transação"
            },
            "med": {
                "MD06": "Solicitação de devolução por suspeita de fraude",
                "SL02": "Devolução por solicitação do recebedor",
                "FR01": "Devolução por fraude confirmada"
            }
        }
