import fitz
import sys

pdf_path = r'D:\Workspace\competitions\Hex\第一届AI全栈黑客松赛题.pdf'
output_path = r'D:\Workspace\competitions\Hex\competition_requirements.txt'

doc = fitz.open(pdf_path)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f'Total pages: {len(doc)}\n')
    f.write('='*80 + '\n')

    for i in range(len(doc)):
        f.write(f'\n=== Page {i+1} ===\n\n')
        f.write(doc[i].get_text())

print(f'Extracted {len(doc)} pages to {output_path}')
