import os
from typing import Any, Dict, Optional
import requests
from qitech_client import QiTechError, QiTechClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

DEFAULT_TIMEOUT = int(os.getenv("QITECH_DEVICE_SCAN_TIMEOUT_SECONDS", os.getenv("QITECH_OCR_TIMEOUT_SECONDS", "30")))


class QitechDeviceScanClient:
    """Cliente simples para o CAAS Device Scan da QiTech.

    Usa cabeçalho `Authorization: <api_key>` conforme exemplos CAAS.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # Prefer environment names: device_scan_key, device_scan_mobile_token, DEVICE_SCAN_API_KEY, QITECH_DEVICE_SCAN_KEY
        self.api_key = (
            api_key
            or os.getenv("DEVICE_SCAN_API_KEY")
            or os.getenv("device_scan_key")
            or os.getenv("device_scan_mobile_token")
            or os.getenv("QITECH_DEVICE_SCAN_KEY")
            or os.getenv("QITECH_API_KEY")
        )
        env_base = os.getenv("QITECH_BASE_URL_DEVICE_SCAN") or os.getenv("QITECH_DEVICE_SCAN_BASE_URL")
        # default base similar to CAAS
        self.base_url = (base_url or env_base or "https://api.sandbox.caas.qitech.app/device_scan").rstrip("/")

        if not self.api_key:
            raise ValueError("QITECH device_scan key não definido (device_scan_key, device_scan_mobile_token ou DEVICE_SCAN_API_KEY).")

        try:
            self.session = QiTechClient._build_session()
        except Exception:
            self.session = requests.Session()

    def _headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        h = {"Authorization": self.api_key}
        if content_type:
            h["Content-Type"] = content_type
        return h

    def send_payload(self, payload: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Envia payload de device-scan conforme documentação CAAS.

        O `payload` deve seguir o formato exigido pelo endpoint (ex.: eventos do SDK mobile).
        """
        # If base_url already points to device_scan endpoint, use it; else append
        if "/device_scan" in self.base_url:
            url = f"{self.base_url}"
        else:
            url = f"{self.base_url}/device_scan"

        headers = self._headers("application/json")

        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede DeviceScan QiTech: {e}") from e

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
            raise QiTechError(resp.status_code, "Falha na chamada DeviceScan QiTech", payload)

    def get_token(self, session_id: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Solicita token para um `session_id` ao endpoint de token do Device Scan.

        Faz POST com JSON {"session_id": "..."} e retorna o JSON da API.
        """
        # Se base_url já apontar para o endpoint /device_scan/token, usa diretamente
        if self.base_url.endswith("/token") or "/device_scan/token" in self.base_url:
            url = f"{self.base_url}"
        elif "/device_scan" in self.base_url:
            url = f"{self.base_url}/token"
        else:
            url = f"{self.base_url}/device_scan/token"

        headers = self._headers("application/json")
        payload = {"session_id": session_id}

        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede DeviceScan QiTech (token): {e}") from e

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
            raise QiTechError(resp.status_code, "Falha ao solicitar token DeviceScan QiTech", payload)

    def get_result(self, session_id: str, timeout: int = DEFAULT_TIMEOUT) -> Any:
        """Recupera resultado do device scan por `session_id` (variações de URL tentadas)."""
        candidates = []
        if "/device_scan" in self.base_url:
            base = self.base_url.rstrip("/")
            candidates.append(f"{base}/{session_id}")
            candidates.append(f"{base}/{session_id}/result")
        else:
            candidates.append(f"{self.base_url}/device_scan/{session_id}")
            candidates.append(f"{self.base_url}/device_scan/{session_id}/result")

        headers = self._headers()
        last_exc: Optional[QiTechError] = None
        for url in candidates:
            try:
                resp = self.session.get(url, headers=headers, timeout=timeout)
            except requests.RequestException as e:
                last_exc = QiTechError(-1, f"Erro de rede DeviceScan QiTech: {e}")
                continue

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
                last_exc = QiTechError(resp.status_code, "Falha ao recuperar resultado DeviceScan QiTech", payload)

        if last_exc:
            raise last_exc
        raise QiTechError(404, "Resultado DeviceScan não encontrado")
