import os
from typing import Any, Dict, Optional
import requests
from qitech_client import QiTechError, QiTechClient
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv(), override=False)

DEFAULT_TIMEOUT = int(os.getenv("QITECH_OCR_TIMEOUT_SECONDS", "30"))


class QitechOCRClient:
    """
    Cliente simples para o CAAS OCR da QiTech.

    Usa cabeçalho `Authorization: <api_key>` conforme exemplo de cURL.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # Prefer environment names used in .env: 'ocr_api_key' and 'QITECH_BASE_URL_OCR'
        self.api_key = (
            api_key
            or os.getenv("OCR_API_KEY")
            or os.getenv("ocr_api_key")
            or os.getenv("QITECH_OCR_API_KEY")
            or os.getenv("QITECH_API_KEY")
        )
        env_base = os.getenv("QITECH_BASE_URL_OCR") or os.getenv("QITECH_OCR_BASE_URL")
        self.base_url = (base_url or env_base or "https://api.sandbox.caas.qitech.app").rstrip("/")

        if not self.api_key:
            raise ValueError("QITECH_OCR_API_KEY (ou QITECH_API_KEY) não definido.")

        # Reuse session construction from QiTechClient (staticmethod)
        try:
            self.session = QiTechClient._build_session()
        except Exception:
            # fallback simples
            self.session = requests.Session()

    def _headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        h = {"Authorization": self.api_key}
        if content_type:
            h["Content-Type"] = content_type
        return h

    def send_image(self, document_b64: str, template: str, file_type: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Envia imagem/base64 para processamento OCR.

        Exemplo JSON:
        {
          "document_b64": "base64...",
          "template": "cnh",
          "file_type": "jpeg"
        }
        """
        # Avoid duplicating '/ocr/image' if the base_url already contains it
        if "/ocr" in self.base_url:
            url = f"{self.base_url}"
        else:
            url = f"{self.base_url}/ocr/image"
        payload = {
            "document_b64": document_b64,
            "template": template,
            "file_type": file_type,
        }
        headers = self._headers("application/json")

        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede OCR QiTech: {e}") from e

        if 200 <= resp.status_code < 300:
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        else:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}
            raise QiTechError(resp.status_code, "Falha na chamada OCR QiTech", payload)

    def get_file(self, image_id: str, timeout: int = DEFAULT_TIMEOUT) -> Any:
        """Recupera o arquivo/processamento: GET /ocr/image/{id}/file

        Retorna JSON quando aplicável, ou bytes brutos se o endpoint retornar binário.
        """
        # Build retrieval URL similarly to avoid duplication
        if "/ocr" in self.base_url:
            url = f"{self.base_url.rstrip('/')}/{image_id}/file"
        else:
            url = f"{self.base_url}/ocr/image/{image_id}/file"
        headers = self._headers()

        try:
            resp = self.session.get(url, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede OCR QiTech: {e}") from e

        if 200 <= resp.status_code < 300:
            ctype = resp.headers.get("Content-Type", "")
            if "application/json" in ctype:
                try:
                    return resp.json()
                except ValueError:
                    return {"raw": resp.text}
            else:
                return resp.content
        else:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}
            raise QiTechError(resp.status_code, "Falha ao recuperar arquivo OCR QiTech", payload)
