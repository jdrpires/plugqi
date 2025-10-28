#!/usr/bin/env python3
"""
Teste da funcionalidade de upload de documentos
"""

import os
import sys
from PIL import Image
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plugqi import PlugQi

def create_test_image():
    """Cria uma imagem de teste"""
    
    # Criar imagem simples 100x100 pixels
    img = Image.new('RGB', (100, 100), color='red')
    
    # Salvar em bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def create_test_pdf():
    """Cria um PDF de teste simples"""
    
    # PDF mínimo válido
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
229
%%EOF"""
    
    return pdf_content

def test_upload_image():
    """Testa upload de imagem"""
    
    plugqi = PlugQi()
    
    try:
        print("🧪 Testando upload de imagem...")
        
        # Criar imagem de teste
        image_content = create_test_image()
        
        # Fazer upload
        result = plugqi.document_upload.upload_content(
            content=image_content,
            filename="test_image.jpg",
            file_type="image/jpeg"
        )
        
        print(f"✅ Upload de imagem realizado!")
        print(f"Document Key: {result['document_key']}")
        print(f"MD5: {result['document_md5']}")
        print(f"Tamanho: {result['size']} bytes")
        
        return result['document_key']
        
    except Exception as e:
        print(f"❌ Erro no upload de imagem: {e}")
        return None

def test_upload_pdf():
    """Testa upload de PDF"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🧪 Testando upload de PDF...")
        
        # Criar PDF de teste
        pdf_content = create_test_pdf()
        
        # Fazer upload
        result = plugqi.document_upload.upload_content(
            content=pdf_content,
            filename="test_document.pdf",
            file_type="application/pdf"
        )
        
        print(f"✅ Upload de PDF realizado!")
        print(f"Document Key: {result['document_key']}")
        print(f"MD5: {result['document_md5']}")
        print(f"Tamanho: {result['size']} bytes")
        
        return result['document_key']
        
    except Exception as e:
        print(f"❌ Erro no upload de PDF: {e}")
        return None

def test_upload_helpers():
    """Testa métodos helper específicos"""
    
    plugqi = PlugQi()
    
    try:
        print("\n🧪 Testando helpers de upload...")
        
        # Criar arquivo temporário
        temp_file = "temp_test_image.jpg"
        
        with open(temp_file, 'wb') as f:
            f.write(create_test_image())
        
        # Testar upload de RG
        rg_key = plugqi.document_upload.upload_rg_front(temp_file)
        print(f"✅ RG Front uploaded: {rg_key}")
        
        # Limpar arquivo temporário
        os.remove(temp_file)
        
        return rg_key
        
    except Exception as e:
        print(f"❌ Erro nos helpers: {e}")
        if os.path.exists("temp_test_image.jpg"):
            os.remove("temp_test_image.jpg")
        return None

if __name__ == "__main__":
    print("📤 TESTE UPLOAD DE DOCUMENTOS")
    print("=" * 50)
    
    # Verificar conectividade
    plugqi = PlugQi()
    if not plugqi.health_check():
        print("❌ Falha na conectividade com QiTech")
        exit(1)
    
    print("✅ Conectividade OK")
    
    # Executar testes
    image_key = test_upload_image()
    pdf_key = test_upload_pdf()
    helper_key = test_upload_helpers()
    
    print(f"\n📊 RESULTADOS:")
    print(f"Upload imagem: {'✅' if image_key else '❌'}")
    print(f"Upload PDF: {'✅' if pdf_key else '❌'}")
    print(f"Helper methods: {'✅' if helper_key else '❌'}")
    
    if image_key or pdf_key or helper_key:
        print(f"\n🎉 UPLOAD DE DOCUMENTOS FUNCIONANDO!")
        
        if image_key:
            print(f"Imagem Document Key: {image_key}")
        if pdf_key:
            print(f"PDF Document Key: {pdf_key}")
        if helper_key:
            print(f"Helper Document Key: {helper_key}")
    else:
        print(f"\n❌ Problemas no upload de documentos")
