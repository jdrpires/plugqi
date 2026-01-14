#!/usr/bin/env python3
"""
Gerador de PDF - Documentação Técnica PlugQi
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle
from reportlab.lib.colors import HexColor, black, white
import re

def generate_tech_pdf():
    """Gera PDF da documentação técnica"""
    
    # Ler arquivo markdown
    with open('INTEGRACAO_TECNICA_COMPLETA.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Criar PDF
    pdf_path = 'INTEGRACAO_TECNICA_COMPLETA.pdf'
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=A4, 
        topMargin=0.8*inch, 
        bottomMargin=0.8*inch,
        leftMargin=0.8*inch,
        rightMargin=0.8*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos customizados para documentação técnica
    title_style = ParagraphStyle(
        'TechTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=24,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'TechHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2c3e50'),
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'TechHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    heading4_style = ParagraphStyle(
        'TechHeading4',
        parent=styles['Heading4'],
        fontSize=12,
        textColor=HexColor('#2c3e50'),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    code_style = ParagraphStyle(
        'TechCode',
        parent=styles['Code'],
        fontSize=8,
        fontName='Courier',
        backgroundColor=HexColor('#f8f9fa'),
        borderColor=HexColor('#dee2e6'),
        borderWidth=1,
        leftIndent=12,
        rightIndent=12,
        spaceBefore=8,
        spaceAfter=8,
        leading=10
    )
    
    normal_style = ParagraphStyle(
        'TechNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    # Lista para elementos do PDF
    story = []
    
    # Processar conteúdo
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
            
        # Título principal
        if line.startswith('# '):
            title = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\{\}\/\\\"\'\`]', '', line[2:])
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
        # Subtítulos nível 2
        elif line.startswith('## '):
            subtitle = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\{\}\/\\\"\'\`]', '', line[3:])
            story.append(Paragraph(subtitle, heading2_style))
            
        # Subtítulos nível 3
        elif line.startswith('### '):
            subsubtitle = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\{\}\/\\\"\'\`]', '', line[4:])
            story.append(Paragraph(subsubtitle, heading3_style))
            
        # Subtítulos nível 4
        elif line.startswith('#### '):
            subsubsubtitle = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\{\}\/\\\"\'\`]', '', line[5:])
            story.append(Paragraph(subsubsubtitle, heading4_style))
            
        # Blocos de código
        elif line.startswith('```'):
            # Encontrar fim do bloco
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            if code_lines:
                code_text = '\n'.join(code_lines)
                # Limitar largura das linhas de código
                formatted_code = []
                for code_line in code_lines:
                    if len(code_line) > 80:
                        # Quebrar linhas longas
                        while len(code_line) > 80:
                            formatted_code.append(code_line[:80])
                            code_line = '    ' + code_line[80:]
                        if code_line.strip():
                            formatted_code.append(code_line)
                    else:
                        formatted_code.append(code_line)
                
                story.append(Preformatted('\n'.join(formatted_code), code_style))
                story.append(Spacer(1, 6))
        
        # Tabelas simples
        elif '|' in line and line.count('|') >= 2:
            table_lines = [line]
            i += 1
            # Coletar linhas da tabela
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i].strip())
                i += 1
            i -= 1  # Voltar uma linha
            
            if len(table_lines) > 1:
                # Processar tabela
                table_data = []
                for table_line in table_lines:
                    if not table_line.startswith('|--'):  # Ignorar separadores
                        cells = [cell.strip() for cell in table_line.split('|')[1:-1]]
                        if cells:
                            table_data.append(cells)
                
                if table_data:
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f8f9fa')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), white),
                        ('GRID', (0, 0), (-1, -1), 1, black)
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 12))
        
        # Texto normal
        elif line and not line.startswith('#'):
            # Limpar emojis e caracteres especiais
            clean_line = re.sub(r'[^\w\s\-\.\,\:\;\(\)\[\]\{\}\/\\\"\'\`\@\#\$\%\^\&\*\+\=\|\<\>\?\!]', '', line)
            if clean_line.strip():
                story.append(Paragraph(clean_line, normal_style))
        
        i += 1
    
    # Gerar PDF
    doc.build(story)
    print(f"PDF tecnico gerado: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    try:
        pdf_file = generate_tech_pdf()
        print(f"Documentacao tecnica PDF: {pdf_file}")
    except Exception as e:
        print(f"Erro: {e}")