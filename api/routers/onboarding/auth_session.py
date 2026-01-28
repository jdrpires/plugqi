import os
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from pydantic import root_validator
import io
import base64
import qrcode
import httpx
from api.auth import get_api_key
from api.utils.redirect_store import set_redirect
from api.db import insert_qi_auth_session
import time

router = APIRouter(prefix="/auth_session", tags=["Risk Solution"])


class AuthSessionCPFRequest(BaseModel):
    id: str = Field(..., description="Identificador único do usuário (externo)", example="user_12345")
    cpf: str = Field(..., description="CPF do cliente", example="111.111.111-11")

    @validator("id", pre=True)
    def ensure_id(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("id inválido")
        return v.strip()

    @validator("cpf", pre=True)
    def normalize_cpf(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("CPF deve ser uma string")
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) != 11:
            raise ValueError("CPF inválido: deve conter 11 dígitos")
        return digits

    @root_validator(pre=True)
    def accept_raw_string(cls, values):
        # If body is a raw JSON string (e.g. just CPF), wrap it into {'cpf': value}
        if isinstance(values, str):
            return {"cpf": values}
        return values

QITECH_BASE = os.getenv("QITECH_BASE_URL_AUTH_SESSION_MANAGER", "https://api.sandbox.caas.qitech.app/auth_session_manager")
QITECH_URL = os.getenv("QITECH_URL", f"{QITECH_BASE}/auth_session")
QITECH_KEY = os.getenv("auth_session_manager_key") or os.getenv("QITECH_API_KEY")
PLUGZ_BASE_URL = os.getenv("PLUGZ_BASE_URL", "http://localhost:8002")


def _find_link(obj: Any) -> str | None:
    if isinstance(obj, str) and obj.startswith("http"):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            r = _find_link(v)
            if r:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = _find_link(v)
            if r:
                return r
    return None


def _find_auth_session_url(obj: Any) -> str | None:
    """Procura explicitamente pelo campo `auth_session_url` (ou variações) na resposta.

    Retorna a URL encontrada ou None. Se não encontrar, não faz fallback aqui.
    """
    if isinstance(obj, dict):
        # checar chaves comuns/variações
        for key in obj.keys():
            if key.lower() in ("auth_session_url", "authsessionurl", "authsession_url", "auth_sessionurl"):
                val = obj.get(key)
                if isinstance(val, str) and val.startswith("http"):
                    return val
        # busca recursiva em valores
        for v in obj.values():
            r = _find_auth_session_url(v)
            if r:
                return r
    if isinstance(obj, list):
        for v in obj:
            r = _find_auth_session_url(v)
            if r:
                return r
    return None


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, str):
        return obj.replace("qitech", "plugz").replace("Qitech", "Plugz")
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


