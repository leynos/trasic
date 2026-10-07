"""Exhaustively compare small dependency graphs with an independent cycle oracle.

The finite scope is all 531 directed graphs on zero to three labelled nodes,
including self-loops, plus each possible dangling edge from those graphs.
This proves agreement within that bound; it is not an unbounded graph proof.
"""
from __future__ import annotations

import sys
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_workspace import WorkspaceFailure, check_graph
from validate_docs import CheckFailure, check_dag


def small_graphs():
    """Generate every edge subset; e.g. one node yields the empty and self edge."""
    for count in range(4):
        nodes = tuple(str(index) for index in range(count))
        possible_edges = tuple(product(nodes, repeat=2))
        for edge_mask in range(1 << len(possible_edges)):
            graph = {node: set() for node in nodes}
            for index, (source, target) in enumerate(possible_edges):
                if edge_mask & (1 << index):
                    graph[source].add(target)
            yield graph


def has_cycle_by_elimination(graph: dict[str, set[str]]) -> bool:
    """Remove dependency-free nodes; a residual subgraph contains a cycle.

    Unlike the production depth-first traversals, this oracle never recurses or
    tracks a visiting path. For example, A -> B removes B, then A; A -> A remains.
    Its test-local input contract requires all edges to refer to existing nodes.
    """
    remaining = {node: set(edges) for node, edges in graph.items()}
    while remaining:
        removable = {node for node, edges in remaining.items() if not edges}
        if not removable:
            return True
        remaining = {node: edges - removable for node, edges in remaining.items()
                     if node not in removable}
    return False


class GraphProperties(unittest.TestCase):
    """Both validators reject exactly the cyclic known-node graphs in the bound."""

    def test_all_small_directed_graphs_agree_with_independent_oracle(self):
        """Cover every edge ordering subset, disconnected component and self-loop."""
        examined = 0
        for graph in small_graphs():
            examined += 1
            with self.subTest(graph=graph):
                cyclic = has_cycle_by_elimination(graph)
                document_graph = {node: sorted(edges) for node, edges in graph.items()}
                if cyclic:
                    with self.assertRaisesRegex(WorkspaceFailure, 'cycle'):
                        check_graph(graph)
                    with self.assertRaisesRegex(CheckFailure, 'cycle'):
                        check_dag(document_graph, 'generated graph')
                else:
                    check_graph(graph)
                    check_dag(document_graph, 'generated graph')
        self.assertEqual(examined, 531, 'Every graph in the finite bound must run')

    def test_each_generated_dangling_edge_is_rejected_with_contract_error(self):
        """Unknown nodes reject through typed failures, including in cyclic graphs."""
        examined = 0
        for graph in small_graphs():
            for node in graph:
                examined += 1
                changed = {name: edges | {'unknown'} if name == node else set(edges)
                           for name, edges in graph.items()}
                with self.subTest(graph=changed):
                    with self.assertRaises(WorkspaceFailure):
                        check_graph(changed)
                    with self.assertRaises(CheckFailure):
                        check_dag({name: sorted(edges) for name, edges in changed.items()},
                                  'generated graph')
        self.assertEqual(examined, 1570, 'Every possible source for a dangling edge must run')

    def test_unknown_dependency_retains_specific_diagnostic(self):
        """A single dangling edge fails explicitly before any dictionary lookup."""
        with self.assertRaisesRegex(WorkspaceFailure, 'unknown dependency missing'):
            check_graph({'owner': {'missing'}})
        with self.assertRaisesRegex(CheckFailure, 'contract: unknown dependency missing'):
            check_dag({'owner': ['missing']}, 'contract')


if __name__ == '__main__':
    unittest.main()
