"""
algorithms/bfs.py
-----------------
Breadth-First Search solver for the Water Jug problem.

Properties
----------
Data structure : collections.deque  (FIFO)
Complete       : Yes
Optimal        : Yes — guarantees the fewest-steps solution
Time           : O(b^d)   b = branching factor (≤6), d = solution depth
Space          : O(b^d)   stores entire frontier
"""

from collections import deque
from .state import State, get_successors, build_result


def solve_bfs(cap1: int, cap2: int, goal: int) -> dict:
    """
    Solve the water jug problem using Breadth-First Search.

    Parameters
    ----------
    cap1 : int   capacity of Jug 1
    cap2 : int   capacity of Jug 2
    goal : int   desired water level (must appear in j1 OR j2)

    Returns
    -------
    Standard result dict — see algorithms/state.py::build_result()
    """
    start = State(0, 0, None, 'Start (both jugs empty)')

    # Trivial case: goal is already satisfied at the start
    if start.j1 == goal or start.j2 == goal:
        return build_result(start, [start], found=True)

    queue    = deque([start])
    visited  = {(start.j1, start.j2)}   # set of (j1, j2) tuples
    explored = []                         # nodes expanded, in order

    while queue:
        state = queue.popleft()
        explored.append(state)

        # Expand all successors
        for next_state in get_successors(state, cap1, cap2):
            key = (next_state.j1, next_state.j2)

            if key in visited:
                continue

            visited.add(key)

            # Goal test at generation time (more efficient)
            if next_state.j1 == goal or next_state.j2 == goal:
                explored.append(next_state)
                return build_result(next_state, explored, found=True)

            queue.append(next_state)

    return build_result(None, explored, found=False)