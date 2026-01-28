import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Simple Markdown-to-PDF converter: strips basic markdown and writes text to PDF.
# Usage: python tools/generate_integration_pdf.py INTEGRATION_RISK_SOLUTION.md output.pdf

import os


def text_from_markdown(md_text: str) -> str:
    # Very small sanitizer: remove markdown headers and code fences
    lines = []
    in_code = False
    for raw in md_text.splitlines():
        if raw.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            lines.append(raw)
            continue
        # remove leading markdown bullets and hashes
        l = raw.lstrip('#').lstrip('-').lstrip(' ')
        lines.append(l)
    return '\n'.join(lines)


def generate_pdf(input_md: str, output_pdf: str):
    with open(input_md, 'r', encoding='utf-8') as f:
        md = f.read()
    text = text_from_markdown(md)

    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin
    line_height = 12

    for paragraph in text.split('\n'):
        if y < margin:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, paragraph[:120])
        y -= line_height
    c.save()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python tools/generate_integration_pdf.py INTEGRATION_RISK_SOLUTION.md output.pdf')
        sys.exit(1)
    input_md = sys.argv[1]
    output_pdf = sys.argv[2]
    if not os.path.exists(input_md):
        print('Input file not found:', input_md)
        sys.exit(2)
    generate_pdf(input_md, output_pdf)
    print('PDF generated:', output_pdf)
