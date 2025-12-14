from core.player import Player
from AI.search import find_best_move, apply_move_to_board


class AIPlayer(Player):
    def _init_(self, id, board, pos, objective, available_walls=10, search_depth=1, wall_bonus_weight=1.0):
        super()._init_(id, board, pos, objective, available_walls)
        self.search_depth = search_depth
        self.wall_bonus_weight = wall_bonus_weight
    
    def ai_move(self):
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