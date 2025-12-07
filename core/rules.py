"""
core/rules.py

Shared constants and definitions for Quoridor.
Used by Board, Player, Movement, and Wall logic.
"""

# ---------------------------------------------------------
# GRID DIMENSIONS
# ---------------------------------------------------------

DEFAULT_PAWN_DIM = 9
DEFAULT_FULL_DIM = DEFAULT_PAWN_DIM * 2 - 1  # 17×17


# ---------------------------------------------------------
# MOVE TYPE CODES
# ---------------------------------------------------------

PAWN_MOVE_CODE = 0
WALL_MOVE_CODE = 1


# ---------------------------------------------------------
# PAWN MOVE DIRECTIONS
# ---------------------------------------------------------

DIRECTIONS = {
    "top":    (-2, 0),
    "down":   (+2, 0),
    "left":   (0, -2),
    "right":  (0, +2),
}

DIRECTIONS["bottom"] = DIRECTIONS["down"]


# ---------------------------------------------------------
# DIAGONAL JUMPS
# ---------------------------------------------------------

DIAGONALS = {
    "topLeft":     (-2, -2),
    "topRight":    (-2, +2),
    "bottomLeft":  (+2, -2),
    "bottomRight": (+2, +2),
}


# ---------------------------------------------------------
# WALL CODES
# ---------------------------------------------------------

HORIZONTAL_CONNECTOR_CODE = 1
VERTICAL_CONNECTOR_CODE   = 2


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def is_inside(y, x, dim):
    return 0 <= y < dim and 0 <= x < dim


def is_cell(y, x):
    return (y % 2 == 0) and (x % 2 == 0)


def is_wall_spot(y, x):
    return (y % 2) != (x % 2)


def is_connector(y, x):
    return (y % 2 == 1 and x % 2 == 1)
