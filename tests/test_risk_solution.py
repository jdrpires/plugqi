import json
import pytest
from unittest.mock import patch, MagicMock

from risk_solution import RiskSolutionClient


def test_compute_webhook_signature():
    endpoint = '/webhook'
    method = 'POST'
    payload = '{"k": "v"}'
    signature_key = 'secret'
    sig = RiskSolutionClient.compute_webhook_signature(endpoint, method, payload, signature_key)
    assert isinstance(sig, str)
    assert len(sig) == 40  # sha1 hex length


def test_send_natural_person_calls_requests_post():
    client = RiskSolutionClient(api_key='APIKEY')
    payload = {'document_number': '123.456.789-12', 'id': 'abc'}

    with patch('risk_solution.requests.post') as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_post.return_value = mock_resp

        resp = client.send_natural_person(payload, analyze=True)

        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        assert 'natural_person' in called_args[0]
        assert called_kwargs['headers']['Authorization'] == 'APIKEY'
        assert resp.status_code == 201


def test_send_natural_person_invalid_cpf_raises():
    client = RiskSolutionClient(api_key='APIKEY')
    payload = {'document_number': 'invalid'}
    with pytest.raises(ValueError):
        client.send_natural_person(payload)
