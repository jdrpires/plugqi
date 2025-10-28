import pytest
from unittest.mock import Mock
from connectors.financial_institution import FinancialInstitutionConnector


class TestFinancialInstitutionConnector:
    
    def setup_method(self):
        """Setup para cada teste"""
        self.mock_client = Mock()
        self.connector = FinancialInstitutionConnector(self.mock_client)
    
    def test_list_institutions(self):
        """Testa listagem de instituições"""
        mock_response = {
            "00000000": {
                "name": "Banco do Brasil S.A.",
                "ispb_number": "00000000",
                "compe_number": "001"
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.list_institutions()
        
        self.mock_client.get.assert_called_once_with("/financial_institution", params={})
        assert result == mock_response
    
    def test_get_by_ispb(self):
        """Testa busca por ISPB"""
        mock_response = {
            "60746948": {
                "name": "Banco Bradesco S.A.",
                "ispb_number": "60746948",
                "compe_number": "237"
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_by_ispb("60746948")
        
        self.mock_client.get.assert_called_once_with("/financial_institution", params={"ispb_number": "60746948"})
        assert result == mock_response
    
    def test_get_by_compe(self):
        """Testa busca por COMPE"""
        mock_response = {
            "60746948": {
                "name": "Itaú Unibanco S.A.",
                "ispb_number": "60746948",
                "compe_number": "341"
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_by_compe("341")
        
        self.mock_client.get.assert_called_once_with("/financial_institution", params={"compe_number": "341"})
        assert result == mock_response
    
    def test_get_by_name(self):
        """Testa busca por nome"""
        mock_response = {
            "data": [{
                "name": "Banco do Brasil S.A.",
                "ispb_number": "00000000",
                "compe_number": "001"
            }]
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_by_name("Banco do Brasil")
        
        self.mock_client.get.assert_called_once_with("/financial_institution", params={"name": "Banco do Brasil"})
        assert result == mock_response
    
    def test_get_paginated(self):
        """Testa busca paginada"""
        mock_response = {
            "data": [
                {"name": "Banco 1", "ispb_number": "00000001"},
                {"name": "Banco 2", "ispb_number": "00000002"}
            ],
            "pagination": {
                "current_page": 1,
                "rows_per_page": 2,
                "total_rows": 230,
                "total_pages": 115
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_paginated(page_number=1, page_size=2)
        
        self.mock_client.get.assert_called_once_with("/financial_institution", params={"page_number": 1, "page_size": 2})
        assert result == mock_response
    
    def test_get_bank_info_found(self):
        """Testa get_bank_info quando encontra banco"""
        mock_response = {
            "60746948": {
                "name": "Itaú Unibanco S.A.",
                "ispb_number": "60746948",
                "compe_number": "341"
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_bank_info("341")
        
        assert result["name"] == "Itaú Unibanco S.A."
        assert result["compe_number"] == "341"
    
    def test_get_bank_info_not_found(self):
        """Testa get_bank_info quando não encontra banco"""
        self.mock_client.get.return_value = {}
        
        result = self.connector.get_bank_info("999")
        
        assert result is None
    
    def test_get_all_active_dict_format(self):
        """Testa get_all_active com formato dict"""
        mock_response = {
            "00000000": {
                "name": "Banco do Brasil S.A.",
                "ispb_number": "00000000",
                "compe_number": "001",
                "is_active": True
            },
            "60746948": {
                "name": "Banco Bradesco S.A.",
                "ispb_number": "60746948",
                "compe_number": "237",
                "is_active": True
            }
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_all_active()
        
        assert len(result) == 2
        assert result[0]["name"] == "Banco do Brasil S.A."
        assert result[1]["name"] == "Banco Bradesco S.A."
    
    def test_get_all_active_paginated_format(self):
        """Testa get_all_active com formato paginado"""
        mock_response = {
            "data": [
                {"name": "Banco 1", "ispb_number": "00000001"},
                {"name": "Banco 2", "ispb_number": "00000002"}
            ],
            "pagination": {"total_rows": 2}
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.get_all_active()
        
        assert len(result) == 2
        assert result[0]["name"] == "Banco 1"
        assert result[1]["name"] == "Banco 2"
    
    def test_search_institutions(self):
        """Testa busca com query"""
        mock_response = {"data": [{"name": "Test Bank"}]}
        self.mock_client.get.return_value = mock_response
        
        result = self.connector.search_institutions("Test")
        
        self.mock_client.get.assert_called_once_with("/financial_institution", params={"name": "Test"})
        assert result == [{"name": "Test Bank"}]
