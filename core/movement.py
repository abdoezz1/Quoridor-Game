# core/movement.py

import numpy as np
from core.rules import DIRECTIONS, DIAGONALS


# ---------------------------------------------------------
# BASIC MOVE HANDLER (up / down / left / right)
# ---------------------------------------------------------
def try_move_direction(player, direction):
    dy, dx = DIRECTIONS[direction]
    y, x = player.pos
    board = player.board.board

    ny, nx = y + dy, x + dx
    wall_y, wall_x = y + dy // 2, x + dx // 2

    # Out of bounds
    if not (0 <= ny < player.board.dimBoard and 0 <= nx < player.board.dimBoard):
        return False

    # Wall blocking movement
    if board[wall_y, wall_x] != 0:
        return False

    # Normal no-player move
    if board[ny, nx] == 0:
        return _apply_move(player, ny, nx)

    # Opponent in front → try jumping
    return _attempt_jump_over_opponent(player, dy, dx)


# ---------------------------------------------------------
# DIAGONAL MOVE (player is blocked → side-step)
# ---------------------------------------------------------
def try_jump_diagonal(player, direction):
    dy, dx = DIAGONALS[direction]
    y, x = player.pos
    board = player.board.board

    ny, nx = y + dy, x + dx

    # bounds
    if not (0 <= ny < player.board.dimBoard and 0 <= nx < player.board.dimBoard):
        return False

    # Requirements:
    #   1. Opponent must be adjacent in x or y direction
    #   2. Jump must be blocked in the forward direction
    #   3. Side cell must NOT be blocked by a wall

    # Horizontal or vertical check
    op_x = board[y, x + 2] != 0 if dx > 0 else board[y, x - 2] != 0
    op_y = board[y - 2, x] != 0 if dy < 0 else board[y + 2, x] != 0

    if not (op_x or op_y):
        return False

    # Wall checks (diagonal is allowed only when forward jump is blocked)
    if board[y + dy // 2, x + dx // 2] != 0:
        return False

    return _apply_move(player, ny, nx)


# ---------------------------------------------------------
# INTERNAL UTILITIES
# ---------------------------------------------------------
def _attempt_jump_over_opponent(player, dy, dx):
    """
    Handle 'jump forward' logic:
        P
        |
        O   <-- Opponent
        |
      empty? → jump
    """
    y, x = player.pos
    board = player.board.board

    # Opponent tile
    mid_y = y + dy
    mid_x = x + dx

    # Target jump tile
    jump_y = y + dy * 2
    jump_x = x + dx * 2

    # Bounds
    if not (0 <= jump_y < player.board.dimBoard and 0 <= jump_x < player.board.dimBoard):
        return False

    # Forward wall check
    wall_y = y + dy // 2
    wall_x = x + dx // 2
    if board[wall_y, wall_x] != 0:
        return False

    # Wall behind opponent
    wall2_y = y + dy * 3 // 2
    wall2_x = x + dx * 3 // 2
    if board[wall2_y, wall2_x] != 0:
        return False

    # Jump tile must be empty
    if board[jump_y, jump_x] != 0:
        return False

    return _apply_move(player, jump_y, jump_x)


def _apply_move(player, ny, nx):
    """Move pawn on board."""
    board = player.board.board

    # Remove old position
    board[player.pos[0], player.pos[1]] = 0

    # Apply new position
    player.pos = np.array([ny, nx], dtype=int)
    board[ny, nx] = player.id

    return True
