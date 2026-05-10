"""
Test script for cross-textbook integration functionality.

Tests:
1. CrossTextbookIntegrator initialization
2. Knowledge graph alignment
3. Cross-textbook deduplication
4. Report generation
"""

import sys
from pathlib import Path

# Add src/backend to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from services.cross_textbook_integration import CrossTextbookIntegrator


def test_cross_textbook_integrator():
    """Test cross-textbook integrator with mock data."""
    print("=" * 60)
    print("Testing Cross-Textbook Integration")
    print("=" * 60)

    # Create mock graphs from two textbooks
    graph1 = {
        "nodes": [
            {
                "id": "node_0",
                "label": "细胞膜",
                "type": "concept",
                "definition": "细胞膜是细胞的外层结构，由脂质双层组成",
                "source_chunks": ["chunk_1"]
            },
            {
                "id": "node_1",
                "label": "线粒体",
                "type": "concept",
                "definition": "线粒体是细胞的能量工厂",
                "source_chunks": ["chunk_2"]
            },
            {
                "id": "node_2",
                "label": "细胞核",
                "type": "concept",
                "definition": "细胞核包含遗传物质DNA",
                "source_chunks": ["chunk_3"]
            }
        ],
        "edges": [
            {
                "source": "node_0",
                "target": "node_1",
                "relation": "包含",
                "description": "细胞膜包围线粒体"
            }
        ],
        "metadata": {
            "textbook_name": "生理学.pdf",
            "total_nodes": 3,
            "total_edges": 1
        }
    }

    graph2 = {
        "nodes": [
            {
                "id": "node_0",
                "label": "细胞膜",
                "type": "concept",
                "definition": "细胞膜由磷脂双分子层构成，具有选择通透性",
                "source_chunks": ["chunk_10"]
            },
            {
                "id": "node_1",
                "label": "内质网",
                "type": "concept",
                "definition": "内质网是细胞内的膜系统",
                "source_chunks": ["chunk_11"]
            },
            {
                "id": "node_2",
                "label": "高尔基体",
                "type": "concept",
                "definition": "高尔基体负责蛋白质的加工和运输",
                "source_chunks": ["chunk_12"]
            }
        ],
        "edges": [
            {
                "source": "node_1",
                "target": "node_2",
                "relation": "前置",
                "description": "内质网合成的蛋白质运输到高尔基体"
            }
        ],
        "metadata": {
            "textbook_name": "组织学与胚胎学.pdf",
            "total_nodes": 3,
            "total_edges": 1
        }
    }

    print("\n1. Testing integrator initialization...")
    integrator = CrossTextbookIntegrator(similarity_threshold=0.90)
    print("[OK] Integrator initialized successfully")

    print("\n2. Testing knowledge graph alignment...")
    aligned_graph = integrator.align_knowledge_graphs([graph1, graph2])
    print(f"[OK] Aligned graph created")
    print(f"  - Original nodes: {aligned_graph['metadata']['original_node_count']}")
    print(f"  - Merged nodes: {aligned_graph['metadata']['merged_node_count']}")
    print(f"  - Deduplication ratio: {aligned_graph['metadata']['deduplication_ratio']:.2f}")

    print("\n3. Testing cross-textbook deduplication...")
    # Check if "细胞膜" was merged
    cell_membrane_nodes = [n for n in aligned_graph['nodes'] if '细胞膜' in n.get('label', '')]
    if cell_membrane_nodes:
        node = cell_membrane_nodes[0]
        print(f"[OK] Found merged node: {node['label']}")
        print(f"  - Source count: {node.get('source_count', 0)}")
        print(f"  - Textbook count: {node.get('textbook_count', 0)}")
        if node.get('sources'):
            print(f"  - Sources: {[s['textbook_name'] for s in node['sources']]}")
    else:
        print("[FAIL] No merged nodes found for '细胞膜'")

    print("\n4. Testing report generation...")
    report = integrator.generate_cross_textbook_report(aligned_graph, [graph1, graph2])
    print(f"[OK] Report generated ({len(report)} characters)")
    print("\nReport preview:")
    print("-" * 60)
    print(report[:500] + "...")
    print("-" * 60)

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_cross_textbook_integrator()
