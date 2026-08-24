"""
algorithms/iddfs.py
-------------------
Iterative Deepening Depth-First Search solver.

Properties
----------
Combines DFS's O(b·d) space efficiency with BFS's optimal-path guarantee.
Re-expands shallow nodes on each iteration — overhead is negligible because
the last level dominates.

Complete       : Yes
Optimal        : Yes — finds the shallowest solution like BFS
Time           : O(b^d)
Space          : O(b·d)   best space of all uninformed searches
"""

from .state import State, get_successors, build_result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def solve_iddfs(cap1: int, cap2: int, goal: int) -> dict:
    """
    Solve the water jug problem using Iterative Deepening DFS.

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

    # Max sensible depth = cap1 * cap2  (state space has at most (cap1+1)*(cap2+1) nodes)
    max_depth = (cap1 + 1) * (cap2 + 1)

    all_explored = []   # accumulate across all iterations for tree animation

    for depth_limit in range(0, max_depth + 1):
        result = _depth_limited_search(
            start, cap1, cap2, goal, depth_limit, set(), all_explored
        )
        if result['found']:
            return result

    return build_result(None, all_explored, found=False)


# ---------------------------------------------------------------------------
# Depth-Limited Search (recursive)
# ---------------------------------------------------------------------------

def _depth_limited_search(state: State, cap1: int, cap2: int, goal: int,
                           limit: int, visited: set, explored: list) -> dict:
    """
    Recursive DLS helper.  Mutates *explored* and *visited* in-place so
    the top-level collector can accumulate nodes across all iterations.
    """
    key = (state.j1, state.j2)

    # Avoid revisiting within this iteration's path
    if key in visited:
        return {'found': False, 'explored': explored}

    visited.add(key)
    explored.append(state)

    # Goal test
    if state.j1 == goal or state.j2 == goal:
        return build_result(state, explored, found=True)

    # Depth cutoff
    if limit == 0:
        return {'found': False, 'explored': explored}

    for next_state in get_successors(state, cap1, cap2):
        nk = (next_state.j1, next_state.j2)
        if nk not in visited:
            result = _depth_limited_search(
                next_state, cap1, cap2, goal, limit - 1,
                visited, explored
            )
            if result['found']:
                return result

    return {'found': False, 'explored': explored}