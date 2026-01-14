from fastapi import APIRouter, HTTPException
from plugqi import PlugQi
from api.schemas import EscrowPJRequest

router = APIRouter(prefix="/accounts/escrow", tags=["Escrow Accounts"])

plugqi = PlugQi()

@router.post("/pj")
def reserve_escrow_pj(payload: EscrowPJRequest):
    """
    Reserve Escrow Account for Legal Person (PJ)
    """
    try:
        # Convert Pydantic model to dict
        # data = payload.dict() # We need to restructure for the connector
        
        # The connector expects specific arguments
        # reservar_conta_escrow_pj(company_document_number, email, foundation_date, name, legal_representatives)
        
        # Prepare legal representatives list of checks/dicts
        legal_reps = [rep.dict() for rep in payload.legal_representatives]
        
        response = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number=payload.company_document_number,
            email=payload.email,
            foundation_date=payload.foundation_date,
            name=payload.name,
            legal_representatives=legal_reps
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
