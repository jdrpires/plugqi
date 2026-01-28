#!/usr/bin/env python3
"""
Gerador de PDF da Documentação de Integração PlugQi
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os

def generate_pdf():
    """Gera PDF da documentação de integração"""
    
    # Ler arquivo markdown
    with open('INTEGRACAO_FLUXO_COMPLETO.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Converter markdown para HTML
    html_content = markdown.markdown(
        markdown_content, 
        extensions=['codehilite', 'fenced_code', 'tables', 'toc']
    )
    
    # CSS para estilização
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "Documentação de Integração PlugQi";
            font-size: 10pt;
            color: #666;
        }
        @bottom-center {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 10pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #333;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        font-size: 24pt;
    }
    
    h2 {
        color: #34495e;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 5px;
        font-size: 18pt;
        margin-top: 30px;
    }
    
    h3 {
        color: #2c3e50;
        font-size: 14pt;
        margin-top: 20px;
    }
    
    h4 {
        color: #34495e;
        font-size: 12pt;
        margin-top: 15px;
    }
    
    code {
        background-color: #f8f9fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 15px;
        overflow-x: auto;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        line-height: 1.3;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
    }
    
    .codehilite {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 15px 0;
        padding-left: 15px;
        color: #555;
        font-style: italic;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    
    .emoji {
        font-size: 14pt;
    }
    
    ul, ol {
        margin: 10px 0;
        padding-left: 20px;
    }
    
    li {
        margin: 5px 0;
    }
    
    .page-break {
        page-break-before: always;
    }
    """
    
    # HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Documentação de Integração PlugQi</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Gerar PDF
    font_config = FontConfiguration()
    html_doc = HTML(string=full_html)
    css_doc = CSS(string=css_content, font_config=font_config)
    
    pdf_path = 'INTEGRACAO_FLUXO_COMPLETO.pdf'
    html_doc.write_pdf(pdf_path, stylesheets=[css_doc], font_config=font_config)
    
    print(f"✅ PDF gerado: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    try:
        pdf_file = generate_pdf()
        print(f"📄 Documentação PDF disponível em: {os.path.abspath(pdf_file)}")
    except ImportError as e:
        print("❌ Dependências não encontradas. Instale com:")
        print("pip install markdown weasyprint")
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")