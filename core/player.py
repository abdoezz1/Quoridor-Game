# core/player.py

import numpy as np
from core.movement import (
    try_move_direction,
    try_jump_diagonal,
    _apply_move,
)
from core.walls import is_wall_placement_valid


class Player:
    colors = ["#467C9E", "#E63946"]

    def __init__(self, id, board, pos, objective, available_walls=10):
        self.id = id
        self.board = board
        self.pos = pos.astype(int)
        self.objective = objective
        self.available_walls = available_walls
        self.color = Player.colors[self.id - 1]

        # Place pawn in board grid
        self.board.board[self.pos[0], self.pos[1]] = self.id

    # ---------------------------------------------------------
    # PUBLIC MOVE HANDLER (called by GUI)
    # ---------------------------------------------------------
    def handle_move(self, direction):
        """
        Receives directions from GUI:
            top / down / left / right
            topLeft / topRight / downLeft / downRight
        """
        success = self.move(direction)
        return success

    def move_to_position(self, target_y, target_x):
        """
        Move player to a specific position (in 17×17 coordinates).
        This is used by the GUI when a valid move cell is clicked.
        Returns True if move was successful, False otherwise.
        """
        # Determine direction from current position to target
        direction = self._get_direction_to(target_y, target_x)
        
        if direction:
            return self.move(direction)
        
        # If no standard direction matches, try direct move for jumps
        # This handles complex jump scenarios
        return self._try_direct_move(target_y, target_x)

    def _get_direction_to(self, target_y, target_x):
        """
        Determine the direction string from current position to target.
        Returns direction string or None if not a standard move.
        """
        y, x = self.pos
        dy = target_y - y
        dx = target_x - x
        
        # Standard moves (distance of 2 in one direction)
        if dy == -2 and dx == 0:
            return "top"
        elif dy == 2 and dx == 0:
            return "down"
        elif dy == 0 and dx == -2:
            return "left"
        elif dy == 0 and dx == 2:
            return "right"
        
        # Diagonal moves (distance of 2 in both directions)
        elif dy == -2 and dx == -2:
            return "topLeft"
        elif dy == -2 and dx == 2:
            return "topRight"
        elif dy == 2 and dx == -2:
            return "downLeft"
        elif dy == 2 and dx == 2:
            return "downRight"
        
        # Jump moves (distance of 4 in one direction) - handled by direction
        elif dy == -4 and dx == 0:
            return "top"
        elif dy == 4 and dx == 0:
            return "down"
        elif dy == 0 and dx == -4:
            return "left"
        elif dy == 0 and dx == 4:
            return "right"
        
        return None

    def _try_direct_move(self, target_y, target_x):
        """
        Try to move directly to target position.
        Used for complex jump scenarios that don't fit standard directions.
        """
        from core.movement import _apply_move
        
        # Verify the target is a valid empty cell
        if self.board.board[target_y, target_x] != 0:
            return False
        
        return _apply_move(self, target_y, target_x)

    # ---------------------------------------------------------
    # HIGH-LEVEL MOVE DISPATCHER
    # ---------------------------------------------------------
    def move(self, direction):
        """
        Delegates logic to movement module.
        """

        # Standard 4-direction movement
        if direction in ["top", "down", "left", "right"]:
            return try_move_direction(self, direction)

        # Diagonal movement (jump-side-step)
        if direction in ["topLeft", "topRight", "downLeft", "downRight"]:
            return try_jump_diagonal(self, direction)

        return False
