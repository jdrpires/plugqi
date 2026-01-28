from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

# --- Shared ---

class AddressSchema(BaseModel):
    street: str
    number: str
    neighborhood: str
    city: str
    uf: str
    postal_code: str
    country: str = "BRA"
    complement: Optional[str] = None

class PhoneSchema(BaseModel):
    international_dial_code: str = "55"
    area_code: str
    number: str
    type: str = "mobile"

class EmailSchema(BaseModel):
    email: EmailStr
    validation_type: str = "company_email"

# --- Risk Solution ---

class RiskNaturalPersonRequest(BaseModel):
    id: Optional[str] = None
    registration_id: Optional[str] = None
    registration_date: Optional[str] = None
    client_category: str = "individual"
    name: str
    document_number: str
    birthdate: str
    gender: str = "male"
    nationality: str = "BRA"
    mother_name: str
    father_name: Optional[str] = None
    monthly_income: int
    declared_assets: int
    occupation: str
    emails: List[EmailSchema]
    phones: List[PhoneSchema]
    address: AddressSchema
    source: Dict[str, Any] = Field(..., example={"source_system": "risk", "id": "abc123"})


class RiskLegalPersonRequest(BaseModel):
    id: Optional[str] = None
    registration_id: Optional[str] = None
    registration_date: Optional[str] = None
    client_category: Optional[str] = "company"
    legal_name: Optional[str] = None
    trading_name: Optional[str] = None
    document_number: Optional[str] = None
    foundation_date: Optional[str] = None
    website: Optional[str] = None
    activity: Optional[str] = None
    activity_code: Optional[str] = None
    merchant_category_code: Optional[str] = None
    tier: Optional[str] = "small"
    annual_revenues: Optional[int] = None
    emails: Optional[List[EmailSchema]] = None
    phones: Optional[List[PhoneSchema]] = None
    address: Optional[AddressSchema] = None
    source: Optional[Dict[str, Any]] = Field(None, example={"source_system": "risk", "id": "xyz789"})
    partners: Optional[List[Dict[str, Any]]] = Field(None, example=[{"name": "Partner Ltda", "document_number": "12345678000195"}])
    legal_representatives: Optional[List[Dict[str, Any]]] = Field(None, example=[{"name": "Rep Name", "individual_document_number": "01234567890"}])

# --- Escrow Account ---

class LegalRepresentative(BaseModel):
    """
    Representante Legal para Escrow PJ
    
    IMPORTANTE: Na etapa de RESERVA, apenas os seguintes campos são enviados à QiTech:
    - name, document_number, birthdate, email (opcional), documents, face (opcional)
    
    Os demais campos (is_pep, marital_status, etc.) são aceitos mas filtrados automaticamente,
    sendo usados apenas na etapa de CONFIRMAÇÃO.
    """
    # Campos principais (usados na RESERVA)
    name: Optional[str] = None
    document_number: Optional[str] = None  # CPF do representante
    birthdate: Optional[str] = None  # Formato: YYYY-MM-DD
    email: Optional[EmailStr] = None
    documents: Optional[Dict[str, Any]] = Field(None, example={
        "national_registry_of_foreigners": {
            "ocr_front_key": "uuid-frente",
            "ocr_back_key": "uuid-verso"
        }
    })
    face: Optional[str] = Field(None, description="UUID da foto facial para biometria")
    
    # Campos alternativos (retrocompatibilidade)
    individual_document_number: Optional[str] = None
    birth_date: Optional[str] = None
    
    # Campos extras (usados apenas na CONFIRMAÇÃO, não na RESERVA)
    address: Optional[AddressSchema] = None
    phone: Optional[PhoneSchema] = None
    is_pep: Optional[bool] = False
    marital_status: Optional[str] = None
    mother_name: Optional[str] = None
    nationality: Optional[str] = None
    person_type: Optional[str] = None

    class Config:
        extra = "allow"

class AccountOwner(BaseModel):
    """Dados do titular da conta (empresa)"""
    company_document_number: str
    email: EmailStr
    foundation_date: str
    name: str

    class Config:
        extra = "allow"

class EscrowPJRequest(BaseModel):
    """Suporta dois formatos:
    1. Formato QiTech: {"account_owner": {...}, "legal_representatives": [...]}
    2. Formato legado: {"company_document_number": ..., "email": ..., ...}
    """
    # Formato QiTech (preferencial)
    account_owner: Optional[AccountOwner] = None
    legal_representatives: Optional[List[LegalRepresentative]] = None
    
    # Formato legado (retrocompatibilidade)
    company_document_number: Optional[str] = None
    email: Optional[EmailStr] = None
    foundation_date: Optional[str] = None
    name: Optional[str] = None
    
    class Config:
        extra = "allow"

# --- Document Upload ---

class DocumentUploadResponse(BaseModel):
    document_key: str
    document_md5: str
    filename: str
    file_type: str
    size: int


# --- Face Recognition Auth ---
class FaceClientSessionRequest(BaseModel):
    user_id: str = Field(..., example="unique_user_identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"purpose": "authentication"})


# --- Device Scan ---
class DeviceScanTokenRequest(BaseModel):
    session_id: str = Field(..., example="03e9b8651cbb8e7b2b1a3d23fca987d7985519a48b3121c2cc6009101cdae97a")


class DeviceScanEventRequest(BaseModel):
    event_type: str = Field(..., example="sdk_event")
    session_id: Optional[str] = Field(None, example="abc123")
    payload: Optional[Dict[str, Any]] = Field(None, example={"device": "info"})
