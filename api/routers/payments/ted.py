from fastapi import APIRouter, Depends, HTTPException
from api.payment_schemas import TedRequest
from connectors.ted import TedConnector
from plugqi import PlugQi
from api.auth import get_api_key

router = APIRouter(prefix="/payments/ted", tags=["Payments - TED"])

# Initialize PlugQi and Connector
plugqi = PlugQi() # Loads env vars
ted_connector = TedConnector(plugqi.client)

@router.post("")
def send_ted(request: TedRequest, auth: dict = Depends(get_api_key)):
    """
    Send a TED Transfer.
    """
    # Build Target Account Dictionary
    target_account = {
        "account_branch": request.recipient.branch,
        "account_number": request.recipient.account_number,
        "account_digit": request.recipient.account_digit,
        "owner_document_number": request.recipient.document_number,
        "owner_name": request.recipient.name,
        "ispb": request.recipient.bank_code,
        "account_type": request.recipient.account_type
    }

    import uuid
    control_key = str(uuid.uuid4())

    response = ted_connector.send_ted(
        account_key=request.account_key,
        request_control_key=control_key,
        target_account=target_account,
        transaction_amount=request.amount
    )

    return response

@router.get("/{ted_key}")
def get_ted(ted_key: str, account_key: str, direction: str = "outgoing", auth: dict = Depends(get_api_key)):
    """
    Get TED details by key.
    """
    return ted_connector.get_ted(account_key, ted_key, direction)
