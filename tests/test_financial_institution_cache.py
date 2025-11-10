#!/usr/bin/env python3
"""
Testes unitários para cache de instituições financeiras
"""

import unittest
import time
from unittest.mock import Mock, patch
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.financial_institution import FinancialInstitutionConnector

class TestFinancialInstitutionCache(unittest.TestCase):
    
    def setUp(self):
        """Setup para cada teste"""
        self.mock_client = Mock()
        self.connector = FinancialInstitutionConnector(self.mock_client)
    
    def test_cache_initialization(self):
        """Teste: Cache inicializa vazio"""
        self.assertEqual(len(self.connector._cache), 0)
        self.assertIsNone(self.connector._cache_timestamp)
        self.assertEqual(self.connector._cache_ttl, 86400)  # 24 horas
    
    def test_cache_validity_empty(self):
        """Teste: Cache vazio é inválido"""
        self.assertFalse(self.connector._is_cache_valid())
    
    def test_cache_validity_fresh(self):
        """Teste: Cache recém criado é válido"""
        self.connector._update_cache("test_key", {"data": "test"})
        self.assertTrue(self.connector._is_cache_valid())
    
    def test_cache_validity_expired(self):
        """Teste: Cache expirado é inválido"""
        # Simular cache antigo
        self.connector._cache_timestamp = time.time() - 90000  # Mais de 24h
        self.assertFalse(self.connector._is_cache_valid())
    
    def test_update_cache(self):
        """Teste: Atualização do cache"""
        test_data = {"ispb": "00000000", "name": "Banco Teste"}
        self.connector._update_cache("test_key", test_data)
        
        self.assertEqual(self.connector._cache["test_key"], test_data)
        self.assertIsNotNone(self.connector._cache_timestamp)
    
    def test_clear_cache(self):
        """Teste: Limpeza do cache"""
        # Adicionar dados ao cache
        self.connector._update_cache("test_key", {"data": "test"})
        self.assertEqual(len(self.connector._cache), 1)
        
        # Limpar cache
        self.connector.clear_cache()
        self.assertEqual(len(self.connector._cache), 0)
        self.assertIsNone(self.connector._cache_timestamp)
    
    def test_get_by_ispb_cached_first_call(self):
        """Teste: Primeira chamada vai para API"""
        # Mock da resposta da API
        mock_response = {"data": [{"ispb_number": "00000000", "name": "Banco Teste"}]}
        self.connector.get_by_ispb = Mock(return_value=mock_response)
        
        result = self.connector.get_by_ispb_cached("00000000")
        
        # Verificar que chamou a API
        self.connector.get_by_ispb.assert_called_once_with("00000000")
        
        # Verificar resultado
        self.assertEqual(result, mock_response)
        
        # Verificar que salvou no cache
        self.assertIn("ispb_00000000", self.connector._cache)
    
    def test_get_by_ispb_cached_second_call(self):
        """Teste: Segunda chamada usa cache"""
        # Preparar cache
        cached_data = {"data": [{"ispb_number": "00000000", "name": "Banco Teste"}]}
        self.connector._update_cache("ispb_00000000", cached_data)
        
        # Mock para verificar que não chama API
        self.connector.get_by_ispb = Mock()
        
        result = self.connector.get_by_ispb_cached("00000000")
        
        # Verificar que NÃO chamou a API
        self.connector.get_by_ispb.assert_not_called()
        
        # Verificar resultado do cache
        self.assertEqual(result, cached_data)
    
    def test_get_by_compe_cached_first_call(self):
        """Teste: Primeira chamada COMPE vai para API"""
        mock_response = {"data": [{"compe_number": "001", "name": "Banco do Brasil"}]}
        self.connector.get_by_compe = Mock(return_value=mock_response)
        
        result = self.connector.get_by_compe_cached("001")
        
        self.connector.get_by_compe.assert_called_once_with("001")
        self.assertEqual(result, mock_response)
        self.assertIn("compe_001", self.connector._cache)
    
    def test_get_by_compe_cached_second_call(self):
        """Teste: Segunda chamada COMPE usa cache"""
        cached_data = {"data": [{"compe_number": "001", "name": "Banco do Brasil"}]}
        self.connector._update_cache("compe_001", cached_data)
        
        self.connector.get_by_compe = Mock()
        
        result = self.connector.get_by_compe_cached("001")
        
        self.connector.get_by_compe.assert_not_called()
        self.assertEqual(result, cached_data)
    
    def test_get_cache_stats(self):
        """Teste: Estatísticas do cache"""
        # Cache vazio
        stats = self.connector.get_cache_stats()
        self.assertEqual(stats["cache_size"], 0)
        self.assertFalse(stats["cache_valid"])
        
        # Adicionar dados ao cache
        self.connector._update_cache("test_key", {"data": "test"})
        
        stats = self.connector.get_cache_stats()
        self.assertEqual(stats["cache_size"], 1)
        self.assertTrue(stats["cache_valid"])
        self.assertEqual(stats["ttl_seconds"], 86400)
        self.assertGreaterEqual(stats["cache_age_seconds"], 0)
    
    def test_get_bank_info_with_cache(self):
        """Teste: get_bank_info usa cache"""
        # Mock dos métodos com cache
        mock_ispb_response = {"data": [{"ispb_number": "00000000", "name": "Banco Teste"}]}
        self.connector.get_by_ispb_cached = Mock(return_value=mock_ispb_response)
        
        result = self.connector.get_bank_info("00000000")
        
        self.connector.get_by_ispb_cached.assert_called_once_with("00000000")
        self.assertEqual(result["name"], "Banco Teste")

if __name__ == '__main__':
    unittest.main()
