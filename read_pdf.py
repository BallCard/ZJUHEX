import sys
try:
    import PyPDF2
except ImportError:
    print("ERROR: PyPDF2 not installed")
    sys.exit(1)

pdf_path = "第一届AI全栈黑客松赛题.pdf"
output_path = "赛题内容.txt"

try:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Try to decrypt with empty password
        if reader.is_encrypted:
            reader.decrypt('')

        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(f"Total pages: {len(reader.pages)}\n\n")
            out.write("="*80 + "\n")

            for i, page in enumerate(reader.pages, 1):
                out.write(f"\n--- Page {i} ---\n\n")
                text = page.extract_text()
                out.write(text)
                out.write("\n\n" + "="*80 + "\n")

        print(f"Successfully extracted {len(reader.pages)} pages to {output_path}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
