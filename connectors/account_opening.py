# connectors/account_opening.py
from typing import Dict, Optional, Any, List
import uuid

class AccountOpeningConnector:
    def __init__(self, client):
        self.client = client

    # Etapa 1: Reserva de Conta (POST)
    def reservar_conta_pj(self, dados_empresa: Dict[str, Any], 
                         representantes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Primeira etapa: reserva conta PJ"""
        payload = {
            "account_owner": dados_empresa,
            "legal_representatives": representantes
        }
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

    # Helpers para construir payloads
    def build_empresa_basica(self, cnpj: str, razao_social: str, email: str, 
                            data_fundacao: str) -> Dict[str, Any]:
        """Helper para dados básicos da empresa"""
        return {
            "company_document_number": cnpj,
            "name": razao_social,
            "email": email,
            "foundation_date": data_fundacao
        }

    def build_representante_legal(self, nome: str, cpf: str, nascimento: str,
                                 documentos: Dict[str, Any], face_key: Optional[str] = None) -> Dict[str, Any]:
        """Helper para representante legal"""
        representante = {
            "name": nome,
            "document_number": cpf,
            "birthdate": nascimento,
            "documents": documentos
        }
        if face_key:
            representante["face"] = face_key
        return representante

    def build_documentos_rg(self, ocr_frente: str, ocr_verso: str) -> Dict[str, Any]:
        """Helper para documentos RG"""
        return {
            "rg": {
                "ocr_front_key": ocr_frente,
                "ocr_back_key": ocr_verso
            }
        }

    def build_documentos_cnh(self, ocr_key: str) -> Dict[str, Any]:
        """Helper para documentos CNH"""
        return {
            "cnh": {
                "ocr_key": ocr_key
            }
        }

    def build_empresa_completa(self, cnpj: str, razao_social: str, nome_fantasia: str,
                              email: str, data_fundacao: str, cnae: str, 
                              endereco: Dict[str, Any], telefone: Dict[str, Any],
                              tipo_empresa: str = "ltda") -> Dict[str, Any]:
        """Helper para dados completos da empresa"""
        return {
            "company_document_number": cnpj,
            "name": razao_social,
            "trading_name": nome_fantasia,
            "email": email,
            "foundation_date": data_fundacao,
            "cnae_code": cnae,
            "company_type": tipo_empresa,
            "person_type": "legal",
            "address": endereco,
            "phone": telefone
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

    def build_conta_destino(self, agencia: str, conta: str, digito: str,
                           documento: str, nome: str, ispb: str, codigo_banco: str) -> Dict[str, Any]:
        """Helper para conta destino autorizada"""
        return {
            "account_branch": agencia,
            "account_number": conta,
            "account_digit": digito,
            "document_number": documento,
            "name": nome,
            "ispb_number": ispb,
            "financial_institution_code_number": codigo_banco
        }

    def build_contrato_assinado(self, document_key: str, assinaturas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Helper para contrato assinado"""
        return {
            "document_key": document_key,
            "signatures": assinaturas
        }

    def build_assinatura(self, nome: str, email: str, cpf: str, telefone: Dict[str, Any],
                        timestamp: str, face_key: str, session_id: str,
                        ip: Optional[str] = None, lat: Optional[str] = None, 
                        lng: Optional[str] = None) -> Dict[str, Any]:
        """Helper para dados de assinatura"""
        assinatura = {
            "signer": {
                "name": nome,
                "email": email,
                "document_number": cpf,
                "phone": telefone
            },
            "authenticity": {
                "timestamp": timestamp,
                "facial_recognition_key": face_key,
                "session_id": session_id
            },
            "authentication_type": "opt-in"
        }
        
        if ip:
            assinatura["authenticity"]["ip_address"] = ip
        if lat:
            assinatura["authenticity"]["lat"] = lat
        if lng:
            assinatura["authenticity"]["lang"] = lng
            
        return assinatura

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
