"""
gui/jug_panel.py
----------------
Animated jug canvas.  Two rectangular jugs are drawn side by side;
water fill levels animate smoothly as each simulation step is replayed.

Drawing approach
----------------
Each draw_state() call:
    1. Clears the canvas (canvas.delete('all'))
    2. Draws jug outlines with rounded-corner effect
    3. Draws water fill rectangle (height proportional to level/capacity)
    4. Draws capacity markers at 25 %, 50 %, 75 % fill lines
    5. Draws current level and capacity text labels
    6. Highlights the jug that contains the goal amount (green border)
"""

import tkinter as tk
import math
from typing import Optional

BG         = "#1E2D3E"
JUG_BORDER = "#4A9EE0"
WATER_TOP  = "#5DADE2"
WATER_BOT  = "#1A6FA8"
WATER_FILL = "#3498DB"
GOAL_GLOW  = "#2ECC71"
EMPTY_FG   = "#7BA8C8"
TEXT_FG    = "#E8EFF6"
MARKER_CLR = "#3A5A7A"


class JugPanel(tk.Frame):
    """
    Tkinter Frame containing a Canvas that draws two animated jugs.
    """

    # Jug dimensions (pixels)
    JUG_W      = 90
    JUG_H      = 220
    JUG_X1     = 55    # left edge of Jug 1
    JUG_X2     = 210   # left edge of Jug 2
    JUG_TOP_Y  = 55    # top edge of both jugs
    LABEL_Y    = 10    # y for capacity label above jug
    BOTTOM_Y_OFFSET = 20  # label below jug

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._cap1: int = 4
        self._cap2: int = 3
        self._j1:   int = 0
        self._j2:   int = 0
        self._goal: Optional[int] = None

        # Draw empty jugs at startup
        self.canvas.bind("<Configure>", self._on_resize)
        self.after(50, lambda: self.draw_state(None, 4, 3))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def draw_state(self, state, cap1: int, cap2: int, goal: int = None):
        """
        Redraw both jugs reflecting *state*.

        Parameters
        ----------
        state : State | None   current simulation state (None = empty)
        cap1  : int            Jug 1 capacity
        cap2  : int            Jug 2 capacity
        goal  : int | None     target volume (used for highlighting)
        """
        self._cap1 = cap1
        self._cap2 = cap2
        self._j1   = state.j1 if state else 0
        self._j2   = state.j2 if state else 0
        self._goal = goal
        self._redraw()

    # ------------------------------------------------------------------
    def _on_resize(self, _event):
        self._redraw()

    # ------------------------------------------------------------------
    def _redraw(self):
        c = self.canvas
        c.delete('all')

        w = c.winfo_width()  or 340
        h = c.winfo_height() or 480

        jug_h  = min(int(h * 0.52), 260)
        jug_w  = min(int(w * 0.28), 100)
        gap    = (w - 2 * jug_w) // 3
        x1     = gap
        x2     = gap * 2 + jug_w
        top_y  = int(h * 0.10)
        bot_y  = top_y + jug_h

        self._draw_jug(c, x1, top_y, jug_w, jug_h,
                       level=self._j1, cap=self._cap1,
                       label="Jug 1", jug_num=1)
        self._draw_jug(c, x2, top_y, jug_w, jug_h,
                       level=self._j2, cap=self._cap2,
                       label="Jug 2", jug_num=2)

        # Action label at the top
        action_text = ""
        if hasattr(self, '_last_action'):
            action_text = self._last_action
        c.create_text(w // 2, top_y - 28, text=action_text,
                      font=("Arial", 9), fill=ACCENT_CLR,
                      anchor=tk.CENTER)

    # ------------------------------------------------------------------
    def _draw_jug(self, c, x, top_y, jug_w, jug_h,
                  level, cap, label, jug_num):
        """Draw one jug at position (x, top_y) with given dimensions."""
        bot_y = top_y + jug_h

        # Determine if this jug contains the goal
        on_goal = (self._goal is not None and level == self._goal and level > 0)

        border_color = GOAL_GLOW if on_goal else JUG_BORDER
        border_width = 3 if on_goal else 2

        # ── Water fill ────────────────────────────────────────────────
        if cap > 0 and level > 0:
            fill_h = int(jug_h * level / cap)
            fill_y = bot_y - fill_h
            # Gradient effect: two rectangles
            c.create_rectangle(x, fill_y, x + jug_w, bot_y,
                                fill=WATER_FILL, outline='', width=0)
            # Lighter top strip (wave effect)
            wave_h = max(4, fill_h // 8)
            c.create_rectangle(x, fill_y, x + jug_w, fill_y + wave_h,
                                fill=WATER_TOP, outline='', width=0)

        # ── Graduation marks ──────────────────────────────────────────
        for pct in (0.25, 0.50, 0.75):
            mark_y = bot_y - int(jug_h * pct)
            c.create_line(x + jug_w - 14, mark_y,
                          x + jug_w,      mark_y,
                          fill=MARKER_CLR, width=1)
            vol = round(cap * pct)
            c.create_text(x + jug_w + 14, mark_y,
                          text=str(vol), font=("Courier", 7),
                          fill=MARKER_CLR, anchor=tk.W)

        # ── Jug outline (drawn AFTER fill so border is on top) ────────
        c.create_rectangle(x, top_y, x + jug_w, bot_y,
                            outline=border_color, width=border_width,
                            fill='')

        # Spout / top opening lines
        c.create_line(x,           top_y, x - 8,          top_y,
                      fill=border_color, width=border_width)
        c.create_line(x + jug_w,  top_y, x + jug_w + 8,  top_y,
                      fill=border_color, width=border_width)

        # ── Labels ────────────────────────────────────────────────────
        # Above: jug name
        c.create_text(x + jug_w // 2, top_y - 18,
                      text=label,
                      font=("Arial", 10, "bold"),
                      fill=GOAL_GLOW if on_goal else TEXT_FG,
                      anchor=tk.CENTER)

        # Below: current level / capacity
        level_text = f"{level} / {cap} L"
        c.create_text(x + jug_w // 2, bot_y + 16,
                      text=level_text,
                      font=("Courier", 11, "bold"),
                      fill=GOAL_GLOW if on_goal else ACCENT_CLR,
                      anchor=tk.CENTER)

        # Percentage fill
        pct_val = int(100 * level / cap) if cap else 0
        c.create_text(x + jug_w // 2, bot_y + 32,
                      text=f"({pct_val}% full)",
                      font=("Arial", 8),
                      fill=EMPTY_FG,
                      anchor=tk.CENTER)

        # Goal badge
        if on_goal:
            c.create_text(x + jug_w // 2, bot_y + 48,
                          text="✅ GOAL!",
                          font=("Arial", 9, "bold"),
                          fill=GOAL_GLOW,
                          anchor=tk.CENTER)


# colour used for accent text (defined here to avoid NameError)
ACCENT_CLR = "#4A9EE0"