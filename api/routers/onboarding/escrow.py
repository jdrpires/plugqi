from fastapi import APIRouter, HTTPException, Body
from pydantic import ValidationError
from typing import Union
from plugqi import PlugQi
from api.schemas import EscrowPJRequest
from qitech_client import QiTechError

router = APIRouter(prefix="/accounts/escrow", tags=["Escrow Accounts"])

plugqi = PlugQi()


def _sanitize(obj: any) -> any:
    if isinstance(obj, str):
        return obj.replace("qitech", "plugz").replace("Qitech", "Plugz")
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


@router.post(
    "/pj",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/EscrowPJRequest"}
                }
            }
        }
    },
)
def reserve_escrow_pj(payload: Union[dict, EscrowPJRequest] = Body(...)):
    """
    Reserve Escrow Account for Legal Person (PJ)
    """
    try:
        # Validar payload com Pydantic
        if isinstance(payload, dict):
            parsed = EscrowPJRequest.parse_obj(payload)
        else:
            parsed = payload
        
        data = parsed.dict(exclude_none=True)
        
        # Determinar formato do payload
        if "account_owner" in data and data["account_owner"]:
            # Formato QiTech
            owner = data["account_owner"]
            company_doc = owner.get("company_document_number")
            email = owner.get("email")
            foundation_date = owner.get("foundation_date")
            name = owner.get("name")
            # Accept multiple shapes: top-level "legal_representatives" or
            # inside account_owner as "company_representatives" (helpers may build this)
            legal_reps_raw = (
                data.get("legal_representatives")
                or owner.get("company_representatives")
                or data.get("company_representatives")
                or []
            )
        else:
            # Formato legado (retrocompatibilidade)
            company_doc = data.get("company_document_number")
            email = data.get("email")
            foundation_date = data.get("foundation_date")
            name = data.get("name")
            legal_reps_raw = data.get("legal_representatives", [])
        
        # Normalizar CNPJ (apenas dígitos)
        company_doc = _digits_only(company_doc)
        
        # Processar representantes legais - APENAS campos aceitos pela QiTech na RESERVA
        # Campos permitidos: name, document_number, birthdate, email, documents, face
        legal_reps = []
        for rep in legal_reps_raw:
            r = dict(rep) if not isinstance(rep, dict) else rep
            
            # Construir representante com APENAS os campos aceitos na reserva
            filtered_rep = {}
            
            # Campos obrigatórios
            if r.get("name"):
                filtered_rep["name"] = r.get("name")
            
            # Documento (normalizar para apenas dígitos)
            doc_num = r.get("document_number") or r.get("individual_document_number")
            if doc_num:
                filtered_rep["document_number"] = _digits_only(doc_num)
            
            # Data de nascimento
            birthdate = r.get("birthdate") or r.get("birth_date")
            if birthdate:
                filtered_rep["birthdate"] = birthdate
            
            # Campos opcionais
            if r.get("email"):
                filtered_rep["email"] = r.get("email")
            
            if r.get("documents"):
                filtered_rep["documents"] = r.get("documents")
            
            if r.get("face"):
                filtered_rep["face"] = r.get("face")
            
            # Só adicionar se tiver pelo menos name e document_number
            if filtered_rep.get("name") and filtered_rep.get("document_number"):
                legal_reps.append(filtered_rep)
        
        # Chamar a função do SDK
        response = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number=company_doc,
            email=email,
            foundation_date=foundation_date,
            name=name,
            legal_representatives=legal_reps,
        )

        return response

    except QiTechError as e:
        # Extract provider payload (may be JSON) and sanitize it before returning
        payload = getattr(e, "payload", None)
        safe = _sanitize(payload) if payload is not None else {"error": "Falha na chamada ao provedor"}
        raise HTTPException(status_code=e.status, detail=safe)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
