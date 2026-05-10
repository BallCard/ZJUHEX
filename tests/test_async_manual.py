"""
Manual test for async_extractor without pytest.

Tests:
1. Cache directory creation
2. Chunk extraction with caching
3. Batch extraction
4. Progress tracking
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from services.async_extractor import AsyncExtractor
from utils.paths import RUNTIME_DIR


def cleanup(job_id):
    """Clean up test data."""
    cache_dir = RUNTIME_DIR / job_id / "extraction_cache"
    if cache_dir.exists():
        for file in cache_dir.glob("*.json"):
            file.unlink()
        cache_dir.rmdir()

    job_dir = RUNTIME_DIR / job_id
    if job_dir.exists():
        state_file = job_dir / "state.json"
        if state_file.exists():
            state_file.unlink()
        job_dir.rmdir()


def test_cache_directory():
    """Test 1: Cache directory creation."""
    print("\n[Test 1] Cache directory creation...")
    job_id = "test_001"
    cleanup(job_id)

    extractor = AsyncExtractor(job_id)
    cache_dir = RUNTIME_DIR / job_id / "extraction_cache"

    assert cache_dir.exists(), "Cache directory not created"
    assert cache_dir.is_dir(), "Cache path is not a directory"
    print("✓ Cache directory created successfully")

    cleanup(job_id)


def test_chunk_extraction_with_cache():
    """Test 2: Chunk extraction with caching."""
    print("\n[Test 2] Chunk extraction with caching...")
    job_id = "test_002"
    cleanup(job_id)

    extractor = AsyncExtractor(job_id)

    chunk = {
        "chunk_id": "chunk_0",
        "content": "细胞膜是由磷脂双层构成的生物膜。",
        "page": 1,
        "char_count": 20
    }

    # Mock LLM extraction
    mock_extraction = {
        "concepts": [
            {"name": "细胞膜", "type": "concept", "definition": "生物膜结构"}
        ],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction) as mock_llm:
        # First call - should hit LLM
        result1 = extractor.extract_chunk(chunk)
        assert result1 is not None, "First extraction failed"
        assert result1["cached"] is False, "First call should not be cached"
        assert mock_llm.call_count == 1, "LLM should be called once"
        print(f"✓ First extraction: {result1['chunk_id']}, cached={result1['cached']}")

        # Second call - should hit cache
        result2 = extractor.extract_chunk(chunk)
        assert result2 is not None, "Second extraction failed"
        assert result2["cached"] is True, "Second call should be cached"
        assert mock_llm.call_count == 1, "LLM should not be called again"
        print(f"✓ Second extraction: {result2['chunk_id']}, cached={result2['cached']}")

    # Verify cache file exists
    cache_file = RUNTIME_DIR / job_id / "extraction_cache" / "chunk_0.json"
    assert cache_file.exists(), "Cache file not created"
    print(f"✓ Cache file created: {cache_file}")

    cleanup(job_id)


def test_batch_extraction():
    """Test 3: Batch extraction."""
    print("\n[Test 3] Batch extraction...")
    job_id = "test_003"
    cleanup(job_id)

    extractor = AsyncExtractor(job_id)

    chunks = [
        {"chunk_id": "chunk_0", "content": "细胞膜是由磷脂双层构成。", "page": 1, "char_count": 15},
        {"chunk_id": "chunk_1", "content": "线粒体是细胞的能量工厂。", "page": 1, "char_count": 15},
        {"chunk_id": "chunk_2", "content": "核糖体是蛋白质合成场所。", "page": 2, "char_count": 15}
    ]

    mock_extraction = {
        "concepts": [{"name": "测试概念", "type": "concept", "definition": "定义"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        results = extractor.extract_batch(chunks)

    assert results["total"] == 3, f"Expected 3 total, got {results['total']}"
    assert results["success_count"] == 3, f"Expected 3 success, got {results['success_count']}"
    assert results["failed_count"] == 0, f"Expected 0 failed, got {results['failed_count']}"
    assert len(results["results"]) == 3, f"Expected 3 results, got {len(results['results'])}"

    print(f"✓ Batch extraction: {results['success_count']}/{results['total']} successful")

    cleanup(job_id)


def test_progress_tracking():
    """Test 4: Progress tracking."""
    print("\n[Test 4] Progress tracking...")
    job_id = "test_004"
    cleanup(job_id)

    extractor = AsyncExtractor(job_id)

    chunks = [
        {"chunk_id": "chunk_0", "content": "测试内容1", "page": 1, "char_count": 10},
        {"chunk_id": "chunk_1", "content": "测试内容2", "page": 1, "char_count": 10}
    ]

    mock_extraction = {
        "concepts": [{"name": "概念", "type": "concept", "definition": "定义"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        extractor.extract_batch(chunks)

    # Check state file
    state_path = RUNTIME_DIR / job_id / "state.json"
    assert state_path.exists(), "State file not created"

    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    assert state["extraction_progress"] == 2, f"Expected progress 2, got {state['extraction_progress']}"
    assert state["extraction_total"] == 2, f"Expected total 2, got {state['extraction_total']}"

    print(f"✓ Progress tracking: {state['extraction_progress']}/{state['extraction_total']}")

    cleanup(job_id)


def test_error_caching():
    """Test 5: Error caching to avoid retries."""
    print("\n[Test 5] Error caching...")
    job_id = "test_005"
    cleanup(job_id)

    extractor = AsyncExtractor(job_id)

    chunk = {
        "chunk_id": "chunk_error",
        "content": "测试错误处理",
        "page": 1,
        "char_count": 10
    }

    with patch.object(extractor.builder, '_extract_knowledge', side_effect=Exception("LLM timeout")) as mock_llm:
        # First call - should fail and cache error
        result1 = extractor.extract_chunk(chunk)
        assert result1 is None, "First call should return None on error"
        assert mock_llm.call_count == 1, "LLM should be called once"
        print("✓ First call failed as expected")

        # Second call - should return cached error (no LLM retry)
        result2 = extractor.extract_chunk(chunk)
        assert result2 is not None, "Second call should return cached error"
        assert result2["status"] == "failed", "Status should be 'failed'"
        assert result2["cached"] is True, "Error should be cached"
        assert mock_llm.call_count == 1, "LLM should not be called again"
        print("✓ Second call returned cached error (no retry)")

    cleanup(job_id)


if __name__ == "__main__":
    print("=" * 60)
    print("Manual Test Suite for AsyncExtractor")
    print("=" * 60)

    try:
        test_cache_directory()
        test_chunk_extraction_with_cache()
        test_batch_extraction()
        test_progress_tracking()
        test_error_caching()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
