"""
gui/control_panel.py
--------------------
Top bar with all user controls:
    • Jug 1 / Jug 2 capacity entry fields
    • Target volume entry field
    • Algorithm dropdown (BFS / DFS / IDDFS / A*)
    • Speed slider (100 ms – 3000 ms per step)
    • Start, Pause/Resume, Reset, Compare All buttons

All input validation lives here so app.py stays clean.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

BG_DARK   = "#1A2B3C"
BG_CTRL   = "#243447"
ACCENT    = "#4A9EE0"
BTN_GREEN = "#27AE60"
BTN_AMBER = "#E67E22"
BTN_RED   = "#C0392B"
BTN_PURP  = "#8E44AD"
TEXT_FG   = "#E8EFF6"
ENTRY_BG  = "#15202E"


class ControlPanel(tk.Frame):
    """
    Horizontal control bar packed into the top of WaterJugApp.

    Callbacks
    ---------
    on_start(cap1, cap2, goal, algo, speed_ms)
    on_pause(is_paused: bool)
    on_reset()
    on_compare(cap1, cap2, goal)
    on_speed_change(speed_ms)
    """

    ALGORITHMS = ['BFS', 'DFS', 'IDDFS', 'A*']

    def __init__(self, parent,
                 on_start:        Callable,
                 on_pause:        Callable,
                 on_reset:        Callable,
                 on_compare:      Callable,
                 on_speed_change: Callable):
        super().__init__(parent, bg=BG_CTRL, pady=6, padx=8)

        self._on_start        = on_start
        self._on_pause        = on_pause
        self._on_reset        = on_reset
        self._on_compare      = on_compare
        self._on_speed_change = on_speed_change

        self._paused   = False
        self._running  = False

        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        lbl_cfg  = dict(bg=BG_CTRL, fg=TEXT_FG, font=("Arial", 9, "bold"))
        entry_cfg = dict(width=5, bg=ENTRY_BG, fg=ACCENT,
                         insertbackground=ACCENT,
                         font=("Courier", 11, "bold"),
                         relief=tk.FLAT, bd=3,
                         justify=tk.CENTER)

        # ── Jug 1 ──
        tk.Label(self, text="Jug 1 (L):", **lbl_cfg).pack(side=tk.LEFT, padx=(0, 2))
        self._e_cap1 = tk.Entry(self, **entry_cfg)
        self._e_cap1.insert(0, "4")
        self._e_cap1.pack(side=tk.LEFT, padx=(0, 12))

        # ── Jug 2 ──
        tk.Label(self, text="Jug 2 (L):", **lbl_cfg).pack(side=tk.LEFT, padx=(0, 2))
        self._e_cap2 = tk.Entry(self, **entry_cfg)
        self._e_cap2.insert(0, "3")
        self._e_cap2.pack(side=tk.LEFT, padx=(0, 12))

        # ── Target ──
        tk.Label(self, text="Target (L):", **lbl_cfg).pack(side=tk.LEFT, padx=(0, 2))
        self._e_goal = tk.Entry(self, **entry_cfg)
        self._e_goal.insert(0, "2")
        self._e_goal.pack(side=tk.LEFT, padx=(0, 20))

        # ── Algorithm ──
        tk.Label(self, text="Algorithm:", **lbl_cfg).pack(side=tk.LEFT, padx=(0, 2))
        self._algo_var = tk.StringVar(value='BFS')
        algo_combo = ttk.Combobox(
            self,
            textvariable=self._algo_var,
            values=self.ALGORITHMS,
            width=7,
            state='readonly',
            font=("Arial", 10, "bold"),
        )
        algo_combo.pack(side=tk.LEFT, padx=(0, 20))

        # ── Speed slider ──
        tk.Label(self, text="Speed:", **lbl_cfg).pack(side=tk.LEFT, padx=(0, 2))
        self._speed_var = tk.IntVar(value=800)
        speed_slider = ttk.Scale(
            self,
            from_=100, to=3000,
            orient=tk.HORIZONTAL,
            variable=self._speed_var,
            length=110,
            command=self._on_slider,
        )
        speed_slider.pack(side=tk.LEFT, padx=(0, 2))
        self._speed_label = tk.Label(self, text="0.8 s",
                                     bg=BG_CTRL, fg=ACCENT,
                                     font=("Courier", 9))
        self._speed_label.pack(side=tk.LEFT, padx=(0, 20))

        # ── Buttons ──
        btn_cfg = dict(relief=tk.FLAT, bd=0, padx=14, pady=5,
                       font=("Arial", 10, "bold"), cursor="hand2")

        self._btn_start = tk.Button(
            self, text="▶  Start", bg=BTN_GREEN, fg="white",
            command=self._handle_start, **btn_cfg)
        self._btn_start.pack(side=tk.LEFT, padx=3)

        self._btn_pause = tk.Button(
            self, text="⏸  Pause", bg=BTN_AMBER, fg="white",
            command=self._handle_pause, state=tk.DISABLED, **btn_cfg)
        self._btn_pause.pack(side=tk.LEFT, padx=3)

        self._btn_reset = tk.Button(
            self, text="↺  Reset", bg=BTN_RED, fg="white",
            command=self._handle_reset, **btn_cfg)
        self._btn_reset.pack(side=tk.LEFT, padx=3)

        self._btn_compare = tk.Button(
            self, text="⚖  Compare All", bg=BTN_PURP, fg="white",
            command=self._handle_compare, **btn_cfg)
        self._btn_compare.pack(side=tk.LEFT, padx=3)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def set_running(self, running: bool):
        """Enable/disable buttons based on simulation state."""
        self._running = running
        self._paused  = False
        if running:
            self._btn_start ['state'] = tk.DISABLED
            self._btn_pause ['state'] = tk.NORMAL
            self._btn_pause .config(text="⏸  Pause")
        else:
            self._btn_start ['state'] = tk.NORMAL
            self._btn_pause ['state'] = tk.DISABLED
            self._btn_pause .config(text="⏸  Pause")

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------

    def _on_slider(self, _val):
        ms = int(self._speed_var.get())
        self._speed_label.config(text=f"{ms/1000:.1f} s")
        self._on_speed_change(ms)

    def _handle_start(self):
        params = self._validate()
        if params is None:
            return
        cap1, cap2, goal = params
        self._on_start(cap1, cap2, goal,
                       self._algo_var.get(),
                       int(self._speed_var.get()))

    def _handle_pause(self):
        self._paused = not self._paused
        self._btn_pause.config(
            text="▶  Resume" if self._paused else "⏸  Pause"
        )
        self._on_pause(self._paused)

    def _handle_reset(self):
        self._on_reset()

    def _handle_compare(self):
        params = self._validate()
        if params is None:
            return
        cap1, cap2, goal = params
        self._on_compare(cap1, cap2, goal)

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    def _validate(self):
        """
        Validate all three entry fields.
        Returns (cap1, cap2, goal) on success, None on failure.
        """
        try:
            cap1 = int(self._e_cap1.get().strip())
            cap2 = int(self._e_cap2.get().strip())
            goal = int(self._e_goal.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Jug capacities and target must be whole numbers.")
            return None

        if cap1 < 1 or cap2 < 1:
            messagebox.showerror("Invalid Input",
                                 "Jug capacity must be at least 1 litre.")
            return None

        if cap1 > 50 or cap2 > 50:
            messagebox.showerror("Invalid Input",
                                 "Jug capacity must not exceed 50 litres.")
            return None

        if goal < 0:
            messagebox.showerror("Invalid Input",
                                 "Target volume cannot be negative.")
            return None

        if goal == 0:
            messagebox.showwarning("Trivial Goal",
                                   "Target is 0 — start state already satisfies the goal.")
            return None

        if goal > max(cap1, cap2):
            messagebox.showerror("Invalid Input",
                                 f"Target {goal} L exceeds the largest jug "
                                 f"({max(cap1, cap2)} L).")
            return None

        return cap1, cap2, goal