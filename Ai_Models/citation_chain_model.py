# Ai_Models/citation_chain_model.py
from __future__ import annotations

from typing import List, Dict, Any
from Utils.graph_tools import build_directed_graph, topological_sort

class CitationChainModel:
    """
    Builds and analyzes citation chains using graph tools.
    Future: validate chain integrity against known databases.
    """
    def build_chain(self, citations: List[Dict[str, str]]) -> Dict[str, Any]:
        # Example citation format: {"paper_id": "A", "cites": "B"}
        edges = [(c["paper_id"], c["cites"]) for c in citations if "cites" in c]
        graph = build_directed_graph(edges)
        topo_order = topological_sort(graph)

        return {
            "graph": graph,
            "topological_order": topo_order,
            "chain_length": len(topo_order),
            "has_cycles": len(topo_order) < len(graph),
        }