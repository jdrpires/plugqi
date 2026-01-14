
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os

# Set env vars before importing main to ensure auth works
os.environ["PLUGQI_API_KEY"] = "test_key"
os.environ["PLG_KEY_CLIENTE_INTERNO"] = "test_client_key"

from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "PlugQi Orchestrator"}

@patch("api.routers.documents.plugqi.document_upload.upload_file")
def test_upload_document(mock_upload):
    # Mock successful upload
    mock_upload.return_value = {
        "document_key": "doc-123",
        "document_md5": "md5-hash",
        "file_type": "text/plain",
        "size": 100
    }
    
    headers = {"X-API-KEY": "test_key"}
    files = {"file": ("test.txt", b"content", "text/plain")}
    
    response = client.post("/api/v1/documents/upload", files=files, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["document_key"] == "doc-123"

@patch("api.routers.risk.RiskSolutionClient")
def test_risk_legal_person(MockClient):
    # Mock dependencies
    mock_instance = MockClient.return_value
    mock_instance.send_legal_person.return_value.status_code = 200
    mock_instance.send_legal_person.return_value.json.return_value = {"status": "approved", "id": "risk-123"}
    
    payload = {
        "legal_name": "Empresa Teste",
        "trading_name": "Teste",
        "document_number": "12.345.678/0001-90",
        "foundation_date": "2020-01-01",
        "activity": "Tech",
        "activity_code": "123",
        "merchant_category_code": "456",
        "annual_revenues": 1000,
        "emails": [{"email": "e@e.com"}],
        "phones": [{"area_code": "11", "number": "999999999"}],
        "address": {
             "street": "Rua", "number": "1", "neighborhood": "B", 
             "city": "C", "uf": "SP", "postal_code": "00000000"
        },
        "source": {},
        "partners": []
    }
    
    headers = {"X-API-KEY": "test_client_key"} # Valid key
    
    # We need to mock os.environ.get for QITECH_API_KEY inside the router's dependency
    with patch("os.environ.get", side_effect=lambda k, d=None: "mock_qi_key" if k == "QITECH_API_KEY" else os.environ.get(k, d)):
         response = client.post("/api/v1/risk/legal-person", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "approved"

@patch("api.routers.escrow.plugqi.account_opening.reservar_conta_escrow_pj")
def test_escrow_pj(mock_reserva):
    # Mock success
    mock_reserva.return_value = {
        "account_request_key": "req-123",
        "status": "created"
    }
    
    payload = {
        "company_document_number": "12.345.678/0001-90",
        "email": "e@e.com",
        "foundation_date": "2020-01-01",
        "name": "Empresa",
        "legal_representatives": [
            {
                "name": "Socio",
                "individual_document_number": "111.222.333-44",
                "birth_date": "1990-01-01",
                "email": "s@s.com",
                "phone": {"area_code": "11", "number": "988887777"},
                "address": {
                    "street": "Rua", "number": "1", "neighborhood": "B", 
                    "city": "C", "uf": "SP", "postal_code": "00000000"
                },
                "mother_name": "Mae",
                "nationality": "BR"
            }
        ]
    }
    
    headers = {"X-API-KEY": "test_key"}
    response = client.post("/api/v1/accounts/escrow/pj", json=payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["account_request_key"] == "req-123"

if __name__ == "__main__":
    # Manually run tests if executed as script
    import pytest
    import sys
    sys.exit(pytest.main(["-v", __file__]))
