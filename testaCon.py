# examples/smoke_test.py
from plugqi.qitech_client import QiTechClient, QiTechError

if __name__ == "__main__":
    client = QiTechClient()  # usa .env
    try:
        # POST /test
        resp = client.post("/test", {"name": "QI Tech"})
        print("POST /test OK:", resp)

        # GET /account com query
        acc = client.get("/account", params={
            "owner_document_number": "22203015837",
            "account_number": "6867083"
        })
        print("GET /account OK:", acc)
    except QiTechError as e:
        print("Erro QiTech:", e.status, e.payload)
