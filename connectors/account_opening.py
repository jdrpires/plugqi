# connectors/account_opening.py
from typing import Dict, Optional, Any, List
import uuid

class AccountOpeningConnector:
    def __init__(self, client):
        self.client = client

    # Etapa 1: Reserva de Conta Escrow (POST) - SCHEMA OFICIAL QITECH
    def reservar_conta_escrow_pf(self, document_number: str, email: str, 
                                birthdate: str, name: str, documents: Dict[str, Any],
                                face_key: str) -> Dict[str, Any]:
        """Reserva conta Escrow PF - Schema oficial QiTech"""
        payload = {
            "account_owner": {
                "document_number": document_number,
                "email": email,
                "birthdate": birthdate,
                "name": name,
                "documents": documents,
                "face": face_key
            }
        }
        return self.client.post("/account_request/escrow", payload)
    
    def reservar_conta_escrow_pj(self, company_document_number: str, email: str,
                                foundation_date: str, name: str,
                                legal_representatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Reserva conta Escrow PJ - Schema oficial QiTech"""
        payload = {
            "account_owner": {
                "company_document_number": company_document_number,
                "email": email,
                "foundation_date": foundation_date,
                "name": name
            },
            "legal_representatives": legal_representatives
        }
        return self.client.post("/account_request/escrow", payload)
    
    # Método legado mantido para compatibilidade
    def reservar_conta_pj(self, account_owner: Dict[str, Any], 
                         signed_contract: Dict[str, Any],
                         destinations: List[Dict[str, Any]],
                         additional_documents: List[str] = None) -> Dict[str, Any]:
        """LEGADO: Primeira etapa reserva conta PJ - usar reservar_conta_escrow_pj"""
        payload = {
            "account_owner": account_owner,
            "signed_contract": signed_contract,
            "destinations": destinations
        }
        
        if additional_documents:
            payload["additional_documents"] = additional_documents
            
        return self.client.post("/account_request/escrow", payload)

    # Etapa 2: Confirmação de Abertura (PATCH)
    def confirmar_abertura_conta(self, account_request_key: str, 
                                dados_completos: Dict[str, Any]) -> Dict[str, Any]:
        """Segunda etapa: confirma abertura da conta"""
        return self.client.patch(f"/account_request/{account_request_key}/escrow", dados_completos)

    # Consultas
    def consultar_status_abertura(self, account_request_key: str) -> Dict[str, Any]:
        """Consulta status da abertura de conta"""
        return self.client.get(f"/account_request/{account_request_key}")

    def listar_solicitacoes_abertura(self, **filters) -> Dict[str, Any]:
        """Lista solicitações de abertura"""
        return self.client.get("/account_request", params=filters)

    # Helpers para construir payloads COMPLETOS
    def build_account_owner_completo(self, cnpj: str, razao_social: str, nome_fantasia: str,
                                    email: str, data_fundacao: str, cnae: str,
                                    endereco: Dict[str, Any], telefone: Dict[str, Any],
                                    representantes: List[Dict[str, Any]],
                                    company_type: str = "ltda") -> Dict[str, Any]:
        """Helper para account_owner completo conforme documentação"""
        return {
            "address": endereco,
            "cnae_code": cnae,
            "company_document_number": cnpj,
            "company_type": company_type,
            "email": email,
            "foundation_date": data_fundacao,
            "name": razao_social,
            "person_type": "legal",
            "phone": telefone,
            "trading_name": nome_fantasia,
            "company_representatives": representantes
        }
    
    def build_company_representative(self, nome: str, cpf: str, nascimento: str,
                                   endereco: Dict[str, Any], email: str, telefone: Dict[str, Any],
                                   nome_mae: str, is_pep: bool = False,
                                   nacionalidade: str = "Brasileira",
                                   estado_civil: str = "single") -> Dict[str, Any]:
        """Helper para representante legal completo"""
        return {
            "name": nome,
            "address": endereco,
            "email": email,
            "birth_date": nascimento,
            "individual_document_number": cpf,
            "is_pep": is_pep,
            "marital_status": estado_civil,
            "mother_name": nome_mae,
            "nationality": nacionalidade,
            "person_type": "natural",
            "phone": telefone
        }
    
    def build_signed_contract(self, document_key: str, assinaturas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Helper para contrato assinado"""
        return {
            "document_key": document_key,
            "signatures": assinaturas
        }
    
    def build_signature(self, nome: str, email: str, cpf: str, telefone: Dict[str, Any],
                       timestamp: str, facial_recognition_key: str, session_id: str,
                       ip_address: str = None, lat: str = None, lng: str = None) -> Dict[str, Any]:
        """Helper para assinatura"""
        authenticity = {
            "timestamp": timestamp,
            "facial_recognition_key": facial_recognition_key,
            "session_id": session_id
        }
        
        if ip_address:
            authenticity["ip_address"] = ip_address
        if lat:
            authenticity["lat"] = lat
        if lng:
            authenticity["lang"] = lng
            
        return {
            "authenticity": authenticity,
            "signer": {
                "name": nome,
                "email": email,
                "phone": telefone,
                "document_number": cpf
            },
            "authentication_type": "opt-in"
        }
    
    def build_destination_account(self, agencia: str, conta: str, digito: str,
                                 documento: str, nome: str, ispb: str, 
                                 codigo_banco: str) -> Dict[str, Any]:
        """Helper para conta destino"""
        return {
            "account_branch": agencia,
            "account_number": conta,
            "account_digit": digito,
            "document_number": documento,
            "name": nome,
            "ispb_number": ispb,
            "financial_institution_code_number": codigo_banco
        }
    
    # Helpers básicos (mantidos para compatibilidade)
    def build_empresa_basica(self, cnpj: str, razao_social: str, email: str, 
                            data_fundacao: str) -> Dict[str, Any]:
        """Helper para dados básicos da empresa (compatibilidade)"""
        return {
            "company_document_number": cnpj,
            "name": razao_social,
            "email": email,
            "foundation_date": data_fundacao
        }
    
    def build_endereco(self, rua: str, numero: str, bairro: str, cidade: str,
                      estado: str, cep: str, complemento: str = "") -> Dict[str, Any]:
        """Helper para endereço"""
        endereco = {
            "street": rua,
            "number": numero,
            "neighborhood": bairro,
            "city": cidade,
            "state": estado,
            "postal_code": cep
        }
        if complemento:
            endereco["complement"] = complemento
        return endereco

    def build_telefone(self, ddi: str, ddd: str, numero: str) -> Dict[str, Any]:
        """Helper para telefone"""
        return {
            "country_code": ddi,
            "area_code": ddd,
            "number": numero
        }

    # Validações
    def validar_cnpj(self, cnpj: str) -> bool:
        """Valida formato CNPJ"""
        import re
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        return len(cnpj_limpo) == 14 and cnpj_limpo.isdigit()

    def validar_cpf(self, cpf: str) -> bool:
        """Valida formato CPF"""
        import re
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        return len(cpf_limpo) == 11 and cpf_limpo.isdigit()

    def get_mock_status_by_document(self, documento: str) -> str:
        """Retorna status mock baseado no primeiro dígito do documento"""
        primeiro_digito = documento[0] if documento else "0"
        
        if primeiro_digito in "01234567":
            return "manual_analysis"
        elif primeiro_digito == "8":
            return "automatic_rejection"
        elif primeiro_digito == "9":
            return "automatic_approval"
        else:
            return "manual_analysis"

    def get_company_types(self) -> Dict[str, str]:
        """Retorna tipos de empresa disponíveis"""
        return {
            "ltda": "Limitada",
            "sa": "Sociedade Anônima", 
            "micro_enterprise": "Micro Empresa",
            "mei": "Micro Empreendedor Individual",
            "me": "Micro Empresa",
            "eireli": "Empresa de Responsabilidade Individual",
            "freelancer": "Freelancer",
            "others": "Outros"
        }

    def get_document_types(self) -> Dict[str, str]:
        """Retorna tipos de documento aceitos"""
        return {
            "rg": "RG - Registro Geral",
            "cnh": "CNH - Carteira Nacional de Habilitação"
        }

    def get_marital_status_options(self) -> Dict[str, str]:
        """Retorna opções de estado civil"""
        return {
            "single": "Solteiro(a)",
            "married": "Casado(a)",
            "widower": "Viúvo(a)",
            "divorced": "Divorciado(a)",
            "separated": "Separado(a)"
        }
    
    def confirmar_abertura_conta_escrow_pj(self, account_request_key: str, 
                                          account_owner: Dict[str, Any],
                                          signed_contract: Dict[str, Any],
                                          destinations: List[Dict[str, Any]],
                                          additional_documents: List[str] = None) -> Dict[str, Any]:
        """Confirmar abertura de conta Escrow PJ - Segunda etapa (PATCH)"""
        
        payload = {
            "account_owner": account_owner,
            "signed_contract": signed_contract,
            "destinations": destinations
        }
        
        if additional_documents:
            payload["additional_documents"] = additional_documents
        
        return self.client.patch(f"/account_request/{account_request_key}/escrow", payload)
