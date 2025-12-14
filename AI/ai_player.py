from core.player import Player
from AI.search import find_best_move, apply_move_to_board
from AI.move_generator import generate_all_moves
import random

DIFFICULTY_SETTINGS = {
    'easy': {
        'search_depth': 1,
        'wall_bonus_weight': 0.5,
        'random_chance': 0.30,  # EDIT 2: Added random chance
        'description': 'Simple AI - looks 1 move ahead'
    },
    'medium': {
        'search_depth': 2,
        'wall_bonus_weight': 1.0,
        'random_chance': 0.10,  # EDIT 2: Added random chance
        'description': 'Balanced AI - uses alpha-beta pruning (depth 2)'
    },
    'hard': {
        'search_depth': 3,
        'wall_bonus_weight': 1.5,
        'random_chance': 0.0,  # EDIT 2: Added random chance
        'description': 'Advanced AI - deep search with strategic walls (depth 3)'
    }
}


class AIPlayer(Player):

    def init(self, id, board, pos, objective, available_walls=10,
                 difficulty='medium'):
        super().init(id, board, pos, objective, available_walls)
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty: str):
        difficulty = difficulty.lower()
        if difficulty not in DIFFICULTY_SETTINGS:
            difficulty = 'medium'

        settings = DIFFICULTY_SETTINGS[difficulty]
        self.difficulty = difficulty
        self.search_depth = settings['search_depth']
        self.wall_bonus_weight = settings['wall_bonus_weight']
        self.random_chance = settings['random_chance']  # EDIT 2: Store random chance

    def ai_move(self):

        # EDIT 3: Random move chance for easier difficulties
        if self.random_chance > 0 and random.random() < self.random_chance:
            valid_moves = generate_all_moves(self.board, self)
            if valid_moves:
                best_move = random.choice(valid_moves)
                apply_move_to_board(self.board, best_move, self)
                self.board.switch_turn()
                return True

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