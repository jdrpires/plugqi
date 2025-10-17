import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock
from connectors.boleto import BoletoConnector

def test_boleto_connector_init():
    """Testa inicialização do BoletoConnector"""
    mock_client = Mock()
    connector = BoletoConnector(mock_client)
    assert connector.client == mock_client

def test_build_payer_data():
    """Testa helper para criar dados do pagador"""
    mock_client = Mock()
    connector = BoletoConnector(mock_client)
    
    payer = connector.build_payer_data(
        name="João Silva",
        document="12345678901",
        email="joao@email.com"
    )
    
    assert payer["name"] == "João Silva"
    assert payer["document_number"] == "12345678901"
    assert payer["person_type"] == "natural"
    assert payer["contact"]["email"] == "joao@email.com"

def test_build_simple_boleto():
    """Testa helper para criar boleto simples"""
    mock_client = Mock()
    connector = BoletoConnector(mock_client)
    
    boleto = connector.build_simple_boleto(
        request_control_key=str(uuid.uuid4()),
        amount=100.50,
        expiration="2024-12-31",
        payer_name="João Silva",
        payer_document="12345678901"
    )
    
    assert boleto["amount"] == 100.50
    assert boleto["expiration"] == "2024-12-31"
    assert boleto["payer_data"]["name"] == "João Silva"

def test_create_boleto_calls_client():
    """Testa se create_boleto chama o client corretamente"""
    mock_client = Mock()
    mock_client.post.return_value = {"bank_slip_key": "test-key"}
    
    connector = BoletoConnector(mock_client)
    
    result = connector.create_boleto("account-key", "profile-key", {"test": "data"})
    
    mock_client.post.assert_called_once_with(
        "/account/account-key/requester_profile/profile-key/bank_slip",
        {"test": "data"}
    )
    assert result == {"bank_slip_key": "test-key"}
