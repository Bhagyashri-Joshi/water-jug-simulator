"""
simulation/controller.py
------------------------
SimulationController drives the step-by-step playback of a solver result.

It uses Tkinter's after() scheduler (single-threaded, safe) to replay
one explored state per tick, updating the three GUI panels in lock-step.

Design principle
----------------
The controller knows about the GUI app object but the AI solver modules
know nothing about the GUI — data flows upward only.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular imports at runtime; only used for type hints
    from gui.app import WaterJugApp


class SimulationController:
    """
    Manages the replay of a completed solver result through the GUI.

    Parameters
    ----------
    app : WaterJugApp   reference to the root Tkinter window
    """

    def __init__(self, app: 'WaterJugApp'):
        self.app            = app
        self._steps: list   = []      # explored states in expansion order
        self._solution_keys: set = set()  # (j1,j2) pairs on the optimal path
        self._index: int    = 0
        self._speed_ms: int = 800     # milliseconds between steps
        self._paused: bool  = False
        self._job           = None    # pending after() callback id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self, result: dict, speed_ms: int):
        """
        Begin replaying *result* (standard solver dict) at *speed_ms* ms/step.
        Cancels any currently running simulation first.
        """
        self._cancel()
        self._steps         = result['explored']
        self._solution_keys = {(s.j1, s.j2) for s in result['solution']}
        self._index         = 0
        self._speed_ms      = max(50, speed_ms)
        self._paused        = False

        # Reset all panels before starting
        self.app.tree_panel.reset()
        self.app.log_panel.clear()
        self.app.jug_panel.draw_state(None, self.app.cap1, self.app.cap2)

        self._tick()

    def pause(self):
        """Pause the animation without losing position."""
        self._paused = True
        self._cancel()

    def resume(self):
        """Resume from the current position."""
        if self._paused:
            self._paused = False
            self._tick()

    def reset(self):
        """Stop the simulation and clear all state."""
        self._cancel()
        self._steps         = []
        self._solution_keys = set()
        self._index         = 0
        self._paused        = False

    def set_speed(self, speed_ms: int):
        """Change playback speed on the fly."""
        self._speed_ms = max(50, speed_ms)

    @property
    def is_running(self) -> bool:
        return self._job is not None and not self._paused

    @property
    def is_finished(self) -> bool:
        return self._index >= len(self._steps)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _tick(self):
        """Process one step and schedule the next."""
        if self._paused:
            return
        if self._index >= len(self._steps):
            # Simulation complete — notify GUI
            self.app.on_simulation_complete()
            return

        state       = self._steps[self._index]
        on_solution = (state.j1, state.j2) in self._solution_keys

        # Update all three panels
        self.app.jug_panel.draw_state(state, self.app.cap1, self.app.cap2)
        self.app.tree_panel.update(state, on_solution)
        self.app.log_panel.append_step(self._index + 1, state, on_solution)

        self._index += 1
        self._job = self.app.after(self._speed_ms, self._tick)

    def _cancel(self):
        """Cancel any pending after() callback."""
        if self._job is not None:
            try:
                self.app.after_cancel(self._job)
            except Exception:
                pass
            self._job = None