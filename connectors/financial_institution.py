#!/usr/bin/env python3
"""
Connector para consulta de instituições financeiras
"""

import time
from typing import Dict, Any, Optional, List

class FinancialInstitutionConnector:
    def __init__(self, client):
        self.client = client
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 86400  # 24 horas
    
    def _is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido"""
        if self._cache_timestamp is None:
            return False
        return (time.time() - self._cache_timestamp) < self._cache_ttl
    
    def _update_cache(self, key: str, value: Any) -> None:
        """Atualiza o cache com nova entrada"""
        if self._cache_timestamp is None:
            self._cache_timestamp = time.time()
        self._cache[key] = value
    
    def clear_cache(self) -> None:
        """Limpa o cache manualmente"""
        self._cache.clear()
        self._cache_timestamp = None

    def list_institutions(self, 
                         ispb_number: Optional[str] = None,
                         name: Optional[str] = None,
                         compe_number: Optional[str] = None,
                         min_str_start_date: Optional[str] = None,
                         max_str_start_date: Optional[str] = None,
                         page_number: Optional[int] = None,
                         page_size: Optional[int] = None) -> Dict[str, Any]:
        """Lista instituições financeiras com filtros opcionais"""
        
        params = {}
        
        if ispb_number:
            params['ispb_number'] = ispb_number
        if name:
            params['name'] = name
        if compe_number:
            params['compe_number'] = compe_number
        if min_str_start_date:
            params['min_str_start_date'] = min_str_start_date
        if max_str_start_date:
            params['max_str_start_date'] = max_str_start_date
        if page_number:
            params['page_number'] = page_number
        if page_size:
            params['page_size'] = page_size
        
        return self.client.get("/financial_institution", params=params)
    
    def get_by_ispb(self, ispb_number: str) -> Dict[str, Any]:
        """Busca instituição por ISPB"""
        return self.list_institutions(ispb_number=ispb_number)
    
    def get_by_name(self, name: str) -> Dict[str, Any]:
        """Busca instituição por nome"""
        return self.list_institutions(name=name)
    
    def get_by_compe(self, compe_number: str) -> Dict[str, Any]:
        """Busca instituição por código COMPE"""
        return self.list_institutions(compe_number=compe_number)
    
    def get_by_ispb_cached(self, ispb_number: str) -> Dict[str, Any]:
        """Busca instituição por ISPB com cache"""
        cache_key = f"ispb_{ispb_number}"
        
        # Verificar cache
        if self._is_cache_valid() and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Buscar na API
        result = self.get_by_ispb(ispb_number)
        
        # Salvar no cache
        self._update_cache(cache_key, result)
        
        return result
    
    def get_by_compe_cached(self, compe_number: str) -> Dict[str, Any]:
        """Busca instituição por COMPE com cache"""
        cache_key = f"compe_{compe_number}"
        
        # Verificar cache
        if self._is_cache_valid() and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Buscar na API
        result = self.get_by_compe(compe_number)
        
        # Salvar no cache
        self._update_cache(cache_key, result)
        
        return result
    
    def get_paginated(self, page_number: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Lista instituições com paginação"""
        return self.list_institutions(page_number=page_number, page_size=page_size)
    
    def get_all_active(self) -> List[Dict[str, Any]]:
        """Retorna todas as instituições ativas (sem paginação)"""
        
        response = self.list_institutions()
        
        # Se resposta tem paginação, retorna data
        if 'data' in response and 'pagination' in response:
            return response['data']
        
        # Se resposta é dict direto, converte para lista
        institutions = []
        for ispb, data in response.items():
            if isinstance(data, dict) and data.get('is_active', False):
                data['ispb_number'] = ispb
                institutions.append(data)
        
        return institutions
    
    def search_institutions(self, query: str) -> List[Dict[str, Any]]:
        """Busca instituições por nome (busca parcial)"""
        
        try:
            response = self.list_institutions(name=query)
            
            # Se resposta tem paginação
            if 'data' in response:
                return response['data']
            
            # Se resposta é dict direto
            institutions = []
            for ispb, data in response.items():
                if isinstance(data, dict):
                    data['ispb_number'] = ispb
                    institutions.append(data)
            
            return institutions
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    def get_bank_info(self, bank_code: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de banco por código (ISPB ou COMPE) com cache"""
        
        # Tentar por ISPB primeiro (com cache)
        try:
            response = self.get_by_ispb_cached(bank_code)
            if 'data' in response and response['data']:
                return response['data'][0]
            elif bank_code in response:
                return response[bank_code]
        except:
            pass
        
        # Tentar por COMPE (com cache)
        try:
            response = self.get_by_compe_cached(bank_code)
            if 'data' in response and response['data']:
                return response['data'][0]
            
            # Buscar no dict direto
            for ispb, data in response.items():
                if isinstance(data, dict) and data.get('compe_number') == bank_code:
                    data['ispb_number'] = ispb
                    return data
        except:
            pass
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "cache_size": len(self._cache),
            "cache_valid": self._is_cache_valid(),
            "cache_age_seconds": time.time() - self._cache_timestamp if self._cache_timestamp else 0,
            "ttl_seconds": self._cache_ttl
        }
