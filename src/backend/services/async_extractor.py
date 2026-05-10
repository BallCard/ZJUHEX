"""
Async knowledge extraction service with caching.

Solves:
- LLM timeout issues (process chunks incrementally)
- Repeated LLM calls (cache results per chunk)
- Progress tracking (update state during processing)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from filelock import FileLock, Timeout
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.knowledge_graph import KnowledgeGraphBuilder
from utils.paths import RUNTIME_DIR
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class AsyncExtractor:
    """Async knowledge extractor with per-chunk caching."""

    def __init__(self, job_id: str):
        """
        Initialize extractor with cache directory.

        Args:
            job_id: Job identifier
        """
        self.job_id = job_id
        self.cache_dir = RUNTIME_DIR / job_id / "extraction_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"AsyncExtractor initialized for job {job_id}")

        # Diagnostic: Check API key before passing
        api_key_to_pass = settings.deepseek_api_key
        logger.info(f"[ASYNC_EXTRACTOR] API key from settings: {api_key_to_pass[:10] if api_key_to_pass and api_key_to_pass != 'your_key_here' else 'NOT CONFIGURED'}...")
        logger.info(f"[ASYNC_EXTRACTOR] API key type: {type(api_key_to_pass)}, length: {len(api_key_to_pass) if api_key_to_pass else 0}")

        # Initialize LLM builder (reuse existing logic)
        self.builder = KnowledgeGraphBuilder(api_key=api_key_to_pass)

    def extract_chunk(self, chunk: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract knowledge from a single chunk with caching.

        Args:
            chunk: Document chunk with chunk_id and content

        Returns:
            Extraction result:
            {
                "chunk_id": "chunk_0",
                "concepts": [...],
                "relationships": [...],
                "cached": True/False,
                "timestamp": "2026-05-10T14:30:00"
            }
            Returns None if extraction fails.
        """
        chunk_id = chunk["chunk_id"]
        cache_file = self.cache_dir / f"{chunk_id}.json"

        # Check cache first
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_result = json.load(f)
                    cached_result["cached"] = True
                    logger.debug(f"Cache hit for {chunk_id}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache read failed for {chunk_id}: {e}")
                # Continue to re-extract

        # Extract using LLM (reuse knowledge_graph logic)
        try:
            extraction = self.builder._extract_knowledge(chunk)

            # Build result
            result = {
                "chunk_id": chunk_id,
                "concepts": extraction.get("concepts", []),
                "relationships": extraction.get("relationships", []),
                "cached": False,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }

            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return result

        except Exception as e:
            # Save error to cache to avoid retrying
            error_result = {
                "chunk_id": chunk_id,
                "concepts": [],
                "relationships": [],
                "cached": False,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)

            logger.error(f"Extraction failed for {chunk_id}: {e}")
            return None

    def extract_batch(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract knowledge from multiple chunks with progress tracking.

        Args:
            chunks: List of document chunks

        Returns:
            {
                "results": [extraction_result, ...],
                "success_count": N,
                "failed_count": M,
                "cached_count": K,
                "total": len(chunks)
            }
        """
        results = []
        success_count = 0
        failed_count = 0
        cached_count = 0

        logger.info(f"Starting batch extraction of {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            # Extract chunk
            result = self.extract_chunk(chunk)

            if result:
                results.append(result)
                if result.get("cached"):
                    cached_count += 1
                if result.get("status") == "success":
                    success_count += 1
                elif result.get("status") == "failed":
                    failed_count += 1
            else:
                failed_count += 1

            # Update progress (will be called by background task)
            progress = i + 1
            self._update_progress(progress, len(chunks))

            # Log progress every 10 chunks
            if (i + 1) % 10 == 0 or (i + 1) == len(chunks):
                logger.info(
                    f"Progress: {i+1}/{len(chunks)} chunks "
                    f"(success: {success_count}, failed: {failed_count}, cached: {cached_count})"
                )

        logger.info(
            f"Batch extraction complete: {success_count} success, {failed_count} failed, "
            f"{cached_count} cached"
        )

        return {
            "results": results,
            "success_count": success_count,
            "failed_count": failed_count,
            "cached_count": cached_count,
            "total": len(chunks)
        }

    def _update_progress(self, current: int, total: int):
        """
        Update extraction progress in job state with file locking.

        Args:
            current: Current progress
            total: Total items
        """
        state_path = RUNTIME_DIR / self.job_id / "state.json"
        lock_path = state_path.with_suffix('.lock')

        try:
            # Acquire file lock with 10s timeout
            with FileLock(str(lock_path), timeout=10):
                # Load existing state
                if state_path.exists():
                    with open(state_path, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                else:
                    state = {}

                # Update progress
                state["extraction_progress"] = current
                state["extraction_total"] = total
                state["updated_at"] = datetime.now().isoformat()

                # Save state
                with open(state_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)

        except Timeout:
            logger.warning(
                f"Failed to acquire lock for state update (job {self.job_id}). "
                f"Progress update skipped."
            )
        except Exception as e:
            logger.error(f"State update failed for job {self.job_id}: {e}")


def extract_knowledge_async(job_id: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function for async extraction.

    Args:
        job_id: Job identifier
        chunks: Document chunks

    Returns:
        Batch extraction results
    """
    extractor = AsyncExtractor(job_id)
    return extractor.extract_batch(chunks)
