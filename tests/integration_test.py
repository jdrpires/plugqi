
import requests
import json
import os

BASE_URL = "http://localhost:8002"

def print_result(step, response):
    print(f"\n--- {step} ---")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    # 1. Health Check
    resp = requests.get(f"{BASE_URL}/health")
    print_result("Health Check", resp)
    assert resp.status_code == 200

    # 2. Upload Document (Mocking a file)
    with open("test_doc.txt", "w") as f:
        f.write("Conteudo de teste")
    
    # Updated to use dynamic key for validation
    headers = {'X-API-KEY': 'chave_dinamica_123'}

    with open("test_doc.txt", "rb") as f:
        files = {'file': ('test_doc.txt', f, 'text/plain')}
        resp = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files, headers=headers)
    
    print_result("Upload Document", resp)
    # Note: connectex error might happen if QiTech is not reachable, but we want to see the error handled.
    
    # 3. Risk Legal Person
    pj_payload = {
        "legal_name": "Empresa Teste LTDA",
        "trading_name": "Empresa Teste",
        "document_number": "12.345.678/0001-90",
        "foundation_date": "2020-01-01",
        "activity": "Tecnologia",
        "activity_code": "62000",
        "merchant_category_code": "5732",
        "annual_revenues": 1000000,
        "emails": [{"email": "contato@empresa.com", "validation_type": "company_email"}],
        "phones": [{"area_code": "11", "number": "999999999", "type": "mobile"}],
        "address": {
            "street": "Rua Teste",
            "number": "100",
            "neighborhood": "Centro",
            "city": "Sao Paulo",
            "uf": "SP",
            "postal_code": "01001000"
        },
        "source": {"network_id": "127.0.0.1"},
        "partners": []
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/risk/legal-person", json=pj_payload, headers=headers)
    print_result("Risk PJ Analysis", resp)

    # 4. Escrow Reservation
    escrow_payload = {
        "company_document_number": "12.345.678/0001-90",
        "email": "contato@empresa.com",
        "foundation_date": "2020-01-01",
        "name": "Empresa Teste LTDA",
        "legal_representatives": [
            {
                "name": "Socio 1",
                "individual_document_number": "123.456.789-00",
                "birth_date": "1990-01-01",
                "email": "socio@empresa.com",
                "phone": {"area_code": "11", "number": "999999999"},
                "address": {
                    "street": "Rua Teste",
                    "number": "100",
                    "neighborhood": "Centro",
                    "city": "Sao Paulo",
                    "uf": "SP",
                    "postal_code": "01001000"
                },
                "mother_name": "Mae Do Socio"
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/api/v1/accounts/escrow/pj", json=escrow_payload, headers=headers)
    print_result("Escrow Reservation", resp)

    # Cleanup
    if os.path.exists("test_doc.txt"):
        os.remove("test_doc.txt")

if __name__ == "__main__":
    try:
        test_api()
        print("\n✅ Test Execution Finished")
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
