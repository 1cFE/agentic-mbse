"""Tests for graph algorithm utilities.

These tests document cycle detection and topological sorting.

Graph Semantics:
    graph[A] = [B, C] means "A depends on B and C"
    i.e., A cannot be computed until B and C are available
"""

from agentic_mbse.sysml.graph import detect_cycles, topological_sort


def test_detect_cycles_no_cycles():
    """detect_cycles returns empty list for acyclic graph.

    Input: A depends on B, B depends on C (no cycles)
    Output: Empty list
    """
    graph = {"A": ["B"], "B": ["C"], "C": []}

    cycles = detect_cycles(graph)

    assert cycles == []


def test_detect_cycles_simple_cycle():
    """detect_cycles finds simple two-node cycle.

    Input: A depends on B, B depends on A (cycle)
    Output: List containing the cycle path
    """
    graph = {"A": ["B"], "B": ["A"]}

    cycles = detect_cycles(graph)

    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B"}


def test_detect_cycles_self_loop():
    """detect_cycles finds self-referencing node.

    Input: A depends on A (self-loop)
    Output: List containing [A] or [A, A]
    """
    graph = {"A": ["A"]}

    cycles = detect_cycles(graph)

    assert len(cycles) == 1
    assert "A" in cycles[0]


def test_detect_cycles_three_node_cycle():
    """detect_cycles finds three-node cycle.

    Input: A → B → C → A
    Output: Cycle containing all three nodes
    """
    graph = {"A": ["B"], "B": ["C"], "C": ["A"]}

    cycles = detect_cycles(graph)

    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B", "C"}


def test_detect_cycles_empty_graph():
    """detect_cycles handles empty graph.

    Input: Empty graph {}
    Output: Empty list
    """
    graph: dict[str, list[str]] = {}

    cycles = detect_cycles(graph)

    assert cycles == []


def test_topological_sort_simple_dag():
    """topological_sort orders nodes by dependency.

    Input: C depends on B, B depends on A, A depends on nothing
    Output: Execution order [A, B, C] (A first since nothing depends on it)

    Note: graph[node] = [dependencies], so execution order starts with
    nodes that have no dependencies.
    """
    graph = {
        "C": ["B"],  # C depends on B
        "B": ["A"],  # B depends on A
        "A": [],  # A depends on nothing
    }

    sorted_nodes, cycle = topological_sort(graph)

    assert cycle is None
    assert sorted_nodes.index("A") < sorted_nodes.index("B")
    assert sorted_nodes.index("B") < sorted_nodes.index("C")


def test_topological_sort_parallel_dependencies():
    """topological_sort handles parallel independent nodes.

    Input: C depends on both A and B (A and B are independent)
    Output: A and B before C (order of A/B doesn't matter)
    """
    graph = {
        "C": ["A", "B"],  # C depends on both
        "A": [],
        "B": [],
    }

    sorted_nodes, cycle = topological_sort(graph)

    assert cycle is None
    assert sorted_nodes.index("A") < sorted_nodes.index("C")
    assert sorted_nodes.index("B") < sorted_nodes.index("C")


def test_topological_sort_detects_cycle():
    """topological_sort returns cycle when graph is cyclic.

    Input: A → C → B → A (cycle)
    Output: Partial sort and cycle path
    """
    graph = {"A": ["C"], "B": ["A"], "C": ["B"]}

    sorted_nodes, cycle = topological_sort(graph)

    assert cycle is not None
    assert len(cycle) >= 2  # Cycle has at least 2 nodes


def test_topological_sort_empty_graph():
    """topological_sort handles empty graph.

    Input: Empty graph {}
    Output: Empty list, no cycle
    """
    graph: dict[str, list[str]] = {}

    sorted_nodes, cycle = topological_sort(graph)

    assert sorted_nodes == []
    assert cycle is None


def test_topological_sort_single_node():
    """topological_sort handles single node.

    Input: Single node with no dependencies
    Output: [node], no cycle
    """
    graph = {"A": []}

    sorted_nodes, cycle = topological_sort(graph)

    assert sorted_nodes == ["A"]
    assert cycle is None


def test_topological_sort_disconnected_components():
    """topological_sort handles disconnected graph components.

    Input: Two independent chains: A→B and C→D
    Output: All nodes sorted, each chain in correct order
    """
    graph = {"A": [], "B": ["A"], "C": [], "D": ["C"]}

    sorted_nodes, cycle = topological_sort(graph)

    assert cycle is None
    assert len(sorted_nodes) == 4
    assert sorted_nodes.index("A") < sorted_nodes.index("B")
    assert sorted_nodes.index("C") < sorted_nodes.index("D")
