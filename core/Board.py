import numpy as np
from core.rules import DEFAULT_PAWN_DIM, DEFAULT_FULL_DIM
from core.rules import PAWN_MOVE_CODE, WALL_MOVE_CODE
from core.player import Player
from ai.ai_player import AIPlayer


class Board:
    """
    Main game state container.
    - Stores the 17×17 board grid
    - Holds Player 1 and Player 2 objects
    - Exposes a clean get_state() for the AI
    - Manages whether game is vs AI or vs human
    """

    def __init__(self, dim=DEFAULT_PAWN_DIM, vs_ai=False):
        # Dimensions
        self.dimPawnBoard = dim                                 # 9 rows of pawn cells
        self.dimWallBoard = self.dimPawnBoard - 1               # 8 wall rows
        self.dimBoard = self.dimPawnBoard + self.dimWallBoard   # 17 × 17 grid

        # Actual game board (walls + players + empty tiles)
        self.board = np.zeros((self.dimBoard, self.dimBoard), dtype=int)

        # Game mode
        self.vs_ai = vs_ai

        # -------------------------------
        # Initialize Players
        # -------------------------------
        # Player 1 starts bottom center
        p1_start = np.array([self.dimBoard - 1, self.dimBoard // 2], dtype=int)
        p2_start = np.array([0, self.dimBoard // 2], dtype=int)

        self.p1 = Player(
            id=1,
            board=self,
            pos=p1_start,
            objective=0,                    # must reach row 0
        )

        if self.vs_ai:
            self.p2 = AIPlayer(
                id=2,
                board=self,
                pos=p2_start,
                objective=self.dimBoard - 1,  # must reach last row
            )
        else:
            self.p2 = Player(
                id=2,
                board=self,
                pos=p2_start,
                objective=self.dimBoard - 1,
            )

        # Track current turn
        self.current_turn = self.p1

    # ---------------------------------------------------------
    # Switching Turns
    # ---------------------------------------------------------
    def switch_turn(self):
        self.current_turn = self.p1 if self.current_turn == self.p2 else self.p2

    # ---------------------------------------------------------
    # AI Move Wrapper
    # ---------------------------------------------------------
    def request_ai_move(self):
        """
        Called by GUI to let AI compute its best move.
        """
        if not isinstance(self.p2, AIPlayer):
            return None

        self.p2.ai_move()

    # ---------------------------------------------------------
    # Snapshot for AI
    # ---------------------------------------------------------
    def get_state(self):
        """
        Returns AI-friendly virtual board structure:
        [
            [p1_position, p1_walls],
            [p2_position, p2_walls],
            17×17 grid copy
        ]
        """
        return [
            [self.p1.pos.copy(), self.p1.available_walls],
            [self.p2.pos.copy(), self.p2.available_walls],
            self.board.copy(),
        ]
