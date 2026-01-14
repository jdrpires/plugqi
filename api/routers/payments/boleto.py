from fastapi import APIRouter, Depends, HTTPException
from api.payment_schemas import BoletoRequest
from connectors.boleto import BoletoConnector
from plugqi import PlugQi
from api.auth import get_api_key
import uuid

router = APIRouter(prefix="/payments/boleto", tags=["Payments - Boleto"])

plugqi = PlugQi()
boleto_connector = BoletoConnector(plugqi.client)

@router.post("")
def create_boleto(request: BoletoRequest, requester_profile_key: str, auth: dict = Depends(get_api_key)):
    """
    Create a Bank Slip (Boleto).
    """
    control_key = str(uuid.uuid4())
    
    boleto_data = boleto_connector.build_simple_boleto(
        request_control_key=control_key,
        amount=request.amount,
        expiration=request.due_date,
        payer_name=request.payer.name,
        payer_document=request.payer.document_number,
        description=request.description
    )
    
    # Enrich payer data with optional address if provided in schema (simplified here)
    
    return boleto_connector.create_boleto(
        account_key=request.account_key,
        requester_profile_key=requester_profile_key,
        boleto_data=boleto_data
    )

@router.get("/{key}")
def get_boleto(key: str, account_key: str, auth: dict = Depends(get_api_key)):
    """
    Get Boleto details.
    """
    return boleto_connector.get_boleto(account_key, key)
