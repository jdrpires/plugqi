from connectors.credit import CreditConnector
from connectors.payment import PaymentConnector
from connectors.boleto import BoletoConnector
from connectors.boleto_payment import BoletoPaymentConnector
from connectors.pix import PixConnector
from connectors.account_opening import AccountOpeningConnector
from connectors.document_upload import DocumentUploadConnector
from connectors.financial_institution import FinancialInstitutionConnector
from qitech_client import QiTechClient, QiTechError


class PlugQi:
    def __init__(self, client: QiTechClient | None = None):
        self.client = client or QiTechClient()
        # Injeta o client nas connectors
        self.credit = CreditConnector(self.client)
        self.payment = PaymentConnector(self.client)
        self.boleto = BoletoConnector(self.client)
        self.boleto_payment = BoletoPaymentConnector(self.client)
        self.pix = PixConnector(self.client)
        self.account_opening = AccountOpeningConnector(self.client)
        self.document_upload = DocumentUploadConnector(self.client)
        self.financial_institution = FinancialInstitutionConnector(self.client)

    def health_check(self) -> bool:
        """
        Verifica conectividade com a API via /test
        Tenta POST /test; se falhar, tenta GET /test/{api_key}
        """
        try:
            r = self.client.post("/test", {"name": "QI Tech"})
            return bool(r)
        except QiTechError:
            # fallback opcional para GET /test/{API_KEY}
            try:
                r = self.client.get(f"/test/{self.client.api_key}")
                return bool(r)
            except Exception:
                return False
