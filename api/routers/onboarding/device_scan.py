from fastapi import APIRouter, HTTPException, Depends, Request, Body
from api.schemas import DeviceScanTokenRequest, DeviceScanEventRequest
import time
import json
from plugqi import PlugQi
from api.auth import get_api_key
from api.db import insert_qi_device_scan

router = APIRouter(prefix="/device_scan", tags=["DeviceScan"])
plugqi = PlugQi()




@router.post("/token")
async def request_device_token(body: DeviceScanTokenRequest = Body(..., example={"session_id":"03e9b8651cbb8e7b2b1a3d23fca987d7985519a48b3121c2cc6009101cdae97a"}), request: Request = None, api_key: dict = Depends(get_api_key)):
    """Solicita token ao CAAS Device Scan para o `session_id` informado.

    Body esperado: {"session_id": "..."}
    """
    if not plugqi.qitech_device_scan:
        raise HTTPException(status_code=503, detail="Device Scan QiTech não configurado")

    session_id = body.session_id if hasattr(body, 'session_id') else None

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id é obrigatório")

    try:
        start = time.perf_counter()
        resp = plugqi.qitech_device_scan.get_token(session_id)
        duracao_ms = int((time.perf_counter() - start) * 1000)

        try:
            resposta_texto = None
            if isinstance(resp, dict):
                try:
                    txt = json.dumps(resp, ensure_ascii=False)
                    resposta_texto = txt if len(txt) <= 100000 else txt[:100000] + "...[truncated]"
                except Exception:
                    resposta_texto = str(resp)
            else:
                resposta_texto = str(resp)

            insert_qi_device_scan(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                evento_tipo="get_token",
                session_id=session_id,
                requisicao={"session_id": session_id},
                resposta=resp if isinstance(resp, dict) else {"raw": str(resp)},
                resposta_texto=resposta_texto,
                codigo_status=200,
                duracao_ms=duracao_ms,
                ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=None,
            )
        except Exception:
            pass

        return resp
    except Exception as e:
        status_code = getattr(e, "status", None)
        payload_err = getattr(e, "payload", None) if hasattr(e, "payload") else None
        try:
            insert_qi_device_scan(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                evento_tipo="get_token",
                session_id=session_id,
                requisicao={"session_id": session_id},
                resposta=payload_err if payload_err is not None else {"error": str(e)},
                resposta_texto=(json.dumps(payload_err, ensure_ascii=False) if isinstance(payload_err, dict) else str(payload_err) if payload_err is not None else str(e)),
                codigo_status=(status_code if status_code is not None else -1),
                duracao_ms=None,
                ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=str(e),
            )
        except Exception:
            pass

        if hasattr(e, "status"):
            raise HTTPException(status_code=getattr(e, "status", 500), detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/result")
async def get_device_scan_result(session_id: str, request: Request, api_key: dict = Depends(get_api_key)):
    if not plugqi.qitech_device_scan:
        raise HTTPException(status_code=503, detail="Device Scan QiTech não configurado")

    try:
        start = time.perf_counter()
        result = plugqi.qitech_device_scan.get_result(session_id)
        duracao_ms = int((time.perf_counter() - start) * 1000)

        try:
            resposta_texto = None
            if isinstance(result, dict):
                try:
                    txt = json.dumps(result, ensure_ascii=False)
                    resposta_texto = txt if len(txt) <= 100000 else txt[:100000] + "...[truncated]"
                except Exception:
                    resposta_texto = str(result)
            else:
                resposta_texto = str(result)

            insert_qi_device_scan(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                evento_tipo=None,
                session_id=session_id,
                requisicao={"action": "get_result", "session_id": session_id},
                resposta=(result if isinstance(result, dict) else {"raw": str(result)}),
                resposta_texto=resposta_texto,
                codigo_status=200,
                duracao_ms=duracao_ms,
                ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=None,
            )
        except Exception:
            pass

        return result
    except Exception as e:
        duracao_ms = None
        status_code = getattr(e, "status", None)
        payload_err = getattr(e, "payload", None) if hasattr(e, "payload") else None
        try:
            insert_qi_device_scan(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                evento_tipo=None,
                session_id=session_id,
                requisicao={"action": "get_result", "session_id": session_id},
                resposta=payload_err if payload_err is not None else {"error": str(e)},
                resposta_texto=(json.dumps(payload_err, ensure_ascii=False) if isinstance(payload_err, dict) else str(payload_err) if payload_err is not None else str(e)),
                codigo_status=(status_code if status_code is not None else -1),
                duracao_ms=duracao_ms,
                ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=str(e),
            )
        except Exception:
            pass

        if hasattr(e, "status"):
            raise HTTPException(status_code=getattr(e, "status", 500), detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
