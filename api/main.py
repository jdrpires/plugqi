from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routers.onboarding import documents, risk, escrow, face_recognition, device_scan
from api.routers.payments import ted, pix, boleto
from api.auth import get_api_key
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="PlugQi Orchestrator API",
    description="Orchestration layer for QiTech integration (Documents, Risk, Escrow, Payments)",
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
app.include_router(documents.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)])
app.include_router(risk.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)])
app.include_router(escrow.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)])
app.include_router(face_recognition.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)])
app.include_router(device_scan.router, prefix="/api/v1/onboarding", dependencies=[Depends(get_api_key)])

# Payments
app.include_router(ted.router, prefix="/api/v1/payments", dependencies=[Depends(get_api_key)])
app.include_router(pix.router, prefix="/api/v1/payments", dependencies=[Depends(get_api_key)])
app.include_router(boleto.router, prefix="/api/v1/payments", dependencies=[Depends(get_api_key)])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PlugQi Orchestrator"}

if __name__ == "__main__":
    import uvicorn
    # Run on port 8002 as requested
    uvicorn.run("api.main:app", host="0.0.0.0", port=8002, reload=True)
