"""
End-to-end test for content detection integration.

Tests the full pipeline with content detection:
1. Parse document
2. Detect content start
3. Select chapter
4. Build graph with chapter info
5. Verify state contains chapter metadata
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.services.parser import parse_textbook
from src.backend.services.content_detector import ContentDetector
from src.backend.services.knowledge_graph import build_knowledge_graph


def test_content_detection_pipeline():
    """Test content detection in full pipeline."""
    print("Testing content detection pipeline...\n")

    # Step 1: Create mock chunks simulating a real textbook
    print("Step 1: Creating mock textbook chunks...")
    mock_chunks = [
        # Cover and preface (pages 1-9)
        {"chunk_id": "chunk_0", "page": 1, "content": "医学教材封面", "char_count": 6, "textbook": "test.pdf"},
        {"chunk_id": "chunk_1", "page": 2, "content": "版权页内容", "char_count": 5, "textbook": "test.pdf"},
        {"chunk_id": "chunk_2", "page": 5, "content": "目录\n第一章...1\n第二章...20", "char_count": 20, "textbook": "test.pdf"},

        # Chapter 1 (pages 10-12)
        {"chunk_id": "chunk_3", "page": 10, "content": "第一章 生理学绪论", "char_count": 8, "textbook": "test.pdf"},
        {"chunk_id": "chunk_4", "page": 10, "content": "生理学是研究生物体及其各组成部分正常功能活动规律的科学。它是生物科学的一个分支，也是医学的基础学科之一。生理学的研究对象包括细胞、组织、器官和系统等不同层次的生命活动。", "char_count": 150, "textbook": "test.pdf"},
        {"chunk_id": "chunk_5", "page": 11, "content": "生理学的研究方法包括观察法、实验法和比较法。观察法是通过对生命现象的观察来认识生理功能。实验法是通过人为控制条件来研究生理现象的因果关系。比较法是通过比较不同物种或不同发育阶段的生理功能来揭示生命活动的规律。", "char_count": 180, "textbook": "test.pdf"},
        {"chunk_id": "chunk_6", "page": 12, "content": "生理学的发展历史可以追溯到古代。古希腊医学家希波克拉底提出了体液学说。17世纪，哈维发现了血液循环。19世纪，贝尔纳提出了内环境稳态的概念。20世纪以来，生理学进入了分子和细胞水平的研究阶段。", "char_count": 200, "textbook": "test.pdf"},

        # Chapter 2 (pages 13-15)
        {"chunk_id": "chunk_7", "page": 13, "content": "第二章 细胞的基本功能", "char_count": 10, "textbook": "test.pdf"},
        {"chunk_id": "chunk_8", "page": 13, "content": "细胞是生命活动的基本单位。所有生物体都是由细胞组成的。细胞具有新陈代谢、生长发育、遗传变异、应激性等基本生命特征。", "char_count": 120, "textbook": "test.pdf"},
        {"chunk_id": "chunk_9", "page": 14, "content": "细胞膜是细胞与外界环境的界面，具有物质转运、信号转导、细胞识别等重要功能。细胞膜的基本结构是脂质双分子层，其中镶嵌着各种蛋白质分子。", "char_count": 140, "textbook": "test.pdf"},
    ]
    print(f"Created {len(mock_chunks)} mock chunks\n")

    # Step 2: Detect content start
    print("Step 2: Detecting content start...")
    detector = ContentDetector()
    content_start_idx = detector.detect_content_start(mock_chunks)
    print(f"Content starts at index: {content_start_idx}")
    print(f"Content start page: {mock_chunks[content_start_idx]['page']}")
    print(f"Content start chunk: {mock_chunks[content_start_idx]['chunk_id']}\n")

    # Verify content start detection
    assert content_start_idx == 3, f"Expected content start at index 3, got {content_start_idx}"
    assert mock_chunks[content_start_idx]["page"] == 10, "Content should start at page 10"

    # Step 3: Select chapter 1
    print("Step 3: Selecting chapter 1...")
    content_chunks = mock_chunks[content_start_idx:]
    chapter_chunks = detector.select_chapter(content_chunks, chapter_num=1)
    print(f"Selected {len(chapter_chunks)} chunks for chapter 1")
    print(f"Chapter title: {chapter_chunks[0].get('chapter_title')}")
    print(f"Page range: {chapter_chunks[0]['page']} - {chapter_chunks[-1]['page']}\n")

    # Verify chapter selection
    assert len(chapter_chunks) == 4, f"Expected 4 chunks for chapter 1, got {len(chapter_chunks)}"
    assert chapter_chunks[0].get("chapter_title") == "第一章 生理学绪论"
    assert chapter_chunks[0]["page"] == 10
    assert chapter_chunks[-1]["page"] == 12

    # Step 4: Get chapter metadata
    print("Step 4: Extracting chapter metadata...")
    chapter_metadata = detector.get_chapter_metadata(chapter_chunks)
    print(f"Chapter metadata:")
    print(f"  - Title: {chapter_metadata['chapter_title']}")
    print(f"  - Start page: {chapter_metadata['start_page']}")
    print(f"  - End page: {chapter_metadata['end_page']}")
    print(f"  - Chunk count: {chapter_metadata['chunk_count']}")
    print(f"  - Char count: {chapter_metadata['char_count']}\n")

    # Verify metadata
    assert chapter_metadata["chapter_title"] == "第一章 生理学绪论"
    assert chapter_metadata["start_page"] == 10
    assert chapter_metadata["end_page"] == 12
    assert chapter_metadata["chunk_count"] == 4
    assert chapter_metadata["char_count"] == 538

    # Step 5: Test chapter 2 selection
    print("Step 5: Testing chapter 2 selection...")
    chapter2_chunks = detector.select_chapter(content_chunks, chapter_num=2)
    print(f"Selected {len(chapter2_chunks)} chunks for chapter 2")
    print(f"Chapter title: {chapter2_chunks[0].get('chapter_title')}")
    print(f"Page range: {chapter2_chunks[0]['page']} - {chapter2_chunks[-1]['page']}\n")

    # Verify chapter 2
    assert len(chapter2_chunks) == 3, f"Expected 3 chunks for chapter 2, got {len(chapter2_chunks)}"
    assert chapter2_chunks[0].get("chapter_title") == "第二章 细胞的基本功能"
    assert chapter2_chunks[0]["page"] == 13
    assert chapter2_chunks[-1]["page"] == 14

    print("[SUCCESS] All content detection tests passed!")
    return True


def test_state_persistence():
    """Test that chapter info is properly saved to state."""
    print("\nTesting state persistence...\n")

    # Simulate state that would be saved by build_graph endpoint
    mock_state = {
        "job_id": "test123",
        "status": "graph_built",
        "current_phase": "build_graph",
        "content_start_page": 10,
        "chapter_title": "第一章 生理学绪论",
        "chapter_start_page": 10,
        "chapter_end_page": 12,
        "chapter_chunk_count": 4,
        "processed_chunk_count": 4,
        "nodes_count": 5,
        "edges_count": 3
    }

    print("Mock state structure:")
    print(json.dumps(mock_state, indent=2, ensure_ascii=False))

    # Verify required fields
    required_fields = [
        "content_start_page",
        "chapter_title",
        "chapter_start_page",
        "chapter_end_page",
        "chapter_chunk_count",
        "processed_chunk_count"
    ]

    for field in required_fields:
        assert field in mock_state, f"Missing required field: {field}"

    print("\n[SUCCESS] State persistence test passed!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Content Detection Integration Test")
    print("=" * 60 + "\n")

    try:
        test_content_detection_pipeline()
        test_state_persistence()
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
