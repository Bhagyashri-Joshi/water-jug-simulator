"""
simulation/tree_builder.py
--------------------------
Converts the flat list of explored States returned by any solver into a
NetworkX DiGraph that can be rendered by TreePanel.

Each node in the graph is a (j1, j2) tuple.
Each directed edge carries a 'label' attribute with the action string.
"""

import networkx as nx
from algorithms.state import State


class TreeBuilder:
    """
    Incrementally builds a NetworkX DiGraph as simulation steps are replayed.

    Usage
    -----
        tb = TreeBuilder()
        tb.reset()
        for state in explored:
            tb.add_state(state)
        G = tb.graph
    """

    def __init__(self):
        self.G: nx.DiGraph = nx.DiGraph()

    # ------------------------------------------------------------------
    def reset(self):
        """Clear the graph for a new simulation run."""
        self.G.clear()

    # ------------------------------------------------------------------
    def add_state(self, state: State):
        """
        Add *state* as a node and draw an edge from its parent (if any).
        Safe to call multiple times with the same state.
        """
        node = (state.j1, state.j2)
        self.G.add_node(node, label=f'({state.j1},{state.j2})')

        if state.parent is not None:
            parent_node = (state.parent.j1, state.parent.j2)
            if not self.G.has_node(parent_node):
                self.G.add_node(parent_node,
                                label=f'({state.parent.j1},{state.parent.j2})')
            # Avoid duplicate edges
            if not self.G.has_edge(parent_node, node):
                self.G.add_edge(parent_node, node, label=state.action)

    # ------------------------------------------------------------------
    @property
    def graph(self) -> nx.DiGraph:
        return self.G

    # ------------------------------------------------------------------
    def build_from_list(self, states: list):
        """
        Convenience: build the full graph from a list of States at once.
        Useful for the Compare-All feature.
        """
        self.reset()
        for s in states:
            self.add_state(s)
        return self.G