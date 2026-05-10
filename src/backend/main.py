"""
FastAPI main application with all API endpoints.

P0 Scope:
- Sequential pipeline endpoints
- State persistence to filesystem (data/runtime/jobs/{job_id}/)
- File upload handling
- All service integrations
"""

import os
import json
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import services
import sys
sys.path.insert(0, str(Path(__file__).parent))

from services.parser import parse_textbook
from services.knowledge_graph import build_knowledge_graph, KnowledgeGraphBuilder
from services.integration import deduplicate_knowledge_graph
from services.report_generator import generate_integration_report
from services.rag import RAGPipeline
from services.content_detector import ContentDetector
from services.async_extractor import AsyncExtractor

# Import unified paths
from utils.paths import get_job_dir, REPORT_DIR, ensure_directories

# Ensure all directories exist
ensure_directories()


# Initialize FastAPI app
app = FastAPI(
    title="Medical Textbook Knowledge Integration System",
    description="AI全栈黑客松 - 学科知识整合智能体",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # P0: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class JobStatus(BaseModel):
    job_id: str
    status: str
    current_phase: str
    created_at: str
    updated_at: str


class RAGQuery(BaseModel):
    question: str
    top_k: int = 3


class RAGResponse(BaseModel):
    question: str
    answer: str
    citations: List[dict]


# Helper functions
def save_job_state(job_id: str, state: dict):
    """Save job state to filesystem."""
    job_dir = get_job_dir(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    state_path = job_dir / "state.json"
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def update_job_state(job_id: str, updates: dict):
    """
    Update job state with incremental changes (merge, not overwrite).

    Args:
        job_id: Job identifier
        updates: Dictionary of fields to update
    """
    job_dir = get_job_dir(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    state_path = job_dir / "state.json"

    # Load existing state
    if state_path.exists():
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
    else:
        state = {}

    # Merge updates
    state.update(updates)
    state["updated_at"] = datetime.now().isoformat()

    # Save state
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_job_state(job_id: str) -> dict:
    """Load job state from filesystem."""
    job_dir = get_job_dir(job_id)
    state_path = job_dir / "state.json"
    if not state_path.exists():
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    with open(state_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# API Endpoints

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Medical Textbook Knowledge Integration System",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/upload")
async def upload_textbook(file: UploadFile = File(...)):
    """
    Upload textbook file.

    Returns:
        job_id: Unique job identifier
        filename: Uploaded filename
    """
    # Generate job ID
    job_id = str(uuid.uuid4())[:8]

    # Create job directory
    job_dir = get_job_dir(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file (sanitize filename to prevent path traversal)
    safe_filename = Path(file.filename).name  # Only take filename, remove path components
    file_path = job_dir / safe_filename
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # Initialize job state
    state = {
        "job_id": job_id,
        "status": "uploaded",
        "current_phase": "upload",
        "filename": file.filename,
        "file_path": str(file_path),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    save_job_state(job_id, state)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "message": "File uploaded successfully"
    }


@app.post("/api/parse/{job_id}")
def parse_document(job_id: str):
    """
    Parse uploaded textbook.

    Args:
        job_id: Job identifier

    Returns:
        chunks_count: Number of parsed chunks
        total_chars: Total character count
    """
    # Load job state
    state = load_job_state(job_id)

    # Parse document
    file_path = state["file_path"]
    chunks = parse_textbook(file_path)

    # Save chunks
    chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    # Update state
    state["status"] = "parsed"
    state["current_phase"] = "parse"
    state["chunks_count"] = len(chunks)
    state["total_chars"] = sum(c["char_count"] for c in chunks)
    state["updated_at"] = datetime.now().isoformat()
    save_job_state(job_id, state)

    return {
        "job_id": job_id,
        "chunks_count": len(chunks),
        "total_chars": state["total_chars"],
        "message": "Document parsed successfully"
    }


def build_graph_task(job_id: str, max_chunks: int = None, chapter_num: int = 1):
    """
    Background task to build knowledge graph.

    Args:
        job_id: Job identifier
        max_chunks: Maximum chunks to process (P0 legacy: for testing)
        chapter_num: Chapter number to process (P1: default=1)
    """
    try:
        # Update status to processing
        update_job_state(job_id, {
            "status": "processing",
            "current_phase": "build_graph",
            "extraction_progress": 0,
            "extraction_total": 0
        })

        # Load chunks
        chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        # P1: Use ContentDetector to select chapter
        detector = ContentDetector()

        # Detect content start (skip cover/preface/TOC)
        content_start_idx = detector.detect_content_start(chunks)
        content_chunks = chunks[content_start_idx:]

        # Select complete chapter
        chapter_chunks = detector.select_chapter(content_chunks, chapter_num=chapter_num)

        # Get chapter metadata
        chapter_metadata = detector.get_chapter_metadata(chapter_chunks)

        # P0 backward compatibility: if max_chunks specified, limit chunks
        if max_chunks is not None:
            processing_chunks = chapter_chunks[:max_chunks]
        else:
            processing_chunks = chapter_chunks

        # Use AsyncExtractor for batch extraction with caching
        extractor = AsyncExtractor(job_id)
        extraction_results = extractor.extract_batch(processing_chunks)

        # Build graph from extraction results
        nodes = []
        edges = []
        node_id_counter = 0

        for result in extraction_results["results"]:
            if result.get("status") != "success":
                continue

            chunk_id = result["chunk_id"]

            # Add nodes
            for concept in result.get("concepts", []):
                nodes.append({
                    "id": f"node_{node_id_counter}",
                    "label": concept["name"],
                    "type": concept.get("type", "concept"),
                    "definition": concept.get("definition", ""),
                    "source_chunks": [chunk_id]
                })
                node_id_counter += 1

            # Add edges (relationships)
            for relation in result.get("relationships", []):
                # Find node IDs by label
                source_node = next((n for n in nodes if n["label"] == relation["source"]), None)
                target_node = next((n for n in nodes if n["label"] == relation["target"]), None)

                if source_node and target_node:
                    edges.append({
                        "source": source_node["id"],
                        "target": target_node["id"],
                        "relation": relation["type"],
                        "description": relation.get("description", "")
                    })

        # Build final graph structure
        graph = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "chunks_processed": extraction_results["success_count"],
                "chunks_failed": extraction_results["failed_count"],
                "chunks_cached": extraction_results["cached_count"]
            }
        }

        # Save graph
        graph_path = get_job_dir(job_id) / "knowledge_graph.json"
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

        # Update state with success
        update_job_state(job_id, {
            "status": "graph_built",
            "current_phase": "build_graph",
            "nodes_count": graph["metadata"]["total_nodes"],
            "edges_count": graph["metadata"]["total_edges"],
            "content_start_page": content_chunks[0]["page"] if content_chunks else 0,
            "chapter_title": chapter_metadata["chapter_title"],
            "chapter_start_page": chapter_metadata["start_page"],
            "chapter_end_page": chapter_metadata["end_page"],
            "chapter_chunk_count": chapter_metadata["chunk_count"],
            "processed_chunk_count": len(processing_chunks),
            "extraction_success": extraction_results["success_count"],
            "extraction_failed": extraction_results["failed_count"],
            "extraction_cached": extraction_results["cached_count"]
        })

    except Exception as e:
        # Update state with error
        update_job_state(job_id, {
            "status": "failed",
            "current_phase": "build_graph",
            "error": str(e)
        })
        print(f"[ERROR] build_graph_task failed for job {job_id}: {e}")


@app.post("/api/build_graph/{job_id}")
async def build_graph(job_id: str, background_tasks: BackgroundTasks, max_chunks: int = None, chapter_num: int = 1):
    """
    Build knowledge graph from parsed chunks (async with background task).

    Args:
        job_id: Job identifier
        background_tasks: FastAPI background tasks
        max_chunks: Maximum chunks to process (P0 legacy: for testing, overrides chapter selection)
        chapter_num: Chapter number to process (P1: default=1, processes complete chapter)

    Returns:
        status: "processing"
        job_id: Job identifier
        message: Status message
    """
    # Verify job exists
    load_job_state(job_id)

    # Add background task
    background_tasks.add_task(build_graph_task, job_id, max_chunks, chapter_num)

    return {
        "status": "processing",
        "job_id": job_id,
        "message": "Knowledge graph construction started. Use /api/jobs/{job_id}/progress to check progress."
    }


@app.post("/api/integrate/{job_id}")
def integrate_knowledge(job_id: str):
    """
    Deduplicate and integrate knowledge graph.

    Args:
        job_id: Job identifier

    Returns:
        original_nodes: Original node count
        deduplicated_nodes: Deduplicated node count
        deduplication_ratio: Ratio after deduplication
    """
    # Load graph
    graph_path = get_job_dir(job_id) / "knowledge_graph.json"
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)

    # Deduplicate
    deduplicated = deduplicate_knowledge_graph(graph)

    # Save deduplicated graph
    dedup_path = get_job_dir(job_id) / "deduplicated_graph.json"
    with open(dedup_path, 'w', encoding='utf-8') as f:
        json.dump(deduplicated, f, ensure_ascii=False, indent=2)

    # Update state
    state = load_job_state(job_id)
    state["status"] = "integrated"
    state["current_phase"] = "integrate"
    state["deduplicated_nodes"] = deduplicated["metadata"]["total_nodes"]
    state["deduplicated_edges"] = deduplicated["metadata"]["total_edges"]
    state["deduplication_ratio"] = deduplicated["metadata"]["deduplication_ratio"]
    state["updated_at"] = datetime.now().isoformat()
    save_job_state(job_id, state)

    return {
        "job_id": job_id,
        "original_nodes": len(graph["nodes"]),
        "deduplicated_nodes": deduplicated["metadata"]["total_nodes"],
        "deduplication_ratio": deduplicated["metadata"]["deduplication_ratio"],
        "message": "Knowledge integrated successfully"
    }


@app.post("/api/generate_report/{job_id}")
def generate_report(job_id: str):
    """
    Generate integration report.

    Args:
        job_id: Job identifier

    Returns:
        report_path: Path to generated report
        compression_ratio: Compression ratio percentage
    """
    # Load data
    chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
    graph_path = get_job_dir(job_id) / "knowledge_graph.json"
    dedup_path = get_job_dir(job_id) / "deduplicated_graph.json"

    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
    with open(dedup_path, 'r', encoding='utf-8') as f:
        deduplicated = json.load(f)

    # Load state to get chapter info
    state = load_job_state(job_id)
    chapter_info = {
        "textbook": state.get("filename", "未知教材"),
        "title": state.get("chapter_title", "未知章节"),
        "start_page": state.get("chapter_start_page", 0),
        "end_page": state.get("chapter_end_page", 0),
        "chunk_count": state.get("chapter_chunk_count", 0),
        "processed_chunks": state.get("processed_chunk_count", 0)
    }

    # Generate report
    report_path = generate_integration_report(chunks, graph, deduplicated, job_id, chapter_info)

    # Calculate compression ratio (use actual content length for consistency with report)
    original_chars = sum(len(c.get("content", "")) for c in chunks)
    deduplicated_chars = sum(
        len(node.get("definition", "")) + len(node["label"])
        for node in deduplicated["nodes"]
    )
    compression_ratio = (deduplicated_chars / original_chars * 100) if original_chars > 0 else 0

    # Update state
    state["status"] = "report_generated"
    state["current_phase"] = "generate_report"
    state["report_path"] = report_path
    state["compression_ratio"] = compression_ratio
    state["updated_at"] = datetime.now().isoformat()
    save_job_state(job_id, state)

    return {
        "job_id": job_id,
        "report_path": report_path,
        "compression_ratio": compression_ratio,
        "meets_target": compression_ratio <= 30,
        "chapter_info": chapter_info,
        "message": "Report generated successfully"
    }


@app.post("/api/rag/index/{job_id}")
def build_rag_index(job_id: str):
    """
    Build RAG index from parsed chunks.

    Args:
        job_id: Job identifier

    Returns:
        vectors_count: Number of vectors indexed
    """
    # Load chunks
    chunks_path = get_job_dir(job_id) / "parsed_chunks.json"
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    # Build index
    pipeline = RAGPipeline()
    pipeline.build_index(chunks)
    pipeline.save_index(job_id)

    # Update state
    state = load_job_state(job_id)
    state["status"] = "rag_indexed"
    state["current_phase"] = "rag_index"
    state["rag_vectors"] = pipeline.index.ntotal
    state["updated_at"] = datetime.now().isoformat()
    save_job_state(job_id, state)

    return {
        "job_id": job_id,
        "vectors_count": pipeline.index.ntotal,
        "message": "RAG index built successfully"
    }


@app.post("/api/rag/query/{job_id}", response_model=RAGResponse)
def query_rag(job_id: str, query: RAGQuery):
    """
    Query RAG pipeline.

    Args:
        job_id: Job identifier
        query: RAG query with question and top_k

    Returns:
        question: Original question
        answer: Generated answer
        citations: Source citations
    """
    # Load index and query
    pipeline = RAGPipeline()
    pipeline.load_index(job_id)

    result = pipeline.query(query.question, query.top_k)

    return RAGResponse(**result)


@app.get("/api/jobs/{job_id}/progress")
def get_progress(job_id: str):
    """
    Get job progress (for async tasks like build_graph).

    Args:
        job_id: Job identifier

    Returns:
        status: Current status (processing/graph_built/failed)
        progress: Current progress count
        total: Total items to process
        percentage: Progress percentage
        error: Error message (if failed)
    """
    state = load_job_state(job_id)

    progress = state.get("extraction_progress", 0)
    total = state.get("extraction_total", 0)
    percentage = (progress / total * 100) if total > 0 else 0

    response = {
        "job_id": job_id,
        "status": state.get("status"),
        "current_phase": state.get("current_phase"),
        "progress": progress,
        "total": total,
        "percentage": round(percentage, 1)
    }

    # Add error if failed
    if state.get("status") == "failed":
        response["error"] = state.get("error", "Unknown error")

    # Add extraction stats if available
    if state.get("status") == "graph_built":
        response["extraction_stats"] = {
            "success": state.get("extraction_success", 0),
            "failed": state.get("extraction_failed", 0),
            "cached": state.get("extraction_cached", 0)
        }

    return response


@app.get("/api/status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str):
    """
    Get job status.

    Args:
        job_id: Job identifier

    Returns:
        Job status information
    """
    state = load_job_state(job_id)

    return JobStatus(
        job_id=state["job_id"],
        status=state["status"],
        current_phase=state["current_phase"],
        created_at=state["created_at"],
        updated_at=state["updated_at"]
    )


@app.get("/api/report/{job_id}")
def get_report(job_id: str):
    """
    Get integration report content.

    Args:
        job_id: Job identifier

    Returns:
        Report content as text
    """
    report_path = REPORT_DIR / f"整合报告_{job_id}.md"

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        "job_id": job_id,
        "content": content
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