@router.post(
    "/",
    response_model=dict,
    summary="Criar sessão de autenticação (CPF)",
    description=(
        "Recebe um identificador único (`id`) e o `cpf` do cliente. O `id` é enviado no campo `id` do payload e o CPF é enviado em `document_number`. "
        "O restante do corpo é fixo conforme o fluxo de integração. Retorna um link white-labeled quando disponível."
    ),
)
async def create_auth_session(
    payload: AuthSessionCPFRequest = Body(..., example={"id": "user_12345", "cpf": "111.111.111-11"}),
    api_key: dict = Depends(get_api_key),
):
    """Cria uma sessão de autenticação usando `id` (único) e `cpf`.

    - Recebe: JSON com campos `id` e `cpf`.
    - Envia ao provedor um payload fixo onde `id` recebe o `id` informado e `document_number` recebe o CPF formatado.
    - Retorna: JSON contendo `link` white-labeled quando o provedor retornar uma URL de sessão; caso contrário retorna a resposta sanitizada.
    """
    if not QITECH_KEY:
        raise HTTPException(status_code=500, detail="auth_session_manager_key not configured")

    cpf = payload.cpf
    external_id = payload.id

    # Formata CPF como xxx.xxx.xxx-xx para compatibilidade com o provedor
    formatted_cpf = f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

    qitech_body = {
        "id": external_id,
        "document_number": formatted_cpf,
        "settings": {
            "steps": [
                {"step": "device_scan"},
                {"step": "face_recognition"},
                {
                    "step": "personal_document",
                    "show_success_screen": True,
                    "show_introduction_screen": True,
                    "document_templates": ["rg", "cnh", "cnh_digital"]
                }
            ],
            "session_expiration_time_in_minutes": 120,
            "token_expiration_seconds": 3600,
            "open_mode": "link"
        }
    }

    headers = {"Authorization": QITECH_KEY, "Content-Type": "application/json"}

    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(QITECH_URL, json=qitech_body, headers=headers)

    duracao_ms = int((time.perf_counter() - start) * 1000)

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        # store error response and raise
        try:
            resp_json = resp.json()
            resp_text = str(resp_json)
        except Exception:
            resp_json = None
            resp_text = resp.text

        insert_qi_auth_session(
            chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
            external_id=external_id,
            cpf=payload.cpf,
            cpf_formatado=formatted_cpf,
            token=None,
            original_link=None,
            requisicao=qitech_body,
            resposta=resp_json,
            resposta_texto=resp_text,
            codigo_status=resp.status_code,
            duracao_ms=duracao_ms,
            ip_cliente=None,
            agente_usuario=None,
            mensagem_erro=resp_text,
        )

        raise HTTPException(status_code=resp.status_code, detail=resp_text)

    data = resp.json()

    # If response contains explicit auth_session_url, return it directly (provider URL)
    auth_url = _find_auth_session_url(data)
    if auth_url:
        insert_qi_auth_session(
            chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
            external_id=external_id,
            cpf=payload.cpf,
            cpf_formatado=formatted_cpf,
            token=None,
            original_link=auth_url,
            requisicao=qitech_body,
            resposta=data if isinstance(data, dict) else {"raw": str(data)},
            resposta_texto=(str(data)[:100000] if data is not None else None),
            codigo_status=200,
            duracao_ms=duracao_ms,
            ip_cliente=None,
            agente_usuario=None,
            mensagem_erro=None,
        )
        # gerar QR code em PNG e retornar como data URL base64
        try:
            img = qrcode.make(auth_url)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            qr_data_url = f"data:image/png;base64,{qr_b64}"
        except Exception:
            qr_data_url = None

        return JSONResponse(content={"link": auth_url, "qr_code": qr_data_url})

    # Fallback: try to find any link in the response and return white-labeled redirect
    link = _find_link(data)
    if link:
        token = str(uuid.uuid4())
        set_redirect(token, link)
        branded = f"{PLUGZ_BASE_URL.rstrip('/')}/r/{token}"

        insert_qi_auth_session(
            chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
            external_id=external_id,
            cpf=payload.cpf,
            cpf_formatado=formatted_cpf,
            token=token,
            original_link=link,
            requisicao=qitech_body,
            resposta=data if isinstance(data, dict) else {"raw": str(data)},
            resposta_texto=(str(data)[:100000] if data is not None else None),
            codigo_status=200,
            duracao_ms=duracao_ms,
            ip_cliente=None,
            agente_usuario=None,
            mensagem_erro=None,
        )

        try:
            img = qrcode.make(branded)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            qr_data_url = f"data:image/png;base64,{qr_b64}"
        except Exception:
            qr_data_url = None

        return JSONResponse(content={"link": branded, "qr_code": qr_data_url})

    # no link found; persist response and return sanitized content
    insert_qi_auth_session(
        chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
        external_id=external_id,
        cpf=payload.cpf,
        cpf_formatado=formatted_cpf,
        token=None,
        original_link=None,
        requisicao=qitech_body,
        resposta=data if isinstance(data, dict) else {"raw": str(data)},
        resposta_texto=(str(data)[:100000] if data is not None else None),
        codigo_status=200,
        duracao_ms=duracao_ms,
        ip_cliente=None,
        agente_usuario=None,
        mensagem_erro=None,
    )

    return JSONResponse(content=_sanitize(data))


@router.get("/{auth_session_id}", response_model=dict, summary="Recuperar auth_session (Risk)", description="Recupera o status/resultado de uma auth_session usando o ID fornecido. Erros são mascarados para não vazar o nome do provedor.")
async def get_auth_session(auth_session_id: str, api_key: dict = Depends(get_api_key)):
    """Proxy para GET /auth_session/{id} do provedor (Risk Solution).

    - Recebe: `auth_session_id` (path)
    - Faz GET no provedor usando `auth_session_manager_key` e retorna o JSON sanitizado.
    - Em erros, a mensagem é mascarada para não expor o nome do provedor.
    """
    if not QITECH_KEY:
        raise HTTPException(status_code=500, detail="auth_session_manager_key not configured")

    target = f"{QITECH_URL.rstrip('/')}/{auth_session_id}"
    headers = {"Authorization": QITECH_KEY}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(target, headers=headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            # provider returned a non-2xx response: sanitize and mask
            try:
                body = resp.json()
            except Exception:
                body = resp.text

            masked = _sanitize(body) if body is not None else {"error": "Erro ao recuperar auth_session"}

            # return masked provider message without leaking provider identifiers
            return JSONResponse(status_code=resp.status_code, content={"error": "Falha ao recuperar sessão", "details": masked})
        except Exception as exc:
            # network/timeouts etc - mask details
            return JSONResponse(status_code=500, content={"error": "Erro interno ao recuperar sessão", "details": "Não foi possível contatar o provedor"})

    # success
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    # sanitize provider mentions (e.g., 'qitech') from returned payload
    safe = _sanitize(data)
    return JSONResponse(content=safe)
