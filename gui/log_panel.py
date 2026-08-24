"""
gui/log_panel.py
----------------
Scrollable text area that logs each simulation step in real time.

Each entry format:
    Step  N │ <action>  │  Jug1: X L   Jug2: Y L

Colour tags
-----------
    'solution'  — green text for steps on the optimal path
    'explored'  — default light text for other explored steps
    'success'   — bold green banner at completion
    'error'     — red banner for no-solution
    'info'      — dim info messages
"""

import tkinter as tk
from tkinter import ttk

BG       = "#0F1923"
FG_DEF   = "#A8C4DC"
FG_SOL   = "#2ECC71"
FG_DEAD  = "#7BA8C8"
FG_ERR   = "#E74C3C"
FG_INFO  = "#5D8AA8"
FG_HEAD  = "#E8EFF6"
BG_SOL   = "#0D2B1A"
BG_DEAD  = "#0F1923"


class LogPanel(tk.Frame):
    """
    Tkinter Frame containing a scrollable Text widget for simulation logs.
    """

    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        # Text widget + scrollbar
        self._text = tk.Text(
            self,
            bg=BG, fg=FG_DEF,
            font=("Courier New", 9),
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED,
            wrap=tk.NONE,
            exportselection=False,
            cursor="arrow",
        )

        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL,
                            command=self._text.yview)
        hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                            command=self._text.xview)
        self._text.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT,  fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._configure_tags()
        self._write_header()

    # ------------------------------------------------------------------
    # Tag configuration
    # ------------------------------------------------------------------

    def _configure_tags(self):
        t = self._text
        t.tag_configure('header',   foreground=FG_HEAD,  font=("Courier New", 9, "bold"))
        t.tag_configure('solution', foreground=FG_SOL,   background=BG_SOL,
                        font=("Courier New", 9, "bold"))
        t.tag_configure('explored', foreground=FG_DEAD)
        t.tag_configure('success',  foreground=FG_SOL,   font=("Courier New", 9, "bold"))
        t.tag_configure('error',    foreground=FG_ERR,   font=("Courier New", 9, "bold"))
        t.tag_configure('info',     foreground=FG_INFO)
        t.tag_configure('sep',      foreground="#2A4A6A")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def clear(self):
        """Clear all log content and restore the header."""
        self._text.configure(state=tk.NORMAL)
        self._text.delete('1.0', tk.END)
        self._text.configure(state=tk.DISABLED)
        self._write_header()

    def append_step(self, step_num: int, state, on_solution: bool):
        """
        Append one simulation step to the log.

        Parameters
        ----------
        step_num    : 1-based step counter
        state       : State object
        on_solution : True if this step is on the optimal path
        """
        tag = 'solution' if on_solution else 'explored'
        marker = "★" if on_solution else "·"

        line = (
            f" {marker} Step {step_num:>4}  │  "
            f"{state.action:<32}  │  "
            f"Jug1: {state.j1:>2} L   "
            f"Jug2: {state.j2:>2} L\n"
        )
        self._append(line, tag)

    def append_message(self, message: str, tag: str = 'info'):
        """Append a plain message line (used for completion/error banners)."""
        sep = "─" * 78
        self._append(f" {sep}\n", 'sep')
        self._append(f" {message}\n", tag)
        self._append(f" {sep}\n", 'sep')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_header(self):
        header = (
            " ┌─────────────────────────────────────────────────"
            "─────────────────────────┐\n"
            " │  Step   │  Action                            "
            "│  Jug 1       Jug 2      │\n"
            " └─────────────────────────────────────────────────"
            "─────────────────────────┘\n"
        )
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, header, 'header')
        self._text.configure(state=tk.DISABLED)

    def _append(self, text: str, tag: str):
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, text, tag)
        self._text.configure(state=tk.DISABLED)
        self._text.see(tk.END)   # auto-scroll to latest line