"""
Cross-textbook knowledge integration service.

P2 Scope:
- Multi-textbook upload and processing
- Cross-textbook semantic alignment
- Deduplication across multiple textbooks
- Contribution analysis per textbook
- Cross-textbook integration report
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class CrossTextbookIntegrator:
    """Integrate knowledge graphs from multiple textbooks."""

    def __init__(self, similarity_threshold: Optional[float] = None):
        """
        Initialize cross-textbook integrator.

        Args:
            similarity_threshold: Cosine similarity threshold (defaults to settings)
        """
        self.similarity_threshold = similarity_threshold or settings.similarity_threshold

        logger.info(f"Loading sentence-transformers model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        logger.info(
            f"Model loaded successfully. Using similarity threshold: {self.similarity_threshold}"
        )

    def align_knowledge_graphs(self, graphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Align and integrate knowledge graphs from multiple textbooks.

        Args:
            graphs: List of knowledge graphs from different textbooks
                    Each graph should have 'nodes', 'edges', and 'metadata' with 'textbook_name'

        Returns:
            Aligned and integrated knowledge graph
        """
        if not graphs:
            logger.warning("No graphs provided for alignment")
            return {"nodes": [], "edges": [], "metadata": {}}

        if len(graphs) == 1:
            logger.info("Single textbook provided, no cross-textbook integration needed")
            return graphs[0]

        logger.info(f"Aligning {len(graphs)} knowledge graphs")

        # Step 1: Merge all nodes with textbook metadata
        all_nodes = []
        for i, graph in enumerate(graphs):
            textbook_name = graph.get('metadata', {}).get('textbook_name', f'教材{i+1}')
            for node in graph.get('nodes', []):
                node_copy = node.copy()
                node_copy['textbook_id'] = i
                node_copy['textbook_name'] = textbook_name
                # Ensure source_chunks is a list
                if 'source_chunks' not in node_copy:
                    node_copy['source_chunks'] = []
                all_nodes.append(node_copy)

        logger.info(f"Total nodes from {len(graphs)} textbooks: {len(all_nodes)}")

        # Step 2: Cross-textbook semantic deduplication
        merged_nodes = self._cross_textbook_dedup(all_nodes)

        logger.info(f"After cross-textbook deduplication: {len(merged_nodes)} nodes")

        # Step 3: Merge edges from all textbooks
        merged_edges = self._merge_edges(graphs, merged_nodes)

        logger.info(f"Total edges after merging: {len(merged_edges)}")

        # Step 4: Calculate metadata
        metadata = {
            'textbook_count': len(graphs),
            'original_node_count': len(all_nodes),
            'merged_node_count': len(merged_nodes),
            'total_edges': len(merged_edges),
            'deduplication_ratio': len(merged_nodes) / len(all_nodes) if all_nodes else 1.0,
            'textbook_names': [g.get('metadata', {}).get('textbook_name', f'教材{i+1}')
                              for i, g in enumerate(graphs)]
        }

        return {
            'nodes': merged_nodes,
            'edges': merged_edges,
            'metadata': metadata
        }

    def _cross_textbook_dedup(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate nodes across textbooks using semantic similarity.

        Args:
            nodes: All nodes from all textbooks

        Returns:
            Merged nodes with source tracking
        """
        if not nodes:
            logger.warning("No nodes provided for cross-textbook deduplication")
            return []

        logger.info(f"Starting cross-textbook deduplication of {len(nodes)} nodes")

        # Compute embeddings for all nodes
        node_texts = [self._get_node_text(node) for node in nodes]
        embeddings = self.model.encode(node_texts, convert_to_numpy=True)

        # Compute cosine similarity matrix
        similarity_matrix = np.dot(embeddings, embeddings.T)
        norms = np.linalg.norm(embeddings, axis=1)
        similarity_matrix = similarity_matrix / (norms[:, None] * norms[None, :] + 1e-8)

        # Find duplicate clusters
        visited = set()
        merged = []

        for i in range(len(nodes)):
            if i in visited:
                continue

            # Find all similar nodes
            similar_indices = []
            for j in range(len(nodes)):
                if j not in visited and similarity_matrix[i, j] >= self.similarity_threshold:
                    similar_indices.append(j)

            # Merge similar nodes
            if similar_indices:
                merged_node = self._merge_similar_nodes([nodes[j] for j in similar_indices])
                merged.append(merged_node)

                # Mark as visited
                visited.update(similar_indices)

        logger.info(f"Cross-textbook deduplication created {len(merged)} merged nodes")
        return merged

    def _merge_similar_nodes(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge semantically similar nodes from different textbooks.

        Args:
            nodes: List of similar nodes to merge

        Returns:
            Merged node with all source information
        """
        # Use first node as base
        base_node = nodes[0].copy()

        # Collect all sources
        sources = []
        textbook_ids = set()
        all_source_chunks = []

        for node in nodes:
            textbook_id = node.get('textbook_id', 0)
            textbook_name = node.get('textbook_name', '未知教材')

            textbook_ids.add(textbook_id)

            # Collect source chunks
            source_chunks = node.get('source_chunks', [])
            all_source_chunks.extend(source_chunks)

            sources.append({
                'textbook_id': textbook_id,
                'textbook_name': textbook_name,
                'label': node.get('label', ''),
                'definition': node.get('definition', ''),
                'source_chunks': source_chunks
            })

        # Update merged node
        base_node['sources'] = sources
        base_node['source_count'] = len(sources)
        base_node['textbook_count'] = len(textbook_ids)
        base_node['source_chunks'] = list(set(all_source_chunks))  # Remove duplicates

        # Add merge decision
        if len(nodes) > 1:
            base_node['merge_decision'] = {
                'action': 'cross_textbook_merge',
                'reason': f'Merged {len(nodes)} similar concepts from {len(textbook_ids)} textbook(s)',
                'merged_count': len(nodes) - 1,
                'textbook_ids': list(textbook_ids)
            }
        else:
            base_node['merge_decision'] = {
                'action': 'keep',
                'reason': 'No cross-textbook duplicates found',
                'merged_count': 0
            }

        return base_node

    def _get_node_text(self, node: Dict[str, Any]) -> str:
        """Get text representation of node for embedding."""
        text = node.get('label', '')
        if node.get('definition'):
            text += ' ' + node['definition']
        return text

    def _merge_edges(self, graphs: List[Dict[str, Any]], merged_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge edges from all textbooks, updating node references.

        Args:
            graphs: Original graphs
            merged_nodes: Merged nodes after deduplication

        Returns:
            Merged edges
        """
        # Create label to merged node ID mapping
        label_to_id = {}
        for node in merged_nodes:
            label = node.get('label', '')
            if label:
                label_to_id[label] = node.get('id', '')

        # Collect all edges
        all_edges = []
        for graph in graphs:
            for edge in graph.get('edges', []):
                source_label = self._get_node_label_by_id(graph, edge.get('source', ''))
                target_label = self._get_node_label_by_id(graph, edge.get('target', ''))

                # Map to merged node IDs
                new_source = label_to_id.get(source_label)
                new_target = label_to_id.get(target_label)

                if new_source and new_target and new_source != new_target:
                    all_edges.append({
                        'source': new_source,
                        'target': new_target,
                        'relation': edge.get('relation', ''),
                        'description': edge.get('description', '')
                    })

        # Remove duplicate edges
        unique_edges = []
        seen = set()
        for edge in all_edges:
            edge_key = (edge['source'], edge['target'], edge['relation'])
            if edge_key not in seen:
                seen.add(edge_key)
                unique_edges.append(edge)

        return unique_edges

    def _get_node_label_by_id(self, graph: Dict[str, Any], node_id: str) -> str:
        """Get node label by ID from graph."""
        for node in graph.get('nodes', []):
            if node.get('id') == node_id:
                return node.get('label', '')
        return ''

    def generate_cross_textbook_report(self, aligned_graph: Dict[str, Any], original_graphs: List[Dict[str, Any]]) -> str:
        """
        Generate cross-textbook integration report.

        Args:
            aligned_graph: Aligned knowledge graph
            original_graphs: Original graphs from each textbook

        Returns:
            Markdown report content
        """
        metadata = aligned_graph.get('metadata', {})
        nodes = aligned_graph.get('nodes', [])

        # Calculate contributions per textbook
        contributions = self._calculate_contributions(nodes, original_graphs)

        # Identify cross-textbook duplicates
        cross_textbook_duplicates = [
            node for node in nodes
            if node.get('textbook_count', 1) > 1
        ]

        # Identify unique contributions per textbook
        unique_contributions = self._identify_unique_contributions(nodes)

        # Generate report
        report = f"""# 跨教材知识整合报告

## 整合概览

- **教材数量**: {metadata.get('textbook_count', 0)}
- **原始知识点总数**: {metadata.get('original_node_count', 0)}
- **整合后知识点数**: {metadata.get('merged_node_count', 0)}
- **去重率**: {(1 - metadata.get('deduplication_ratio', 1.0)) * 100:.1f}%
- **跨教材重复知识点**: {len(cross_textbook_duplicates)}

## 各教材贡献度

{self._format_contributions(contributions)}

## 跨教材重复知识点（前10个）

{self._format_duplicates(cross_textbook_duplicates[:10])}

## 各教材独有知识点

{self._format_unique_contributions(unique_contributions)}

## 知识互补性分析

{self._analyze_complementarity(nodes, original_graphs)}
"""
        return report

    def _calculate_contributions(self, nodes: List[Dict[str, Any]], original_graphs: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Calculate contribution statistics per textbook."""
        contributions = {}

        for i, graph in enumerate(original_graphs):
            textbook_name = graph.get('metadata', {}).get('textbook_name', f'教材{i+1}')

            # Count nodes from this textbook
            nodes_from_textbook = sum(
                1 for node in nodes
                if any(source.get('textbook_id') == i for source in node.get('sources', []))
            )

            # Count unique nodes (only in this textbook)
            unique_nodes = sum(
                1 for node in nodes
                if node.get('textbook_count', 1) == 1 and
                   any(source.get('textbook_id') == i for source in node.get('sources', []))
            )

            contributions[i] = {
                'textbook_name': textbook_name,
                'total_nodes': nodes_from_textbook,
                'unique_nodes': unique_nodes,
                'shared_nodes': nodes_from_textbook - unique_nodes
            }

        return contributions

    def _identify_unique_contributions(self, nodes: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Identify unique knowledge points per textbook."""
        unique_by_textbook = {}

        for node in nodes:
            if node.get('textbook_count', 1) == 1:
                sources = node.get('sources', [])
                if sources:
                    textbook_id = sources[0].get('textbook_id', 0)
                    if textbook_id not in unique_by_textbook:
                        unique_by_textbook[textbook_id] = []
                    unique_by_textbook[textbook_id].append(node)

        return unique_by_textbook

    def _format_contributions(self, contributions: Dict[int, Dict[str, Any]]) -> str:
        """Format contribution statistics as markdown table."""
        lines = ["| 教材 | 贡献知识点 | 独有知识点 | 共享知识点 |",
                 "|------|-----------|-----------|-----------|"]

        for textbook_id in sorted(contributions.keys()):
            contrib = contributions[textbook_id]
            lines.append(
                f"| {contrib['textbook_name']} | "
                f"{contrib['total_nodes']} | "
                f"{contrib['unique_nodes']} | "
                f"{contrib['shared_nodes']} |"
            )

        return '\n'.join(lines)

    def _format_duplicates(self, duplicates: List[Dict[str, Any]]) -> str:
        """Format cross-textbook duplicates as markdown list."""
        if not duplicates:
            return "无跨教材重复知识点"

        lines = []
        for i, node in enumerate(duplicates, 1):
            label = node.get('label', '未知')
            sources = node.get('sources', [])
            textbook_names = [s.get('textbook_name', '未知') for s in sources]

            lines.append(f"{i}. **{label}**")
            lines.append(f"   - 出现在: {', '.join(textbook_names)}")
            lines.append(f"   - 定义: {node.get('definition', '无')[:100]}...")
            lines.append("")

        return '\n'.join(lines)

    def _format_unique_contributions(self, unique_contributions: Dict[int, List[Dict[str, Any]]]) -> str:
        """Format unique contributions per textbook."""
        if not unique_contributions:
            return "所有知识点均为跨教材共享"

        lines = []
        for textbook_id in sorted(unique_contributions.keys()):
            nodes = unique_contributions[textbook_id]
            if nodes:
                textbook_name = nodes[0].get('sources', [{}])[0].get('textbook_name', f'教材{textbook_id+1}')
                lines.append(f"### {textbook_name} ({len(nodes)}个独有知识点)")
                lines.append("")

                for node in nodes[:5]:  # Show first 5
                    lines.append(f"- **{node.get('label', '未知')}**: {node.get('definition', '无')[:80]}...")

                if len(nodes) > 5:
                    lines.append(f"- ... 还有 {len(nodes) - 5} 个")
                lines.append("")

        return '\n'.join(lines)

    def _analyze_complementarity(self, nodes: List[Dict[str, Any]], original_graphs: List[Dict[str, Any]]) -> str:
        """Analyze knowledge complementarity across textbooks."""
        total_nodes = len(nodes)
        shared_nodes = sum(1 for node in nodes if node.get('textbook_count', 1) > 1)
        unique_nodes = total_nodes - shared_nodes

        complementarity_ratio = (unique_nodes / total_nodes * 100) if total_nodes > 0 else 0

        analysis = f"""
- **知识重叠度**: {(shared_nodes / total_nodes * 100):.1f}% ({shared_nodes}/{total_nodes})
- **知识互补度**: {complementarity_ratio:.1f}% ({unique_nodes}/{total_nodes})

"""

        if complementarity_ratio > 50:
            analysis += "**结论**: 各教材知识互补性强，整合价值高。"
        elif complementarity_ratio > 30:
            analysis += "**结论**: 各教材有一定互补性，整合可减少冗余。"
        else:
            analysis += "**结论**: 各教材知识重叠度高，整合可显著压缩内容。"

        return analysis
