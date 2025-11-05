"""Fleet manager placeholder.

Minimal manager that provides basic API used in tests/docs.
"""
from typing import List, Dict


class FleetManager:
    def __init__(self):
        self.nodes: List[str] = []

    def add_node(self, node_id: str) -> None:
        if node_id not in self.nodes:
            self.nodes.append(node_id)

    def remove_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.nodes.remove(node_id)

    def list_nodes(self) -> List[str]:
        return list(self.nodes)
