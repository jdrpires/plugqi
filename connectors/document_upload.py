#!/usr/bin/env python3
"""
Connector para upload de documentos na QiTech
"""

import hashlib
import os
from typing import Dict, Any, Union

class DocumentUploadConnector:
    def __init__(self, client):
        self.client = client

    def upload_file(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """Upload de arquivo local"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        filename = os.path.basename(file_path)
        
        # Detectar tipo do arquivo se não fornecido
        if not file_type:
            file_type = self._detect_file_type(filename)
        
        return self._upload_content(file_content, filename, file_type)
    
    def upload_content(self, content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """Upload de conteúdo em bytes"""
        return self._upload_content(content, filename, file_type)
    
    def _upload_content(self, content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """Executa upload do conteúdo"""
        
        # Calcular MD5 do arquivo
        md5_hash = hashlib.md5(content).hexdigest()
        
        # Preparar arquivo para upload
        files = {
            'file': (filename, content, file_type)
        }
        
        try:
            response = self.client.post_file("/upload", files, md5_hash=md5_hash)
            
            document_key = response.get('document_key')
            document_md5 = response.get('document_md5')
            
            print(f"✅ Upload realizado com sucesso!")
            print(f"Document Key: {document_key}")
            print(f"MD5: {document_md5}")
            
            return {
                'document_key': document_key,
                'document_md5': document_md5,
                'filename': filename,
                'file_type': file_type,
                'size': len(content)
            }
            
        except Exception as e:
            print(f"❌ Erro no upload: {e}")
            raise
    
    def _detect_file_type(self, filename: str) -> str:
        """Detecta tipo do arquivo pela extensão"""
        
        ext = filename.lower().split('.')[-1]
        
        type_map = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        
        return type_map.get(ext, 'application/octet-stream')
    
    def upload_rg_front(self, file_path: str) -> str:
        """Upload frente do RG"""
        result = self.upload_file(file_path, 'image/jpeg')
        return result['document_key']
    
    def upload_rg_back(self, file_path: str) -> str:
        """Upload verso do RG"""
        result = self.upload_file(file_path, 'image/jpeg')
        return result['document_key']
    
    def upload_cnh(self, file_path: str) -> str:
        """Upload CNH"""
        result = self.upload_file(file_path, 'image/jpeg')
        return result['document_key']
    
    def upload_proof_of_residence(self, file_path: str) -> str:
        """Upload comprovante de residência"""
        result = self.upload_file(file_path, 'application/pdf')
        return result['document_key']
    
    def get_document_url(self, document_key: str) -> Dict[str, Any]:
        """Consulta URL do documento (válida por 10 minutos)"""
        
        try:
            response = self.client.get(f"/document/{document_key}/url")
            
            document_url = response.get('document_url')
            signed_document_url = response.get('signed_document_url')
            expiration_datetime = response.get('expiration_datetime')
            
            print(f"✅ URL do documento obtida!")
            print(f"Document Key: {document_key}")
            print(f"Expira em: {expiration_datetime}")
            
            return {
                'document_key': document_key,
                'document_url': document_url,
                'signed_document_url': signed_document_url,
                'expiration_datetime': expiration_datetime
            }
            
        except Exception as e:
            print(f"❌ Erro ao consultar documento: {e}")
            raise
    
    def download_document(self, document_key: str) -> bytes:
        """Baixa conteúdo do documento"""
        
        import requests
        
        try:
            # Obter URL do documento
            doc_info = self.get_document_url(document_key)
            document_url = doc_info['document_url']
            
            # Baixar documento
            response = requests.get(document_url)
            response.raise_for_status()
            
            print(f"✅ Documento baixado: {len(response.content)} bytes")
            
            return response.content
            
        except Exception as e:
            print(f"❌ Erro ao baixar documento: {e}")
            raise

    def upload_company_statute(self, file_path: str) -> str:
        """Upload estatuto da empresa"""
        result = self.upload_file(file_path, 'application/pdf')
        return result['document_key']
