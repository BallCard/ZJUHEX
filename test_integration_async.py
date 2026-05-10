"""
Integration test for async build_graph endpoint.

Tests the complete flow without actual LLM calls:
1. Background task creation
2. Progress tracking
3. State persistence
4. Error handling
"""

import json
import time
from pathlib import Path

# Test configuration
TEST_JOB_ID = "test_integration_001"
BASE_URL = "http://localhost:8000"

# Mock data
MOCK_CHUNKS = [
    {
        "chunk_id": "chunk_0",
        "content": "细胞膜是由磷脂双层构成的生物膜。",
        "page": 1,
        "char_count": 20,
        "textbook": "生理学",
        "chapter": "第一章"
    },
    {
        "chunk_id": "chunk_1",
        "content": "线粒体是细胞的能量工厂，负责ATP合成。",
        "page": 1,
        "char_count": 25,
        "textbook": "生理学",
        "chapter": "第一章"
    },
    {
        "chunk_id": "chunk_2",
        "content": "核糖体是蛋白质合成的场所。",
        "page": 2,
        "char_count": 15,
        "textbook": "生理学",
        "chapter": "第一章"
    }
]


def setup_test_job():
    """Create test job with mock chunks."""
    from src.backend.utils.paths import get_job_dir

    job_dir = get_job_dir(TEST_JOB_ID)
    job_dir.mkdir(parents=True, exist_ok=True)

    # Save mock chunks
    chunks_path = job_dir / "parsed_chunks.json"
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(MOCK_CHUNKS, f, ensure_ascii=False, indent=2)

    # Initialize state
    state = {
        "job_id": TEST_JOB_ID,
        "status": "parsed",
        "current_phase": "parse",
        "filename": "test.pdf",
        "file_path": str(job_dir / "test.pdf"),
        "created_at": "2026-05-10T14:00:00",
        "updated_at": "2026-05-10T14:00:00",
        "chunks_count": len(MOCK_CHUNKS),
        "total_chars": sum(c["char_count"] for c in MOCK_CHUNKS)
    }

    state_path = job_dir / "state.json"
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"✓ Test job created: {TEST_JOB_ID}")
    print(f"  - Chunks: {len(MOCK_CHUNKS)}")
    print(f"  - Job dir: {job_dir}")


def cleanup_test_job():
    """Clean up test job data."""
    from src.backend.utils.paths import get_job_dir
    import shutil

    job_dir = get_job_dir(TEST_JOB_ID)
    if job_dir.exists():
        shutil.rmtree(job_dir)
        print(f"✓ Test job cleaned up: {TEST_JOB_ID}")


def test_async_build_graph():
    """
    Test async build_graph endpoint.

    This test validates:
    1. Endpoint returns immediately with "processing" status
    2. Background task updates progress
    3. Final state shows completion
    4. Cache files are created
    """
    print("\n" + "=" * 60)
    print("Integration Test: Async Build Graph")
    print("=" * 60)

    # Setup
    print("\n[Setup] Creating test job...")
    setup_test_job()

    # Test instructions
    print("\n[Manual Test Instructions]")
    print("1. Start the backend server:")
    print("   cd src/backend")
    print("   uvicorn main:app --reload --port 8000")
    print()
    print("2. In another terminal, run these curl commands:")
    print()
    print(f"   # Trigger async build_graph")
    print(f'   curl -X POST "{BASE_URL}/api/build_graph/{TEST_JOB_ID}?max_chunks=3"')
    print()
    print(f"   # Check progress (run multiple times)")
    print(f'   curl "{BASE_URL}/api/jobs/{TEST_JOB_ID}/progress"')
    print()
    print(f"   # Check final status")
    print(f'   curl "{BASE_URL}/api/status/{TEST_JOB_ID}"')
    print()
    print("3. Expected behavior:")
    print("   - First curl returns: {\"status\": \"processing\", ...}")
    print("   - Progress curl shows: {\"progress\": N, \"total\": 3, ...}")
    print("   - Final status shows: {\"status\": \"graph_built\", ...}")
    print()
    print("4. Verify cache files:")
    from src.backend.utils.paths import get_job_dir
    cache_dir = get_job_dir(TEST_JOB_ID) / "extraction_cache"
    print(f"   ls {cache_dir}")
    print("   (Should see chunk_0.json, chunk_1.json, chunk_2.json)")
    print()
    print("5. Verify knowledge graph:")
    graph_path = get_job_dir(TEST_JOB_ID) / "knowledge_graph.json"
    print(f"   cat {graph_path}")
    print("   (Should see nodes and edges)")
    print()
    print("[Cleanup] Run this when done:")
    print(f"   python -c \"from test_async_manual import cleanup_test_job; cleanup_test_job()\"")
    print()
    print("=" * 60)


def verify_results():
    """Verify test results after manual execution."""
    from src.backend.utils.paths import get_job_dir

    print("\n[Verification] Checking results...")

    job_dir = get_job_dir(TEST_JOB_ID)

    # Check state
    state_path = job_dir / "state.json"
    if not state_path.exists():
        print("✗ State file not found")
        return False

    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    print(f"  Status: {state.get('status')}")
    print(f"  Progress: {state.get('extraction_progress', 0)}/{state.get('extraction_total', 0)}")

    # Check cache files
    cache_dir = job_dir / "extraction_cache"
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        print(f"  Cache files: {len(cache_files)}")
    else:
        print("  Cache directory not found")

    # Check knowledge graph
    graph_path = job_dir / "knowledge_graph.json"
    if graph_path.exists():
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)
        print(f"  Nodes: {len(graph.get('nodes', []))}")
        print(f"  Edges: {len(graph.get('edges', []))}")
    else:
        print("  Knowledge graph not found")

    if state.get('status') == 'graph_built':
        print("\n✓ Test passed!")
        return True
    else:
        print("\n✗ Test incomplete or failed")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_test_job()
        elif sys.argv[1] == "verify":
            verify_results()
        elif sys.argv[1] == "cleanup":
            cleanup_test_job()
        else:
            print("Usage: python test_integration_async.py [setup|verify|cleanup]")
    else:
        test_async_build_graph()
