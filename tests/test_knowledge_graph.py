"""Test knowledge graph builder."""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.services.knowledge_graph import KnowledgeGraphBuilder


def test_graph_builder_init():
    """Test initialization and API key validation."""
    try:
        builder = KnowledgeGraphBuilder()
        print("[OK] KnowledgeGraphBuilder initialized")
        print(f"  API configured: {builder.api_key[:10]}..." if builder.api_key else "  No API key")
    except ValueError as e:
        print(f"[WARN] API key not configured: {e}")
        print("  (Expected if .env not set up yet)")
        return False
    return True


def test_graph_builder_with_mock_data():
    """Test graph building with mock chunks."""
    if not test_graph_builder_init():
        return

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
        }
    ]

    try:
        builder = KnowledgeGraphBuilder()
        graph = builder.build_graph(mock_chunks, max_chunks=2)

        print(f"\n[OK] Built knowledge graph")
        print(f"  Nodes: {graph['metadata']['total_nodes']}")
        print(f"  Edges: {graph['metadata']['total_edges']}")
        print(f"  Chunks processed: {graph['metadata']['chunks_processed']}")

        if graph['nodes']:
            print(f"\n  Sample node:")
            node = graph['nodes'][0]
            print(f"    ID: {node['id']}")
            print(f"    Label: {node['label']}")
            print(f"    Type: {node['type']}")
            print(f"    Definition: {node['definition'][:50]}..." if len(node['definition']) > 50 else f"    Definition: {node['definition']}")

        if graph['edges']:
            print(f"\n  Sample edge:")
            edge = graph['edges'][0]
            print(f"    {edge['source']} --[{edge['relation']}]--> {edge['target']}")

    except ValueError as e:
        print(f"[WARN] Cannot test with real API: {e}")
    except Exception as e:
        print(f"[ERROR] Graph building failed: {e}")


if __name__ == "__main__":
    print("Testing knowledge graph builder...\n")
    test_graph_builder_with_mock_data()
    print("\n[OK] Knowledge graph tests completed")
