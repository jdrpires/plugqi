from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
import shutil
import os
import uuid
from fastapi.responses import JSONResponse
from plugqi import PlugQi
from api.schemas import DocumentUploadResponse
from api.auth import get_api_key
from api.db import insert_qi_document
import time

router = APIRouter(prefix="/uploads", tags=["Escrow"])

# reuse temp uploads dir
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

plugqi = PlugQi()


@router.post("/", response_model=DocumentUploadResponse)
async def upload_for_escrow(file: UploadFile = File(...), request: Request = None, api_key: dict = Depends(get_api_key)):
    """Upload de documento para uso na abertura de conta Escrow.

    Protegido por API key interna. Retorna `document_key` que pode ser usado
    ao reservar a conta.
    """
    temp_path = None
    try:
        file_ext = os.path.splitext(file.filename)[1]
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        start = time.perf_counter()
        # delegate to existing connector which uploads to provider
        result = plugqi.document_upload.upload_file(temp_path)
        duracao_ms = int((time.perf_counter() - start) * 1000)

        # cleanup temp file
        try:
            os.remove(temp_path)
        except Exception:
            pass

        # persist log
        try:
            insert_qi_document(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                document_key=result.get("document_key"),
                filename=file.filename,
                file_type=result.get("file_type"),
                size=result.get("size"),
                requisicao={"action": "upload", "filename": file.filename},
                resposta=result,
                resposta_texto=str(result)[:100000] if result is not None else None,
                codigo_status=200,
                duracao_ms=duracao_ms,
                ip_cliente=(request.client.host if request and getattr(request, "client", None) else None),
                agente_usuario=(request.headers.get("user-agent") if request else None),
                mensagem_erro=None,
            )
        except Exception:
            pass

        return JSONResponse(content={
            "document_key": result["document_key"],
            "document_md5": result["document_md5"],
            "filename": file.filename,
            "file_type": result.get("file_type", "unknown"),
            "size": result.get("size", 0)
        })

    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))



def _sanitize(obj: any) -> any:
    if isinstance(obj, str):
        return obj.replace("qitech", "plugz").replace("Qitech", "Plugz")
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


@router.get("/{document_key}")
async def get_document_info(document_key: str, api_key: dict = Depends(get_api_key)):
    """Consulta informações de um documento enviado (document_key).

    Retorna `document_url`, `signed_document_url` e `expiration_datetime` (sanitizado).
    """
    if not plugqi.document_upload:
        raise HTTPException(status_code=503, detail="Document upload connector não configurado")

    try:
        info = plugqi.document_upload.get_document_url(document_key)
        safe = _sanitize(info)

        try:
            insert_qi_document(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                document_key=document_key,
                filename=None,
                file_type=None,
                size=None,
                requisicao={"action": "get_info", "document_key": document_key},
                resposta=info,
                resposta_texto=str(info)[:100000] if info is not None else None,
                codigo_status=200,
                duracao_ms=None,
                ip_cliente=(None),
                agente_usuario=(None),
                mensagem_erro=None,
            )
        except Exception:
            pass

        return JSONResponse(content=safe)
    except Exception as e:
        # Mask provider error details and persist error log
        try:
            insert_qi_document(
                chave_api=(api_key.get("key") if isinstance(api_key, dict) else None),
                document_key=document_key,
                filename=None,
                file_type=None,
                size=None,
                requisicao={"action": "get_info", "document_key": document_key},
                resposta=None,
                resposta_texto=str(e)[:100000],
                codigo_status=500,
                duracao_ms=None,
                ip_cliente=None,
                agente_usuario=None,
                mensagem_erro=str(e),
            )
        except Exception:
            pass

        return JSONResponse(status_code=500, content={"error": "Falha ao consultar documento", "details": "Não foi possível obter informações do documento"})
