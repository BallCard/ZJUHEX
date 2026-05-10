"""
Tests for content_detector module.

Test cases:
1. Detect content start (skip cover/preface/TOC)
2. Select complete chapter
3. Handle edge cases (no chapter markers, multiple markers)
"""

import pytest
from src.backend.services.content_detector import ContentDetector


class TestContentDetector:
    """Test ContentDetector class."""

    def test_detect_content_start_by_page_number(self):
        """Test detection by skipping pages < 10."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 1, "content": "封面", "char_count": 2},
            {"chunk_id": "chunk_1", "page": 2, "content": "版权页", "char_count": 3},
            {"chunk_id": "chunk_2", "page": 5, "content": "目录", "char_count": 2},
            {"chunk_id": "chunk_3", "page": 10, "content": "第一章 绪论", "char_count": 6},
            {"chunk_id": "chunk_4", "page": 11, "content": "生理学是研究...", "char_count": 100},
        ]

        detector = ContentDetector()
        start_idx = detector.detect_content_start(chunks)

        # Should skip to page 10
        assert start_idx == 3
        assert chunks[start_idx]["page"] == 10

    def test_detect_content_start_by_chapter_marker(self):
        """Test detection by chapter markers."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 8, "content": "目录内容", "char_count": 50},
            {"chunk_id": "chunk_1", "page": 9, "content": "第一章 绪论", "char_count": 6},
            {"chunk_id": "chunk_2", "page": 10, "content": "生理学是研究...", "char_count": 100},
        ]

        detector = ContentDetector()
        start_idx = detector.detect_content_start(chunks)

        # Should detect "第一章"
        assert start_idx == 1

    def test_detect_content_start_by_char_count_jump(self):
        """Test detection by character count jump (TOC -> content)."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 8, "content": "目录项1", "char_count": 10},
            {"chunk_id": "chunk_1", "page": 9, "content": "目录项2", "char_count": 12},
            {"chunk_id": "chunk_2", "page": 10, "content": "这是一段很长的正文内容，包含了大量的文字描述和详细的解释说明，字数远超目录项。" * 10, "char_count": 500},
        ]

        detector = ContentDetector()
        start_idx = detector.detect_content_start(chunks)

        # Should detect char count jump
        assert start_idx == 2

    def test_select_chapter_basic(self):
        """Test selecting a complete chapter."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 10, "content": "第一章 绪论", "char_count": 6},
            {"chunk_id": "chunk_1", "page": 11, "content": "生理学是研究...", "char_count": 100},
            {"chunk_id": "chunk_2", "page": 12, "content": "生理学的发展...", "char_count": 120},
            {"chunk_id": "chunk_3", "page": 13, "content": "第二章 细胞", "char_count": 5},
            {"chunk_id": "chunk_4", "page": 14, "content": "细胞是生命...", "char_count": 90},
        ]

        detector = ContentDetector()
        chapter_chunks = detector.select_chapter(chunks, chapter_num=1)

        # Should select chunks 0-2 (第一章)
        assert len(chapter_chunks) == 3
        assert chapter_chunks[0]["chunk_id"] == "chunk_0"
        assert chapter_chunks[-1]["chunk_id"] == "chunk_2"

    def test_select_chapter_with_metadata(self):
        """Test chapter selection returns metadata."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 10, "content": "第一章 绪论", "char_count": 6},
            {"chunk_id": "chunk_1", "page": 11, "content": "生理学是研究...", "char_count": 100},
            {"chunk_id": "chunk_2", "page": 12, "content": "第二章 细胞", "char_count": 5},
        ]

        detector = ContentDetector()
        chapter_chunks = detector.select_chapter(chunks, chapter_num=1)

        # Check metadata
        assert chapter_chunks[0].get("chapter_title") == "第一章 绪论"
        assert chapter_chunks[0]["page"] == 10
        assert chapter_chunks[-1]["page"] == 11

    def test_select_chapter_no_marker(self):
        """Test chapter selection when no chapter marker found."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 10, "content": "正文内容1", "char_count": 100},
            {"chunk_id": "chunk_1", "page": 11, "content": "正文内容2", "char_count": 120},
            {"chunk_id": "chunk_2", "page": 12, "content": "正文内容3", "char_count": 90},
        ]

        detector = ContentDetector()
        chapter_chunks = detector.select_chapter(chunks, chapter_num=1)

        # Should return all chunks with default title
        assert len(chapter_chunks) == 3
        assert chapter_chunks[0].get("chapter_title") == "第1章"

    def test_select_chapter_second_chapter(self):
        """Test selecting second chapter."""
        chunks = [
            {"chunk_id": "chunk_0", "page": 10, "content": "第一章 绪论", "char_count": 6},
            {"chunk_id": "chunk_1", "page": 11, "content": "生理学是研究...", "char_count": 100},
            {"chunk_id": "chunk_2", "page": 12, "content": "第二章 细胞", "char_count": 5},
            {"chunk_id": "chunk_3", "page": 13, "content": "细胞是生命...", "char_count": 90},
            {"chunk_id": "chunk_4", "page": 14, "content": "第三章 组织", "char_count": 5},
        ]

        detector = ContentDetector()
        chapter_chunks = detector.select_chapter(chunks, chapter_num=2)

        # Should select chunks 2-3 (第二章)
        assert len(chapter_chunks) == 2
        assert chapter_chunks[0]["chunk_id"] == "chunk_2"
        assert chapter_chunks[-1]["chunk_id"] == "chunk_3"
        assert chapter_chunks[0].get("chapter_title") == "第二章 细胞"

    def test_chapter_marker_patterns(self):
        """Test various chapter marker patterns."""
        test_cases = [
            ("第一章 绪论", True),
            ("第1章 绪论", True),
            ("第一章", True),
            ("Chapter 1", True),
            ("Chapter 1: Introduction", True),
            ("1. 绪论", False),  # Not a chapter marker
            ("一、绪论", False),  # Not a chapter marker
        ]

        detector = ContentDetector()
        for content, expected in test_cases:
            result = detector._is_chapter_marker(content)
            assert result == expected, f"Failed for: {content}"

    def test_extract_chapter_title(self):
        """Test extracting chapter title from content."""
        test_cases = [
            ("第一章 绪论", "第一章 绪论"),
            ("第1章 细胞的基本功能", "第1章 细胞的基本功能"),
            ("Chapter 1: Introduction", "Chapter 1: Introduction"),
            ("第二章\n细胞", "第二章"),  # Only first line
        ]

        detector = ContentDetector()
        for content, expected in test_cases:
            result = detector._extract_chapter_title(content)
            assert result == expected, f"Failed for: {content}"
