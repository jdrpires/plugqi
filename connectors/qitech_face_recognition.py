import os
from typing import Any, Dict, Optional
import requests
from qitech_client import QiTechError, QiTechClient
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv(), override=False)

DEFAULT_TIMEOUT = int(os.getenv("QITECH_OCR_TIMEOUT_SECONDS", "30"))


class QitechFaceRecognitionClient:
    """
    Cliente simples para o CAAS Face Recognition da QiTech.

    Usa cabeçalho `Authorization: <api_key>` conforme exemplo de cURL/documentação CAAS.
    Fornece um método genérico `analyze_image` e um `get_result` para recuperar
    resultados/arquivo quando aplicável.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # Prefer environment names used in .env: 'face_recognition_key' and 'QITECH_BASE_URL_FACE_RECOGNITION'
        self.api_key = (
            api_key
            or os.getenv("FACE_RECOGNITION_KEY")
            or os.getenv("face_recognition_key")
            or os.getenv("QITECH_FACE_RECOGNITION_KEY")
        )
        env_base = os.getenv("QITECH_BASE_URL_FACE_RECOGNITION") or os.getenv("QITECH_FACE_RECOGNITION_BASE_URL")
        self.base_url = (base_url or env_base or "https://api.sandbox.caas.qitech.app/face_recognition").rstrip("/")

        if not self.api_key:
            raise ValueError("QITECH face_recognition key não definido (face_recognition_key).")

        try:
            self.session = QiTechClient._build_session()
        except Exception:
            self.session = requests.Session()

    def _headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        h = {"Authorization": self.api_key}
        if content_type:
            h["Content-Type"] = content_type
        return h

    def analyze_image(self, image_b64: str, file_type: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Envia imagem (base64) para processamento de face recognition.

        Envia JSON com a chave `image` conforme documentação CAAS:
        {
          "image": "<base64>"
        }
        Opcionalmente inclui `file_type` quando informado.
        """
        # Prefer explicit '/face_recognition/image' when present
        if "/face_recognition/image" in self.base_url:
            url = f"{self.base_url}"
        elif "/face_recognition" in self.base_url:
            url = f"{self.base_url}/image"
        else:
            url = f"{self.base_url}/face_recognition/image"

        payload: Dict[str, Any] = {"image": image_b64}
        if file_type:
            payload["file_type"] = file_type
        headers = self._headers("application/json")

        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede FaceRecognition QiTech: {e}") from e

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
            raise QiTechError(resp.status_code, "Falha na chamada FaceRecognition QiTech", payload)

    def get_result(self, image_id: str, timeout: int = DEFAULT_TIMEOUT) -> Any:
        """Recupera resultado/arquivo de processamento de face recognition.

        Tenta algumas variações de URL compatíveis com o OCR client.
        Retorna JSON quando aplicável, ou bytes brutos se binário.
        """
        # Tenta formar URLs de recuperação sem duplicar segmento
        candidates = []
        if "/face_recognition" in self.base_url:
            base = self.base_url.rstrip("/")
            candidates.append(f"{base}/{image_id}")
            candidates.append(f"{base}/{image_id}/file")
        else:
            candidates.append(f"{self.base_url}/face_recognition/{image_id}")
            candidates.append(f"{self.base_url}/face_recognition/{image_id}/file")
            candidates.append(f"{self.base_url}/face_recognition/image/{image_id}")
            candidates.append(f"{self.base_url}/face_recognition/image/{image_id}/file")

        headers = self._headers()

        last_exc: Optional[QiTechError] = None
        for url in candidates:
            try:
                resp = self.session.get(url, headers=headers, timeout=timeout)
            except requests.RequestException as e:
                last_exc = QiTechError(-1, f"Erro de rede FaceRecognition QiTech: {e}")
                continue

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
                last_exc = QiTechError(resp.status_code, "Falha ao recuperar resultado FaceRecognition QiTech", payload)

        if last_exc:
            raise last_exc
        raise QiTechError(404, "Resultado FaceRecognition não encontrado")

    def authenticate(self, payload: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Chama o endpoint de autenticação do Face Recognition CAAS.

        O corpo (`payload`) é enviado como JSON. Tenta localizar o endpoint
        em variações comuns: '/face_recognition/authentication', '/face_recognition/auth', '/authentication'.
        """
        # Resolve URL preferindo explicit endpoints
        if self.base_url.endswith("/authentication") or "/face_recognition/authentication" in self.base_url:
            url = f"{self.base_url}"
        elif self.base_url.endswith("/auth") or "/face_recognition/auth" in self.base_url:
            url = f"{self.base_url}"
        elif "/face_recognition" in self.base_url:
            url = f"{self.base_url}/authentication"
        else:
            url = f"{self.base_url}/face_recognition/authentication"

        headers = self._headers("application/json")

        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede FaceRecognition QiTech (auth): {e}") from e

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
            raise QiTechError(resp.status_code, "Falha na chamada Auth FaceRecognition QiTech", payload)

    def get_client_session(self, user_id: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Gera um client session key para uso nas SDKs (POST /face_recognition/client_session).

        Body: {"user_id": "..."}
        """
        if "/face_recognition/client_session" in self.base_url:
            url = f"{self.base_url}"
        elif "/face_recognition" in self.base_url:
            url = f"{self.base_url}/client_session"
        else:
            url = f"{self.base_url}/face_recognition/client_session"

        headers = self._headers("application/json")
        payload = {"user_id": user_id}

        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede FaceRecognition QiTech (client_session): {e}") from e

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
            raise QiTechError(resp.status_code, "Falha ao solicitar client_session FaceRecognition QiTech", payload)
