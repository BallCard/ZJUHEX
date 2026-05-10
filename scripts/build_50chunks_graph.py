"""
Build knowledge graph from 50 chunks locally.
"""
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

from services.parser import DocumentParser
from services.knowledge_graph import KnowledgeGraphBuilder

def main():
    print("=== 构建50-chunk知识图谱 ===\n")

    # Parse document
    print("1. 解析文档...")
    parser = DocumentParser()
    pdf_path = Path("textbooks/03_生理学.pdf")
    chunks = parser.parse_pdf(str(pdf_path))
    print(f"   解析完成: {len(chunks)} chunks\n")

    # Build graph with 50 chunks
    print("2. 构建知识图谱 (50 chunks)...")
    builder = KnowledgeGraphBuilder()
    graph = builder.build_graph(chunks, max_chunks=50)

    print(f"   图谱构建完成:")
    print(f"   - 节点数: {len(graph['nodes'])}")
    print(f"   - 边数: {len(graph['edges'])}\n")

    # Convert to Cytoscape format
    print("3. 转换为Cytoscape格式...")
    cytoscape_data = []

    for node in graph['nodes']:
        cytoscape_data.append({
            "data": {
                "id": node['id'],
                "label": node['label'],
                "category": node.get('type', 'concept'),
                "definition": node.get('definition', ''),
                "textbook": "03_生理学.pdf",
                "source_page": node.get('source_page', 0),
                "source_chunk": node.get('source_chunks', [''])[0] if node.get('source_chunks') else '',
                "neighbors": []
            }
        })

    for edge in graph['edges']:
        cytoscape_data.append({
            "data": {
                "id": f"edge_{edge['source']}_{edge['target']}",
                "source": edge['source'],
                "target": edge['target'],
                "relationship": edge.get('relation', 'related_to')
            }
        })

    # Save to file
    output_path = Path("graph_50chunks.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cytoscape_data, f, ensure_ascii=False, indent=2)

    print(f"   已保存到: {output_path}\n")
    print("=== 完成 ===")

if __name__ == "__main__":
    main()
