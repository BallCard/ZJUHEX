"""Test parser with sample PDF or mock data."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.services.parser import DocumentParser


def test_parser_basic():
    """Test parser with basic functionality."""
    parser = DocumentParser(chunk_size_min=500, chunk_size_max=800)

    # Test text cleaning
    dirty_text = "这是一段   文本\n\n\n包含多余空格"
    clean = parser._clean_text(dirty_text)
    print(f"Clean text: {clean}")
    assert "  " not in clean

    # Test paragraph splitting
    text = "第一段内容。\n\n第二段内容。"
    paras = parser._split_paragraphs(text)
    print(f"Paragraphs: {paras}")
    assert len(paras) == 2

    print("[OK] Basic parser tests passed")


def test_parser_with_pdf():
    """Test parser with actual PDF if available."""
    pdf_path = Path("data/textbooks/03_生理学.pdf")

    if not pdf_path.exists():
        print(f"[WARN] PDF not found at {pdf_path}, skipping PDF test")
        print("  (This is expected if textbook not uploaded yet)")
        return

    parser = DocumentParser()
    chunks = parser.parse_pdf(str(pdf_path))

    print(f"\n[OK] Parsed {len(chunks)} chunks")
    print(f"  Total chars: {parser.get_total_chars(chunks)}")

    if chunks:
        print(f"\n  Sample chunk:")
        print(f"    ID: {chunks[0]['chunk_id']}")
        print(f"    Page: {chunks[0]['page']}")
        print(f"    Chars: {chunks[0]['char_count']}")
        print(f"    Content preview: {chunks[0]['content'][:100]}...")


if __name__ == "__main__":
    print("Testing parser service...\n")
    test_parser_basic()
    test_parser_with_pdf()
    print("\n[OK] All parser tests completed")
