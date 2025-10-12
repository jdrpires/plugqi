# tests/conftest.py
import os
import sys
import json
import hashlib
import pathlib
import inspect
import pytest

# 1) garante que a raiz do projeto está no sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 2) importa seu cliente na raiz
from qitech_client import QiTechClient  # seu arquivo está na raiz do repo

# 3) helper: instanciar QiTechClient mapeando nomes de argumentos automaticamente
def build_client_dynamic(cfg):
    sig = inspect.signature(QiTechClient.__init__)
    params = sig.parameters

    def first_present(candidates):
        for name in candidates:
            if name in params:
                return name
        return None

    kw = {}

    # base_url
    k = first_present(["base_url", "base", "host", "api_base", "endpoint", "base_uri", "baseUri"])
    if k:
        kw[k] = cfg.base_url

    # api_client_key (nome varia muito entre libs)
    k = first_present([
        "api_client_key", "client_key", "api_client", "x_client_key",
        "api_client_id", "api_client_header", "api_clientkey"
    ])
    if k:
        kw[k] = cfg.api_client_key

    # private_key_pem
    k = first_present([
        "private_key_pem", "private_key", "pem", "signing_key",
        "jwt_private_key", "es512_private_key"
    ])
    if k:
        kw[k] = cfg.private_key_pem

    # api_key pública (usada no /test/{API_KEY})
    k = first_present(["api_key", "key", "api_token", "public_key", "client_id", "api_key_id"])
    if k:
        kw[k] = cfg.api_key

    try:
        return QiTechClient(**kw)
    except TypeError as e:
        raise AssertionError(
            f"Não consegui instanciar QiTechClient com kwargs={kw}.\n"
            f"Assinatura do __init__: {sig}"
        ) from e


# 4) config dummy para rodar os testes sem vazar segredo real
class DummyCfg:
    def __init__(self, base_url, api_client_key, private_key_pem, api_key):
        self.base_url = base_url
        self.api_client_key = api_client_key
        self.private_key_pem = private_key_pem
        self.api_key = api_key


@pytest.fixture
def sandbox_cfg():
    return DummyCfg(
        base_url=os.environ.get("QITECH_BASE_URL_SANDBOX", "https://sandbox.qitech.example"),
        api_client_key="sandbox-client-key",
        private_key_pem=os.environ.get("QITECH_PVT_SANDBOX", "-----BEGIN PRIVATE KEY-----\n...test...\n-----END PRIVATE KEY-----"),
        api_key="sandbox-api-key",
    )


@pytest.fixture
def prod_cfg():
    return DummyCfg(
        base_url=os.environ.get("QITECH_BASE_URL_PROD", "https://api.qitech.example"),
        api_client_key="prod-client-key",
        private_key_pem=os.environ.get("QITECH_PVT_PROD", "-----BEGIN PRIVATE KEY-----\n...test...\n-----END PRIVATE KEY-----"),
        api_key="prod-api-key",
    )


@pytest.fixture
def client_sandbox(sandbox_cfg):
    return build_client_dynamic(sandbox_cfg)


@pytest.fixture
def md5_of():
    def _inner(d):
        payload = json.dumps(d, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return hashlib.md5(payload).hexdigest()
    return _inner
