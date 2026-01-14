from fastapi import APIRouter, HTTPException, Depends
from plugqi import PlugQi
from api.schemas import RiskNaturalPersonRequest, RiskLegalPersonRequest
from fastapi import APIRouter, HTTPException, Depends
from plugqi import PlugQi
from api.schemas import RiskNaturalPersonRequest, RiskLegalPersonRequest
from api.auth import get_api_key

router = APIRouter(prefix="/risk", tags=["Risk Solution"])

# Manual client factory removed as we use PlugQi now

@router.post("/natural-person", include_in_schema=False)
def analyze_natural_person(payload: RiskNaturalPersonRequest, auth: dict = Depends(get_api_key)):
    """
    Submit Natural Person for Risk Analysis (Hidden)
    """
    try:
        plugqi = PlugQi()
        data = payload.dict(exclude_none=True)
        
        # Retorna objeto requests.Response
        response = plugqi.risk.send_natural_person(data)
        
        if response.status_code not in (200, 201):
             try:
                 detail = response.json()
             except:
                 detail = response.text
             raise HTTPException(status_code=response.status_code, detail=detail)
             
        return response.json()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legal-person")
def analyze_legal_person(payload: RiskLegalPersonRequest, auth: dict = Depends(get_api_key)):
    """
    Submit Legal Person for Risk Analysis
    """
    try:
        plugqi = PlugQi()
        data = payload.dict(exclude_none=True)
        
        response = plugqi.risk.send_legal_person(data)
        
        if response.status_code not in (200, 201):
             try:
                 detail = response.json()
             except:
                 detail = response.text
             raise HTTPException(status_code=response.status_code, detail=detail)
             
        return response.json()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
