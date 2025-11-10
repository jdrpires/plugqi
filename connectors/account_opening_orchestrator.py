"""
Orquestrador para Abertura de Conta
Gerencia o fluxo completo: upload documentos → validação → criação conta → verificação status
"""

import time
import uuid
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime


class AccountStatus(Enum):
    PENDING_DOCUMENTS = "pending_documents"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    ACCOUNT_REQUESTED = "account_requested"
    PENDING_KYC = "pending_kyc_analysis"
    PENDING_ADDITIONAL_DATA = "pending_additional_data"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"


class AccountOpeningOrchestrator:
    def __init__(self, plugqi_client):
        self.client = plugqi_client
        self.document_upload = plugqi_client.document_upload
        self.account_opening = plugqi_client.account_opening
        self.webhook = plugqi_client.webhook if hasattr(plugqi_client, 'webhook') else None
        
    def create_account_pf_complete(self, person_data: Dict[str, Any], 
                                  documents_paths: Dict[str, str]) -> Dict[str, Any]:
        """
        Fluxo completo de abertura de conta PF
        1. Upload documentos
        2. Validação
        3. Criação conta
        4. Monitoramento status
        """
        workflow_id = str(uuid.uuid4())
        
        result = {
            "workflow_id": workflow_id,
            "status": AccountStatus.PENDING_DOCUMENTS.value,
            "steps": [],
            "account_request_key": None,
            "documents": {},
            "errors": [],
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Etapa 1: Upload de Documentos
            result["steps"].append({"step": "upload_documents", "status": "started", "timestamp": datetime.now().isoformat()})
            
            documents_uploaded = self._upload_documents(documents_paths)
            result["documents"] = documents_uploaded
            result["status"] = AccountStatus.DOCUMENTS_UPLOADED.value
            
            result["steps"].append({"step": "upload_documents", "status": "completed", "timestamp": datetime.now().isoformat()})
            
            # Etapa 2: Validação de Documentos
            result["steps"].append({"step": "validate_documents", "status": "started", "timestamp": datetime.now().isoformat()})
            
            validation_result = self._validate_documents(documents_uploaded)
            if not validation_result["valid"]:
                result["errors"].extend(validation_result["errors"])
                result["status"] = AccountStatus.ERROR.value
                return result
                
            result["steps"].append({"step": "validate_documents", "status": "completed", "timestamp": datetime.now().isoformat()})
            
            # Etapa 3: Criação da Conta
            result["steps"].append({"step": "create_account", "status": "started", "timestamp": datetime.now().isoformat()})
            
            account_response = self.account_opening.reservar_conta_escrow_pf(
                document_number=person_data["document_number"],
                email=person_data["email"],
                birthdate=person_data["birthdate"],
                name=person_data["name"],
                documents=documents_uploaded,
                face_key=documents_uploaded.get("face_key", "")
            )
            
            result["account_request_key"] = account_response.get("account_request_key")
            result["status"] = AccountStatus.ACCOUNT_REQUESTED.value
            
            result["steps"].append({"step": "create_account", "status": "completed", "timestamp": datetime.now().isoformat()})
            
            # Etapa 4: Monitoramento de Status
            result["steps"].append({"step": "monitor_status", "status": "started", "timestamp": datetime.now().isoformat()})
            
            final_status = self._monitor_account_status(result["account_request_key"])
            result["status"] = final_status
            result["final_account_data"] = self._get_account_details(result["account_request_key"])
            
            result["steps"].append({"step": "monitor_status", "status": "completed", "timestamp": datetime.now().isoformat()})
            
        except Exception as e:
            result["status"] = AccountStatus.ERROR.value
            result["errors"].append(f"Workflow error: {str(e)}")
            
        result["completed_at"] = datetime.now().isoformat()
        return result
    
    def create_account_pj_complete(self, company_data: Dict[str, Any],
                                  legal_representatives: List[Dict[str, Any]],
                                  documents_paths: Dict[str, str]) -> Dict[str, Any]:
        """
        Fluxo completo de abertura de conta PJ
        """
        workflow_id = str(uuid.uuid4())
        
        result = {
            "workflow_id": workflow_id,
            "status": AccountStatus.PENDING_DOCUMENTS.value,
            "steps": [],
            "account_request_key": None,
            "documents": {},
            "errors": [],
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Etapa 1: Upload de Documentos
            result["steps"].append({"step": "upload_documents", "status": "started", "timestamp": datetime.now().isoformat()})
            
            documents_uploaded = self._upload_documents(documents_paths)
            result["documents"] = documents_uploaded
            
            result["steps"].append({"step": "upload_documents", "status": "completed", "timestamp": datetime.now().isoformat()})
            
            # Etapa 2: Criação da Conta PJ
            result["steps"].append({"step": "create_account", "status": "started", "timestamp": datetime.now().isoformat()})
            
            account_response = self.account_opening.reservar_conta_escrow_pj(
                company_document_number=company_data["document_number"],
                email=company_data["email"],
                foundation_date=company_data["foundation_date"],
                name=company_data["name"],
                legal_representatives=legal_representatives
            )
            
            result["account_request_key"] = account_response.get("account_request_key")
            result["status"] = AccountStatus.ACCOUNT_REQUESTED.value
            
            result["steps"].append({"step": "create_account", "status": "completed", "timestamp": datetime.now().isoformat()})
            
            # Etapa 3: Monitoramento
            final_status = self._monitor_account_status(result["account_request_key"])
            result["status"] = final_status
            result["final_account_data"] = self._get_account_details(result["account_request_key"])
            
        except Exception as e:
            result["status"] = AccountStatus.ERROR.value
            result["errors"].append(f"Workflow error: {str(e)}")
            
        result["completed_at"] = datetime.now().isoformat()
        return result
    
    def _upload_documents(self, documents_paths: Dict[str, str]) -> Dict[str, str]:
        """Upload todos os documentos necessários"""
        uploaded_docs = {}
        
        for doc_type, file_path in documents_paths.items():
            try:
                if doc_type == "rg_front":
                    doc_key = self.document_upload.upload_rg_front(file_path)
                elif doc_type == "rg_back":
                    doc_key = self.document_upload.upload_rg_back(file_path)
                elif doc_type == "cnh":
                    doc_key = self.document_upload.upload_cnh(file_path)
                elif doc_type == "proof_residence":
                    doc_key = self.document_upload.upload_proof_of_residence(file_path)
                elif doc_type == "company_statute":
                    doc_key = self.document_upload.upload_company_statute(file_path)
                else:
                    doc_key = self.document_upload.upload_file(file_path)
                    
                uploaded_docs[doc_type] = doc_key
                
            except Exception as e:
                raise Exception(f"Erro no upload do documento {doc_type}: {str(e)}")
                
        return uploaded_docs
    
    def _validate_documents(self, documents: Dict[str, str]) -> Dict[str, Any]:
        """Valida se os documentos foram salvos corretamente"""
        validation_result = {"valid": True, "errors": []}
        
        for doc_type, doc_key in documents.items():
            try:
                # Tenta obter URL do documento para validar
                doc_info = self.document_upload.get_document_url(doc_key)
                if not doc_info.get("url"):
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Documento {doc_type} não foi salvo corretamente")
                    
            except Exception as e:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Erro na validação do documento {doc_type}: {str(e)}")
                
        return validation_result
    
    def _monitor_account_status(self, account_request_key: str, max_attempts: int = 10) -> str:
        """Monitora o status da conta até conclusão"""
        for attempt in range(max_attempts):
            try:
                status_response = self.account_opening.consultar_status_abertura(account_request_key)
                current_status = status_response.get("status", "unknown")
                
                # Status finais
                if current_status in ["approved", "rejected"]:
                    return current_status
                    
                # Aguarda antes da próxima verificação
                time.sleep(5)
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    return AccountStatus.ERROR.value
                time.sleep(2)
                
        return AccountStatus.PENDING_KYC.value
    
    def _get_account_details(self, account_request_key: str) -> Dict[str, Any]:
        """Obtém detalhes finais da conta"""
        try:
            return self.account_opening.consultar_status_abertura(account_request_key)
        except Exception as e:
            return {"error": f"Erro ao obter detalhes da conta: {str(e)}"}
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Consulta status de um workflow específico"""
        # Em implementação real, isso seria salvo em banco de dados
        return {"message": "Implementar persistência de workflows"}
    
    def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Retoma um workflow interrompido"""
        # Em implementação real, recuperaria estado do banco
        return {"message": "Implementar recuperação de workflows"}
    
    # Métodos auxiliares para construção de dados
    def build_person_data(self, name: str, document: str, email: str, 
                         birthdate: str, **kwargs) -> Dict[str, Any]:
        """Helper para dados de pessoa física"""
        return {
            "name": name,
            "document_number": document,
            "email": email,
            "birthdate": birthdate,
            **kwargs
        }
    
    def build_company_data(self, name: str, document: str, email: str,
                          foundation_date: str, **kwargs) -> Dict[str, Any]:
        """Helper para dados de empresa"""
        return {
            "name": name,
            "document_number": document,
            "email": email,
            "foundation_date": foundation_date,
            **kwargs
        }
    
    def build_legal_representative(self, name: str, document: str, email: str,
                                  birthdate: str, **kwargs) -> Dict[str, Any]:
        """Helper para representante legal"""
        return {
            "name": name,
            "document_number": document,
            "email": email,
            "birthdate": birthdate,
            **kwargs
        }
