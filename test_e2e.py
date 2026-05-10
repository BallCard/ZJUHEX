"""End-to-end test of the complete pipeline."""

import sys
import time
import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_api_connection():
    """Test if API is accessible."""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        print(f"[OK] API accessible: {response.json()}")
        return True
    except Exception as e:
        print(f"[ERROR] API not accessible: {e}")
        return False

def test_upload():
    """Test file upload."""
    pdf_path = Path("data/textbooks/03_生理学.pdf")

    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        return None

    print(f"\n[INFO] Uploading {pdf_path.name}...")

    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path.name, f, 'application/pdf')}
        response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Upload successful, job_id: {data['job_id']}")
        return data['job_id']
    else:
        print(f"[ERROR] Upload failed: {response.status_code} - {response.text}")
        return None

def test_parse(job_id):
    """Test document parsing."""
    print(f"\n[INFO] Parsing document...")
    response = requests.post(f"{API_BASE}/api/parse/{job_id}", timeout=60)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Parsed {data['chunks_count']} chunks, {data['total_chars']} chars")
        return True
    else:
        print(f"[ERROR] Parse failed: {response.status_code} - {response.text}")
        return False

def test_build_graph(job_id):
    """Test knowledge graph construction."""
    print(f"\n[INFO] Building knowledge graph (max 3 chunks)...")
    response = requests.post(f"{API_BASE}/api/build_graph/{job_id}?max_chunks=3", timeout=120)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Built graph with {data['nodes_count']} nodes, {data['edges_count']} edges")
        return True
    else:
        print(f"[ERROR] Build graph failed: {response.status_code} - {response.text}")
        return False

def test_integrate(job_id):
    """Test deduplication."""
    print(f"\n[INFO] Deduplicating knowledge graph...")
    response = requests.post(f"{API_BASE}/api/integrate/{job_id}", timeout=120)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Deduplicated: {data['original_nodes']} -> {data['deduplicated_nodes']} nodes")
        print(f"    Deduplication ratio: {data['deduplication_ratio']:.2f}")
        return True
    else:
        print(f"[ERROR] Integration failed: {response.status_code} - {response.text}")
        return False

def test_generate_report(job_id):
    """Test report generation."""
    print(f"\n[INFO] Generating integration report...")
    response = requests.post(f"{API_BASE}/api/generate_report/{job_id}", timeout=60)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Report generated: {data['report_path']}")
        print(f"    Compression ratio: {data['compression_ratio']:.2f}%")
        print(f"    Meets target (<=30%): {data['meets_target']}")
        return True
    else:
        print(f"[ERROR] Report generation failed: {response.status_code} - {response.text}")
        return False

def test_rag_index(job_id):
    """Test RAG index building."""
    print(f"\n[INFO] Building RAG index...")
    response = requests.post(f"{API_BASE}/api/rag/index/{job_id}", timeout=120)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] RAG index built with {data['vectors_count']} vectors")
        return True
    else:
        print(f"[ERROR] RAG index failed: {response.status_code} - {response.text}")
        return False

def test_rag_query(job_id):
    """Test RAG query."""
    question = "细胞膜的结构是什么？"
    print(f"\n[INFO] Testing RAG query: {question}")

    response = requests.post(
        f"{API_BASE}/api/rag/query/{job_id}",
        json={"question": question, "top_k": 3},
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] RAG query successful")
        print(f"    Question: {data['question']}")
        print(f"    Answer: {data['answer'][:100]}...")
        print(f"    Citations: {len(data['citations'])} sources")
        for i, citation in enumerate(data['citations'], 1):
            print(f"      [{i}] {citation['textbook']} p{citation['page']}")
        return True
    else:
        print(f"[ERROR] RAG query failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run end-to-end test."""
    print("="*60)
    print("End-to-End Pipeline Test")
    print("="*60)

    # Test API connection
    if not test_api_connection():
        print("\n[FATAL] API not accessible. Make sure server is running:")
        print("  cd src/backend")
        print("  uvicorn main:app --reload --port 8000")
        return

    # Test upload
    job_id = test_upload()
    if not job_id:
        return

    # Test pipeline
    steps = [
        ("Parse", test_parse),
        ("Build Graph", test_build_graph),
        ("Integrate", test_integrate),
        ("Generate Report", test_generate_report),
        ("RAG Index", test_rag_index),
        ("RAG Query", test_rag_query)
    ]

    for step_name, step_func in steps:
        if not step_func(job_id):
            print(f"\n[FATAL] Pipeline stopped at: {step_name}")
            return
        time.sleep(1)  # Brief pause between steps

    print("\n" + "="*60)
    print("[SUCCESS] End-to-end pipeline completed!")
    print("="*60)
    print(f"\nJob ID: {job_id}")
    print(f"Report: report/整合报告_{job_id}.md")
    print(f"State: data/runtime/jobs/{job_id}/state.json")

if __name__ == "__main__":
    main()
