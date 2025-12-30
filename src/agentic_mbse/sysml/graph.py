"""Graph algorithm utilities for dependency analysis.

This module provides functions for analyzing directed graphs represented
as adjacency lists, including cycle detection and topological sorting.

Graph Semantics:
    graph[A] = [B, C] means "A depends on B and C"
    i.e., A cannot be computed until B and C are available
    This is the OPPOSITE of "A is imported by B and C"
"""

from collections import defaultdict, deque


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect all cycles in a directed graph.

    Uses depth-first search with recursion stack to find back edges
    that indicate cycles.

    Args:
        graph: Adjacency list where graph[node] = [dependencies]

    Returns:
        List of cycle paths. Each cycle is a list of node names
        forming the cycle. Returns empty list if no cycles.

    Example:
        >>> graph = {"A": ["B"], "B": ["A"]}
        >>> cycles = detect_cycles(graph)
        >>> print(cycles)  # [["A", "B"]]
    """
    if not graph:
        return []

    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        """DFS traversal tracking current path for cycle detection."""
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path + [neighbor])
            elif neighbor in rec_stack:
                # Found cycle - extract cycle path
                if neighbor in path:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                else:
                    # Self-loop or neighbor is current node
                    cycle = [neighbor]
                # Avoid duplicate cycles
                cycle_set = frozenset(cycle)
                if not any(frozenset(c) == cycle_set for c in cycles):
                    cycles.append(cycle)

        rec_stack.remove(node)

    for node in graph:
        if node not in visited:
            dfs(node, [node])

    return cycles


def topological_sort(
    graph: dict[str, list[str]],
) -> tuple[list[str], list[str] | None]:
    """Topologically sort a directed graph.

    Uses Kahn's algorithm (BFS-based) to produce a valid execution order
    where each node appears after all its dependencies.

    Args:
        graph: Adjacency list where graph[node] = [dependencies]

    Returns:
        Tuple of (sorted_nodes, cycle_path):
        - sorted_nodes: List of nodes in dependency order (dependencies first)
        - cycle_path: None if acyclic, otherwise list of nodes in a cycle

    Example:
        >>> graph = {"C": ["B"], "B": ["A"], "A": []}
        >>> sorted_nodes, cycle = topological_sort(graph)
        >>> print(sorted_nodes)  # ["A", "B", "C"]
        >>> print(cycle)  # None
    """
    if not graph:
        return [], None

    # Collect all nodes (including those only appearing as dependencies)
    all_nodes: set[str] = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)

    # Build reverse graph: who depends on each node
    reverse_graph: dict[str, list[str]] = defaultdict(list)
    for node, deps in graph.items():
        for dep in deps:
            reverse_graph[dep].append(node)

    # Calculate in-degree: count of dependencies for each node
    in_degree: dict[str, int] = {node: len(graph.get(node, [])) for node in all_nodes}

    # Start with nodes that have no dependencies
    queue: deque[str] = deque([node for node in all_nodes if in_degree[node] == 0])

    sorted_nodes: list[str] = []
    while queue:
        node = queue.popleft()
        sorted_nodes.append(node)

        # For each node that depends on this node, decrease its in-degree
        for dependent in reverse_graph[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # Check for cycle
    if len(sorted_nodes) != len(all_nodes):
        # Cycle detected - find it
        remaining = [n for n in all_nodes if n not in sorted_nodes]
        remaining_graph = {n: graph.get(n, []) for n in remaining}
        cycles = detect_cycles(remaining_graph)
        cycle_path = cycles[0] if cycles else list(remaining)[:2]
        return sorted_nodes, cycle_path

    return sorted_nodes, None
