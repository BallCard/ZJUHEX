"""Quick test - parse only, skip LLM calls."""

import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def quick_test():
    """Test parse and check results."""
    print("Quick Test - Parse Only\n")

    # 1. Upload
    pdf_path = Path("data/textbooks/03_生理学.pdf")
    print(f"[1/2] Uploading {pdf_path.name}...")

    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path.name, f, 'application/pdf')}
        response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)

    job_id = response.json()['job_id']
    print(f"      Job ID: {job_id}")

    # 2. Parse
    print(f"\n[2/2] Parsing document...")
    response = requests.post(f"{API_BASE}/api/parse/{job_id}", timeout=60)
    data = response.json()

    print(f"\n[RESULTS]")
    print(f"  Chunks: {data['chunks_count']}")
    print(f"  Total chars: {data['total_chars']:,}")
    print(f"  Job directory: data/runtime/jobs/{job_id}/")

    # Check saved files
    import json
    chunks_file = Path(f"data/runtime/jobs/{job_id}/parsed_chunks.json")
    if chunks_file.exists():
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"\n[SAMPLE CHUNK]")
        print(f"  Chunk ID: {chunks[0]['chunk_id']}")
        print(f"  Page: {chunks[0]['page']}")
        print(f"  Chars: {chunks[0]['char_count']}")
        print(f"  Content: {chunks[0]['content'][:100]}...")

    print(f"\n[SUCCESS] Parse completed!")
    print(f"\nNote: Skipping LLM steps (build_graph, integrate, etc.) due to timeout issues.")
    print(f"      These require DeepSeek API calls which take >2 minutes per chunk.")

if __name__ == "__main__":
    quick_test()
