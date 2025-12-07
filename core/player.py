# core/player.py

import numpy as np
from core.movement import (
    try_move_direction,
    try_jump_diagonal,
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
