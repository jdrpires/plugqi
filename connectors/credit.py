from ..qitech_client import QiTechClient

class CreditConnector(QiTechClient):
    def create_debt(self, borrower_data, financial_data):
        return self._make_request('POST', '/debt', {
            'borrower': borrower_data,
            'financial': financial_data
        })
    
    def get_debt(self, debt_key):
        return self._make_request('GET', f'/debt/{debt_key}')
    
    def list_debts(self):
        return self._make_request('GET', '/debt')
    
    def simulate_credit(self, amount, installments):
        return self._make_request('POST', '/debt/simulation', {
            'borrowed_amount': amount,
            'number_of_installments': installments
        })
