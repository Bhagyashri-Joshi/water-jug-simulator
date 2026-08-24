"""
gui/app.py
----------
Root Tkinter window.  Lays out the four regions:
    TOP  — ControlPanel (inputs + buttons)
    LEFT — JugPanel     (animated jugs)
    MID  — TreePanel    (live state-space tree)
    BOT  — LogPanel     (step-by-step log)

Also owns the SimulationController and dispatches solver calls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from math import gcd
import time

from gui.control_panel import ControlPanel
from gui.jug_panel     import JugPanel
from gui.tree_panel    import TreePanel
from gui.log_panel     import LogPanel
from simulation.controller import SimulationController

# Solver imports
from algorithms.bfs    import solve_bfs
from algorithms.dfs    import solve_dfs
from algorithms.iddfs  import solve_iddfs
from algorithms.astar  import solve_astar

# Colour constants shared across the app
BG_DARK  = "#1A2B3C"
BG_MID   = "#243447"
BG_PANEL = "#1E2D3E"
ACCENT   = "#4A9EE0"
TEXT_FG  = "#E8EFF6"


_SOLVERS = {
    'BFS':   solve_bfs,
    'DFS':   solve_dfs,
    'IDDFS': solve_iddfs,
    'A*':    solve_astar,
}


class WaterJugApp(tk.Tk):
    """Main application window (1200 × 780 px, non-resizable)."""

    WIN_W = 1200
    WIN_H = 780

    def __init__(self):
        super().__init__()
        self.title("Water Jug Problem Simulator — AI Mini Project")
        self.resizable(True, True)
        self.minsize(1000, 700)
        self.configure(bg=BG_DARK)

        # Try to set a dark title bar on Windows
        try:
            self.wm_attributes('-alpha', 1.0)
        except Exception:
            pass

        # Public attributes read by SimulationController
        self.cap1: int = 4
        self.cap2: int = 3

        self._controller = SimulationController(self)
        self._last_result: dict | None = None

        self._build_layout()
        self._center_window()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        # ── Top bar ──────────────────────────────────────────────────
        top_frame = tk.Frame(self, bg=BG_DARK, pady=4)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # App title in top bar
        title_lbl = tk.Label(
            top_frame,
            text="💧 Water Jug Problem Simulator",
            font=("Arial", 16, "bold"),
            bg=BG_DARK, fg=ACCENT,
        )
        title_lbl.pack(side=tk.LEFT, padx=14)

        subtitle_lbl = tk.Label(
            top_frame,
            text="AI Search Algorithms  •  Interactive Visualiser",
            font=("Arial", 9),
            bg=BG_DARK, fg="#7BA8C8",
        )
        subtitle_lbl.pack(side=tk.LEFT, padx=0)

        # Separator
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X)

        # ── Control panel ─────────────────────────────────────────────
        self.control_panel = ControlPanel(
            self,
            on_start=self._on_start,
            on_pause=self._on_pause,
            on_reset=self._on_reset,
            on_compare=self._on_compare_all,
            on_speed_change=self._on_speed_change,
        )
        self.control_panel.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        sep2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep2.pack(fill=tk.X)

        # ── Main content area (left + tree panels) ────────────────────
        content_frame = tk.Frame(self, bg=BG_DARK)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left — Jug panel
        jug_outer = tk.Frame(content_frame, bg=BG_MID,
                             relief=tk.FLAT, bd=0, width=320)
        jug_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=6)
        jug_outer.pack_propagate(False)

        jug_title = tk.Label(jug_outer, text="🫙  Jug Simulation",
                             font=("Arial", 11, "bold"),
                             bg=BG_MID, fg=ACCENT)
        jug_title.pack(pady=(6, 0))

        self.jug_panel = JugPanel(jug_outer)
        self.jug_panel.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Right — Tree panel
        tree_outer = tk.Frame(content_frame, bg=BG_MID, relief=tk.FLAT, bd=0)
        tree_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                        padx=(4, 8), pady=6)

        tree_title = tk.Label(tree_outer, text="🌳  State-Space Tree",
                              font=("Arial", 11, "bold"),
                              bg=BG_MID, fg=ACCENT)
        tree_title.pack(pady=(6, 0))

        self.tree_panel = TreePanel(tree_outer)
        self.tree_panel.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # ── Bottom — Log panel ────────────────────────────────────────
        sep3 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep3.pack(fill=tk.X)

        log_outer = tk.Frame(self, bg=BG_DARK, height=200)
        log_outer.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(4, 8))
        log_outer.pack_propagate(False)

        log_title = tk.Label(log_outer,
                             text="📋  Step-by-Step Log",
                             font=("Arial", 10, "bold"),
                             bg=BG_DARK, fg=ACCENT)
        log_title.pack(anchor=tk.W)

        self.log_panel = LogPanel(log_outer)
        self.log_panel.pack(fill=tk.BOTH, expand=True)

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - self.WIN_W) // 2
        y  = (sh - self.WIN_H) // 2
        self.geometry(f"{self.WIN_W}x{self.WIN_H}+{x}+{y}")

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _on_start(self, cap1: int, cap2: int, goal: int, algo: str, speed_ms: int):
        """Called by ControlPanel after it has validated inputs."""
        # GCD feasibility check
        g = gcd(cap1, cap2)
        if goal % g != 0:
            ans = messagebox.askyesno(
                "Potentially Infeasible",
                f"Target {goal} is not divisible by GCD({cap1},{cap2}) = {g}.\n"
                f"No solution may exist.  Run anyway?",
            )
            if not ans:
                return

        self.cap1 = cap1
        self.cap2 = cap2

        solver = _SOLVERS[algo]
        result = solver(cap1, cap2, goal)
        self._last_result = result

        if not result['found']:
            messagebox.showinfo(
                "No Solution",
                f"No solution exists for this configuration.\n"
                f"Explored {result['steps']} states.",
            )

        self.control_panel.set_running(True)
        self._controller.start(result, speed_ms)

    def _on_pause(self, is_paused: bool):
        if is_paused:
            self._controller.pause()
        else:
            self._controller.resume()

    def _on_reset(self):
        self._controller.reset()
        self.control_panel.set_running(False)
        self.tree_panel.reset()
        self.log_panel.clear()
        self.jug_panel.draw_state(None, self.cap1, self.cap2)

    def _on_compare_all(self, cap1: int, cap2: int, goal: int):
        """Run all 4 algorithms and show a comparison popup."""
        from gui.compare_window import CompareWindow
        CompareWindow(self, cap1, cap2, goal)

    def _on_speed_change(self, speed_ms: int):
        self._controller.set_speed(speed_ms)

    # ------------------------------------------------------------------
    # Called by SimulationController when replay is done
    # ------------------------------------------------------------------

    def on_simulation_complete(self):
        self.control_panel.set_running(False)
        r = self._last_result
        if r and r['found']:
            self.log_panel.append_message(
                f"Simulation complete — Solution found in "
                f"{len(r['solution']) - 1} steps  "
                f"({r['steps']} nodes explored)",
                tag='success'
            )
        elif r:
            self.log_panel.append_message(
                "No solution found — all states exhausted.",
                tag='error'
            )