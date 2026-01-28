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


@router.post("/legal-person", openapi_extra={
    "requestBody": {
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RiskLegalPersonRequest"},
                "example": {
                    "id": "NewTest03",
                    "registration_date": "2026-01-15T14:37:15Z",
                    "legal_name": "Teste Barbershop LTDA",
                    "trading_name": "Teste Barbershop",
                    "document_number": "91.111.111/0001-11",
                    "foundation_date": "1992-09-15",
                    "activity": "Barber Shops",
                    "activity_code": "96.02-5-01",
                    "merchant_category_code": "0742",
                    "annual_revenues": 500000,
                    "legal_representatives": [
                        {
                            "name": "John Partner",
                            "document_number": "111.111.111-11",
                            "birthdate": "1992-09-15",
                            "gender": "male",
                            "nationality": "BRA",
                            "mother_name": "Maria Partner's Mother",
                            "occupation": "Teacher",
                            "emails": [
                                {
                                    "email": "johnsample@test.com"
                                }
                            ],
                            "documents": {
                                "cnh_digital": {
                                    "ocr_key": "a6e30ed3-6384-471f-9c0e-df5ea5799305"
                                }
                            },
                            "address": {
                                "street": "Rua do Teste",
                                "number": "111",
                                "neighborhood": "Bairro do Exemplo",
                                "city": "Aparecida de Goiânia",
                                "uf": "GO",
                                "postal_code": "74000-000"
                            },
                            "source": {
                                "session_id": "21667555-2311-4580-a2dd-cda00399f736"
                            },
                            "face": {
                                "registration_key": "20f41ebe-5d51-428d-855d-ef3ff10927db"
                            }
                        }
                    ],
                    "emails": [
                        {
                            "email": "contato@teste.com.br"
                        }
                    ],
                    "phones": [
                        {
                            "area_code": "62",
                            "number": "999999999"
                        }
                    ],
                    "address": {
                        "street": "Rua do Teste",
                        "number": "111",
                        "neighborhood": "Bairro do Exemplo",
                        "city": "Aparecida de Goiânia",
                        "uf": "GO",
                        "postal_code": "74000-000"
                    },
                    "source": {
                        "session_id": "21667555-2311-4580-a2dd-cda00399f736"
                    }
                }
            }
        }
    }
})
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
