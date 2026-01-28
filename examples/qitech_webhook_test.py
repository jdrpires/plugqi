"""Script de teste: envia um webhook de exemplo para o endpoint e consulta o status.

Uso:
  python examples/qitech_webhook_test.py

Configure via env vars (opcionais):
  WEBHOOK_URL (default http://localhost:8000/webhooks/qitech/onboarding)
  STATUS_URL (default http://localhost:8000/webhooks/qitech/status)
  QITECH_WEBHOOK_SECRET

O script cria um payload exemplo, calcula a assinatura usando
`RiskSolutionClient.compute_webhook_signature` e faz POST. Depois faz um GET
para recuperar o status.
"""
import os
import json
import requests
from datetime import datetime, timezone
from risk_solution import RiskSolutionClient


WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'http://localhost:8000/webhooks/qitech/onboarding')
STATUS_URL = os.environ.get('STATUS_URL', 'http://localhost:8000/webhooks/qitech/status')
WEBHOOK_SECRET = os.environ.get('QITECH_WEBHOOK_SECRET', os.environ.get('QITECH_WEBHOOK_SECRET', 'change-me'))


def main():
    # Example payload
    payload = {
        "registration_id": "reg-12345",
        "natural_person_id": "np-999",
        "analysis_status": "APPROVED",
        "event_date": datetime.now(timezone.utc).isoformat(),
        "reason": "Análise automatizada OK",
        "extra": {"score": 92}
    }
    payload_text = json.dumps(payload, ensure_ascii=False)

    sig = RiskSolutionClient.compute_webhook_signature('/webhooks/qitech/onboarding', 'POST', payload_text, WEBHOOK_SECRET)

    headers = {
        'Content-Type': 'application/json',
        'Signature': sig
    }

    print('POST ->', WEBHOOK_URL)
    r = requests.post(WEBHOOK_URL, data=payload_text.encode('utf-8'), headers=headers)
    print('POST status:', r.status_code, r.text)

    # Now query status by registration id
    params = {'id_registro': payload['registration_id']}
    print('GET ->', STATUS_URL, 'params=', params)
    g = requests.get(STATUS_URL, params=params)
    print('GET status:', g.status_code)
    try:
        print('GET body:', json.dumps(g.json(), indent=2, ensure_ascii=False))
    except Exception:
        print('GET body (raw):', g.text)


if __name__ == '__main__':
    main()
