# connectors/payment.py
from ..qitech_client import QiTechClient

class PaymentConnector:
    def __init__(self, client: QiTechClient):
        self.client = client

    def create_pix_payment(self, amount, recipient_key):
        return self.client.post("/pix/payment", {
            "amount": amount,
            "recipient_key": recipient_key
        })

    def get_payment_status(self, payment_id):
        return self.client.get(f"/payment/{payment_id}")

    def create_ted_payment(self, amount, bank_data):
        return self.client.post("/ted/payment", {
            "amount": amount,
            "bank_account": bank_data
        })
