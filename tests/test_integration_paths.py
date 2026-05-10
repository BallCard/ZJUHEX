"""
Integration test for path management across all services.

Tests that all services correctly use unified paths regardless of startup directory.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add src/backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from utils.paths import get_job_dir, REPORT_DIR, ensure_directories


def test_job_state_persistence():
    """Test that job state can be saved and loaded from any directory."""
    from main import save_job_state, load_job_state

    job_id = "test_integration"
    test_state = {
        "job_id": job_id,
        "status": "test",
        "data": "test_data"
    }

    # Save state
    save_job_state(job_id, test_state)

    # Verify file exists at correct location
    job_dir = get_job_dir(job_id)
    state_file = job_dir / "state.json"
    assert state_file.exists(), f"State file not found at {state_file}"

    # Load state
    loaded_state = load_job_state(job_id)
    assert loaded_state["job_id"] == job_id
    assert loaded_state["status"] == "test"

    print(f"[OK] Job state saved to: {state_file}")
    print(f"[OK] Job state loaded successfully")

    # Cleanup
    state_file.unlink()
    job_dir.rmdir()


def test_report_generation_path():
    """Test that report generator uses correct absolute path."""
    from services.report_generator import ReportGenerator

    generator = ReportGenerator()

    # Create minimal test data
    chunks = [
        {"chunk_id": "chunk_0", "char_count": 100, "content": "test"}
    ]
    graph = {
        "nodes": [{"id": "n1", "label": "test", "type": "concept", "definition": "test def"}],
        "edges": []
    }
    deduplicated = {
        "nodes": [{"id": "n1", "label": "test", "type": "concept", "definition": "test def", "source_chunks": ["chunk_0"]}],
        "edges": [],
        "metadata": {"total_nodes": 1, "total_edges": 0}
    }

    job_id = "test_report"
    report_path = generator.generate_report(chunks, graph, deduplicated, job_id)

    # Verify report is at correct location
    expected_path = REPORT_DIR / f"整合报告_{job_id}.md"
    assert Path(report_path) == expected_path, f"Report path mismatch: {report_path} != {expected_path}"
    assert expected_path.exists(), f"Report file not found at {expected_path}"

    print(f"[OK] Report generated at: {report_path}")

    # Cleanup
    expected_path.unlink()


def test_rag_index_path():
    """Test that RAG pipeline uses correct absolute paths."""
    # Skip if dependencies not available
    try:
        from services.rag import RAGPipeline
    except ImportError as e:
        print(f"[SKIP] RAG test skipped: {e}")
        return

    # Create minimal test data
    chunks = [
        {
            "chunk_id": "chunk_0",
            "textbook": "test.pdf",
            "page": 1,
            "content": "这是一个测试文本用于验证RAG路径管理",
            "char_count": 20
        }
    ]

    job_id = "test_rag"

    try:
        pipeline = RAGPipeline()
        pipeline.build_index(chunks)
        pipeline.save_index(job_id)

        # Verify index files are at correct location
        job_dir = get_job_dir(job_id)
        index_file = job_dir / "faiss.index"
        chunks_file = job_dir / "chunks_for_rag.json"

        assert index_file.exists(), f"Index file not found at {index_file}"
        assert chunks_file.exists(), f"Chunks file not found at {chunks_file}"

        print(f"[OK] RAG index saved to: {job_dir}")

        # Test loading
        pipeline2 = RAGPipeline()
        pipeline2.load_index(job_id)
        assert pipeline2.index is not None
        assert len(pipeline2.chunks) == 1

        print(f"[OK] RAG index loaded successfully")

        # Cleanup
        index_file.unlink()
        chunks_file.unlink()
        job_dir.rmdir()

    except ValueError as e:
        if "DEEPSEEK_API_KEY" in str(e):
            print(f"[SKIP] RAG test skipped: API key not configured")
        else:
            raise


def test_paths_from_different_directory():
    """Test that all paths work when starting from a different directory."""
    original_dir = Path.cwd()

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            # Change to temp directory
            os.chdir(tmp_dir)
            print(f"[INFO] Changed to directory: {tmp_dir}")

            # Re-import to test
            from utils.paths import PROJECT_ROOT, get_job_dir, REPORT_DIR

            # Verify paths are still absolute and correct
            assert PROJECT_ROOT.is_absolute()
            assert REPORT_DIR.is_absolute()
            assert get_job_dir("test").is_absolute()

            # Verify paths point to project, not temp directory
            assert str(PROJECT_ROOT) != tmp_dir
            assert "Hex" in str(PROJECT_ROOT)

            print(f"[OK] Paths remain correct from different directory")

        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    print("=" * 60)
    print("Integration Test: Path Management Across Services")
    print("=" * 60)

    ensure_directories()

    test_job_state_persistence()
    print()

    test_report_generation_path()
    print()

    test_rag_index_path()
    print()

    test_paths_from_different_directory()
    print()

    print("=" * 60)
    print("All integration tests passed!")
    print("=" * 60)
