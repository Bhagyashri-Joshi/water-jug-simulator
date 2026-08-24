"""
algorithms/state.py
-------------------
Immutable State namedtuple shared by every solver module.
Also provides get_successors() and reconstruct_path() utilities.
"""

from collections import namedtuple


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------
# We wrap namedtuple in a class so we can attach custom __hash__ / __eq__
# that ignores the 'parent' back-pointer (two states are equal if j1==j2).
# This is critical for visited-set membership tests.
# ---------------------------------------------------------------------------

class State:
    """
    Represents a single node in the Water Jug state space.

    Attributes
    ----------
    j1     : int        current water level in Jug 1
    j2     : int        current water level in Jug 2
    parent : State|None back-pointer to the state that produced this one
    action : str        human-readable description of the move taken
    """
    __slots__ = ('j1', 'j2', 'parent', 'action')

    def __init__(self, j1: int, j2: int, parent=None, action: str = 'Start'):
        object.__setattr__(self, 'j1',     j1)
        object.__setattr__(self, 'j2',     j2)
        object.__setattr__(self, 'parent', parent)
        object.__setattr__(self, 'action', action)

    # Make immutable
    def __setattr__(self, *_):
        raise AttributeError("State is immutable")

    # Equality and hash ignore the back-pointer — only water levels matter
    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return self.j1 == other.j1 and self.j2 == other.j2

    def __hash__(self):
        return hash((self.j1, self.j2))

    def __repr__(self):
        return f"State(j1={self.j1}, j2={self.j2}, action='{self.action}')"

    # Needed for heapq (A* tie-breaking)
    def __lt__(self, other):
        return (self.j1, self.j2) < (other.j1, other.j2)


# ---------------------------------------------------------------------------
# 6 Operators
# ---------------------------------------------------------------------------

def get_successors(state: State, cap1: int, cap2: int) -> list:
    """
    Return a list of valid successor States from *state* given jug
    capacities cap1 and cap2.

    The six possible operations are:
        OP1  Fill Jug 1 completely
        OP2  Fill Jug 2 completely
        OP3  Empty Jug 1
        OP4  Empty Jug 2
        OP5  Pour Jug 1 → Jug 2
        OP6  Pour Jug 2 → Jug 1
    """
    j1, j2 = state.j1, state.j2
    successors = []

    # OP1 — Fill Jug 1
    if j1 < cap1:
        successors.append(State(cap1, j2, state, f'Fill Jug 1 to {cap1} L'))

    # OP2 — Fill Jug 2
    if j2 < cap2:
        successors.append(State(j1, cap2, state, f'Fill Jug 2 to {cap2} L'))

    # OP3 — Empty Jug 1
    if j1 > 0:
        successors.append(State(0, j2, state, 'Empty Jug 1'))

    # OP4 — Empty Jug 2
    if j2 > 0:
        successors.append(State(j1, 0, state, 'Empty Jug 2'))

    # OP5 — Pour Jug 1 → Jug 2
    if j1 > 0 and j2 < cap2:
        pour = min(j1, cap2 - j2)
        successors.append(State(j1 - pour, j2 + pour, state,
                                f'Pour {pour} L  Jug 1 → Jug 2'))

    # OP6 — Pour Jug 2 → Jug 1
    if j2 > 0 and j1 < cap1:
        pour = min(j2, cap1 - j1)
        successors.append(State(j1 + pour, j2 - pour, state,
                                f'Pour {pour} L  Jug 2 → Jug 1'))

    return successors


# ---------------------------------------------------------------------------
# Path reconstruction
# ---------------------------------------------------------------------------

def reconstruct_path(goal_state: State) -> list:
    """Walk back-pointers from goal_state to root and return the path
    ordered from start → goal."""
    path = []
    s = goal_state
    while s is not None:
        path.append(s)
        s = s.parent
    return list(reversed(path))


# ---------------------------------------------------------------------------
# Result builder helper (used by every solver)
# ---------------------------------------------------------------------------

def build_result(goal_state, explored: list, found: bool) -> dict:
    """
    Construct the standard solver return dict.

    Returns
    -------
    {
        'solution' : list[State]   — path from start to goal ([] if not found)
        'explored' : list[State]   — all nodes visited in expansion order
        'found'    : bool
        'steps'    : int           — total nodes expanded
    }
    """
    return {
        'solution': reconstruct_path(goal_state) if found else [],
        'explored': explored,
        'found':    found,
        'steps':    len(explored),
    }