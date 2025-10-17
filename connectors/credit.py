# connectors/credit.py

class CreditConnector:
    def __init__(self, client):
        self.client = client

    def create_debt(self, borrower_data, financial_data):
        return self.client.post("/debt", {
            "borrower": borrower_data,
            "financial": financial_data
        })

    def get_debt(self, debt_key):
        return self.client.get(f"/debt/{debt_key}")

    def list_debts(self):
        return self.client.get("/debt")

    def simulate_credit(self, amount, installments):
        return self.client.post("/debt/simulation", {
            "borrowed_amount": amount,
            "number_of_installments": installments
        })
