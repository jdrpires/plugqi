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
    source: Dict[str, Any]


class RiskLegalPersonRequest(BaseModel):
    id: Optional[str] = None
    registration_id: Optional[str] = None
    registration_date: Optional[str] = None
    client_category: str = "company"
    legal_name: str
    trading_name: str
    document_number: str
    foundation_date: str
    website: Optional[str] = None
    activity: str
    activity_code: str
    merchant_category_code: str
    tier: str = "small"
    annual_revenues: int
    emails: List[EmailSchema]
    phones: List[PhoneSchema]
    address: AddressSchema
    source: Dict[str, Any]
    partners: List[Dict[str, Any]]

# --- Escrow Account ---

class LegalRepresentative(BaseModel):
    name: str
    individual_document_number: str
    birth_date: str
    email: EmailStr
    address: AddressSchema
    phone: PhoneSchema
    is_pep: bool = False
    marital_status: str = "single"
    mother_name: str
    nationality: str = "Brasileira"
    person_type: str = "natural"

class EscrowPJRequest(BaseModel):
    company_document_number: str
    email: EmailStr
    foundation_date: str
    name: str
    legal_representatives: List[LegalRepresentative]

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
