"""
Document parsing service using PyMuPDF (fitz).

P0 Scope:
- Parse single PDF textbook (03_生理学.pdf)
- Extract text with page numbers
- Simple paragraph-based chunking (500-800 chars)
- Return structured chunks for downstream processing
"""

import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path
import re


class DocumentParser:
    """Parse PDF documents and chunk text for processing."""

    def __init__(self, chunk_size_min: int = 500, chunk_size_max: int = 800):
        """
        Initialize parser with chunking parameters.

        Args:
            chunk_size_min: Minimum characters per chunk
            chunk_size_max: Maximum characters per chunk
        """
        self.chunk_size_min = chunk_size_min
        self.chunk_size_max = chunk_size_max

    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Parse PDF and extract text with metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of chunks with metadata:
            [
                {
                    "chunk_id": "chunk_0",
                    "textbook": "03_生理学.pdf",
                    "page": 1,
                    "content": "text content...",
                    "char_count": 650
                },
                ...
            ]
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        doc = fitz.open(str(pdf_path))
        textbook_name = pdf_path.name

        chunks = []
        chunk_id = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            # Clean text
            text = self._clean_text(text)

            # Split into paragraphs
            paragraphs = self._split_paragraphs(text)

            # Chunk paragraphs
            for para in paragraphs:
                if len(para.strip()) < 50:  # Skip very short paragraphs
                    continue

                # If paragraph is within chunk size, use as-is
                if self.chunk_size_min <= len(para) <= self.chunk_size_max:
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id}",
                        "textbook": textbook_name,
                        "page": page_num + 1,  # 1-indexed
                        "content": para.strip(),
                        "char_count": len(para.strip())
                    })
                    chunk_id += 1

                # If paragraph is too long, split by sentences
                elif len(para) > self.chunk_size_max:
                    sub_chunks = self._split_long_paragraph(para)
                    for sub_chunk in sub_chunks:
                        chunks.append({
                            "chunk_id": f"chunk_{chunk_id}",
                            "textbook": textbook_name,
                            "page": page_num + 1,
                            "content": sub_chunk.strip(),
                            "char_count": len(sub_chunk.strip())
                        })
                        chunk_id += 1

                # If paragraph is too short, accumulate until reaching min size
                # (simplified: just skip for P0)

        doc.close()
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers (simple pattern)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split by double newlines or sentence-ending punctuation followed by newline
        paragraphs = re.split(r'\n\n+|\n(?=[。！？])', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """Split long paragraph into chunks by sentences."""
        # Split by Chinese sentence endings
        sentences = re.split(r'([。！？])', paragraph)

        # Recombine sentences with their punctuation
        combined = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                combined.append(sentences[i] + sentences[i + 1])
            else:
                combined.append(sentences[i])

        # Group sentences into chunks
        chunks = []
        current_chunk = ""

        for sentence in combined:
            if len(current_chunk) + len(sentence) <= self.chunk_size_max:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def get_chunk_count(self, chunks: List[Dict[str, Any]]) -> int:
        """Get total number of chunks."""
        return len(chunks)

    def get_total_chars(self, chunks: List[Dict[str, Any]]) -> int:
        """Get total character count across all chunks."""
        return sum(chunk["char_count"] for chunk in chunks)


def parse_textbook(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Convenience function to parse a textbook PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        List of parsed chunks with metadata
    """
    parser = DocumentParser()
    return parser.parse_pdf(pdf_path)
