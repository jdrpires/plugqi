# connectors/pix.py
from typing import Dict, Optional, Any, List
import uuid
from datetime import datetime

class PixConnector:
    def __init__(self, client):
        self.client = client

    # ========== CONSULTA DE CHAVE PIX ==========
    
    def consultar_chave_pix(self, pix_key: str) -> Dict[str, Any]:
        """Consulta chave PIX para obter end_to_end_id e dados do destinatário"""
        return self.client.get(f"/pix_key/{pix_key}")

    # ========== TRANSFERÊNCIAS PIX ==========
    
    def enviar_pix_chave(self, account_key: str, target_pix_key: str, transaction_amount: float,
                        end_to_end_id: str, pix_message: str = "", 
                        request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia PIX por chave PIX"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "pix_transfer_type": "key",
            "target_pix_key": target_pix_key,
            "transaction_amount": transaction_amount,
            "end_to_end_id": end_to_end_id,
            "pix_message": pix_message
        }
        return self.client.post(f"/account/{account_key}/pix_transfer", payload)
    
    def enviar_pix_manual(self, account_key: str, target_account: Dict[str, Any], 
                         transaction_amount: float, pix_message: str = "",
                         request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia PIX por dados bancários (manual)"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "pix_transfer_type": "manual",
            "target_account": target_account,
            "transaction_amount": transaction_amount,
            "pix_message": pix_message
        }
        return self.client.post(f"/account/{account_key}/pix_transfer", payload)
    
    def enviar_pix_qr_estatico(self, account_key: str, target_pix_key: str, 
                              transaction_amount: float, end_to_end_id: str,
                              receiver_conciliation_id: str = "", pix_message: str = "",
                              request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia PIX por QR Code estático"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "pix_transfer_type": "static_qr_code",
            "target_pix_key": target_pix_key,
            "transaction_amount": transaction_amount,
            "end_to_end_id": end_to_end_id,
            "pix_message": pix_message
        }
        if receiver_conciliation_id:
            payload["receiver_conciliation_id"] = receiver_conciliation_id
        return self.client.post(f"/account/{account_key}/pix_transfer", payload)
    
    def enviar_pix_qr_dinamico(self, account_key: str, target_pix_key: str,
                              transaction_amount: float, end_to_end_id: str,
                              receiver_conciliation_id: str, pix_message: str = "",
                              request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia PIX por QR Code dinâmico"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "pix_transfer_type": "dynamic_qr_code",
            "target_pix_key": target_pix_key,
            "receiver_conciliation_id": receiver_conciliation_id,
            "transaction_amount": transaction_amount,
            "end_to_end_id": end_to_end_id,
            "pix_message": pix_message
        }
        return self.client.post(f"/account/{account_key}/pix_transfer", payload)

    # ========== DEVOLUÇÃO PIX ==========
    
    def solicitar_devolucao_pix(self, account_key: str, pix_transfer_key: str,
                               reversal_amount: float, reversal_reason: str,
                               reversal_message: str = "",
                               request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Solicita devolução de PIX recebido"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "reversal_amount": reversal_amount,
            "reversal_reason": reversal_reason,
            "reversal_message": reversal_message
        }
        return self.client.post(f"/account/{account_key}/pix_transfer/{pix_transfer_key}/reversal", payload)

    # ========== CONSULTAS ==========
    
    def consultar_transferencia_pix(self, account_key: str, pix_transfer_key: str,
                                   direction: str = "outgoing") -> Dict[str, Any]:
        """Consulta transferência PIX específica"""
        return self.client.get(f"/account/{account_key}/pix_transfer/{pix_transfer_key}/{direction}")
    
    def listar_transferencias_pix(self, account_key: str, direction: str = "outgoing",
                                 **filters) -> Dict[str, Any]:
        """Lista transferências PIX da conta"""
        params = {"pix_transfer_direction": direction, **filters}
        return self.client.get(f"/account/{account_key}/pix_transfers", params=params)

    # ========== PIX EM LOTE ==========
    
    def enviar_pix_lote(self, account_key: str, pix_transfers: List[Dict[str, Any]],
                       request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Envia múltiplas transferências PIX em lote"""
        payload = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "pix_transfers": pix_transfers
        }
        return self.client.post(f"/account/{account_key}/pix_transfer_batch", payload)
    
    def listar_lotes_pix(self, account_key: str, **filters) -> Dict[str, Any]:
        """Lista transações em lote de uma conta"""
        return self.client.get(f"/account/{account_key}/pix_transfer_batches", params=filters)
    
    def consultar_lote_pix(self, account_key: str, pix_transfer_batch_key: str) -> Dict[str, Any]:
        """Consulta transação em lote específica"""
        return self.client.get(f"/account/{account_key}/pix_transfer_batch/{pix_transfer_batch_key}")
    
    def listar_transferencias_lote(self, account_key: str, pix_transfer_batch_key: str,
                                  **filters) -> Dict[str, Any]:
        """Lista transferências de um lote específico"""
        return self.client.get(f"/account/{account_key}/pix_transfer_batch/{pix_transfer_batch_key}/pix_transfers", 
                              params=filters)

    # ========== HELPERS ==========
    
    def build_dados_destinatario(self, nome: str, documento: str, banco: str, 
                                agencia: str, conta: str, tipo_conta: str = "checking_account") -> Dict[str, Any]:
        """Helper para criar dados do destinatário (compatibilidade)"""
        return self.build_target_account(
            account_branch=agencia,
            account_digit="",  # Será extraído da conta se necessário
            account_number=conta,
            owner_document_number=documento,
            owner_name=nome,
            account_type=tipo_conta,
            ispb=banco
        )

    def build_target_account(self, account_branch: str, account_digit: str, account_number: str,
                           owner_document_number: str, owner_name: str, account_type: str,
                           ispb: str) -> Dict[str, Any]:
        """Helper para construir dados da conta destino"""
        return {
            "account_branch": account_branch,
            "account_digit": account_digit,
            "account_number": account_number,
            "owner_document_number": owner_document_number,
            "owner_name": owner_name,
            "account_type": account_type,
            "ispb": ispb
        }
    
    def build_pix_transfer_lote(self, pix_transfer_type: str, transaction_amount: float,
                               target_pix_key: str = "", target_account: Dict[str, Any] = None,
                               end_to_end_id: str = "", receiver_conciliation_id: str = "",
                               pix_message: str = "", request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Helper para construir item de PIX em lote"""
        transfer = {
            "request_control_key": request_control_key or str(uuid.uuid4()),
            "pix_transfer_type": pix_transfer_type,
            "transaction_amount": transaction_amount,
            "pix_message": pix_message
        }
        
        if target_pix_key:
            transfer["target_pix_key"] = target_pix_key
        if target_account:
            transfer["target_account"] = target_account
        if end_to_end_id:
            transfer["end_to_end_id"] = end_to_end_id
        if receiver_conciliation_id:
            transfer["receiver_conciliation_id"] = receiver_conciliation_id
            
        return transfer

    # ========== VALIDAÇÕES ==========
    
    def validar_chave_pix(self, tipo: str, valor: str) -> bool:
        """Valida formato de chave PIX"""
        import re
        
        if tipo == "cpf":
            cpf = re.sub(r'[^0-9]', '', valor)
            return len(cpf) == 11 and cpf.isdigit()
        elif tipo == "cnpj":
            cnpj = re.sub(r'[^0-9]', '', valor)
            return len(cnpj) == 14 and cnpj.isdigit()
        elif tipo == "email":
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, valor))
        elif tipo == "telefone":
            phone_pattern = r'^\+55\d{10,11}$'
            return bool(re.match(phone_pattern, valor))
        elif tipo == "aleatoria":
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
            return bool(re.match(uuid_pattern, valor, re.IGNORECASE))
        return False

    def get_account_types(self) -> Dict[str, str]:
        """Retorna tipos de conta disponíveis"""
        return {
            "checking_account": "Conta Corrente",
            "salary_account": "Conta Salário", 
            "saving_account": "Conta Poupança",
            "payment_account": "Conta de Pagamentos"
        }

    def get_reversal_reasons(self) -> Dict[str, str]:
        """Retorna motivos de devolução disponíveis"""
        return {
            "client_request": "Solicitação do cliente",
            "reconciliation": "Reconciliação por erro operacional"
        }

    def get_transfer_types(self) -> Dict[str, str]:
        """Retorna tipos de transferência PIX"""
        return {
            "manual": "PIX por dados bancários",
            "key": "PIX por chave PIX",
            "static_qr_code": "PIX por QR Code estático",
            "dynamic_qr_code": "PIX por QR Code dinâmico",
            "reversal": "Devolução PIX"
        }

    # ========== MÉTODOS LEGADOS (COMPATIBILIDADE) ==========
    
    def criar_chave_pix(self, account_key: str, tipo_chave: str, valor_chave: str, 
                       request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """MÉTODO LEGADO - Funcionalidade não disponível na API atual"""
        raise NotImplementedError("Gestão de chaves PIX não disponível na API QiTech atual")
    
    def listar_chaves_pix(self, account_key: str) -> Dict[str, Any]:
        """MÉTODO LEGADO - Funcionalidade não disponível na API atual"""
        raise NotImplementedError("Gestão de chaves PIX não disponível na API QiTech atual")
    
    def deletar_chave_pix(self, pix_key: str, request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """MÉTODO LEGADO - Funcionalidade não disponível na API atual"""
        raise NotImplementedError("Gestão de chaves PIX não disponível na API QiTech atual")
    
    def criar_qr_code_estatico(self, account_key: str, pix_key: str, valor: float,
                              descricao: str = "", request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """MÉTODO LEGADO - Funcionalidade não disponível na API atual"""
        raise NotImplementedError("Criação de QR Code não disponível na API QiTech atual")
    
    def criar_qr_code_dinamico(self, account_key: str, pix_key: str, valor: float,
                              descricao: str = "", expiracao: Optional[str] = None,
                              request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """MÉTODO LEGADO - Funcionalidade não disponível na API atual"""
        raise NotImplementedError("Criação de QR Code não disponível na API QiTech atual")

    # ========== MÉTODOS SIMPLIFICADOS ==========
    
    def enviar_pix_automatico(self, account_key: str, pix_key: str, valor: float,
                             descricao: str = "", request_control_key: Optional[str] = None) -> Dict[str, Any]:
        """Método automatizado: consulta chave PIX + envia transferência"""
        try:
            # 1. Consulta a chave PIX para obter end_to_end_id
            consulta = self.consultar_chave_pix(pix_key)
            end_to_end_id = consulta.get('end_to_end_id')
            
            if not end_to_end_id:
                raise ValueError("end_to_end_id não encontrado na consulta da chave PIX")
            
            # 2. Envia o PIX com o end_to_end_id obtido
            return self.enviar_pix_chave(
                account_key=account_key,
                target_pix_key=pix_key,
                transaction_amount=valor,
                end_to_end_id=end_to_end_id,
                pix_message=descricao,
                request_control_key=request_control_key
            )
            
        except Exception as e:
            return {"error": f"Erro no PIX automático: {str(e)}"}
    
    def enviar_pix_simples(self, account_key: str, pix_key: str, valor: float, 
                          end_to_end_id: str, descricao: str = "") -> Dict[str, Any]:
        """Método simplificado para enviar PIX por chave (com end_to_end_id conhecido)"""
        return self.enviar_pix_chave(
            account_key=account_key,
            target_pix_key=pix_key,
            transaction_amount=valor,
            end_to_end_id=end_to_end_id,
            pix_message=descricao
        )
    
    def enviar_pix_dados_bancarios(self, account_key: str, agencia: str, conta: str, 
                                  digito: str, documento: str, nome: str, 
                                  tipo_conta: str, ispb: str, valor: float,
                                  descricao: str = "") -> Dict[str, Any]:
        """Método simplificado para enviar PIX por dados bancários"""
        target_account = self.build_target_account(
            account_branch=agencia,
            account_digit=digito,
            account_number=conta,
            owner_document_number=documento,
            owner_name=nome,
            account_type=tipo_conta,
            ispb=ispb
        )
        
        return self.enviar_pix_manual(
            account_key=account_key,
            target_account=target_account,
            transaction_amount=valor,
            pix_message=descricao
        )
