"""
Tests for async_extractor service.

Validates:
- Per-chunk caching
- Cache hit/miss behavior
- Progress tracking
- Error handling and caching
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from services.async_extractor import AsyncExtractor
from utils.paths import RUNTIME_DIR


@pytest.fixture
def test_job_id():
    """Test job ID."""
    return "test_async_001"


@pytest.fixture
def test_chunks():
    """Sample chunks for testing."""
    return [
        {
            "chunk_id": "chunk_0",
            "content": "细胞膜是由磷脂双层构成的生物膜。",
            "page": 1,
            "char_count": 20
        },
        {
            "chunk_id": "chunk_1",
            "content": "线粒体是细胞的能量工厂，负责ATP合成。",
            "page": 1,
            "char_count": 25
        },
        {
            "chunk_id": "chunk_2",
            "content": "核糖体是蛋白质合成的场所。",
            "page": 2,
            "char_count": 15
        }
    ]


@pytest.fixture
def extractor(test_job_id):
    """Create AsyncExtractor instance."""
    return AsyncExtractor(test_job_id)


@pytest.fixture(autouse=True)
def cleanup(test_job_id):
    """Clean up test cache after each test."""
    yield
    # Clean up cache directory
    cache_dir = RUNTIME_DIR / test_job_id / "extraction_cache"
    if cache_dir.exists():
        for file in cache_dir.glob("*.json"):
            file.unlink()
        cache_dir.rmdir()

    # Clean up job directory
    job_dir = RUNTIME_DIR / test_job_id
    if job_dir.exists():
        state_file = job_dir / "state.json"
        if state_file.exists():
            state_file.unlink()
        job_dir.rmdir()


def test_cache_directory_creation(extractor, test_job_id):
    """Test that cache directory is created on init."""
    cache_dir = RUNTIME_DIR / test_job_id / "extraction_cache"
    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_extract_chunk_success(extractor, test_chunks):
    """Test successful chunk extraction."""
    chunk = test_chunks[0]

    # Mock LLM extraction
    mock_extraction = {
        "concepts": [
            {"name": "细胞膜", "type": "concept", "definition": "生物膜结构"}
        ],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        result = extractor.extract_chunk(chunk)

    assert result is not None
    assert result["chunk_id"] == "chunk_0"
    assert result["status"] == "success"
    assert len(result["concepts"]) == 1
    assert result["concepts"][0]["name"] == "细胞膜"
    assert result["cached"] is False
    assert "timestamp" in result


def test_extract_chunk_caching(extractor, test_chunks):
    """Test that extraction results are cached."""
    chunk = test_chunks[0]

    # Mock LLM extraction
    mock_extraction = {
        "concepts": [{"name": "细胞膜", "type": "concept", "definition": "生物膜"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction) as mock_llm:
        # First call - should hit LLM
        result1 = extractor.extract_chunk(chunk)
        assert result1["cached"] is False
        assert mock_llm.call_count == 1

        # Second call - should hit cache
        result2 = extractor.extract_chunk(chunk)
        assert result2["cached"] is True
        assert mock_llm.call_count == 1  # No additional LLM call

        # Results should be identical (except cached flag)
        assert result1["chunk_id"] == result2["chunk_id"]
        assert result1["concepts"] == result2["concepts"]


def test_extract_chunk_cache_file_exists(extractor, test_chunks, test_job_id):
    """Test that cache file is created."""
    chunk = test_chunks[0]

    mock_extraction = {
        "concepts": [{"name": "细胞膜", "type": "concept", "definition": "生物膜"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        extractor.extract_chunk(chunk)

    # Check cache file exists
    cache_file = RUNTIME_DIR / test_job_id / "extraction_cache" / "chunk_0.json"
    assert cache_file.exists()

    # Verify cache content
    with open(cache_file, 'r', encoding='utf-8') as f:
        cached_data = json.load(f)

    assert cached_data["chunk_id"] == "chunk_0"
    assert cached_data["status"] == "success"
    assert len(cached_data["concepts"]) == 1


def test_extract_chunk_error_handling(extractor, test_chunks):
    """Test that extraction errors are cached to avoid retries."""
    chunk = test_chunks[0]

    # Mock LLM failure
    with patch.object(extractor.builder, '_extract_knowledge', side_effect=Exception("LLM timeout")) as mock_llm:
        result = extractor.extract_chunk(chunk)

        assert result is None
        assert mock_llm.call_count == 1

        # Second call should return cached error (no LLM retry)
        result2 = extractor.extract_chunk(chunk)
        assert result2 is not None
        assert result2["status"] == "failed"
        assert "error" in result2
        assert result2["cached"] is True
        assert mock_llm.call_count == 1  # No retry


def test_extract_batch(extractor, test_chunks):
    """Test batch extraction with progress tracking."""
    mock_extraction = {
        "concepts": [{"name": "测试概念", "type": "concept", "definition": "定义"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        results = extractor.extract_batch(test_chunks)

    assert results["total"] == 3
    assert results["success_count"] == 3
    assert results["failed_count"] == 0
    assert results["cached_count"] == 0
    assert len(results["results"]) == 3


def test_extract_batch_with_failures(extractor, test_chunks):
    """Test batch extraction with some failures."""
    def mock_extract_side_effect(chunk):
        if chunk["chunk_id"] == "chunk_1":
            raise Exception("LLM error")
        return {
            "concepts": [{"name": "概念", "type": "concept", "definition": "定义"}],
            "relationships": []
        }

    with patch.object(extractor.builder, '_extract_knowledge', side_effect=mock_extract_side_effect):
        results = extractor.extract_batch(test_chunks)

    assert results["total"] == 3
    assert results["success_count"] == 2
    assert results["failed_count"] == 1


def test_extract_batch_progress_tracking(extractor, test_chunks, test_job_id):
    """Test that progress is updated during batch extraction."""
    mock_extraction = {
        "concepts": [{"name": "概念", "type": "concept", "definition": "定义"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        extractor.extract_batch(test_chunks)

    # Check state file for progress
    state_path = RUNTIME_DIR / test_job_id / "state.json"
    assert state_path.exists()

    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    assert state["extraction_progress"] == 3
    assert state["extraction_total"] == 3


def test_extract_batch_caching_behavior(extractor, test_chunks):
    """Test that batch extraction uses cache on second run."""
    mock_extraction = {
        "concepts": [{"name": "概念", "type": "concept", "definition": "定义"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction) as mock_llm:
        # First batch - all fresh
        results1 = extractor.extract_batch(test_chunks)
        assert results1["cached_count"] == 0
        assert mock_llm.call_count == 3

        # Second batch - all cached
        results2 = extractor.extract_batch(test_chunks)
        assert results2["cached_count"] == 3
        assert mock_llm.call_count == 3  # No additional calls


def test_concurrent_extraction_safety(extractor, test_chunks):
    """Test that concurrent extractions don't conflict."""
    chunk = test_chunks[0]

    mock_extraction = {
        "concepts": [{"name": "概念", "type": "concept", "definition": "定义"}],
        "relationships": []
    }

    with patch.object(extractor.builder, '_extract_knowledge', return_value=mock_extraction):
        # Simulate concurrent calls
        result1 = extractor.extract_chunk(chunk)
        result2 = extractor.extract_chunk(chunk)

    # Both should succeed (second uses cache)
    assert result1 is not None
    assert result2 is not None
    assert result2["cached"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
