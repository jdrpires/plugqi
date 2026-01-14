#!/usr/bin/env python3
"""
Gerador PDF Final para Cliente
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.colors import HexColor

def generate_client_pdf():
    """Gera PDF único para envio ao cliente"""
    
    # Ler documentação real
    with open('DOC_INTEGRACAO/INTEGRACAO_REAL.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar PDF
    pdf_path = 'DOC_INTEGRACAO/PlugQi_Integracao_Cliente.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ClientTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#2c3e50'),
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'ClientHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    code_style = ParagraphStyle(
        'ClientCode',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        backgroundColor=HexColor('#f8f9fa'),
        leftIndent=10,
        rightIndent=10,
        spaceBefore=8,
        spaceAfter=8
    )
    
    # Processar conteúdo
    story = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        if line.startswith('# '):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], heading_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], heading_style))
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                story.append(Preformatted('\n'.join(code_lines), code_style))
        elif line and not line.startswith('#'):
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line.strip():
                story.append(Paragraph(clean_line, styles['Normal']))
                story.append(Spacer(1, 4))
        
        i += 1
    
    # Adicionar instruções Postman
    story.append(Paragraph("Instrucoes Postman", heading_style))
    story.append(Paragraph("1. Importar PlugQi_Collection_Real.json", styles['Normal']))
    story.append(Paragraph("2. Importar PlugQi_Environment.json", styles['Normal']))
    story.append(Paragraph("3. Configurar tokens no Environment", styles['Normal']))
    story.append(Paragraph("4. Testar as 7 funcionalidades validadas", styles['Normal']))
    
    doc.build(story)
    print(f"PDF cliente gerado: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_client_pdf()