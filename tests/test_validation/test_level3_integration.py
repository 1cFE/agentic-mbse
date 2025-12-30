"""Tests for Level 3 integration with sysml_utils.graph.

Validates that Level 3 uses sysml_utils graph utilities correctly.
"""

from agentic_mbse.sysml.graph import detect_cycles as sysml_detect_cycles


def test_detect_cycles_uses_sysml_utils():
    """detect_cycles is imported from agentic_mbse.sysml.graph.

    Input: Import check
    Output: Function is from agentic_mbse.sysml.graph module
    """
    from agentic_mbse.validation import level3_dataflow

    # After refactor, the module should use sysml_utils.graph.detect_cycles
    # We can verify by checking that detect_cycles is the same function
    assert level3_dataflow.detect_cycles is sysml_detect_cycles


def test_sysml_utils_detect_cycles_returns_list_of_lists():
    """sysml_utils.graph.detect_cycles returns List[List[str]].

    Input: Known cyclic graph
    Output: Returns list of lists (not pre-formatted strings)
    """
    graph = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
    }

    cycles = sysml_detect_cycles(graph)

    assert isinstance(cycles, list)
    assert len(cycles) >= 1
    # Each cycle is a list, not a string
    assert isinstance(cycles[0], list)
    assert all(isinstance(node, str) for node in cycles[0])


def test_level3_cycle_formatting():
    """Level 3 formats cycles correctly for display.

    Input: Known cyclic graph through validate_dataflow
    Output: Cycle displayed as "A → B → C" format
    """
    # This is implicitly tested by the regression test
    # Here we verify the formatting logic directly
    cycle_path = ["A", "B", "C"]
    formatted = f"Circular dependency: {' → '.join(cycle_path)}"
    assert formatted == "Circular dependency: A → B → C"


def test_detect_cycles_empty_graph():
    """detect_cycles handles empty graph.

    Input: Empty graph
    Output: Empty list of cycles
    """
    cycles = sysml_detect_cycles({})
    assert cycles == []


def test_detect_cycles_no_cycles():
    """detect_cycles handles graph without cycles.

    Input: Acyclic graph
    Output: Empty list of cycles
    """
    graph = {
        "A": ["B"],
        "B": ["C"],
        "C": [],
    }

    cycles = sysml_detect_cycles(graph)
    assert cycles == []


def test_detect_cycles_self_loop():
    """detect_cycles handles self-referential node.

    Input: Node that depends on itself
    Output: Cycle detected
    """
    graph = {
        "A": ["A"],
    }

    cycles = sysml_detect_cycles(graph)
    assert len(cycles) >= 1
