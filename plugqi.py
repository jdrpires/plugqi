from connectors.credit import CreditConnector
from connectors.payment import PaymentConnector
from connectors.boleto import BoletoConnector
from connectors.boleto_payment import BoletoPaymentConnector
from connectors.pix import PixConnector
from connectors.account_opening import AccountOpeningConnector
from connectors.account_opening_orchestrator import AccountOpeningOrchestrator
from connectors.document_upload import DocumentUploadConnector
from connectors.financial_institution import FinancialInstitutionConnector
from connectors.automatic_transfer import AutomaticTransferConnector
import os
from connectors.ted import TedConnector
from connectors.ted_schedule import TedScheduleConnector
from connectors.risk_solution import RiskSolutionClient
from qitech_client import QiTechClient, QiTechError
from connectors.qitech_ocr import QitechOCRClient
from connectors.qitech_face_recognition import QitechFaceRecognitionClient
from connectors.qitech_device_scan import QitechDeviceScanClient


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
        self.ted = TedConnector(self.client)
        self.ted_schedule = TedScheduleConnector(self.client)
        
        # Risk Solution usa Key separada. Se não houver, usa MOCK.
        risk_key = os.getenv("QITECH_API_KEY", "MOCK_KEY")
        self.risk = RiskSolutionClient(api_key=risk_key)
        # OCR CAAS (usa chave/API separada definida em QITECH_OCR_API_KEY)
        try:
            self.qitech_ocr = QitechOCRClient()
        except Exception:
            self.qitech_ocr = None
        # Face Recognition CAAS (usa chave/API separada definida em .env)
        try:
            self.qitech_face_recognition = QitechFaceRecognitionClient()
        except Exception:
            self.qitech_face_recognition = None
        # Device Scan CAAS (usa token/chave separada definida em .env)
        try:
            self.qitech_device_scan = QitechDeviceScanClient()
        except Exception:
            self.qitech_device_scan = None
        
        # Orquestrador (inicializado após os outros connectors)
        self.account_orchestrator = AccountOpeningOrchestrator(self)

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
