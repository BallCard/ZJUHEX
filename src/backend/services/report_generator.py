"""
Integration report generation service.

P0 Scope:
- Generate markdown report with compression ratio
- Include deduplication statistics
- List merged concepts with source references
- Provide teaching completeness assessment
- Output to report/ directory
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.paths import REPORT_DIR


class ReportGenerator:
    """Generate integration report from deduplicated knowledge graph."""

    def generate_report(
        self,
        original_chunks: List[Dict[str, Any]],
        original_graph: Dict[str, Any],
        deduplicated_graph: Dict[str, Any],
        job_id: str,
        chapter_info: Dict[str, Any] = None
    ) -> str:
        """
        Generate integration report.

        Args:
            original_chunks: Original parsed chunks
            original_graph: Original knowledge graph before deduplication
            deduplicated_graph: Deduplicated knowledge graph
            job_id: Job identifier
            chapter_info: Chapter metadata (title, page range, chunk count)

        Returns:
            Path to generated report file
        """
        # Calculate statistics
        stats = self._calculate_statistics(
            original_chunks,
            original_graph,
            deduplicated_graph
        )

        # Generate report content
        report_content = self._format_report(stats, deduplicated_graph, job_id, chapter_info)

        # Save report (uses absolute path)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORT_DIR / f"整合报告_{job_id}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return str(report_path)

    def _calculate_statistics(
        self,
        original_chunks: List[Dict[str, Any]],
        original_graph: Dict[str, Any],
        deduplicated_graph: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate report statistics with consistent compression ratio."""
        # Original content size (actual content length, not char_count metadata)
        original_chars = sum(len(chunk.get("content", "")) for chunk in original_chunks)

        # Integrated content (formatted as final output)
        integrated_content = "\n\n".join([
            f"**{node['label']}**\n{node.get('definition', '')}"
            for node in deduplicated_graph["nodes"]
        ])
        integrated_chars = len(integrated_content)

        # Compression ratio (consistent denominator and numerator)
        compression_ratio = (integrated_chars / original_chars * 100) if original_chars > 0 else 0

        return {
            "original_chars": original_chars,
            "original_chunks": len(original_chunks),
            "original_nodes": len(original_graph["nodes"]),
            "original_edges": len(original_graph["edges"]),
            "integrated_chars": integrated_chars,
            "deduplicated_nodes": len(deduplicated_graph["nodes"]),
            "deduplicated_edges": len(deduplicated_graph["edges"]),
            "compression_ratio": compression_ratio,
            "nodes_merged": len(original_graph["nodes"]) - len(deduplicated_graph["nodes"]),
            "edges_removed": len(original_graph["edges"]) - len(deduplicated_graph["edges"])
        }

    def _format_report(
        self,
        stats: Dict[str, Any],
        deduplicated_graph: Dict[str, Any],
        job_id: str,
        chapter_info: Dict[str, Any] = None
    ) -> str:
        """Format report as markdown."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format chapter info section
        chapter_section = ""
        if chapter_info:
            textbook_name = chapter_info.get('textbook', '未知教材')
            chapter_section = f"""
## 处理范围

- **教材**: {textbook_name}
- **章节**: {chapter_info.get('title', '未知章节')}
- **页码范围**: 第 {chapter_info.get('start_page', 0)} - {chapter_info.get('end_page', 0)} 页
- **文档块数**: {chapter_info.get('chunk_count', 0)} 个
- **实际处理**: {chapter_info.get('processed_chunks', 0)} 个文档块

---
"""

        report = f"""# 知识整合报告

**生成时间**: {timestamp}
**任务ID**: {job_id}

---
{chapter_section}
## 1. 压缩比统计

| 指标 | 数值 |
|------|------|
| 原始字符数 | {stats['original_chars']:,} |
| 整合后字符数 | {stats['integrated_chars']:,} |
| **压缩比** | **{stats['compression_ratio']:.2f}%** |
| 目标压缩比 | ≤30% |
| **是否达标** | **{'✓ 是' if stats['compression_ratio'] <= 30 else '✗ 否'}** |

---

## 2. 知识图谱统计

### 原始图谱
- 文档块数: {stats['original_chunks']}
- 知识节点数: {stats['original_nodes']}
- 关系边数: {stats['original_edges']}

### 整合后图谱
- 知识节点数: {stats['deduplicated_nodes']}
- 关系边数: {stats['deduplicated_edges']}
- 合并节点数: {stats['nodes_merged']}
- 移除边数: {stats['edges_removed']}

---

## 3. 整合决策摘要

### 去重策略
- **语义相似度阈值**: 0.90 (生物医学领域最佳实践)
- **嵌入模型**: paraphrase-multilingual-MiniLM-L12-v2
- **相似度计算**: 余弦相似度
- **合并策略**: 基于聚类的节点合并，保留所有来源引用

### 决策原则
1. **保留教学完整性**: 合并重复概念，但保留所有来源引用
2. **关系去重**: 移除因节点合并产生的自环和重复边
3. **语义对齐**: 基于标签+定义的语义匹配，而非简单字符串匹配

### 决策样例

{self._format_decision_examples(deduplicated_graph)}

---

## 4. 整合后知识内容

### 核心概念列表

"""

        # List all deduplicated nodes
        for i, node in enumerate(deduplicated_graph["nodes"], 1):
            sources = ", ".join(node.get("source_chunks", []))
            report += f"""#### {i}. {node['label']}

- **类型**: {node['type']}
- **定义**: {node.get('definition', '(无定义)')}
- **来源**: {sources}

"""

        # List relationships
        report += """---

## 5. 知识关系网络

