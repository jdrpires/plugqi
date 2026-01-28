import os
import uuid
from typing import Any
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

# Endpoints (auth_session is fixed; upload URL can be overridden via env)
QITECH_URL = os.getenv("QITECH_URL", "https://api.sandbox.caas.qitech.app/auth_session_manager/auth_session")
QITECH_UPLOAD_URL = os.getenv("QITECH_UPLOAD_URL", "https://api.sandbox.caas.qitech.app/documents/upload")
QITECH_API_KEY = os.getenv("QITECH_API_KEY")
PLUGZ_BASE_URL = os.getenv("PLUGZ_BASE_URL", "http://localhost:8000")

app = FastAPI(title="Plugz Orchestrator - Auth & Upload Proxy")

# Simple in-memory redirect store. Replace with persistent store in production.
_redirect_store: dict[str, str] = {}


@app.post("/auth_session")
async def create_auth_session(request: Request):
    body = await request.json()
    if not QITECH_API_KEY:
        raise HTTPException(status_code=500, detail="QITECH_API_KEY not configured")

    headers = {"Authorization": QITECH_API_KEY, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(QITECH_URL, json=body, headers=headers)

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()

    # Try to find the first http(s) link in nested response
    def find_link(obj: Any) -> str | None:
        if isinstance(obj, str) and obj.startswith("http"):
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                r = find_link(v)
                if r:
                    return r
        if isinstance(obj, list):
            for v in obj:
                r = find_link(v)
                if r:
                    return r
        return None

    link = find_link(data)

    if link:
        # create a white-labeled redirect link hosted on this orchestrator
        token = str(uuid.uuid4())
        _redirect_store[token] = link
        branded_link = f"{PLUGZ_BASE_URL.rstrip('/')}/r/{token}"

        # return a minimal white-labeled response
        return JSONResponse(content={"link": branded_link})

    # If no link found, sanitize any mention of Qitech in strings and return
    def sanitize(obj: Any) -> Any:
        if isinstance(obj, str):
            return obj.replace("qitech", "plugz").replace("Qitech", "Plugz")
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    return JSONResponse(content=sanitize(data))


@app.post("/upload_documents")
async def upload_documents(request: Request):
    """Proxy file upload to Qitech and return sanitized response or link.

    Accepts `multipart/form-data` and forwards files + fields to `QITECH_UPLOAD_URL`.
    Set `QITECH_UPLOAD_URL` in `.env` if your Qitech upload endpoint differs.
    """
    if not QITECH_API_KEY:
        raise HTTPException(status_code=500, detail="QITECH_API_KEY not configured")

    form = await request.form()

    files_payload = []
    data_payload = {}

    for key, value in form.multi_items():
        if hasattr(value, "filename"):
            # it's an UploadFile
            upload: UploadFile = value  # type: ignore
            content = await upload.read()
            files_payload.append((key, (upload.filename, content, upload.content_type or "application/octet-stream")))
        else:
            data_payload[key] = str(value)

    headers = {"Authorization": QITECH_API_KEY}

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(QITECH_UPLOAD_URL, headers=headers, data=data_payload or None, files=files_payload or None)

    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # Forward sanitized response
    def sanitize(obj: Any) -> Any:
        if isinstance(obj, str):
            return obj.replace("qitech", "plugz").replace("Qitech", "Plugz")
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    # try parse JSON, otherwise return text
    try:
        data = resp.json()
        return JSONResponse(content=sanitize(data))
    except Exception:
        return JSONResponse(content={"result": sanitize(resp.text)})


@app.get("/r/{token}")
async def redirect(token: str):
    target = _redirect_store.get(token)
    if not target:
        raise HTTPException(status_code=404, detail="link not found")
    return RedirectResponse(url=target)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("orchestrator_auth_session:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
