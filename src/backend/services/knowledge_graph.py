"""
Knowledge graph construction service using LLM extraction.

P0 Scope:
- Process first 10 chunks for demo (time constraint)
- Extract knowledge nodes (concepts, terms, definitions)
- Identify relationships (前置依赖, 并列, 包含, 应用)
- Use DeepSeek API for extraction
- Output custom JSON structure (nodes + edges)
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class KnowledgeGraphBuilder:
    """Build knowledge graph from parsed document chunks using LLM."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with DeepSeek API.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key or self.api_key == "your_key_here":
            raise ValueError("DEEPSEEK_API_KEY not configured in .env file")

        # DeepSeek is OpenAI-compatible
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    def build_graph(self, chunks: List[Dict[str, Any]], max_chunks: int = 10) -> Dict[str, Any]:
        """
        Build knowledge graph from document chunks.

        Args:
            chunks: Parsed document chunks
            max_chunks: Maximum chunks to process (P0: 3 for small sample validation)

        Returns:
            Knowledge graph structure:
            {
                "nodes": [
                    {
                        "id": "node_0",
                        "label": "细胞膜",
                        "type": "concept",
                        "definition": "...",
                        "source_chunks": ["chunk_0", "chunk_3"]
                    },
                    ...
                ],
                "edges": [
                    {
                        "source": "node_0",
                        "target": "node_1",
                        "relation": "前置依赖",
                        "description": "..."
                    },
                    ...
                ]
            }
        """
        # Limit chunks for P0 demo
        chunks_to_process = chunks[:max_chunks]

        nodes = []
        edges = []
        node_id_counter = 0

        for chunk in chunks_to_process:
            # Extract knowledge from chunk
            extraction = self._extract_knowledge(chunk)

            # Add nodes
            for concept in extraction.get("concepts", []):
                nodes.append({
                    "id": f"node_{node_id_counter}",
                    "label": concept["name"],
                    "type": concept.get("type", "concept"),
                    "definition": concept.get("definition", ""),
                    "source_chunks": [chunk["chunk_id"]]
                })
                node_id_counter += 1

            # Add edges (relationships)
            for relation in extraction.get("relationships", []):
                # Find node IDs by label
                source_node = self._find_node_by_label(nodes, relation["source"])
                target_node = self._find_node_by_label(nodes, relation["target"])

                if source_node and target_node:
                    edges.append({
                        "source": source_node["id"],
                        "target": target_node["id"],
                        "relation": relation["type"],
                        "description": relation.get("description", "")
                    })

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "chunks_processed": len(chunks_to_process)
            }
        }

    def _extract_knowledge(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge from a single chunk using LLM.

        Args:
            chunk: Document chunk with content

        Returns:
            Extracted knowledge:
            {
                "concepts": [
                    {"name": "细胞膜", "type": "concept", "definition": "..."},
                    ...
                ],
                "relationships": [
                    {"source": "细胞膜", "target": "磷脂双层", "type": "包含", "description": "..."},
                    ...
                ]
            }
        """
        prompt = f"""你是医学知识图谱构建专家。从以下文本中提取知识点和关系。

文本内容：
{chunk['content']}

请提取：
1. 核心概念（名词、术语、定义）
2. 概念之间的关系（前置依赖、并列、包含、应用）

以JSON格式返回，格式如下：
{{
    "concepts": [
        {{"name": "概念名称", "type": "concept", "definition": "简短定义"}},
        ...
    ],
    "relationships": [
        {{"source": "概念A", "target": "概念B", "type": "前置依赖|并列|包含|应用", "description": "关系说明"}},
        ...
    ]
}}

只返回JSON，不要其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是医学知识图谱构建专家，擅长从文本中提取结构化知识。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            extraction = json.loads(content)
            return extraction

        except Exception as e:
            print(f"[WARN] LLM extraction failed for chunk {chunk['chunk_id']}: {e}")
            return {"concepts": [], "relationships": []}

    def _find_node_by_label(self, nodes: List[Dict[str, Any]], label: str) -> Optional[Dict[str, Any]]:
        """Find node by label."""
        for node in nodes:
            if node["label"] == label:
                return node
        return None

    def save_graph(self, graph: Dict[str, Any], output_path: str):
        """Save knowledge graph to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)


def build_knowledge_graph(chunks: List[Dict[str, Any]], max_chunks: int = 10) -> Dict[str, Any]:
    """
    Convenience function to build knowledge graph.

    Args:
        chunks: Parsed document chunks
        max_chunks: Maximum chunks to process

    Returns:
        Knowledge graph structure
    """
    builder = KnowledgeGraphBuilder()
    return builder.build_graph(chunks, max_chunks)
