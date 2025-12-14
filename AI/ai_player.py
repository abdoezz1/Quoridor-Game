"""
AI Player Module for Quoridor
==============================
Implements AI opponent with multiple difficulty levels.

Difficulty Levels:
------------------
- EASY:   Depth 1, greedy move selection, no wall strategy
          Algorithm: Single-ply lookahead with basic heuristic

- MEDIUM: Depth 2, alpha-beta pruning, basic wall placement
          Algorithm: 2-ply alpha-beta with path difference heuristic

- HARD:   Depth 3, alpha-beta pruning, strategic wall placement
          Algorithm: 3-ply alpha-beta with advanced evaluation
          (considers wall count, path blocking, positional advantage)
"""

from core.player import Player
from AI.search import find_best_move, apply_move_to_board


# Difficulty level configurations
DIFFICULTY_SETTINGS = {
    'easy': {
        'search_depth': 1,
        'wall_bonus_weight': 0.5,
        'description': 'Simple AI - looks 1 move ahead'
    },
    'medium': {
        'search_depth': 2,
        'wall_bonus_weight': 1.0,
        'description': 'Balanced AI - uses alpha-beta pruning (depth 2)'
    },
    'hard': {
        'search_depth': 3,
        'wall_bonus_weight': 1.5,
        'description': 'Advanced AI - deep search with strategic walls (depth 3)'
    }
}


class AIPlayer(Player):
    """
    AI-controlled player using Minimax with Alpha-Beta pruning.

    The AI evaluates positions based on:
    - Path length difference (shorter path = better)
    - Available walls (more walls = more options)
    - Strategic wall placement to block opponent
    """

    def __init__(self, id, board, pos, objective, available_walls=10,
                 difficulty='medium'):
        super().__init__(id, board, pos, objective, available_walls)
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty: str):
        """
        Set AI difficulty level.

        Args:
            difficulty: 'easy', 'medium', or 'hard'
        """
        difficulty = difficulty.lower()
        if difficulty not in DIFFICULTY_SETTINGS:
            difficulty = 'medium'

        settings = DIFFICULTY_SETTINGS[difficulty]
        self.difficulty = difficulty
        self.search_depth = settings['search_depth']
        self.wall_bonus_weight = settings['wall_bonus_weight']

    def ai_move(self):
        """
        Execute AI move using the configured search algorithm.

        Returns:
            bool: True if move was successful, False otherwise
        """
        # Get best move from search
        best_move = find_best_move(
            self.board,
            self,
            self.search_depth,
            self.wall_bonus_weight
        )

        if best_move is None:
            print("AI couldn't find a valid move!")
            return False

        # Apply move to actual board
        apply_move_to_board(self.board, best_move, self)

        # Switch turn
        self.board.switch_turn()

        return True
