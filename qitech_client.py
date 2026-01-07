# plugqi/qitech_client.py
import os
import json
from typing import Any, Dict, Optional, Tuple
from hashlib import md5
from datetime import datetime, timezone
from urllib.parse import urlsplit
from requests.models import PreparedRequest

import requests
from jose import jwt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv, find_dotenv

# Carrega o .env da raiz do projeto (funciona em qualquer diretório de execução)
load_dotenv(find_dotenv(), override=False)

DEFAULT_TIMEOUT = int(os.getenv("QITECH_TIMEOUT_SECONDS", "30"))

class QiTechError(Exception):
    def __init__(self, status: int, message: str, payload: Optional[dict] = None):
        super().__init__(f"[QiTechError] {status} - {message}")
        self.status = status
        self.payload = payload or {}

class QiTechClient:
    """
    Cliente QiTech com assinatura JWT ES512.
    Garante MD5 correto e assinatura exata do URI (incluindo querystring).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key_path: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("QITECH_CLIENT_KEY") or os.getenv("QITECH_API_KEY")
        self.private_key_path = private_key_path or os.getenv("QITECH_PRIVATE_KEY_PATH")
        self.base_url = (base_url or os.getenv("QITECH_BASE_URL") or "https://api-auth.sandbox.qitech.app").rstrip("/")

        if not self.api_key:
            raise ValueError("QITECH_CLIENT_KEY (ou QITECH_API_KEY) não definido.")
        if not self.private_key_path:
            raise ValueError("QITECH_PRIVATE_KEY_PATH não definido.")

        self.private_key_pem = self._load_private_key_pem()
        self.session = self._build_session()

    # ---------- Infraestrutura ----------

    @staticmethod
    def _build_session() -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST", "DELETE"]),
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        return s

    @staticmethod
    def _utc_timestamp() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _load_private_key_pem(self) -> str:
        """
        Aceita:
          - Caminho para arquivo PEM (ex.: ./keys/ec_p521_private.pem)
          - PEM inline (multilinha ou com \n)
          - BASE64:<conteúdo> (opcional)
        """
        raw = (self.private_key_path or "").strip()

        # Remove aspas acidentais
        if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
            raw = raw[1:-1].strip()

        # PEM inline (multilinha real)
        if raw.startswith("-----BEGIN"):
            return raw

        # PEM inline com "\n" literais
        if "\\n" in raw and "BEGIN" in raw:
            return raw.replace("\\n", "\n")

        # BASE64:<conteúdo>
        if raw.startswith("BASE64:"):
            import base64
            b64 = raw.split("BASE64:", 1)[1].strip()
            return base64.b64decode(b64).decode("utf-8")

        # Caminho: expande ~ e variáveis; tenta CWD e raiz do pacote
        raw_expanded = os.path.expanduser(os.path.expandvars(raw))
        path_cwd = os.path.abspath(raw_expanded)
        pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path_pkg = os.path.abspath(os.path.join(pkg_root, raw_expanded.lstrip("./")))

        for candidate in (path_cwd, path_pkg):
            if os.path.exists(candidate):
                with open(candidate, "r", encoding="utf-8") as f:
                    return f.read()

        raise ValueError("QITECH_PRIVATE_KEY_PATH inválido: nem PEM inline nem caminho de arquivo existente.")

    # ---------- MD5 e JWT ----------

    @staticmethod
    def _payload_md5_bytes(b: bytes) -> str:
        return md5(b).hexdigest()

    def _jwt_for(self, method: str, endpoint: str, pmd5: str) -> str:
        return jwt.encode(
            claims={
                "payload_md5": pmd5,
                "timestamp": self._utc_timestamp(),
                "method": method.upper(),
                "uri": endpoint,
            },
            key=self.private_key_pem,
            algorithm="ES512",
            headers={"typ": "JWT", "alg": "ES512"},
        )

    # ---------- Core ----------

    def _request(
        self,
        method: str,
        endpoint: str,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Tuple[str, bytes, str]]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        file_md5: Optional[str] = None,
    ) -> Dict[str, Any]:
        method = method.upper()
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        # --- 0) Monta URL relativa exata com query ordenada ---
        pr = PreparedRequest()
        params_sorted = {k: params[k] for k in sorted(params.keys())} if params else None
        pr.prepare_url("https://dummy.local" + endpoint, params_sorted)
        parts = urlsplit(pr.url)
        relative_url = parts.path + (("?" + parts.query) if parts.query else "")

        # --- 1) Monta bytes e MD5 ---
        encoded_body: bytes = b""
        content_type_json = False

        if files:
            # Para upload de arquivos, usar MD5 fornecido ou calcular do arquivo
            if file_md5:
                pmd5 = file_md5
            else:
                first_key = next(iter(files))
                file_tuple = files[first_key]
                file_bytes = b""
                if isinstance(file_tuple, (tuple, list)) and len(file_tuple) >= 2 and isinstance(file_tuple[1], (bytes, bytearray)):
                    file_bytes = file_tuple[1]  # type: ignore
                pmd5 = self._payload_md5_bytes(file_bytes)
        else:
            if method in ("GET", "DELETE"):
                encoded_body = b""
                pmd5 = self._payload_md5_bytes(b"{}")  # QI: usa "{}" em GET/DELETE
            else:
                encoded_body = json.dumps(json_body or {}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                content_type_json = True
                pmd5 = self._payload_md5_bytes(encoded_body)

        # --- 2) Gera JWT assinando exatamente o mesmo relative_url ---
        token = self._jwt_for(method, relative_url, pmd5)
        headers = {"AUTHORIZATION": token, "API-CLIENT-KEY": self.api_key}
        if content_type_json:
            headers["Content-Type"] = "application/json"

        # --- 3) Envia request com o mesmo relative_url ---
        url = f"{self.base_url}{relative_url}"

        try:
            if files:
                resp = self.session.request(method="POST", url=url, headers=headers, files=files, timeout=timeout)
            else:
                if method in ("GET", "DELETE"):
                    resp = self.session.request(method=method, url=url, headers=headers, timeout=timeout)
                else:
                    resp = self.session.request(
                        method=method, url=url, headers=headers, data=encoded_body, timeout=timeout
                    )
        except requests.RequestException as e:
            raise QiTechError(-1, f"Erro de rede: {e}") from e

        # --- 4) Trata resposta ---
        if 200 <= resp.status_code < 300:
            if not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        else:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"raw": resp.text}
            raise QiTechError(resp.status_code, "Falha na chamada à QiTech", payload)

    # ---------- Métodos públicos ----------

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", endpoint, json_body=json_body)

    def patch(self, endpoint: str, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("PATCH", endpoint, json_body=json_body)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("DELETE", endpoint, params=params)

    def post_file(
        self,
        endpoint: str,
        files: Dict[str, Tuple[str, bytes, str]],
        params: Optional[Dict[str, Any]] = None,
        md5_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload de arquivo com MD5 específico para autenticação
        """
        return self._request("POST", endpoint, files=files, params=params, file_md5=md5_hash)

    # ---------- Helper público para gerar headers de autenticação (útil para Postman/local proxy) ----------
    def auth_headers_for(
        self,
        method: str,
        endpoint: str,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Tuple[str, bytes, str]]] = None,
        file_md5: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Gera um dicionário com os headers necessários para autenticação junto à QiTech:
        - 'AUTHORIZATION': JWT ES512
        - 'API-CLIENT-KEY': chave de cliente
        - 'Content-Type': 'application/json' quando aplicável

        Este método replica a lógica de cálculo do MD5 do payload usada internamente,
        permitindo que ferramentas externas (ex.: Postman) obtenham o token para
        executar requests assinadas.
        """
        method = (method or "GET").upper()

        # prepara endpoint no formato relativo (/path?query)
        endpoint_rel = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        # calcula pmd5 conforme a lógica interna
        if files:
            if file_md5:
                pmd5 = file_md5
            else:
                first_key = next(iter(files))
                file_tuple = files[first_key]
                file_bytes = b""
                if isinstance(file_tuple, (tuple, list)) and len(file_tuple) >= 2 and isinstance(file_tuple[1], (bytes, bytearray)):
                    file_bytes = file_tuple[1]
                pmd5 = self._payload_md5_bytes(file_bytes)
            content_type_json = False
        else:
            if method in ("GET", "DELETE"):
                pmd5 = self._payload_md5_bytes(b"{}")
                content_type_json = False
            else:
                encoded_body = json.dumps(json_body or {}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                pmd5 = self._payload_md5_bytes(encoded_body)
                content_type_json = True

        token = self._jwt_for(method, endpoint_rel, pmd5)
        headers: Dict[str, str] = {"AUTHORIZATION": token, "API-CLIENT-KEY": self.api_key}
        if content_type_json:
            headers["Content-Type"] = "application/json"

        return headers
