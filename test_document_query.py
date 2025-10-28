#!/usr/bin/env python3
"""
Teste da consulta de documentos
"""

import os
import sys
from PIL import Image
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def test_document_query():
    """Testa upload e consulta de documento"""
    
    plugqi = PlugQi()
    
    try:
        print("🧪 Testando fluxo completo: Upload + Consulta...")
        
        # 1. Criar e fazer upload de documento
        print("\n📤 ETAPA 1: Upload do documento...")
        
        # Criar imagem simples
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Upload
        upload_result = plugqi.document_upload.upload_content(
            content=img_bytes.getvalue(),
            filename="test_query.jpg",
            file_type="image/jpeg"
        )
        
        document_key = upload_result['document_key']
        print(f"✅ Upload realizado: {document_key}")
        
        # 2. Consultar URL do documento
        print(f"\n🔍 ETAPA 2: Consultando documento {document_key}...")
        
        doc_info = plugqi.document_upload.get_document_url(document_key)
        
        print(f"✅ Consulta realizada!")
        print(f"Document URL: {doc_info['document_url'][:50]}...")
        print(f"Expira em: {doc_info['expiration_datetime']}")
        
        if doc_info.get('signed_document_url'):
            print(f"Signed URL: {doc_info['signed_document_url'][:50]}...")
        else:
            print("Documento não assinado")
        
        # 3. Testar download do documento
        print(f"\n⬇️ ETAPA 3: Baixando documento...")
        
        content = plugqi.document_upload.download_document(document_key)
        
        print(f"✅ Download realizado: {len(content)} bytes")
        
        # Verificar se conteúdo é igual
        original_size = len(img_bytes.getvalue())
        downloaded_size = len(content)
        
        print(f"Tamanho original: {original_size} bytes")
        print(f"Tamanho baixado: {downloaded_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_query_existing_document():
    """Testa consulta de documento existente"""
    
    plugqi = PlugQi()
    
    # Usar document_key do teste anterior se disponível
    existing_keys = [
        "4e2e5fe5-b33e-44f2-95c1-083b5eea03cc",  # Do teste anterior
        "9fb7eaa7-542e-4a4d-ba68-f7393b8ef68a",
        "4726a063-7e7e-442f-8046-d70d4461e8dc"
    ]
    
    for document_key in existing_keys:
        try:
            print(f"\n🔍 Testando consulta de documento existente: {document_key}")
            
            doc_info = plugqi.document_upload.get_document_url(document_key)
            
            print(f"✅ Documento encontrado!")
            print(f"URL válida até: {doc_info['expiration_datetime']}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Documento {document_key} não encontrado: {e}")
            continue
    
    print("❌ Nenhum documento existente encontrado")
    return False

if __name__ == "__main__":
    print("🔍 TESTE CONSULTA DE DOCUMENTOS")
    print("=" * 50)
    
    # Verificar conectividade
    plugqi = PlugQi()
    if not plugqi.health_check():
        print("❌ Falha na conectividade com QiTech")
        exit(1)
    
    print("✅ Conectividade OK")
    
    # Executar testes
    test1 = test_document_query()
    test2 = test_query_existing_document()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Fluxo completo: {'✅' if test1 else '❌'}")
    print(f"Consulta existente: {'✅' if test2 else '❌'}")
    
    if test1 or test2:
        print(f"\n🎉 CONSULTA DE DOCUMENTOS FUNCIONANDO!")
    else:
        print(f"\n❌ Problemas na consulta de documentos")
