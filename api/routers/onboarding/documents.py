from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Request
import shutil
import os
import uuid
import base64
import io
import time
from fastapi.responses import StreamingResponse
import json
from plugqi import PlugQi
from api.schemas import DocumentUploadResponse
from api.auth import get_api_key
from api.db import insert_qi_ocr

router = APIRouter(prefix="/documents", tags=["Documents"])

# Initialize PlugQi client
plugqi = PlugQi()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentUploadResponse, include_in_schema=False)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document using PlugQi Document Connector.
    """
    try:
        # Save temp file
        file_ext = os.path.splitext(file.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Use connector to upload
        # We assume file type detection inside connector or pass it if needed
        result = plugqi.document_upload.upload_file(temp_path)
        
        # Cleanup
        os.remove(temp_path)
        
        return DocumentUploadResponse(
            document_key=result['document_key'],
            document_md5=result['document_md5'],
            filename=file.filename,
            file_type=result.get('file_type', 'unknown'),
            size=result.get('size', 0)
        )
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr", include_in_schema=False)
async def send_document_ocr(
    file: UploadFile = File(...),
    template: str = Form(...),
    file_type: str = Form(None),
    request: Request = None,
    api_key: dict = Depends(get_api_key),
):
    """Recebe arquivo via multipart, envia ao OCR da QiTech e retorna o JSON de resposta."""
    if not plugqi.qitech_ocr:
        raise HTTPException(status_code=503, detail="OCR QiTech não configurado")

    try:
        content = await file.read()
        file_type_det = file_type or os.path.splitext(file.filename)[1].lstrip(".") or "jpeg"

        # Build minimal request payload to store (omit base64)
        requisicao = {
            "template": template,
            "file_type": file_type_det,
            "filename": file.filename,
            "size": len(content)
        }

        start = time.perf_counter()
        try:
            document_b64 = base64.b64encode(content).decode("utf-8")
            resp = plugqi.qitech_ocr.send_image(document_b64=document_b64, template=template, file_type=file_type_det)
            duracao_ms = int((time.perf_counter() - start) * 1000)
            codigo_status = 200

            # tenta extrair id da resposta
            id_imagem = None
            if isinstance(resp, dict):
                id_imagem = resp.get("id") or resp.get("image_id") or resp.get("imageId")

            # Persist log (não armazenamos a base64 completa)
            try:
                # montar resposta_texto redundante
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

                insert_qi_ocr(
                    chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                    modelo=template,
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
                # Não falhar a request principal se logging falhar
                pass

            return resp

        except Exception as e:
            duracao_ms = int((time.perf_counter() - start) * 1000)
            # Se for QiTechError, ele tem status e payload
            status_code = getattr(e, "status", None)
            payload = getattr(e, "payload", None) if hasattr(e, "payload") else None

            try:
                # montar resposta_texto redundante para erro
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

                insert_qi_ocr(
                    chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                    modelo=template,
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

            # Re-raise as HTTPException with appropriate status
            if hasattr(e, "status"):
                raise HTTPException(status_code=getattr(e, "status", 500), detail=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/ocr/{image_id}/file", include_in_schema=False)
async def get_document_ocr_file(image_id: str, request: Request, api_key: dict = Depends(get_api_key)):
    """Recupera arquivo ou resultado do OCR pela `image_id` retornada no envio."""
    if not plugqi.qitech_ocr:
        raise HTTPException(status_code=503, detail="OCR QiTech não configurado")

    try:
        start = time.perf_counter()
        result = plugqi.qitech_ocr.get_file(image_id)
        duracao_ms = int((time.perf_counter() - start) * 1000)

        # Persist retrieval log
        try:
            # montar resposta_texto
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

            insert_qi_ocr(
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
            insert_qi_ocr(
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
            raise HTTPException(status_code=getattr(e, "status", 500), detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
