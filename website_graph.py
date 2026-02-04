from typing import Dict, List, Tuple
import yaml
import numpy as np
from embedder import TextEmbedder


class WebsiteGraph:
    def __init__(self, scope: str):
        self.scope: str = scope
        self.summary: str = ""
        self.nodes: Dict[int, dict] = {}
        self.edges: Dict[int, dict] = {}
        self._next_id: int = 0
        self.text_embedder = TextEmbedder()

    def _get_next_id(self) -> int:
        self._next_id += 1
        return self._next_id

    def to_dict(self) -> dict:
        def filter_node(node):
            node_copy = node.copy()
            node_copy.pop("snapshot_embedding", None)
            node_copy.pop("snapshot", None)
            return node_copy
        return {
            "metadata": {
            "scope": self.scope,
            "summary": self.summary
            },
            "nodes": [filter_node(node) for node in self.nodes.values()],
            "edges": list(self.edges.values())
        }

    def to_yaml(self) -> str:
        data = self.to_dict()
        return yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    def add_node(self, url: str, title: str, snapshot: str) -> int:
        id = self._get_next_id()
        node = {
            "id": id,
            "url": url,
            "title": title,
            "snapshot": snapshot,
            "snapshot_hex": self.text_embedder.get_text_hex_prefix(snapshot),
            "snapshot_embedding": self.text_embedder.encode(snapshot),
            "desc": "",
            "features": [],
            "datas": []
        }
        self.nodes[id] = node
        return id

    def delete_node(self, id: int) -> None:
        if id in self.nodes:
            del self.nodes[id]
        for edge_id in [edge_id for edge_id, edge in self.edges.items() if edge["from"] == id or edge["to"] == id]:
            del self.edges[edge_id]

    def update_node(self, id: int, property: str, value: str | List[str]) -> None:
        if id in self.nodes:
            if property not in ['desc', 'features', 'datas']:
                raise ValueError("Can only update 'desc', 'features', or 'datas' properties.")
            self.nodes[id][property] = value

    def update_edge(self, from_id: int, to_id: int, operation: str) -> None:
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError("Both from_id and to_id must exist in nodes.")
        id = f"{from_id}->{to_id}"
        edge = {
            "from": from_id,
            "to": to_id,
            "operation": operation
        }
        self.edges[id] = edge

    def delete_edge(self, from_id: int, to_id: int) -> None:
        id = f"{from_id}->{to_id}"
        if id in self.edges:
            del self.edges[id]

    def compute_snapshot_similarity_matrix(self) -> Tuple[np.ndarray, List[int]]:
        if not self.nodes:
            return np.array([]), []
        node_ids = sorted(self.nodes.keys())
        embeddings = [self.nodes[node_id]["snapshot_embedding"] for node_id in node_ids]
        similarity_matrix = self.text_embedder.similarity_matrix(embeddings)
        return similarity_matrix, node_ids

    def similarity_matrix_to_table(self) -> str:
        similarity_matrix, node_ids = self.compute_snapshot_similarity_matrix()
        if len(node_ids) == 0:
            return "No nodes available"
        max_id_len = max(len(str(node_id)) for node_id in node_ids)
        col_width = max(max_id_len, 5)
        header = f"| {'Node':<{col_width}} |"
        for node_id in node_ids:
            header += f" {str(node_id):>{col_width}} |"
        separator = f"|{'-' * (col_width + 2)}|"
        for _ in node_ids:
            separator += f"{'-' * (col_width + 2)}|"
        rows = []
        for i, node_id in enumerate(node_ids):
            row = f"| {str(node_id):<{col_width}} |"
            for j in range(len(node_ids)):
                sim_value = similarity_matrix[i, j]
                row += f" {sim_value:>{col_width}.3f} |"
            rows.append(row)
        table = "\n".join([header, separator] + rows)
        return table

    def query_similarity_to_table(self, query: str) -> str:
        if not self.nodes:
            return "No nodes available"
        node_ids = sorted(self.nodes.keys())
        embeddings = [self.nodes[node_id]["snapshot_embedding"] for node_id in node_ids]
        similarities = self.text_embedder.similarity_to_many(query, embeddings)
        max_id_len = max(len(str(node_id)) for node_id in node_ids)
        id_width = max(max_id_len, 4)
        sim_width = 10
        header = f"| {'Node':^{id_width}} | {'Similarity':^{sim_width}} |"
        separator = f"|{'-' * (id_width + 2)}|{'-' * (sim_width + 2)}|"
        rows = []
        sorted_indices = np.argsort(similarities)[::-1]
        for idx in sorted_indices:
            node_id = node_ids[idx]
            sim_value = similarities[idx]
            row = f"| {str(node_id):^{id_width}} | {sim_value:^{sim_width}.4f} |"
            rows.append(row)
        table = "\n".join([header, separator] + rows)
        return table


if __name__ == "__main__":
    graph = WebsiteGraph(scope="example.com")
    node1_id = graph.add_node(
        url="http://example.com/page1",
        title="Page 1",
        snapshot="你好"
    )
    node2_id = graph.add_node(
        url="http://example.com/page2",
        title="Page 2",
        snapshot="你好"
    )
    node3_id = graph.add_node(
        url="http://example.com/page3",
        title="Page 3",
        snapshot="Hello world"
    )
    graph.update_edge(from_id=node1_id, to_id=node2_id, operation="link")
    print(graph.to_yaml())

    print("\n=== Similarity Matrix ===")
    print(graph.similarity_matrix_to_table())

    print("\n=== Query Similarity ===")
    print(graph.query_similarity_to_table("Test"))
