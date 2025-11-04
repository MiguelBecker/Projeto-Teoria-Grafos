from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class EdgeMeta:
    logradouro: str | None = None
    observacao: str | None = None

class Graph:
    def __init__(self):
        self._adj: Dict[str, List[Tuple[str, float, EdgeMeta]]] = {}

    def add_node(self, u: str):
        if u not in self._adj:
            self._adj[u] = []

    def add_edge(self, u: str, v: str, w: float = 1.0, meta: EdgeMeta | None = None):
        if meta is None:
            meta = EdgeMeta()
        self.add_node(u)
        self.add_node(v)
        self._adj[u].append((v, w, meta))
        self._adj[v].append((u, w, meta))

    def neighbors(self, u: str):
        return self._adj.get(u, [])

    def nodes(self):
        return list(self._adj.keys())

    def edges(self):
        seen = set()
        res = []
        for u, lst in self._adj.items():
            for v, w, meta in lst:
                key = tuple(sorted((u, v)))
                if key in seen:
                    continue
                seen.add(key)
                res.append((u, v, w, meta))
        return res

    def degree(self, u: str) -> int:
        return len(self._adj.get(u, []))

    def order(self) -> int:
        return len(self._adj)

    def size(self) -> int:
        return sum(len(v) for v in self._adj.values()) // 2
