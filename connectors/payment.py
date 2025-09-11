from ..qitech_client import QiTechClient

class PaymentConnector(QiTechClient):
    def create_pix_payment(self, amount, recipient_key):
        return self._make_request('POST', '/pix/payment', {
            'amount': amount,
            'recipient_key': recipient_key
        })
    
    def get_payment_status(self, payment_id):
        return self._make_request('GET', f'/payment/{payment_id}')
    
    def create_ted_payment(self, amount, bank_data):
        return self._make_request('POST', '/ted/payment', {
            'amount': amount,
            'bank_account': bank_data
        })
