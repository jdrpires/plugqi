#!/usr/bin/env python3
"""
Gerador de PDF Simples da Documentação de Integração PlugQi
Usando reportlab para compatibilidade com Windows
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.colors import HexColor
import re

def generate_simple_pdf():
    """Gera PDF simples da documentação"""
    
    # Ler arquivo markdown
    with open('INTEGRACAO_FLUXO_COMPLETO.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar PDF
    pdf_path = 'INTEGRACAO_FLUXO_COMPLETO.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#2c3e50'),
        spaceAfter=20
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#34495e'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#2c3e50'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        backgroundColor=HexColor('#f8f9fa'),
        borderColor=HexColor('#e9ecef'),
        borderWidth=1,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=10,
        spaceAfter=10
    )
    
    # Lista para armazenar elementos do PDF
    story = []
    
    # Processar conteúdo linha por linha
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        # Título principal
        if line.startswith('# '):
            title = line[2:].replace('🔄', '').strip()
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
        # Subtítulos
        elif line.startswith('## '):
            subtitle = line[3:].replace('📋', '').replace('🚀', '').replace('🔧', '').replace('📊', '').replace('⚠️', '').replace('🧪', '').strip()
            story.append(Paragraph(subtitle, heading2_style))
            
        # Sub-subtítulos
        elif line.startswith('### '):
            subsubtitle = line[4:].strip()
            story.append(Paragraph(subsubtitle, heading3_style))
            
        # Blocos de código
        elif line.startswith('```'):
            # Encontrar fim do bloco de código
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            if code_lines:
                code_text = '\n'.join(code_lines)
                story.append(Preformatted(code_text, code_style))
                story.append(Spacer(1, 6))
        
        # Texto normal
        elif line and not line.startswith('#'):
            # Remover emojis para melhor compatibilidade
            clean_line = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\{\}\/\\\"\'\`\@\#\$\%\^\&\*\+\=\|\<\>\?\!]', '', line)
            if clean_line.strip():
                story.append(Paragraph(clean_line, styles['Normal']))
                story.append(Spacer(1, 6))
        
        i += 1
    
    # Gerar PDF
    doc.build(story)
    print(f"PDF gerado: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    try:
        pdf_file = generate_simple_pdf()
        print(f"Documentacao PDF disponivel em: {pdf_file}")
    except ImportError:
        print("Instale reportlab: pip install reportlab")
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")