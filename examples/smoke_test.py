# examples/smoke_test.py
import sys, os

from qitech_client import QiTechClient, QiTechError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json

def print_response(title, response):
    print(f"\n=== {title} ===")
    print(json.dumps(response, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    client = QiTechClient(
        api_key="48f5f0b3-e796-4ff6-85ee-f59b1413c500",
        private_key_path="/Users/jeanpires/GitHub/plugqi/keys/ec_p521_private.pem",
        base_url="https://api-auth.sandbox.qitech.app",
    )
    try:
        r = client.post("/test", {"name": "QI Tech"})
        print_response("POST /test", r)

        acc = client.get("/account", params={
            "owner_document_number": "22203015837",
            "account_number": "68670834"
        })
        print_response("GET /account", acc)
    except QiTechError as e:
        print("QiTechError:", e.status, e.payload)
