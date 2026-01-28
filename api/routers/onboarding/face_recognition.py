from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, Body
from api.schemas import FaceClientSessionRequest
import shutil
import os
import uuid
import base64
import io
import time
import json
from fastapi.responses import StreamingResponse
from plugqi import PlugQi
from api.auth import get_api_key
from api.db import insert_qi_face_recognition

router = APIRouter(prefix="/documents", tags=["Documents"])

# Initialize PlugQi client
plugqi = PlugQi()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/face_recognition")
async def send_document_face_recognition(
    file: UploadFile = File(...),
    request: Request = None,
    api_key: dict = Depends(get_api_key),
):
    """Recebe arquivo via multipart, envia ao Face Recognition da QiTech e retorna o JSON de resposta."""
    if not plugqi.qitech_face_recognition:
        raise HTTPException(status_code=503, detail="Face Recognition QiTech não configurado")

    try:
        content = await file.read()
        file_type_det = os.path.splitext(file.filename)[1].lstrip(".") or "jpeg"
        requisicao = {
            "file_type": file_type_det,
            "filename": file.filename,
            "size": len(content),
        }

        start = time.perf_counter()
        try:
            document_b64 = base64.b64encode(content).decode("utf-8")
            resp = plugqi.qitech_face_recognition.analyze_image(image_b64=document_b64)
            duracao_ms = int((time.perf_counter() - start) * 1000)
            codigo_status = 200

            id_imagem = None
            if isinstance(resp, dict):
                id_imagem = resp.get("id") or resp.get("image_id") or resp.get("imageId")

            try:
                resposta_texto = None
                if isinstance(resp, dict):
                    try:
                        txt = json.dumps(resp, ensure_ascii=False)
                        resposta_texto = txt if len(txt) <= 100000 else txt[:100000] + "...[truncated]"
                    except Exception:
                        resposta_texto = str(resp)
                elif isinstance(resp, str):
                    resposta_texto = resp if len(resp) <= 100000 else resp[:100000] + "...[truncated]"
                elif isinstance(resp, (bytes, bytearray)):
                    resposta_texto = f"<binary len={len(resp)}>"
                else:
                    resposta_texto = str(resp)

                insert_qi_face_recognition(
                    chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                    modelo=None,
                    tipo_arquivo=file_type_det,
                    nome_arquivo=file.filename,
                    id_imagem=id_imagem,
                    requisicao=requisicao,
                    resposta=resp if isinstance(resp, dict) else {"raw": str(resp)},
                    resposta_texto=resposta_texto,
                    codigo_status=codigo_status,
                    duracao_ms=duracao_ms,
                    ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                    agente_usuario=(request.headers.get("user-agent") if request else None),
                    mensagem_erro=None,
                )
            except Exception:
                pass

            return resp

        except Exception as e:
            duracao_ms = int((time.perf_counter() - start) * 1000)
            status_code = getattr(e, "status", None)
            payload = getattr(e, "payload", None) if hasattr(e, "payload") else None

            try:
                resposta_texto = None
                if payload is None:
                    resposta_texto = str(e)
                elif isinstance(payload, dict):
                    try:
                        txt = json.dumps(payload, ensure_ascii=False)
                        resposta_texto = txt if len(txt) <= 100000 else txt[:100000] + "...[truncated]"
                    except Exception:
                        resposta_texto = str(payload)
                else:
                    resposta_texto = str(payload)

                insert_qi_face_recognition(
                    chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                    modelo=None,
                    tipo_arquivo=file_type_det,
                    nome_arquivo=file.filename,
                    id_imagem=None,
                    requisicao=requisicao,
                    resposta=payload if payload is not None else {"error": str(e)},
                    resposta_texto=resposta_texto,
                    codigo_status=(status_code if status_code is not None else -1),
                    duracao_ms=duracao_ms,
                    ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                    agente_usuario=(request.headers.get("user-agent") if request else None),
                    mensagem_erro=str(e),
                )
            except Exception:
                pass

            if hasattr(e, "status"):
                detail = payload if payload is not None else str(e)
                raise HTTPException(status_code=getattr(e, "status", 500), detail=detail)
            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/face_recognition/client_session")
