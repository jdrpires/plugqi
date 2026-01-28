import re
import hmac
import hashlib
import requests
import uuid
from typing import Optional, Dict, Any

CPF_REGEX = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
CNPJ_REGEX = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$"


class RiskSolutionClient:
    def __init__(self, api_key: str, base_url: str = "https://api.sandbox.caas.qitech.app/onboarding/"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/') + '/'
        self.headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        # Detecta modo mock se a chave for inválida ou explícita
        self.is_mock = not api_key or "EXAMPLE" in api_key or "MOCK" in api_key

    def _validate_cpf(self, cpf: str) -> bool:
        return bool(re.match(CPF_REGEX, cpf))

    def _validate_cnpj(self, cnpj: str) -> bool:
        return bool(re.match(CNPJ_REGEX, cnpj))

    def _mock_response(self, payload: dict, is_legal: bool = False) -> requests.Response:
        """Simula uma resposta de sucesso da QiTech"""
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b'{"status": "APPROVED", "registration_id": "mock-reg-123", "id": "mock-id-456", "message": "Simulated Response"}'
        
        # Gera dados dinâmicos para o mock parecer real
        resp_data = {
             "id": str(uuid.uuid4()),
             "registration_id": f"reg-{uuid.uuid4()}",
             "analysis_status": "APPROVED",
             "message": "Approved (MOCK MODE)"
        }
        import json
        resp._content = json.dumps(resp_data).encode('utf-8')
        return resp

    def send_natural_person(self, payload: dict, analyze: bool = True) -> requests.Response:
        if self.is_mock:
            return self._mock_response(payload, is_legal=False)
            
        # Removidas validações - deixar QiTech validar
        url = f"{self.base_url}natural_person"
        params = {'analyze': str(analyze).lower()}
        return requests.post(url, json=payload, headers=self.headers, params=params)

    def send_legal_person(self, payload: dict, analyze: bool = True) -> requests.Response:
        if self.is_mock:
            return self._mock_response(payload, is_legal=True)

        # Removidas validações - deixar QiTech validar
        url = f"{self.base_url}legal_person"
        params = {'analyze': str(analyze).lower()}
        return requests.post(url, json=payload, headers=self.headers, params=params)

    def update_natural_person(self, person_id: str, payload: dict) -> requests.Response:
        if self.is_mock: return self._mock_response(payload)
        url = f"{self.base_url}natural_person/{person_id}"
        return requests.put(url, json=payload, headers=self.headers)

    def update_legal_person(self, person_id: str, payload: dict) -> requests.Response:
        if self.is_mock: return self._mock_response(payload)
        url = f"{self.base_url}legal_person/{person_id}"
        return requests.put(url, json=payload, headers=self.headers)

    def get_natural_person(self, person_id: str) -> requests.Response:
        if self.is_mock: return self._mock_response({})
        url = f"{self.base_url}natural_person/{person_id}"
        return requests.get(url, headers=self.headers)

    def get_legal_person(self, person_id: str) -> requests.Response:
        if self.is_mock: return self._mock_response({})
        url = f"{self.base_url}legal_person/{person_id}"
        return requests.get(url, headers=self.headers)

    def get_pdf(self, person_type: str, person_id: str, base64: bool = False) -> requests.Response:
        if self.is_mock:
             r = requests.Response()
             r.status_code = 200
             r._content = b"%PDF-1.4 mock content"
             return r
        if person_type not in ('natural_person', 'legal_person'):
            raise ValueError('person_type must be natural_person or legal_person')
        url = f"{self.base_url}{person_type}/{person_id}/pdf"
        params = {'base64': 'true'} if base64 else None
        return requests.get(url, headers=self.headers, params=params)

    @staticmethod
    def compute_webhook_signature(endpoint: str, method: str, payload: str, signature_key: str) -> str:
        message = (endpoint + method + payload).encode('utf-8')
        h = hmac.new(signature_key.encode('utf-8'), message, hashlib.sha1)
        return h.hexdigest()
