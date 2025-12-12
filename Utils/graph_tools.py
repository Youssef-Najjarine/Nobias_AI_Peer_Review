# Utils/graph_tools.py

from typing import Dict, List, Set, Tuple, Iterable


def build_directed_graph(edges: Iterable[Tuple[str, str]]) -> Dict[str, Set[str]]:
    """
    Build a simple adjacency-list representation of a directed graph.

    Example:
        edges = [("A", "B"), ("A", "C"), ("B", "C")]
        graph = {"A": {"B", "C"}, "B": {"C"}, "C": set()}

    This can be used, for example, to represent a citation graph
    where nodes are paper IDs and edges are (paper -> cited_paper).
    """
    graph: Dict[str, Set[str]] = {}
    for src, dst in edges:
        if src not in graph:
            graph[src] = set()
        if dst not in graph:
            graph[dst] = set()
        graph[src].add(dst)
    return graph


def reverse_graph(graph: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Reverse all edges in a directed graph.

    Example:
        {"A": {"B", "C"}, "B": {"C"}, "C": set()}
        -> {"A": set(), "B": {"A"}, "C": {"A", "B"}}
    """
    reversed_graph: Dict[str, Set[str]] = {node: set() for node in graph}
    for src, neighbors in graph.items():
        for dst in neighbors:
            reversed_graph.setdefault(dst, set()).add(src)
    return reversed_graph


def depth_first_search(graph: Dict[str, Set[str]], start: str) -> List[str]:
    """
    Simple DFS traversal from a starting node.
    Returns the list of visited nodes in traversal order.
    """
    visited: Set[str] = set()
    order: List[str] = []

    def _dfs(node: str):
        if node in visited:
            return
        visited.add(node)
        order.append(node)
        for neighbor in sorted(graph.get(node, [])):
            _dfs(neighbor)

    if start in graph:
        _dfs(start)
    return order


def topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    """
    Perform a topological sort on a DAG represented as an adjacency list.
    If cycles are present, nodes in a cycle may appear in arbitrary order,
    but the function will still return a linearization.

    Useful for ordering dependencies, e.g., a chain of citations
    or staged computations.
    """
    in_degree: Dict[str, int] = {node: 0 for node in graph}
    for src, neighbors in graph.items():
        for dst in neighbors:
            in_degree[dst] = in_degree.get(dst, 0) + 1
            if dst not in graph:
                graph[dst] = set()

    # Kahn's algorithm
    queue: List[str] = [node for node, deg in in_degree.items() if deg == 0]
    result: List[str] = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If some nodes weren't processed (cycle), append them
    if len(result) < len(graph):
        for node in graph:
            if node not in result:
                result.append(node)

    return result
