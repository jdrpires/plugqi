from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

# Generic Payment Schemas

class PaymentRecipient(BaseModel):
    name: str = Field(..., description="Recipient Name")
    document_number: str = Field(..., description="CPF/CNPJ")
    bank_code: Optional[str] = Field(None, description="ISPB/Bank Code (for TED/Manual PIX)")
    branch: Optional[str] = Field(None, description="Branch Number")
    account_number: Optional[str] = Field(None, description="Account Number")
    account_digit: Optional[str] = Field(None, description="Account Digit")
    account_type: Optional[str] = Field("checking_account", description="checking_account, savings_account, etc.")

class TedRequest(BaseModel):
    account_key: str = Field(..., description="Source Account Key")
    amount: float = Field(..., gt=0, description="Amount to transfer")
    recipient: PaymentRecipient
    description: Optional[str] = Field(None, description="Transfer Description")

class PixKeyTransferRequest(BaseModel):
    account_key: str = Field(..., description="Source Account Key")
    pix_key: str = Field(..., description="Target PIX Key")
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class PixManualTransferRequest(BaseModel):
    account_key: str = Field(..., description="Source Account Key")
    recipient: PaymentRecipient
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class BoletoRequest(BaseModel):
    account_key: str = Field(..., description="Account issuing the Boleto")
    amount: float = Field(..., gt=0)
    due_date: str = Field(..., description="YYYY-MM-DD")
    payer: PaymentRecipient
    description: Optional[str] = None
