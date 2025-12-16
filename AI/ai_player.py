from core.player import Player
from AI.search import find_best_move, apply_move_to_board
from AI.move_generator import generate_all_moves
import random

DIFFICULTY_SETTINGS = {
    'easy': {
        'search_depth': 1,
        'wall_bonus_weight': 0.5,
        'random_chance': 0.30,
        'description': 'Simple AI - looks 1 move ahead'
    },
    'medium': {
        'search_depth': 2,
        'wall_bonus_weight': 1.0,
        'random_chance': 0.10,
        'description': 'Balanced AI - uses alpha-beta pruning (depth 2)'
    },
    'hard': {
        'search_depth': 3,
        'wall_bonus_weight': 1.5,
        'random_chance': 0.0,
        'description': 'Advanced AI - deep search with strategic walls (depth 3)'
    }
}


class AIPlayer(Player):

    def __init__(self, id, board, pos, objective, available_walls=10,
                 difficulty='medium'):
        super().__init__(id, board, pos, objective, available_walls)
        self.set_difficulty(difficulty)
        self.position_history = []  # Track recent positions

    def set_difficulty(self, difficulty: str):
        difficulty = difficulty.lower()
        if difficulty not in DIFFICULTY_SETTINGS:
            difficulty = 'medium'

        settings = DIFFICULTY_SETTINGS[difficulty]
        self.difficulty = difficulty
        self.search_depth = settings['search_depth']
        self.wall_bonus_weight = settings['wall_bonus_weight']
        self.random_chance = settings['random_chance']

    def ai_move(self):
        if self.random_chance > 0 and random.random() < self.random_chance:
            valid_moves = generate_all_moves(self.board, self)
            if valid_moves:
                best_move = random.choice(valid_moves)
                self._update_history(best_move)  # Track position
                apply_move_to_board(self.board, best_move, self)
                self.board.switch_turn()
                return True

        best_move = find_best_move(
            self.board,
            self,
            self.search_depth,
            self.wall_bonus_weight,
            self.position_history  # Pass history to search
        )

        if best_move is None:
            print("AI couldn't find a valid move!")
            return False

        self._update_history(best_move)  # Track position
        apply_move_to_board(self.board, best_move, self)
        self.board.switch_turn()
        return True

    def _update_history(self, move):
        """Track recent positions to prevent oscillation."""
        if move[0] == "pawn":
            pos = (int(move[1][0]), int(move[1][1]))
            self.position_history.append(pos)
            
            # Keep only last 6 positions
            if len(self.position_history) > 6:
                self.position_history.pop(0)

    def reset_history(self):
        """Call when starting a new game."""
        self.position_history = []