"""
algorithms/dfs.py
-----------------
Depth-First Search solver for the Water Jug problem.

Properties
----------
Data structure : list used as a LIFO stack
Complete       : Yes  (with visited set to avoid cycles)
Optimal        : No   — may return a longer path than BFS
Time           : O(b^m)  m = max depth of state space
Space          : O(b·m)  stores only current path + stack frontier
"""

from .state import State, get_successors, build_result


def solve_dfs(cap1: int, cap2: int, goal: int) -> dict:
    """
    Solve the water jug problem using iterative Depth-First Search.

    Parameters
    ----------
    cap1 : int   capacity of Jug 1
    cap2 : int   capacity of Jug 2
    goal : int   desired water level

    Returns
    -------
    Standard result dict — see algorithms/state.py::build_result()
    """
    start = State(0, 0, None, 'Start (both jugs empty)')

    if start.j1 == goal or start.j2 == goal:
        return build_result(start, [start], found=True)

    stack    = [start]
    visited  = set()
    explored = []

    while stack:
        state = stack.pop()   # LIFO — DFS behaviour

        key = (state.j1, state.j2)
        if key in visited:
            continue

        visited.add(key)
        explored.append(state)

        # Goal test
        if state.j1 == goal or state.j2 == goal:
            return build_result(state, explored, found=True)

        # Push successors in reverse order so the first successor
        # is explored first (consistent left-to-right operator ordering)
        for next_state in reversed(get_successors(state, cap1, cap2)):
            nk = (next_state.j1, next_state.j2)
            if nk not in visited:
                stack.append(next_state)

    return build_result(None, explored, found=False)