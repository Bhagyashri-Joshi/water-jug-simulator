"""
gui/tree_panel.py
-----------------
Embeds a Matplotlib Figure inside a Tkinter Frame and renders a live
NetworkX DiGraph of the explored state-space tree.

Node colour coding
------------------
    Light blue  (#AED6F1)  — discovered but not yet visited
    Orange      (#F39C12)  — currently being expanded (frontier)
    Green       (#2ECC71)  — on the optimal solution path
    Red         (#E74C3C)  — expanded but not on solution (dead-end branch)
    Grey        (#BDC3C7)  — start node

Layout strategy
---------------
Try graphviz 'dot' (hierarchical) first; fall back to a custom
top-down BFS layout if pygraphviz is not installed.
"""

import tkinter as tk
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches

from simulation.tree_builder import TreeBuilder
from algorithms.state import State

BG_FIG    = "#1E2D3E"
BG_AXES   = "#1E2D3E"
EDGE_CLR  = "#4A7FA5"
FONT_CLR  = "#E8EFF6"


class TreePanel(tk.Frame):
    """
    Tkinter Frame containing the live state-space tree visualisation.
    """

    # Node colours
    COL_UNVISITED = "#AED6F1"
    COL_FRONTIER  = "#F39C12"
    COL_SOLUTION  = "#2ECC71"
    COL_DEAD      = "#E74C3C"
    COL_START     = "#BDC3C7"
    COL_CURRENT   = "#FFFFFF"

    def __init__(self, parent):
        super().__init__(parent, bg=BG_FIG)

        self._builder = TreeBuilder()
        self._node_colors: dict = {}   # (j1,j2) -> hex colour
        self._solution_keys: set = set()
        self._current_node = None

        # Matplotlib figure
        self._fig = Figure(figsize=(5.5, 4.5), dpi=110,
                           facecolor=BG_FIG)
        self._ax  = self._fig.add_subplot(111)
        self._ax.set_facecolor(BG_AXES)
        self._fig.subplots_adjust(left=0.02, right=0.98,
                                  top=0.88, bottom=0.05)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self._draw_empty()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self):
        """Clear the tree for a new simulation run."""
        self._builder.reset()
        self._node_colors.clear()
        self._solution_keys.clear()
        self._current_node = None
        self._draw_empty()

    def set_solution_keys(self, keys: set):
        """
        Tell the tree panel which (j1,j2) pairs are on the solution path
        so it can colour them green once they are reached.
        """
        self._solution_keys = keys

    def update(self, state: State, on_solution: bool):
        """
        Add *state* to the tree and redraw.

        Parameters
        ----------
        state       : newly expanded State
        on_solution : True if this node is on the optimal path
        """
        node = (state.j1, state.j2)

        # Add to graph
        self._builder.add_state(state)

        # Assign colour
        if node == (0, 0) and state.parent is None:
            color = self.COL_START
        elif on_solution:
            color = self.COL_SOLUTION
        else:
            color = self.COL_DEAD

        self._node_colors[node] = color
        self._current_node      = node

        self._redraw()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _draw_empty(self):
        self._ax.clear()
        self._ax.set_facecolor(BG_AXES)
        self._ax.set_title("State-Space Tree will appear here",
                            color=FONT_CLR, fontsize=9,
                            fontfamily='monospace', pad=8)
        self._ax.axis('off')
        self._canvas.draw()

    def _redraw(self):
        G = self._builder.graph
        if G.number_of_nodes() == 0:
            self._draw_empty()
            return

        self._ax.clear()
        self._ax.set_facecolor(BG_AXES)

        # Layout
        pos = self._get_layout(G)

        # Node colours list (must be in G.nodes() order)
        node_list   = list(G.nodes())
        colors      = [self._node_colors.get(n, self.COL_UNVISITED)
                       for n in node_list]
        # Highlight current node with white border effect by drawing twice
        border_clrs = ['white' if n == self._current_node else BG_AXES
                       for n in node_list]

        # Labels
        labels = {n: f"({n[0]},{n[1]})" for n in node_list}

        # Draw edges
        nx.draw_networkx_edges(
            G, pos, ax=self._ax,
            edge_color=EDGE_CLR,
            arrows=True,
            arrowsize=12,
            arrowstyle='-|>',
            node_size=700,
            width=1.5,
            connectionstyle='arc3,rad=0.05',
        )

        # Draw node halos (current node highlight)
        nx.draw_networkx_nodes(
            G, pos, ax=self._ax,
            nodelist=node_list,
            node_color=border_clrs,
            node_size=850,
        )

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos, ax=self._ax,
            nodelist=node_list,
            node_color=colors,
            node_size=720,
        )

        # Draw labels
        nx.draw_networkx_labels(
            G, pos, labels=labels, ax=self._ax,
            font_size=8, font_color=FONT_CLR,
            font_weight='bold',
        )

        # Edge action labels (only if graph is small enough to be readable)
        if G.number_of_edges() <= 30:
            edge_labels = nx.get_edge_attributes(G, 'label')
            # Shorten labels
            short_labels = {}
            for (u, v), lbl in edge_labels.items():
                # Truncate long action strings
                short_labels[(u, v)] = lbl[:18] + '…' if len(lbl) > 18 else lbl
            nx.draw_networkx_edge_labels(
                G, pos, edge_labels=short_labels, ax=self._ax,
                font_size=6.5, font_color="#A0C4E8",
                bbox=dict(boxstyle='round,pad=0.15',
                          facecolor=BG_AXES, alpha=0.8, edgecolor='none'),
            )

        # Legend
        legend_patches = [
            mpatches.Patch(color=self.COL_START,    label='Start'),
            mpatches.Patch(color=self.COL_SOLUTION, label='Solution Path'),
            mpatches.Patch(color=self.COL_DEAD,     label='Explored'),
            mpatches.Patch(color=self.COL_CURRENT,  label='Current'),
        ]
        self._ax.legend(
            handles=legend_patches,
            loc='upper right',
            fontsize=7,
            framealpha=0.6,
            facecolor=BG_FIG,
            labelcolor=FONT_CLR,
        )

        node_count = G.number_of_nodes()
        self._ax.set_title(
            f"Nodes explored: {node_count}",
            color=FONT_CLR, fontsize=9, pad=8,
        )
        self._ax.axis('off')
        self._canvas.draw()

    # ------------------------------------------------------------------
    def _get_layout(self, G: nx.DiGraph) -> dict:
        """
        Try graphviz dot layout (hierarchical); fall back to a manual
        BFS-based top-down layout that works without graphviz.
        """
        try:
            import pygraphviz  # noqa: F401
            pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
            return pos
        except Exception:
            pass

        # Manual hierarchical layout — BFS from root (0,0)
        return self._hierarchical_layout(G)

    def _hierarchical_layout(self, G: nx.DiGraph) -> dict:
        """
        Assign (x, y) coordinates layer by layer using BFS from (0,0).
        Nodes without a path from root are placed at the bottom.
        """
        root = (0, 0)
        if root not in G:
            root = next(iter(G.nodes())) if G.nodes() else None
        if root is None:
            return {}

        layers = {}   # node -> depth
        queue  = [root]
        visited = {root}
        layers[root] = 0

        while queue:
            next_q = []
            for node in queue:
                for child in G.successors(node):
                    if child not in visited:
                        visited.add(child)
                        layers[child] = layers[node] + 1
                        next_q.append(child)
            queue = next_q

        # Nodes not reached from root (disconnected)
        max_depth = max(layers.values(), default=0)
        for node in G.nodes():
            if node not in layers:
                max_depth += 1
                layers[node] = max_depth

        # Group by depth
        from collections import defaultdict
        depth_groups = defaultdict(list)
        for node, depth in layers.items():
            depth_groups[depth].append(node)

        pos = {}
        max_layer_w = max(len(v) for v in depth_groups.values())
        x_scale = max(2.0, max_layer_w * 1.2)

        for depth, nodes in depth_groups.items():
            n = len(nodes)
            for i, node in enumerate(sorted(nodes)):
                x = (i - (n - 1) / 2) * (x_scale / max(n, 1))
                y = -depth * 1.8
                pos[node] = (x, y)

        return pos