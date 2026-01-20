from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
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


@router.post("/pj")
def reserve_escrow_pj(payload: dict):
    """
    Reserve Escrow Account for Legal Person (PJ)
    - Normaliza CNPJ/CPF removendo pontuação
    - Captura erros do provedor e retorna payload sanitizado sem citar o provedor
    """
    try:
        # Accept both flat payloads and wrapped {"account_owner": {...}, "legal_representatives": [...]}
        if "account_owner" in payload and isinstance(payload.get("account_owner"), dict):
            owner = payload.get("account_owner", {})
            data = {
                "company_document_number": owner.get("company_document_number") or owner.get("document_number") or owner.get("cnpj"),
                "email": owner.get("email"),
                "foundation_date": owner.get("foundation_date") or owner.get("foundationDate"),
                "name": owner.get("name") or owner.get("legal_name") or owner.get("company_name"),
                "legal_representatives": payload.get("legal_representatives", []),
            }
        else:
            data = payload

        # Normalize representative field names to match EscrowPJRequest / LegalRepresentative
        reps = []
        for rep in data.get("legal_representatives", []):
            r = dict(rep)
            if "individual_document_number" not in r and "document_number" in r:
                r["individual_document_number"] = r.get("document_number")
            if "birth_date" not in r and "birthdate" in r:
                r["birth_date"] = r.get("birthdate")
            reps.append(r)
        data["legal_representatives"] = reps

        # Validate/parse using the existing Pydantic model
        parsed = EscrowPJRequest.parse_obj(data)

        # Normalize company document (CNPJ) to digits only
        company_doc = _digits_only(parsed.company_document_number)

        # Normalize legal representatives individual_document_number
        legal_reps = []
        for rep in parsed.legal_representatives:
            d = rep.dict()
            if "individual_document_number" in d and d["individual_document_number"]:
                d["individual_document_number"] = _digits_only(d["individual_document_number"]) 
            legal_reps.append(d)

        response = plugqi.account_opening.reservar_conta_escrow_pj(
            company_document_number=company_doc,
            email=parsed.email,
            foundation_date=parsed.foundation_date,
            name=parsed.name,
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
