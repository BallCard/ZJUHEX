"""
RAG (Retrieval-Augmented Generation) service with citations.

P0 Scope:
- FAISS vector-only retrieval (top-3)
- sentence-transformers embedding (same as deduplication)
- DeepSeek for answer generation
- Citation tracking: textbook name, page, content snippet
- Return answer with source references
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class RAGPipeline:
    """RAG pipeline with FAISS retrieval and citation tracking."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize RAG pipeline.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key or self.api_key == "your_key_here":
            raise ValueError("DEEPSEEK_API_KEY not configured in .env file")

        # Initialize embedding model
        print("[INFO] Loading sentence-transformers model for RAG...")
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("[INFO] Model loaded")

        # Initialize LLM client
        self.llm_client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

        # FAISS index and chunks (loaded later)
        self.index = None
        self.chunks = None

    def build_index(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build FAISS index from document chunks.

        Args:
            chunks: Parsed document chunks

        Returns:
            Path to saved index directory
        """
        if not chunks:
            raise ValueError("No chunks provided for indexing")

        self.chunks = chunks

        # Generate embeddings
        print(f"[INFO] Generating embeddings for {len(chunks)} chunks...")
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)

        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance (equivalent to cosine for normalized vectors)

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

        print(f"[INFO] FAISS index built with {self.index.ntotal} vectors")

        return "faiss_index_built"

    def save_index(self, job_id: str):
        """
        Save FAISS index and chunks to disk.

        Args:
            job_id: Job identifier
        """
        if self.index is None or self.chunks is None:
            raise ValueError("Index not built yet")

        # Create job directory
        job_dir = Path(f"data/runtime/jobs/{job_id}")
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = job_dir / "faiss.index"
        faiss.write_index(self.index, str(index_path))

        # Save chunks metadata
        chunks_path = job_dir / "chunks_for_rag.json"
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

        print(f"[INFO] Index saved to {job_dir}")

    def load_index(self, job_id: str):
        """
        Load FAISS index and chunks from disk.

        Args:
            job_id: Job identifier
        """
        job_dir = Path(f"data/runtime/jobs/{job_id}")

        # Load FAISS index
        index_path = job_dir / "faiss.index"
        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")
        self.index = faiss.read_index(str(index_path))

        # Load chunks metadata
        chunks_path = job_dir / "chunks_for_rag.json"
        if not chunks_path.exists():
            raise FileNotFoundError(f"Chunks not found: {chunks_path}")
        with open(chunks_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)

        print(f"[INFO] Index loaded from {job_dir}")

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query RAG pipeline with a question.

        Args:
            question: User question
            top_k: Number of chunks to retrieve (default: 3)

        Returns:
            Answer with citations:
            {
                "question": "...",
                "answer": "...",
                "citations": [
                    {
                        "textbook": "03_生理学.pdf",
                        "page": 5,
                        "content": "...",
                        "chunk_id": "chunk_3"
                    },
                    ...
                ]
            }
        """
        if self.index is None or self.chunks is None:
            raise ValueError("Index not loaded. Call build_index() or load_index() first.")

        # Retrieve relevant chunks
        retrieved_chunks = self._retrieve(question, top_k)

        # Generate answer with LLM
        answer = self._generate_answer(question, retrieved_chunks)

        # Format citations
        citations = [
            {
                "textbook": chunk["textbook"],
                "page": chunk["page"],
                "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "chunk_id": chunk["chunk_id"]
            }
            for chunk in retrieved_chunks
        ]

        return {
            "question": question,
            "answer": answer,
            "citations": citations
        }

    def _retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant chunks using FAISS.

        Args:
            query: Query text
            top_k: Number of chunks to retrieve

        Returns:
            List of retrieved chunks
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)

        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)

        # Get chunks
        retrieved = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                retrieved.append(self.chunks[idx])

        return retrieved

    def _generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate answer using LLM with retrieved context.

        Args:
            question: User question
            context_chunks: Retrieved context chunks

        Returns:
            Generated answer
        """
        # Build context from chunks
        context = "\n\n".join([
            f"[来源: {chunk['textbook']}, 第{chunk['page']}页]\n{chunk['content']}"
            for chunk in context_chunks
        ])

        prompt = f"""你是医学知识问答专家。基于以下参考资料回答问题。

参考资料：
{context}

问题：{question}

要求：
1. 基于参考资料回答，不要编造信息
2. 如果参考资料不足以回答问题，明确说明
3. 回答要准确、简洁、专业
4. 使用中文回答

回答："""

        try:
            response = self.llm_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是医学知识问答专家，擅长基于参考资料准确回答问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            print(f"[ERROR] LLM generation failed: {e}")
            return f"抱歉，生成回答时出错：{e}"


def build_rag_index(chunks: List[Dict[str, Any]], job_id: str) -> RAGPipeline:
    """
    Convenience function to build RAG index.

    Args:
        chunks: Parsed document chunks
        job_id: Job identifier

    Returns:
        RAG pipeline with built index
    """
    pipeline = RAGPipeline()
    pipeline.build_index(chunks)
    pipeline.save_index(job_id)
    return pipeline


def query_rag(question: str, job_id: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Convenience function to query RAG pipeline.

    Args:
        question: User question
        job_id: Job identifier
        top_k: Number of chunks to retrieve

    Returns:
        Answer with citations
    """
    pipeline = RAGPipeline()
    pipeline.load_index(job_id)
    return pipeline.query(question, top_k)
