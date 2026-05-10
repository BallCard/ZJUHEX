"""Test knowledge integration and deduplication."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.services.integration import KnowledgeIntegrator


def test_deduplication():
    """Test deduplication with mock graph."""
    print("[INFO] Testing knowledge deduplication...")

    # Mock graph with duplicate nodes
    mock_graph = {
        "nodes": [
            {
                "id": "node_0",
                "label": "细胞膜",
                "type": "concept",
                "definition": "由磷脂双层构成的生物膜",
                "source_chunks": ["chunk_0"]
            },
            {
                "id": "node_1",
                "label": "细胞膜",
                "type": "concept",
                "definition": "细胞的外层结构，具有选择性通透性",
                "source_chunks": ["chunk_1"]
            },
            {
                "id": "node_2",
                "label": "磷脂双层",
                "type": "concept",
                "definition": "细胞膜的基本结构",
                "source_chunks": ["chunk_0"]
            },
            {
                "id": "node_3",
                "label": "膜蛋白",
                "type": "concept",
                "definition": "嵌入细胞膜的蛋白质",
                "source_chunks": ["chunk_2"]
            }
        ],
        "edges": [
            {
                "source": "node_0",
                "target": "node_2",
                "relation": "包含",
                "description": "细胞膜包含磷脂双层"
            },
            {
                "source": "node_1",
                "target": "node_2",
                "relation": "包含",
                "description": "细胞膜包含磷脂双层"
            },
            {
                "source": "node_0",
                "target": "node_3",
                "relation": "包含",
                "description": "细胞膜包含膜蛋白"
            }
        ]
    }

    print(f"\n[INFO] Original graph:")
    print(f"  Nodes: {len(mock_graph['nodes'])}")
    print(f"  Edges: {len(mock_graph['edges'])}")

    # Test deduplication
    integrator = KnowledgeIntegrator(similarity_threshold=0.90)
    deduplicated = integrator.deduplicate_graph(mock_graph)

    print(f"\n[OK] Deduplicated graph:")
    print(f"  Nodes: {deduplicated['metadata']['total_nodes']}")
    print(f"  Edges: {deduplicated['metadata']['total_edges']}")
    print(f"  Original nodes: {deduplicated['metadata']['original_nodes']}")
    print(f"  Deduplication ratio: {deduplicated['metadata']['deduplication_ratio']:.2f}")

    # Show merged nodes
    print(f"\n[INFO] Merged nodes:")
    for node in deduplicated['nodes']:
        if len(node['source_chunks']) > 1:
            print(f"  {node['label']}: merged from {len(node['source_chunks'])} chunks")
            print(f"    Sources: {node['source_chunks']}")

    print(f"\n[INFO] Edges after deduplication:")
    for edge in deduplicated['edges']:
        print(f"  {edge['source']} --[{edge['relation']}]--> {edge['target']}")


if __name__ == "__main__":
    print("Testing knowledge integration...\n")
    test_deduplication()
    print("\n[OK] Integration tests completed")
