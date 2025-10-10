from jose import jwt
import json
from datetime import datetime, timezone
from hashlib import md5
import requests

def get_auth_header(endpoint, method, CLIENT_PRIVATE_KEY, API_KEY, request_body=None):

    if request_body is None:
        request_body = {}

    #O objeto de data e hora informado deve estar em UTC e deve seguir o padrão da norma internacional ISO 8601 ("2023-06-26T19:48:32.759844Z")
    #timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # ISO 8601 UTC com timezone-aware (corrige o DeprecationWarning)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    #Definimos o algoritmo de codificação JWT
    jwt_header = {
        "typ": "JWT",
        "alg": "ES512"
    }

    #Construir hash em MD5 para assinatura no cabeçalho (header) utilizando o payload
    json_body = json.dumps(request_body)
    md5_hash = md5(json_body.encode()).hexdigest()

    #Essas são as infromações necessárias para assinatura do cabeçalho
    jwt_body = {
        "payload_md5": md5_hash,
        "timestamp": timestamp,
        "method": method,
        "uri": endpoint
    }

    #Realizar criptografia do header
    encoded_header_token = jwt.encode(
        claims=jwt_body,
        key=CLIENT_PRIVATE_KEY,
        algorithm="ES512",
        headers=jwt_header
    )

    #Montar header assinado
    signed_header = {
        "AUTHORIZATION": encoded_header_token,
        "API-CLIENT-KEY": API_KEY
    }

    return signed_header


if __name__ == "__main__":

    #Utilizaremos as variáveis base_url, endpoint, method e request_body. Neste exemplo faremos um POST no endpoint "/test".
    #As chaves contidas neste exemplo são apenas para fins de demonstração. Por favor, utilize suas próprias chaves.
    API_KEY = "48f5f0b3-e796-4ff6-85ee-f59b1413c500"

    CLIENT_PRIVATE_KEY = '''-----BEGIN EC PRIVATE KEY-----
MIHcAgEBBEIBaU+1JPZI1/DSogwgKERD/aQIXJPw02WBiywWDHXI+dOD6oobIMJz
1n1ZstyjDsbU1M8nkqEJwPgo9Ke8CCNTw5ygBwYFK4EEACOhgYkDgYYABACDfNU8
Ubwz58UUa3wPaXrHyzqwcKskYdKTbTtGumn8hsi1ZC+7eGYYjj1hyJCU8X6+6knh
pki7KC5jNaK4gDnlwgEFS3ZmxDXzrS1hUro+mdfz/3wfJAZ1yJki3jMEHg0FqRKF
ThxY+nLJk+Wr6MyNpjBMPvjv2KY/xFkLNQHmi1MY6A==
-----END EC PRIVATE KEY-----'''

    BASE_URL = "https://api-auth.sandbox.qitech.app"
    METHOD = "POST" #GET ou POST
    REQUEST_BODY = {
        "name": "QI Tech"
    }

    #Para fazer um GET na /test, é necessário inserir a API key ao final, enquanto para fazer um POST no mesmo endpoint, não é necessário
    if METHOD == 'GET':
        ENDPOINT = f"/test/{API_KEY}"
        signed_header = get_auth_header(ENDPOINT, METHOD, CLIENT_PRIVATE_KEY, API_KEY)
        response = requests.get(f"{BASE_URL}{ENDPOINT}", headers=signed_header)
    else:
        ENDPOINT = f"/test/"
        signed_header = get_auth_header(ENDPOINT, METHOD, CLIENT_PRIVATE_KEY, API_KEY, REQUEST_BODY)
        response = requests.post(f"{BASE_URL}{ENDPOINT}", json=REQUEST_BODY, headers=signed_header)

    print(response.status_code)
    print(response.json())

    # Teste da API de account
    print("\n--- Testando API de Account ---")
    ACCOUNT_ENDPOINT = "/account"
    ACCOUNT_PARAMS = "?owner_document_number=22203015837&account_number=6867083"
    ACCOUNT_METHOD = "GET"
    
    account_signed_header = get_auth_header(ACCOUNT_ENDPOINT, ACCOUNT_METHOD, CLIENT_PRIVATE_KEY, API_KEY)
    account_response = requests.get(f"{BASE_URL}{ACCOUNT_ENDPOINT}{ACCOUNT_PARAMS}", headers=account_signed_header)
    
    print(f"Account Status: {account_response.status_code}")
    print(f"Account Response: {account_response.json()}")
