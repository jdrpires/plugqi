from jose import jwt
import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path
import requests

def load_private_key(pem_path: str) -> str:
    pem = Path(pem_path).read_text().strip()
    # Verificação defensiva: precisa ser privada
    if "BEGIN EC PRIVATE KEY" not in pem and "BEGIN PRIVATE KEY" not in pem:
        raise ValueError("O arquivo não contém uma CHAVE PRIVADA em PEM.")
    return pem

def get_auth_header(endpoint, method, client_private_key_pem, api_key, request_body=None):
    if request_body is None:
        request_body = {}

    # ISO 8601 UTC com timezone-aware (corrige o DeprecationWarning)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    jwt_header = {"typ": "JWT", "alg": "ES512"}

    # MD5 estável (sem espaços extras)
    json_body = json.dumps(request_body, separators=(",", ":"))
    md5_hash = md5(json_body.encode("utf-8")).hexdigest()

    jwt_body = {
        "payload_md5": md5_hash,
        "timestamp": timestamp,
        "method": method,
        "uri": endpoint
    }

    token = jwt.encode(
        claims=jwt_body,
        key=client_private_key_pem,   # <-- **PRIVADA** aqui
        algorithm="ES512",
        headers=jwt_header
    )

    return {"AUTHORIZATION": token, "API-CLIENT-KEY": api_key}

if __name__ == "__main__":
    API_KEY = "48f5f0b3-e796-4ff6-85ee-f59b1413c500"
    BASE_URL = "https://api-auth.sandbox.qitech.app"
    METHOD = "POST"
    REQUEST_BODY = {"name": "QI Tech"}

    # Leia a **privada**
    CLIENT_PRIVATE_KEY = load_private_key("ec512-private.pem")

    if METHOD == "GET":
        ENDPOINT = f"/test/{API_KEY}"
        headers = get_auth_header(ENDPOINT, METHOD, CLIENT_PRIVATE_KEY, API_KEY)
        resp = requests.get(f"{BASE_URL}{ENDPOINT}", headers=headers)
    else:
        ENDPOINT = "/test/"
        headers = get_auth_header(ENDPOINT, METHOD, CLIENT_PRIVATE_KEY, API_KEY, REQUEST_BODY)
        resp = requests.post(f"{BASE_URL}{ENDPOINT}", json=REQUEST_BODY, headers=headers)

    print(resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
