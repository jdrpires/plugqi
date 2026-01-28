from fastapi import APIRouter, Depends, HTTPException
from api.payment_schemas import PixKeyTransferRequest, PixManualTransferRequest, PaymentRecipient
from connectors.pix import PixConnector
from plugqi import PlugQi
from api.auth import get_api_key
import uuid

router = APIRouter(prefix="/payments/pix", tags=["Payments - PIX"])

plugqi = PlugQi()
pix_connector = PixConnector(plugqi.client)

@router.get("/key/{key_value}")
def consult_pix_key(key_value: str, auth: dict = Depends(get_api_key)):
    """
    Consult a PIX Key to get recipient details.
    """
    return pix_connector.consultar_chave_pix(key_value)

@router.post("/transfer/key")
def send_pix_key(request: PixKeyTransferRequest, auth: dict = Depends(get_api_key)):
    """
    Send PIX using a Target Key.
    """
    # 1. Consult Key to get End-to-End ID
    key_data = pix_connector.consultar_chave_pix(request.pix_key)
    end_to_end = key_data.get("end_to_end_id")
    
    if not end_to_end:
         raise HTTPException(status_code=400, detail="Invalid PIX Key or unable to resolve End-to-End ID")

    # 2. Send Transfer
    response = pix_connector.enviar_pix_chave(
        account_key=request.account_key,
        target_pix_key=request.pix_key,
        transaction_amount=request.amount,
        end_to_end_id=end_to_end,
        pix_message=request.description,
        request_control_key=str(uuid.uuid4())
    )
    return response

@router.post("/transfer/manual")
def send_pix_manual(request: PixManualTransferRequest, auth: dict = Depends(get_api_key)):
    """
    Send PIX using Manual Bank Data (Ag/Account/CPF).
    """
    target_account = {
        "account_branch": request.recipient.branch,
        "account_number": request.recipient.account_number,
        "account_digit": request.recipient.account_digit,
        "owner_document_number": request.recipient.document_number,
        "owner_name": request.recipient.name,
        "ispb": request.recipient.bank_code,
        "account_type": request.recipient.account_type
    }

    response = pix_connector.enviar_pix_manual(
        account_key=request.account_key,
        target_account=target_account,
        transaction_amount=request.amount,
        pix_message=request.description,
        request_control_key=str(uuid.uuid4())
    )
    return response

@router.post("/qr/static")
def generate_static_qr(key: str, amount: float, auth: dict = Depends(get_api_key)):
    """
    Generate a Static QR Code (Legacy support / simplified).
    Note: Real implementation requires Key ID + TxID logic.
    """
    return {"message": "Endpoint pending implementation in Connector logic", "status": "not_implemented"}
