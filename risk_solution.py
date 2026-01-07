import re
import hmac
import hashlib
import requests
from typing import Optional


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

    def _validate_cpf(self, cpf: str) -> bool:
        return bool(re.match(CPF_REGEX, cpf))

    def _validate_cnpj(self, cnpj: str) -> bool:
        return bool(re.match(CNPJ_REGEX, cnpj))

    def send_natural_person(self, payload: dict, analyze: bool = True) -> requests.Response:
        if 'document_number' not in payload:
            raise ValueError('document_number is required in payload')
        if not self._validate_cpf(payload['document_number']):
            raise ValueError('document_number must be a CPF formatted as ###.###.###-##')
        url = f"{self.base_url}natural_person"
        params = {'analyze': str(analyze).lower()}
        return requests.post(url, json=payload, headers=self.headers, params=params)

    def send_legal_person(self, payload: dict, analyze: bool = True) -> requests.Response:
        if 'document_number' not in payload:
            raise ValueError('document_number is required in payload')
        if not self._validate_cnpj(payload['document_number']):
            raise ValueError('document_number must be a CNPJ formatted as ##.###.###/####-##')
        url = f"{self.base_url}legal_person"
        params = {'analyze': str(analyze).lower()}
        return requests.post(url, json=payload, headers=self.headers, params=params)

    def update_natural_person(self, person_id: str, payload: dict) -> requests.Response:
        url = f"{self.base_url}natural_person/{person_id}"
        return requests.put(url, json=payload, headers=self.headers)

    def update_legal_person(self, person_id: str, payload: dict) -> requests.Response:
        url = f"{self.base_url}legal_person/{person_id}"
        return requests.put(url, json=payload, headers=self.headers)

    def get_natural_person(self, person_id: str) -> requests.Response:
        url = f"{self.base_url}natural_person/{person_id}"
        return requests.get(url, headers=self.headers)

    def get_legal_person(self, person_id: str) -> requests.Response:
        url = f"{self.base_url}legal_person/{person_id}"
        return requests.get(url, headers=self.headers)

    def get_pdf(self, person_type: str, person_id: str, base64: bool = False) -> requests.Response:
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
