"""
Test P2 Step 1: Important fixes (file locking, input validation, LLM timeout).
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from filelock import FileLock, Timeout
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from services.async_extractor import AsyncExtractor
from fastapi.testclient import TestClient
from main import app


class TestFileLocking:
    """Test file locking in async_extractor."""

    def test_file_lock_prevents_concurrent_writes(self):
        """Test that file lock prevents race conditions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            job_id = "test_job"
            state_path = Path(tmpdir) / job_id / "state.json"
            state_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = state_path.with_suffix('.lock')

            # Initialize state
            state_path.write_text(json.dumps({"counter": 0}), encoding='utf-8')

            # Simulate concurrent updates
            with FileLock(str(lock_path), timeout=10):
                # First process holds lock
                state = json.loads(state_path.read_text(encoding='utf-8'))
                state["counter"] += 1

                # Second process should timeout
                with pytest.raises(Timeout):
                    with FileLock(str(lock_path), timeout=0.1):
                        pass

                # Save state
                state_path.write_text(json.dumps(state), encoding='utf-8')

            # Verify state is consistent
            final_state = json.loads(state_path.read_text(encoding='utf-8'))
            assert final_state["counter"] == 1

    def test_async_extractor_uses_file_lock(self):
        """Test that AsyncExtractor._update_progress uses file lock."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock RUNTIME_DIR
            with patch('services.async_extractor.RUNTIME_DIR', Path(tmpdir)):
                job_id = "test_job"
                extractor = AsyncExtractor(job_id)

                # Update progress
                extractor._update_progress(5, 10)

                # Verify state file exists
                state_path = Path(tmpdir) / job_id / "state.json"
                assert state_path.exists()

                # Verify state content
                state = json.loads(state_path.read_text(encoding='utf-8'))
                assert state["extraction_progress"] == 5
                assert state["extraction_total"] == 10

    def test_file_lock_timeout_handling(self):
        """Test that lock timeout is handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('services.async_extractor.RUNTIME_DIR', Path(tmpdir)):
                job_id = "test_job"
                extractor = AsyncExtractor(job_id)

                state_path = Path(tmpdir) / job_id / "state.json"
                state_path.parent.mkdir(parents=True, exist_ok=True)
                lock_path = state_path.with_suffix('.lock')

                # Hold lock externally
                external_lock = FileLock(str(lock_path), timeout=10)
                external_lock.acquire()

                try:
                    # This should timeout but not crash
                    extractor._update_progress(1, 10)
                    # Should print warning but continue
                finally:
                    external_lock.release()


class TestInputValidation:
    """Test input validation for chapter_num."""

    def test_chapter_num_validation_rejects_zero(self):
        """Test that chapter_num=0 is rejected."""
        client = TestClient(app)

        # Upload a dummy file first
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", b"dummy content", "application/pdf")}
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Try to build graph with invalid chapter_num
        response = client.post(f"/api/build_graph/{job_id}?chapter_num=0")
        assert response.status_code == 400
        assert "Invalid chapter_num" in response.json()["detail"]

    def test_chapter_num_validation_rejects_over_100(self):
        """Test that chapter_num>100 is rejected."""
        client = TestClient(app)

        # Upload a dummy file first
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", b"dummy content", "application/pdf")}
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Try to build graph with invalid chapter_num
        response = client.post(f"/api/build_graph/{job_id}?chapter_num=101")
        assert response.status_code == 400
        assert "Invalid chapter_num" in response.json()["detail"]

    def test_chapter_num_validation_accepts_valid_range(self):
        """Test that chapter_num in [1, 100] is accepted."""
        client = TestClient(app)

        # Upload a dummy file first
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", b"dummy content", "application/pdf")}
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]

        # Mock parse to avoid actual parsing
        with patch('main.load_job_state') as mock_load:
            mock_load.return_value = {"job_id": job_id, "status": "uploaded"}

            # Try valid chapter_num values
            for chapter_num in [1, 50, 100]:
                response = client.post(f"/api/build_graph/{job_id}?chapter_num={chapter_num}")
                # Should accept (202 or 200, not 400)
                assert response.status_code in [200, 202], f"chapter_num={chapter_num} should be accepted"


class TestLLMTimeout:
    """Test LLM timeout configuration."""

    def test_knowledge_graph_has_timeout(self):
        """Test that knowledge_graph LLM calls have timeout."""
        from services.knowledge_graph import KnowledgeGraphBuilder

        builder = KnowledgeGraphBuilder()

        # Mock OpenAI client
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"concepts": [], "relationships": []}'))]
        builder.client.chat.completions.create = Mock(return_value=mock_response)

        # Extract knowledge
        chunk = {"chunk_id": "test", "content": "test content"}
        builder._extract_knowledge(chunk)

        # Verify timeout was passed
        call_kwargs = builder.client.chat.completions.create.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 60

    def test_rag_has_timeout(self):
        """Test that RAG LLM calls have timeout."""
        from services.rag import RAGPipeline

        pipeline = RAGPipeline()

        # Mock OpenAI client
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test answer"))]
        pipeline.llm_client.chat.completions.create = Mock(return_value=mock_response)

        # Mock chunks
        pipeline.chunks = [{"chunk_id": "test", "content": "test", "textbook": "test.pdf", "page": 1}]

        # Generate answer
        pipeline._generate_answer("test question", pipeline.chunks)

        # Verify timeout was passed
        call_kwargs = pipeline.llm_client.chat.completions.create.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
