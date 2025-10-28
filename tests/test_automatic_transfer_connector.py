import pytest
from unittest.mock import Mock
from connectors.automatic_transfer import AutomaticTransferConnector


class TestAutomaticTransferConnector:
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_client = Mock()
        self.connector = AutomaticTransferConnector(self.mock_client)
    
    def test_build_destination_basic(self):
        """Testa helper build_destination básico"""
        destination = self.connector.build_destination(
            account_branch="0001",
            account_number="123456",
            account_digit="7",
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001"
        )
        
        expected = {
            "account_branch": "0001",
            "account_number": "123456",
            "account_digit": "7",
            "document_number": "12345678901",
            "name": "João Silva",
            "financial_institutions_code_number": "001"
        }
        
        assert destination == expected
    
    def test_build_destination_with_percentage(self):
        """Testa helper com percentage"""
        destination = self.connector.build_destination(
            account_branch="0001",
            account_number="123456",
            account_digit="7",
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001",
            percentage=50
        )
        
        assert destination["percentage"] == 50
    
    def test_build_destination_with_pix(self):
        """Testa helper com PIX"""
        destination = self.connector.build_destination(
            account_branch="0001",
            account_number="123456",
            account_digit="7",
            document_number="12345678901",
            name="João Silva",
            financial_institutions_code_number="001",
            is_pix_transfer=True
        )
        
        assert destination["is_pix_transfer"] is True
    
    def test_create_split_percentage_rule(self):
        """Testa criação de regra split percentage"""
        self.mock_client.post.return_value = {"rule": "split_percentage"}
        
        destinations = [{"percentage": 100}]
        result = self.connector.create_split_percentage_rule(
            account_key="test-key",
            destinations=destinations
        )
        
        # Verifica se POST foi chamado
        self.mock_client.post.assert_called_once()
        
        # Verifica argumentos da chamada
        call_args = self.mock_client.post.call_args
        endpoint = call_args[0][0]
        data = call_args[0][1]
        
        assert endpoint == "/baas/automatic_transfer/transfer_configuration"
        assert data["rule"] == "split_percentage"
        assert data["account_key"] == "test-key"
        assert data["rule_configuration"]["destinations"] == destinations
    
    def test_create_split_equal_rule(self):
        """Testa criação de regra split equal"""
        self.mock_client.post.return_value = {"rule": "split_equal"}
        
        destinations = [{"name": "Test"}]
        result = self.connector.create_split_equal_rule(
            account_key="test-key",
            destinations=destinations
        )
        
        self.mock_client.post.assert_called_once()
        call_args = self.mock_client.post.call_args
        data = call_args[0][1]
        
        assert data["rule"] == "split_equal"
    
    def test_create_single_beneficiary_rule(self):
        """Testa criação de regra single beneficiary"""
        self.mock_client.post.return_value = {"rule": "single_beneficiary"}
        
        destination = {"name": "Test"}
        result = self.connector.create_single_beneficiary_rule(
            account_key="test-key",
            destination=destination
        )
        
        self.mock_client.post.assert_called_once()
        call_args = self.mock_client.post.call_args
        data = call_args[0][1]
        
        assert data["rule"] == "single_beneficiary"
        assert data["rule_configuration"]["destination"] == destination
    
    def test_deactivate_rule(self):
        """Testa desativação de regra"""
        self.mock_client.put.return_value = {"is_active": False}
        
        result = self.connector.deactivate_rule(
            automatic_transfer_key="test-key",
            rule_type="split_percentage",
            rule_configuration={"test": "config"}
        )
        
        self.mock_client.put.assert_called_once()
        call_args = self.mock_client.put.call_args
        data = call_args[0][1]
        
        assert data["is_active"] is False
        assert data["automatic_transfer_key"] == "test-key"
