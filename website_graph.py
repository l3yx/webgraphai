from typing import Dict, List
import yaml
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
            "snapshot_embedding": self.text_embedder._encode(snapshot),
            "desc": "",
            "features": "",
            "datas": ""
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


if __name__ == "__main__":
    graph = WebsiteGraph(scope="example.com")
    node1_id = graph.add_node(
        url="http://example.com/page1",
        title="Page 1",
        desc="This is page 1",
        snapshot="abcdef123456",
        features=["feature1", "feature2"],
        datas=["data1", "data2"]
    )
    node2_id = graph.add_node(
        url="http://example.com/page2",
        title="Page 2",
        desc="This is page 2",
        snapshot="123456abcdef",
        features=["feature3"],
        datas=["data3"]
    )
    graph.update_edge(from_id=node1_id, to_id=node2_id, operation="link")
    print(graph.to_yaml())
