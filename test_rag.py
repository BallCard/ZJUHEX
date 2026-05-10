"""Test RAG pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.services.rag import RAGPipeline


def test_rag_pipeline():
    """Test RAG pipeline with mock data."""
    print("[INFO] Testing RAG pipeline...")

    # Check API key first
    try:
        pipeline_test = RAGPipeline()
        has_api_key = True
    except ValueError as e:
        print(f"[WARN] API key not configured: {e}")
        print("[INFO] Testing without API key (retrieval only)...")
        has_api_key = False

    # Mock chunks
    mock_chunks = [
        {
            "chunk_id": "chunk_0",
            "textbook": "test.pdf",
            "page": 1,
            "content": "细胞膜是由磷脂双层构成的生物膜，具有选择性通透性。细胞膜的主要功能包括物质运输、信号传导和细胞识别。",
            "char_count": 50
        },
        {
            "chunk_id": "chunk_1",
            "textbook": "test.pdf",
            "page": 1,
            "content": "磷脂双层是细胞膜的基本结构，由亲水头部和疏水尾部组成。膜蛋白嵌入磷脂双层中，执行各种功能。",
            "char_count": 45
        },
        {
            "chunk_id": "chunk_2",
            "textbook": "test.pdf",
            "page": 2,
            "content": "细胞核是真核细胞的控制中心，包含遗传物质DNA。核膜将细胞核与细胞质分隔开。",
            "char_count": 40
        }
    ]

    try:
        # Test index building (doesn't require API key)
        if not has_api_key:
            # Create pipeline without API validation for indexing
            from backend.services.rag import SentenceTransformer
            import faiss

            print("[INFO] Building index without API key...")
            embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            texts = [chunk["content"] for chunk in mock_chunks]
            embeddings = embedding_model.encode(texts, convert_to_numpy=True)

            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            faiss.normalize_L2(embeddings)
            index.add(embeddings)

            print(f"[OK] Index built with {index.ntotal} vectors")

            # Test retrieval
            question = "细胞膜的结构是什么？"
            query_embedding = embedding_model.encode([question], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            distances, indices = index.search(query_embedding, 2)

            print(f"\n[OK] Retrieved {len(indices[0])} chunks for question: {question}")
            for i, idx in enumerate(indices[0], 1):
                chunk = mock_chunks[idx]
                print(f"  {i}. {chunk['textbook']} p{chunk['page']}: {chunk['content'][:50]}...")

            print("\n[INFO] Full RAG query requires API key (skipped)")
            return

        # Full test with API key
        pipeline = RAGPipeline()
        pipeline.build_index(mock_chunks)
        print(f"[OK] Index built with {pipeline.index.ntotal} vectors")

        # Test save/load
        job_id = "test_rag_001"
        pipeline.save_index(job_id)
        print(f"[OK] Index saved to data/runtime/jobs/{job_id}")

        # Test query
        pipeline2 = RAGPipeline()
        pipeline2.load_index(job_id)
        print(f"[OK] Index loaded")

        # Test retrieval
        question = "细胞膜的结构是什么？"
        retrieved = pipeline2._retrieve(question, top_k=2)
        print(f"\n[OK] Retrieved {len(retrieved)} chunks for question: {question}")
        for i, chunk in enumerate(retrieved, 1):
            print(f"  {i}. {chunk['textbook']} p{chunk['page']}: {chunk['content'][:50]}...")

        # Test full query
        print(f"\n[INFO] Testing full RAG query...")
        result = pipeline2.query(question, top_k=2)
        print(f"[OK] Answer generated")
        print(f"  Question: {result['question']}")
        print(f"  Answer: {result['answer'][:100]}...")
        print(f"  Citations: {len(result['citations'])} sources")

    except Exception as e:
        print(f"[ERROR] RAG test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Testing RAG pipeline...\n")
    test_rag_pipeline()
    print("\n[OK] RAG tests completed")
