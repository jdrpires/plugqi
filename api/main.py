from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from api.routers.onboarding import documents, risk, escrow, face_recognition, device_scan, auth_session, escrow_uploads
from api.routers.payments import ted, pix, boleto
from api.auth import get_api_key, api_key_header
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="PlugQi Orchestrator API",
    description="Camada de orquestração para integração (Onboarding, Risk, Escrow, Pagamentos)",
    version="1.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# CORS (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with Security
# Onboarding
app.include_router(documents.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)], include_in_schema=False)
app.include_router(risk.router, prefix="/api/v1/onboarding", dependencies=[Security(api_key_header)])
app.include_router(escrow.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)])
app.include_router(face_recognition.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)], include_in_schema=False)
app.include_router(device_scan.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)], include_in_schema=False)

# Auth session (moved under Risk Solution)
app.include_router(auth_session.router, prefix="/api/v1/onboarding/risk", dependencies=[Depends(get_api_key)])
app.include_router(escrow_uploads.router, prefix="/api/v1/onboarding/escrow", dependencies=[Depends(get_api_key)])

# Payments
app.include_router(ted.router, prefix="/api/v1/payments", dependencies=[Depends(get_api_key)])
app.include_router(pix.router, prefix="/api/v1/payments", dependencies=[Depends(get_api_key)])
app.include_router(boleto.router, prefix="/api/v1/payments", dependencies=[Depends(get_api_key)])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PlugQi Orchestrator"}


@app.get("/r/{token}", include_in_schema=False)
def redirect_token(token: str):
    from api.utils.redirect_store import get_redirect
    target = get_redirect(token)
    if not target:
        raise HTTPException(status_code=404, detail="link not found")
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=target)

if __name__ == "__main__":
    import uvicorn
    # Run on port 8002 as requested
    uvicorn.run("api.main:app", host="0.0.0.0", port=8002, reload=True)