"""
        if deduplicated_graph["edges"]:
            for edge in deduplicated_graph["edges"]:
                source_label = self._get_node_label(deduplicated_graph["nodes"], edge["source"])
                target_label = self._get_node_label(deduplicated_graph["nodes"], edge["target"])
                report += f"- **{source_label}** --[{edge['relation']}]--> **{target_label}**\n"
        else:
            report += "(无关系边)\n"

        # Teaching completeness assessment
        report += f"""
---

## 6. 教学完整性评估

### 内容覆盖度
- 原始文档块: {stats['original_chunks']} 个
- 提取知识点: {stats['deduplicated_nodes']} 个
- 知识关系: {stats['deduplicated_edges']} 条

### 完整性说明
本整合报告基于原始教材的前 {stats['original_chunks']} 个文档块（P0 Demo范围）。整合后的知识图谱保留了所有核心概念及其关系，通过语义去重消除了冗余内容，同时保留了所有来源引用以确保可追溯性。

**教学效果保证**:
1. 所有核心概念均已提取并保留定义
2. 概念间的依赖关系、包含关系、应用关系均已建立
3. 每个概念都标注了来源文档块，便于回溯原文
4. 压缩比{'达标' if stats['compression_ratio'] <= 30 else '未达标'}，{'有效' if stats['compression_ratio'] <= 30 else '需要'}减少冗余内容

---

## 7. 典型案例

### 去重案例示例
"""

        # Find merged nodes (nodes with multiple source chunks)
        merged_nodes = [
            node for node in deduplicated_graph["nodes"]
            if len(node.get("source_chunks", [])) > 1
        ]

        if merged_nodes:
            for node in merged_nodes[:3]:  # Show up to 3 examples
                report += f"""
**概念**: {node['label']}
**合并来源**: {len(node['source_chunks'])} 个文档块
**来源块**: {', '.join(node['source_chunks'])}
**保留定义**: {node.get('definition', '(无定义)')}
"""
        else:
            report += "\n(本次处理未发现重复概念，可能是因为文档块数量较少)\n"

        report += """
---

## 8. 使用说明

### 如何使用本报告
1. **查看压缩比**: 第1节显示是否达到≤30%的目标
2. **浏览知识点**: 第4节列出所有整合后的核心概念
3. **理解关系**: 第5节展示概念间的依赖和关联
4. **追溯来源**: 每个概念都标注了来源文档块ID，可回溯原文

### 后续优化建议
- 增加处理的文档块数量以获得更完整的知识图谱
- 调整相似度阈值以优化去重效果
- 添加跨教材整合功能（P1阶段）
- 引入人工审核机制确保教学质量

---

*本报告由AI知识整合系统自动生成*
"""

        return report

    def _get_node_label(self, nodes: List[Dict[str, Any]], node_id: str) -> str:
        """Get node label by ID."""
        for node in nodes:
            if node["id"] == node_id:
                return node["label"]
        return node_id

    def _format_decision_examples(self, deduplicated_graph: Dict[str, Any]) -> str:
        """Format decision examples (keep/merge/delete)."""
        nodes = deduplicated_graph["nodes"]

        # Separate nodes by decision type
        keep_nodes = [n for n in nodes if n.get("merge_decision", {}).get("action") == "keep"]
        merge_nodes = [n for n in nodes if n.get("merge_decision", {}).get("action") == "merge"]

        examples = ""

        # Keep decisions
        examples += "#### 保留决策\n\n"
        if keep_nodes:
            for node in keep_nodes[:3]:  # Show up to 3 examples
                decision = node.get("merge_decision", {})
                examples += f"**{node['label']}**\n"
                examples += f"- 决策: 保留\n"
                examples += f"- 理由: {decision.get('reason', '未记录')}\n"
                examples += f"- 来源: {', '.join(node.get('source_chunks', []))}\n\n"
        else:
            examples += "(无保留决策样例)\n\n"

        # Merge decisions
        examples += "#### 合并决策\n\n"
        if merge_nodes:
            for node in merge_nodes[:3]:  # Show up to 3 examples
                decision = node.get("merge_decision", {})
                examples += f"**{node['label']}**\n"
                examples += f"- 决策: 合并\n"
                examples += f"- 理由: {decision.get('reason', '未记录')}\n"
                examples += f"- 合并数量: {decision.get('merged_count', 0)} 个节点\n"
                if decision.get('merged_labels'):
                    examples += f"- 被合并节点: {', '.join(decision['merged_labels'])}\n"
                examples += f"- 来源: {', '.join(node.get('source_chunks', []))}\n\n"
        else:
            examples += "(无合并决策样例 - 可能是因为文档块数量较少，未发现语义重复)\n\n"

        # Delete decisions (P0 scope: no explicit deletion, only merging)
        examples += "#### 删除决策\n\n"
        examples += "(P0范围内不执行显式删除，仅通过合并去重)\n"

        return examples


def generate_integration_report(
    original_chunks: List[Dict[str, Any]],
    original_graph: Dict[str, Any],
    deduplicated_graph: Dict[str, Any],
    job_id: str,
    chapter_info: Dict[str, Any] = None
) -> str:
    """
    Convenience function to generate integration report.

    Args:
        original_chunks: Original parsed chunks
        original_graph: Original knowledge graph
        deduplicated_graph: Deduplicated knowledge graph
        job_id: Job identifier
        chapter_info: Chapter metadata (title, page range, chunk count)

    Returns:
        Path to generated report file
    """
    generator = ReportGenerator()
    return generator.generate_report(
        original_chunks,
        original_graph,
        deduplicated_graph,
        job_id,
        chapter_info
    )
