"""End-to-end test of the complete pipeline.

Tests both single-textbook and cross-textbook integration workflows.
"""

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

def test_upload_multiple():
    """Test multiple file upload for cross-textbook integration."""
    pdf_paths = [
        Path("data/textbooks/03_生理学.pdf"),
        Path("data/textbooks/02_组织学与胚胎学.pdf")
    ]

    # Check if files exist
    available_files = [p for p in pdf_paths if p.exists()]
    if len(available_files) < 2:
        print(f"[WARNING] Need at least 2 PDFs for cross-textbook test")
        print(f"  Available: {len(available_files)}, Required: 2")
        return None

    print(f"\n[INFO] Uploading {len(available_files)} textbooks...")

    files = [('files', (p.name, open(p, 'rb'), 'application/pdf')) for p in available_files]

    try:
        response = requests.post(f"{API_BASE}/api/upload_multiple", files=files, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Upload successful, job_id: {data['job_id']}, textbook_count: {data['textbook_count']}")
            return data['job_id']
        else:
            print(f"[ERROR] Upload failed: {response.status_code} - {response.text}")
            return None
    finally:
        # Close file handles
        for _, (_, f, _) in files:
            f.close()

def test_parse_multiple(job_id):
    """Test parsing multiple textbooks."""
    print(f"\n[INFO] Parsing multiple textbooks...")
    response = requests.post(f"{API_BASE}/api/parse_multiple/{job_id}", timeout=120)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Parsed {data['textbook_count']} textbooks")
        for tb_id, info in data['results'].items():
            print(f"    {info['textbook_name']}: {info['chunks_count']} chunks")
        return True
    else:
        print(f"[ERROR] Parse multiple failed: {response.status_code} - {response.text}")
        return False

def test_build_graphs_multiple(job_id):
    """Test building knowledge graphs for multiple textbooks."""
    print(f"\n[INFO] Building knowledge graphs for multiple textbooks...")
    response = requests.post(f"{API_BASE}/api/build_graphs_multiple/{job_id}?max_chunks=3", timeout=180)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Started building graphs, task_id: {data.get('task_id', 'N/A')}")

        # Poll for completion
        max_wait = 120  # 2 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            progress_response = requests.get(f"{API_BASE}/api/jobs/{job_id}/progress", timeout=5)
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                status = progress_data.get('status', 'unknown')
                print(f"    Status: {status}, Progress: {progress_data.get('progress', 0)}%")

                if status == 'completed':
                    print(f"[OK] All graphs built successfully")
                    return True
                elif status == 'failed':
                    print(f"[ERROR] Graph building failed: {progress_data.get('error', 'Unknown error')}")
                    return False

            time.sleep(5)

        print(f"[WARNING] Graph building timeout after {max_wait}s")
        return False
    else:
        print(f"[ERROR] Build graphs multiple failed: {response.status_code} - {response.text}")
        return False

def test_cross_integrate(job_id):
    """Test cross-textbook integration."""
    print(f"\n[INFO] Running cross-textbook integration...")
    response = requests.post(f"{API_BASE}/api/cross_integrate/{job_id}", timeout=180)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Cross-textbook integration completed")
        print(f"    Total nodes: {data['total_nodes']}")
        print(f"    Deduplicated nodes: {data['deduplicated_nodes']}")
        print(f"    Deduplication ratio: {data['deduplication_ratio']:.2f}")
        print(f"    Textbook count: {data['textbook_count']}")
        return True
    else:
        print(f"[ERROR] Cross integration failed: {response.status_code} - {response.text}")
        return False

def test_cross_report(job_id):
    """Test cross-textbook report retrieval."""
    print(f"\n[INFO] Retrieving cross-textbook report...")
    response = requests.get(f"{API_BASE}/api/cross_report/{job_id}", timeout=30)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Cross-textbook report retrieved")
        print(f"    Report length: {len(data['report'])} chars")
        print(f"    Report preview: {data['report'][:200]}...")
        return True
    else:
        print(f"[ERROR] Cross report retrieval failed: {response.status_code} - {response.text}")
        return False

def test_cross_graph(job_id):
    """Test cross-textbook graph retrieval for visualization."""
    print(f"\n[INFO] Retrieving cross-textbook graph for visualization...")
    response = requests.get(f"{API_BASE}/api/cross_graph/{job_id}", timeout=30)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Cross-textbook graph retrieved")
        print(f"    Nodes: {len(data['nodes'])}")
        print(f"    Edges: {len(data['edges'])}")

        # Check node structure
        if data['nodes']:
            sample_node = data['nodes'][0]
            print(f"    Sample node keys: {list(sample_node.keys())}")

        return True
    else:
        print(f"[ERROR] Cross graph retrieval failed: {response.status_code} - {response.text}")
        return False

def test_single_textbook_pipeline():
    """Test single textbook complete pipeline."""
    print("\n" + "="*60)
    print("TEST 1: Single Textbook Pipeline")
    print("="*60)

    # Test upload
    job_id = test_upload()
    if not job_id:
        return False

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
            return False
        time.sleep(1)

    print("\n[SUCCESS] Single textbook pipeline completed!")
    print(f"Job ID: {job_id}")
    print(f"Report: report/整合报告_{job_id}.md")

    return True

def test_multi_textbook_pipeline():
    """Test cross-textbook integration pipeline."""
    print("\n" + "="*60)
    print("TEST 2: Cross-Textbook Integration Pipeline")
    print("="*60)

    # Test multiple upload
    job_id = test_upload_multiple()
    if not job_id:
        print("[SKIP] Cross-textbook test skipped (insufficient files)")
        return True  # Not a failure, just skipped

    # Test cross-textbook pipeline
    steps = [
        ("Parse Multiple", test_parse_multiple),
        ("Build Graphs Multiple", test_build_graphs_multiple),
        ("Cross Integrate", test_cross_integrate),
        ("Cross Report", test_cross_report),
        ("Cross Graph", test_cross_graph)
    ]

    for step_name, step_func in steps:
        if not step_func(job_id):
            print(f"\n[FATAL] Cross-textbook pipeline stopped at: {step_name}")
            return False
        time.sleep(1)

    print("\n[SUCCESS] Cross-textbook pipeline completed!")
    print(f"Job ID: {job_id}")
    print(f"Report: report/跨教材整合报告_{job_id}.md")

    return True

def test_graph_visualization():
    """Test graph visualization data format."""
    print("\n" + "="*60)
    print("TEST 3: Graph Visualization Data Format")
    print("="*60)

    # Use existing job or create new one
    job_id = test_upload()
    if not job_id:
        return False

    # Quick pipeline to get graph data
    if not test_parse(job_id):
        return False
    if not test_build_graph(job_id):
        return False

    # Test graph data retrieval
    print(f"\n[INFO] Retrieving graph data for visualization...")
    response = requests.get(f"{API_BASE}/api/graph/{job_id}", timeout=30)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Graph data retrieved")
        print(f"    Nodes: {len(data.get('nodes', []))}")
        print(f"    Edges: {len(data.get('edges', []))}")

        # Validate Cytoscape.js format
        if data.get('nodes'):
            sample_node = data['nodes'][0]
            required_keys = ['data']
            if all(k in sample_node for k in required_keys):
                print(f"[OK] Node format valid for Cytoscape.js")
            else:
                print(f"[WARNING] Node format may not be compatible with Cytoscape.js")

        if data.get('edges'):
            sample_edge = data['edges'][0]
            required_keys = ['data']
            if all(k in sample_edge for k in required_keys):
                print(f"[OK] Edge format valid for Cytoscape.js")
            else:
                print(f"[WARNING] Edge format may not be compatible with Cytoscape.js")

        return True
    else:
        print(f"[ERROR] Graph retrieval failed: {response.status_code} - {response.text}")
        return False

def main():
    """Run all end-to-end tests."""
    print("="*60)
    print("End-to-End Test Suite")
    print("="*60)

    # Test API connection
    if not test_api_connection():
        print("\n[FATAL] API not accessible. Make sure server is running:")
        print("  cd src/backend")
        print("  uvicorn main:app --reload --port 8000")
        return

    # Run all test suites
    results = {
        "Single Textbook Pipeline": test_single_textbook_pipeline(),
        "Cross-Textbook Pipeline": test_multi_textbook_pipeline(),
        "Graph Visualization": test_graph_visualization()
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[FAILURE] Some tests failed. Check logs above.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
