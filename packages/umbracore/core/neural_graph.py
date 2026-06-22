import json
from pathlib import Path
from datetime import datetime

class NeuralGraph:
    """
    🧠 Vespera Neural Graph: Structured, deeply queryable associative memory.
    """
    def __init__(self, db_path: str = "data/neural_graph.json"):
        self.db_path = Path(db_path)
        self.nodes = {}
        self.edges = []
        self._load()

    def _load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = data.get("edges", [])
            except Exception:
                pass

    def _save(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=2)

    def add_node(self, node_id: str, data: dict):
        self.nodes[node_id] = {
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def add_edge(self, source_id: str, target_id: str, relation: str):
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relation": relation,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def query_concept(self, concept: str):
        # Extremely basic associative query matching
        results = []
        for node_id, node_data in self.nodes.items():
            if concept.lower() in node_id.lower() or concept.lower() in str(node_data).lower():
                results.append((node_id, node_data))
        return results

neural_graph = NeuralGraph()