async def face_recognition_client_session(payload: FaceClientSessionRequest = Body(..., example={"user_id": "unique_user_identifier"}), request: Request = None, api_key: dict = Depends(get_api_key)):
    """Gera um client session key para uso nas SDKs (POST /face_recognition/client_session)."""
    if not plugqi.qitech_face_recognition:
        raise HTTPException(status_code=503, detail="Face Recognition QiTech não configurado")

    try:
        start = time.perf_counter()
        resp = plugqi.qitech_face_recognition.get_client_session(payload.user_id)
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

            insert_qi_face_recognition(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                modelo="client_session",
                tipo_arquivo=None,
                nome_arquivo=None,
                id_imagem=None,
                requisicao=payload.dict(),
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
            insert_qi_face_recognition(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                modelo="client_session",
                tipo_arquivo=None,
                nome_arquivo=None,
                id_imagem=None,
                requisicao=payload.dict() if hasattr(payload, 'dict') else {},
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
            detail = payload_err if payload_err is not None else str(e)
            raise HTTPException(status_code=getattr(e, "status", 500), detail=detail)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/face_recognition/{image_id}/file")
async def get_document_face_recognition_file(image_id: str, request: Request, api_key: dict = Depends(get_api_key)):
    """Recupera arquivo ou resultado do Face Recognition pela `image_id` retornada no envio."""
    if not plugqi.qitech_face_recognition:
        raise HTTPException(status_code=503, detail="Face Recognition QiTech não configurado")

    try:
        start = time.perf_counter()
        result = plugqi.qitech_face_recognition.get_result(image_id)
        duracao_ms = int((time.perf_counter() - start) * 1000)

        try:
            if isinstance(result, dict):
                try:
                    txt = json.dumps(result, ensure_ascii=False)
                    resposta_texto = txt if len(txt) <= 100000 else txt[:100000] + "...[truncated]"
                except Exception:
                    resposta_texto = str(result)
            elif isinstance(result, str):
                resposta_texto = result if len(result) <= 100000 else result[:100000] + "...[truncated]"
            elif isinstance(result, (bytes, bytearray)):
                resposta_texto = f"<binary len={len(result)}>"
            else:
                resposta_texto = str(result)

            insert_qi_face_recognition(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                modelo=None,
                tipo_arquivo=None,
                nome_arquivo=None,
                id_imagem=image_id,
                requisicao={"action": "get_file", "image_id": image_id},
                resposta=(result if isinstance(result, dict) else {"raw_type": type(result).__name__}),
                resposta_texto=resposta_texto,
                codigo_status=200,
                duracao_ms=duracao_ms,
                ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=None,
            )
        except Exception:
            pass

        if isinstance(result, (bytes, bytearray)):
            return StreamingResponse(io.BytesIO(result), media_type="application/octet-stream")
        return result
    except Exception as e:
        duracao_ms = None
        status_code = getattr(e, "status", None)
        payload = getattr(e, "payload", None) if hasattr(e, "payload") else None
        try:
            insert_qi_face_recognition(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                modelo=None,
                tipo_arquivo=None,
                nome_arquivo=None,
                id_imagem=image_id,
                requisicao={"action": "get_file", "image_id": image_id},
                resposta=payload if payload is not None else {"error": str(e)},
                resposta_texto=(json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else str(payload) if payload is not None else str(e)),
                codigo_status=(status_code if status_code is not None else -1),
                duracao_ms=duracao_ms,
                ip_cliente=request.client.host if request and getattr(request, "client", None) else None,
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=str(e),
            )
        except Exception:
            pass

        if hasattr(e, "status"):
            detail = payload if payload is not None else str(e)
            raise HTTPException(status_code=getattr(e, "status", 500), detail=detail)
        raise HTTPException(status_code=500, detail=str(e))
