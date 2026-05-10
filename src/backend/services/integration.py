"""
Knowledge deduplication and integration service.

P0 Scope:
- Within-textbook deduplication (single textbook demo)
- Semantic similarity using sentence-transformers
- Cosine similarity threshold 0.90 (biomedical domain)
- Merge duplicate nodes, preserve all source references
- Output deduplicated graph
"""

import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer


class KnowledgeIntegrator:
    """Deduplicate and integrate knowledge graph nodes."""

    def __init__(self, similarity_threshold: float = 0.90):
        """
        Initialize integrator with embedding model.

        Args:
            similarity_threshold: Cosine similarity threshold for deduplication (0.90 for biomedical)
        """
        self.similarity_threshold = similarity_threshold
        # Load multilingual model for Chinese text
        print("[INFO] Loading sentence-transformers model...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("[INFO] Model loaded")

    def deduplicate_graph(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deduplicate knowledge graph nodes based on semantic similarity.

        Args:
            graph: Knowledge graph with nodes and edges

        Returns:
            Deduplicated graph with merged nodes
        """
        nodes = graph["nodes"]
        edges = graph["edges"]

        if not nodes:
            return graph

        # Compute embeddings for all nodes
        node_texts = [self._get_node_text(node) for node in nodes]
        embeddings = self.model.encode(node_texts, convert_to_numpy=True)

        # Find duplicate clusters
        duplicate_clusters = self._find_duplicates(nodes, embeddings)

        # Merge duplicates
        merged_nodes = self._merge_nodes(nodes, duplicate_clusters)

        # Update edges with new node IDs
        node_id_mapping = self._create_id_mapping(nodes, duplicate_clusters)
        updated_edges = self._update_edges(edges, node_id_mapping)

        return {
            "nodes": merged_nodes,
            "edges": updated_edges,
            "metadata": {
                "total_nodes": len(merged_nodes),
                "total_edges": len(updated_edges),
                "original_nodes": len(nodes),
                "deduplication_ratio": len(merged_nodes) / len(nodes) if nodes else 1.0
            }
        }

    def _get_node_text(self, node: Dict[str, Any]) -> str:
        """Get text representation of node for embedding."""
        # Combine label and definition for better semantic matching
        text = node["label"]
        if node.get("definition"):
            text += " " + node["definition"]
        return text

    def _find_duplicates(self, nodes: List[Dict[str, Any]], embeddings: np.ndarray) -> List[List[int]]:
        """
        Find duplicate node clusters using cosine similarity.

        Args:
            nodes: List of nodes
            embeddings: Node embeddings

        Returns:
            List of duplicate clusters (each cluster is list of node indices)
        """
        n = len(nodes)
        visited = set()
        clusters = []

        # Compute cosine similarity matrix
        similarity_matrix = np.dot(embeddings, embeddings.T)
        norms = np.linalg.norm(embeddings, axis=1)
        similarity_matrix = similarity_matrix / (norms[:, None] * norms[None, :])

        for i in range(n):
            if i in visited:
                continue

            # Find all nodes similar to node i
            cluster = [i]
            visited.add(i)

            for j in range(i + 1, n):
                if j in visited:
                    continue

                if similarity_matrix[i, j] >= self.similarity_threshold:
                    cluster.append(j)
                    visited.add(j)

            clusters.append(cluster)

        return clusters

    def _merge_nodes(self, nodes: List[Dict[str, Any]], clusters: List[List[int]]) -> List[Dict[str, Any]]:
        """
        Merge duplicate nodes in each cluster.

        Args:
            nodes: Original nodes
            clusters: Duplicate clusters

        Returns:
            Merged nodes with decision metadata
        """
        merged_nodes = []

        for cluster in clusters:
            if len(cluster) == 1:
                # No duplicates, keep as-is
                node = nodes[cluster[0]].copy()
                node["merge_decision"] = {
                    "action": "keep",
                    "reason": "No semantic duplicates found (similarity < 0.90)",
                    "merged_count": 0
                }
                merged_nodes.append(node)
            else:
                # Merge duplicates
                representative = nodes[cluster[0]]
                merged_node = {
                    "id": representative["id"],
                    "label": representative["label"],
                    "type": representative["type"],
                    "definition": representative["definition"],
                    "source_chunks": [],
                    "merge_decision": {
                        "action": "merge",
                        "reason": f"Merged {len(cluster)} semantically similar nodes (similarity >= 0.90)",
                        "merged_count": len(cluster) - 1,
                        "merged_labels": [nodes[idx]["label"] for idx in cluster[1:]]
                    }
                }

                # Collect all source chunks from duplicates
                for idx in cluster:
                    node = nodes[idx]
                    merged_node["source_chunks"].extend(node.get("source_chunks", []))

                # Remove duplicate source chunks
                merged_node["source_chunks"] = list(set(merged_node["source_chunks"]))

                merged_nodes.append(merged_node)

        return merged_nodes

    def _create_id_mapping(self, nodes: List[Dict[str, Any]], clusters: List[List[int]]) -> Dict[str, str]:
        """
        Create mapping from old node IDs to new node IDs after merging.

        Args:
            nodes: Original nodes
            clusters: Duplicate clusters

        Returns:
            Mapping {old_id: new_id}
        """
        mapping = {}

        for cluster in clusters:
            representative_id = nodes[cluster[0]]["id"]
            for idx in cluster:
                old_id = nodes[idx]["id"]
                mapping[old_id] = representative_id

        return mapping

    def _update_edges(self, edges: List[Dict[str, Any]], id_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Update edge node IDs after merging.

        Args:
            edges: Original edges
            id_mapping: Node ID mapping

        Returns:
            Updated edges with deduplicated self-loops removed
        """
        updated_edges = []

        for edge in edges:
            new_source = id_mapping.get(edge["source"], edge["source"])
            new_target = id_mapping.get(edge["target"], edge["target"])

            # Skip self-loops created by merging
            if new_source == new_target:
                continue

            updated_edges.append({
                "source": new_source,
                "target": new_target,
                "relation": edge["relation"],
                "description": edge.get("description", "")
            })

        # Remove duplicate edges
        unique_edges = []
        seen = set()

        for edge in updated_edges:
            edge_key = (edge["source"], edge["target"], edge["relation"])
            if edge_key not in seen:
                seen.add(edge_key)
                unique_edges.append(edge)

        return unique_edges


def deduplicate_knowledge_graph(graph: Dict[str, Any], similarity_threshold: float = 0.90) -> Dict[str, Any]:
    """
    Convenience function to deduplicate knowledge graph.

    Args:
        graph: Knowledge graph
        similarity_threshold: Similarity threshold for deduplication

    Returns:
        Deduplicated graph
    """
    integrator = KnowledgeIntegrator(similarity_threshold)
    return integrator.deduplicate_graph(graph)
