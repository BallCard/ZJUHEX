"""
Manual test for content_detector without pytest dependency.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.services.content_detector import ContentDetector


def test_detect_content_start_by_page_number():
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

    assert start_idx == 3, f"Expected 3, got {start_idx}"
    assert chunks[start_idx]["page"] == 10
    print("[PASS] test_detect_content_start_by_page_number")


def test_detect_content_start_by_chapter_marker():
    """Test detection by chapter markers."""
    chunks = [
        {"chunk_id": "chunk_0", "page": 8, "content": "目录内容", "char_count": 50},
        {"chunk_id": "chunk_1", "page": 9, "content": "第一章 绪论", "char_count": 6},
        {"chunk_id": "chunk_2", "page": 10, "content": "生理学是研究...", "char_count": 100},
    ]

    detector = ContentDetector()
    start_idx = detector.detect_content_start(chunks)

    assert start_idx == 1, f"Expected 1, got {start_idx}"
    print("[PASS] test_detect_content_start_by_chapter_marker")


def test_select_chapter_basic():
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

    assert len(chapter_chunks) == 3, f"Expected 3 chunks, got {len(chapter_chunks)}"
    assert chapter_chunks[0]["chunk_id"] == "chunk_0"
    assert chapter_chunks[-1]["chunk_id"] == "chunk_2"
    print("[PASS] test_select_chapter_basic")


def test_select_chapter_with_metadata():
    """Test chapter selection returns metadata."""
    chunks = [
        {"chunk_id": "chunk_0", "page": 10, "content": "第一章 绪论", "char_count": 6},
        {"chunk_id": "chunk_1", "page": 11, "content": "生理学是研究...", "char_count": 100},
        {"chunk_id": "chunk_2", "page": 12, "content": "第二章 细胞", "char_count": 5},
    ]

    detector = ContentDetector()
    chapter_chunks = detector.select_chapter(chunks, chapter_num=1)

    assert chapter_chunks[0].get("chapter_title") == "第一章 绪论"
    assert chapter_chunks[0]["page"] == 10
    assert chapter_chunks[-1]["page"] == 11
    print("[PASS] test_select_chapter_with_metadata")


def test_chapter_marker_patterns():
    """Test various chapter marker patterns."""
    test_cases = [
        ("第一章 绪论", True),
        ("第1章 绪论", True),
        ("第一章", True),
        ("Chapter 1", True),
        ("Chapter 1: Introduction", True),
        ("1. 绪论", False),
        ("一、绪论", False),
    ]

    detector = ContentDetector()
    for content, expected in test_cases:
        result = detector._is_chapter_marker(content)
        assert result == expected, f"Failed for: {content}, expected {expected}, got {result}"

    print("[PASS] test_chapter_marker_patterns")


def test_get_chapter_metadata():
    """Test extracting chapter metadata."""
    chunks = [
        {"chunk_id": "chunk_0", "page": 10, "content": "第一章 绪论", "char_count": 100, "chapter_title": "第一章 绪论"},
        {"chunk_id": "chunk_1", "page": 11, "content": "生理学是研究...", "char_count": 200, "chapter_title": "第一章 绪论"},
        {"chunk_id": "chunk_2", "page": 12, "content": "生理学的发展...", "char_count": 150, "chapter_title": "第一章 绪论"},
    ]

    detector = ContentDetector()
    metadata = detector.get_chapter_metadata(chunks)

    assert metadata["chapter_title"] == "第一章 绪论"
    assert metadata["start_page"] == 10
    assert metadata["end_page"] == 12
    assert metadata["chunk_count"] == 3
    assert metadata["char_count"] == 450
    print("[PASS] test_get_chapter_metadata")


if __name__ == "__main__":
    print("Running manual tests for ContentDetector...\n")

    try:
        test_detect_content_start_by_page_number()
        test_detect_content_start_by_chapter_marker()
        test_select_chapter_basic()
        test_select_chapter_with_metadata()
        test_chapter_marker_patterns()
        test_get_chapter_metadata()

        print("\n[SUCCESS] All tests passed!")
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
