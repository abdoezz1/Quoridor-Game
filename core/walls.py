"""
core/walls.py

Handles Quoridor wall placement logic:
- validates legality
- checks overlap and collision
- validates that paths remain available
"""

import numpy as np
from collections import deque

from core.rules import (
    is_inside,
    is_wall_spot,
    HORIZONTAL_CONNECTOR_CODE,
    VERTICAL_CONNECTOR_CODE,
)


# =========================================================
# PUBLIC API
# =========================================================

def is_wall_placement_valid(board, y, x):
    """
    Check if a wall can be placed at logical (y, x).

    This does NOT place the wall — it only validates.
    """

    dim = board.dimBoard
    grid = board.board

    # ---------------------------------------------
    # 1. Check inside bounds
    # ---------------------------------------------
    if not is_inside(y, x, dim):
        return False

    # ---------------------------------------------
    # 2. Must be a valid wall location
    # ---------------------------------------------
    if not is_wall_spot(y, x):
        return False

    # ---------------------------------------------
    # 3. Determine orientation
    # ---------------------------------------------
    if y % 2 == 1 and x % 2 == 0:
        orientation = "H"
    elif y % 2 == 0 and x % 2 == 1:
        orientation = "V"
    else:
        return False  # invalid location

    # ---------------------------------------------
    # 4. Get occupied coordinates
    # ---------------------------------------------
    segs, connector = _wall_cells(y, x, orientation)

    # Out of bounds check
    for sy, sx in segs + [connector]:
        if not is_inside(sy, sx, dim):
            return False

    # ---------------------------------------------
    # 5. Check overlap with existing walls
    # ---------------------------------------------
    if grid[connector[0], connector[1]] != 0:
        return False

    for sy, sx in segs:
        if grid[sy, sx] != 0:
            return False

    # ---------------------------------------------
    # 6. Simulate placement & check shortest paths
    # ---------------------------------------------
    return _check_paths_after_simulated_wall(board, segs, connector)


def place_wall(board, y, x, player):
    """
    Actually place the wall (after validity check).
    """

    dim = board.dimBoard
    grid = board.board

    if not is_wall_placement_valid(board, y, x):
        return False

    # Deduce orientation
    orientation = "H" if y % 2 == 1 else "V"
    segs, connector = _wall_cells(y, x, orientation)

    # Paint board
    for sy, sx in segs:
        grid[sy, sx] = 1  # wall segment

    # Orientation-specific connector code
    if orientation == "H":
        grid[connector[0], connector[1]] = HORIZONTAL_CONNECTOR_CODE
    else:
        grid[connector[0], connector[1]] = VERTICAL_CONNECTOR_CODE

    # Deduct walls (each wall costs 1)
    player.available_walls -= 1

    return True


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _wall_cells(y, x, orientation):
    """
    Returns:
        segments = [(y1, x1), (y2, x2)]
        connector = (cy, cx)
    """
    if orientation == "H":
        seg1 = (y, x)
        seg2 = (y, x + 2)
        connector = (y, x + 1)
    else:  # "V"
        seg1 = (y, x)
        seg2 = (y + 2, x)
        connector = (y + 1, x)

    return [seg1, seg2], connector


def _check_paths_after_simulated_wall(board, segs, connector):
    """
    Simulate the wall, check BFS connectivity for both players.
    """

    grid = board.board

    # Temporarily place wall
    removed_values = []
    for sy, sx in segs:
        removed_values.append(grid[sy, sx])
        grid[sy, sx] = 1

    removed_connector = grid[connector[0], connector[1]]
    grid[connector[0], connector[1]] = 1

    # Check path exists for p1 and p2
    ok = (
        _player_has_path(board, board.p1) and
        _player_has_path(board, board.p2)
    )

    # Undo the simulation
    for (sy, sx), v in zip(segs, removed_values):
        grid[sy, sx] = v

    grid[connector[0], connector[1]] = removed_connector

    return ok


def _player_has_path(board, player):
    """
    BFS from player's position until reaching objective row.

    Pawns move through even-even tiles only.
    """

    start = tuple(player.pos)
    target_row = player.objective

    dim = board.dimBoard
    grid = board.board

    q = deque([start])
    visited = {start}

    # Movement vectors: (±2,0), (0,±2)
    moves = [(2, 0), (-2, 0), (0, 2), (0, -2)]

    while q:
        y, x = q.popleft()

        # Reached goal row
        if y == target_row:
            return True

        for dy, dx in moves:
            ny, nx = y + dy, x + dx

            if not is_inside(ny, nx, dim):
                continue

            # Check wall between (y,x) and (ny,nx)
            wall_y = y + dy // 2
            wall_x = x + dx // 2
            if grid[wall_y, wall_x] != 0:
                continue

            # Check cell occupancy
            if (ny, nx) not in visited and grid[ny, nx] in (0, player.id):
                visited.add((ny, nx))
                q.append((ny, nx))

    return False
