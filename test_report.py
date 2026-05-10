"""Test report generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.services.report_generator import ReportGenerator


def test_report_generation():
    """Test report generation with mock data."""
    print("[INFO] Testing report generation...")

    # Mock data
    mock_chunks = [
        {"chunk_id": "chunk_0", "char_count": 500},
        {"chunk_id": "chunk_1", "char_count": 600},
        {"chunk_id": "chunk_2", "char_count": 550}
    ]

    mock_original_graph = {
        "nodes": [
            {"id": "node_0", "label": "细胞膜", "type": "concept", "definition": "由磷脂双层构成的生物膜", "source_chunks": ["chunk_0"]},
            {"id": "node_1", "label": "细胞膜", "type": "concept", "definition": "细胞的外层结构", "source_chunks": ["chunk_1"]},
            {"id": "node_2", "label": "磷脂双层", "type": "concept", "definition": "细胞膜的基本结构", "source_chunks": ["chunk_0"]},
            {"id": "node_3", "label": "膜蛋白", "type": "concept", "definition": "嵌入细胞膜的蛋白质", "source_chunks": ["chunk_2"]}
        ],
        "edges": [
            {"source": "node_0", "target": "node_2", "relation": "包含", "description": ""},
            {"source": "node_1", "target": "node_2", "relation": "包含", "description": ""},
            {"source": "node_0", "target": "node_3", "relation": "包含", "description": ""}
        ]
    }

    mock_deduplicated_graph = {
        "nodes": [
            {"id": "node_0", "label": "细胞膜", "type": "concept", "definition": "由磷脂双层构成的生物膜", "source_chunks": ["chunk_0", "chunk_1"]},
            {"id": "node_2", "label": "磷脂双层", "type": "concept", "definition": "细胞膜的基本结构", "source_chunks": ["chunk_0"]},
            {"id": "node_3", "label": "膜蛋白", "type": "concept", "definition": "嵌入细胞膜的蛋白质", "source_chunks": ["chunk_2"]}
        ],
        "edges": [
            {"source": "node_0", "target": "node_2", "relation": "包含", "description": ""},
            {"source": "node_0", "target": "node_3", "relation": "包含", "description": ""}
        ]
    }

    # Generate report
    generator = ReportGenerator()
    report_path = generator.generate_report(
        mock_chunks,
        mock_original_graph,
        mock_deduplicated_graph,
        job_id="test_001"
    )

    print(f"\n[OK] Report generated: {report_path}")

    # Read and display report preview
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        print(f"\n[INFO] Report preview (first 30 lines):")
        for line in lines[:30]:
            print(f"  {line}")

    # Check compression ratio
    if "压缩比" in content:
        print(f"\n[OK] Report contains compression ratio")
    if "整合后知识内容" in content:
        print(f"[OK] Report contains integrated knowledge content")
    if "教学完整性评估" in content:
        print(f"[OK] Report contains teaching completeness assessment")


if __name__ == "__main__":
    print("Testing report generation...\n")
    test_report_generation()
    print("\n[OK] Report generation tests completed")
