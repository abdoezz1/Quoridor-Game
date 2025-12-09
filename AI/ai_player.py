# ai/ai_player.py

import numpy as np
from core.player import Player
from core.walls import is_wall_placement_valid, place_wall
from AI.evaluation import evaluate_board
from AI.move_generator import generate_all_moves
from collections import deque


class AIPlayer(Player):
    """
    AI-controlled player that uses Minimax with Alpha-Beta pruning
    to select optimal moves.
    
    Supports multiple difficulty levels:
    - Easy: Depth 1, random-ish play
    - Medium: Depth 2, decent lookahead
    - Hard: Depth 3, strong tactical play
    """
    
    def __init__(self, id, board, pos, objective, available_walls=10, difficulty="medium"):
        super().__init__(id, board, pos, objective, available_walls)
        
        # Set search depth based on difficulty
        self.difficulty = difficulty.lower()
        if self.difficulty == "easy":
            self.max_depth = 1
        elif self.difficulty == "medium":
            self.max_depth = 2
        else:  # hard
            self.max_depth = 3
    
    def ai_move(self):
        """
        Main AI decision-making function.
        Uses Minimax with Alpha-Beta pruning to find best move.
        """
        
        # Get best move using minimax
        best_move = self._minimax_search()
        
        if best_move is None:
            print("AI couldn't find a valid move!")
            return False
        
        # Execute the best move
        return self._execute_move(best_move)
    
    def _minimax_search(self):
        """
        Performs Minimax search with Alpha-Beta pruning.
        Returns the best move as (move_type, move_data)
        """
        
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Generate all possible moves
        possible_moves = generate_all_moves(self.board, self)
        
        # If no moves available, return None
        if not possible_moves:
            return None
        
        # Easy mode: add some randomness
        if self.difficulty == "easy":
            import random
            if random.random() < 0.3:  # 30% chance of random move
                return random.choice(possible_moves)
        
        # Evaluate each possible move
        for move in possible_moves:
            # Simulate the move
            undo_info = self._simulate_move(move)
            
            # Get score from opponent's perspective (minimize)
            score = self._minimax(self.max_depth - 1, alpha, beta, False)
            
            # Undo the move
            self._undo_move(move, undo_info)
            
            # Update best move
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
        
        return best_move
    
    def _minimax(self, depth, alpha, beta, is_maximizing):
        """
        Recursive minimax with alpha-beta pruning.
        
        Args:
            depth: remaining search depth
            alpha: best score for maximizing player
            beta: best score for minimizing player
            is_maximizing: True if current player is AI
        
        Returns:
            evaluation score
        """
        
        # Terminal condition: depth reached or game over
        if depth == 0 or self._is_game_over():
            return evaluate_board(self.board, self)
        
        current_player = self if is_maximizing else self._get_opponent()
        possible_moves = generate_all_moves(self.board, current_player)
        
        # No valid moves
        if not possible_moves:
            return evaluate_board(self.board, self)
        
        if is_maximizing:
            max_score = float('-inf')
            for move in possible_moves:
                undo_info = self._simulate_move(move)
                score = self._minimax(depth - 1, alpha, beta, False)
                self._undo_move(move, undo_info)
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_score
        else:
            min_score = float('inf')
            for move in possible_moves:
                undo_info = self._simulate_move(move)
                score = self._minimax(depth - 1, alpha, beta, True)
                self._undo_move(move, undo_info)
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_score
    
    def _simulate_move(self, move):
        """
        Apply a move to the board and return undo information.
        
        Args:
            move: (move_type, move_data)
                - For pawn: ("pawn", direction)
                - For wall: ("wall", (y, x))
        
        Returns:
            undo_info: dict with information to reverse the move
        """
        move_type, move_data = move
        
        if move_type == "pawn":
            # Store old position
            old_pos = self.pos.copy()
            
            # Execute pawn move
            direction = move_data
            self.move(direction)
            
            return {
                'type': 'pawn',
                'old_pos': old_pos,
                'player': self if self.board.current_turn == self else self._get_opponent()
            }
        
        elif move_type == "wall":
            # Store wall information
            y, x = move_data
            
            # Determine orientation
            if y % 2 == 1 and x % 2 == 0:
                orientation = "H"
            else:
                orientation = "V"
            
            # Get wall cells
            if orientation == "H":
                seg1, seg2 = (y, x), (y, x + 2)
                connector = (y, x + 1)
            else:
                seg1, seg2 = (y, x), (y + 2, x)
                connector = (y + 1, x)
            
            # Store old grid values
            grid = self.board.board
            old_values = {
                seg1: grid[seg1[0], seg1[1]],
                seg2: grid[seg2[0], seg2[1]],
                connector: grid[connector[0], connector[1]]
            }
            
            # Place wall
            player = self if self.board.current_turn == self else self._get_opponent()
            place_wall(self.board, y, x, player)
            
            return {
                'type': 'wall',
                'cells': [seg1, seg2, connector],
                'old_values': old_values,
                'player': player
            }
        
        return None
    
    def _undo_move(self, move, undo_info):
        """
        Reverse a simulated move.
        """
        if undo_info['type'] == 'pawn':
            # Restore old position
            player = undo_info['player']
            grid = self.board.board
            
            # Clear current position
            grid[player.pos[0], player.pos[1]] = 0
            
            # Restore old position
            player.pos = undo_info['old_pos']
            grid[player.pos[0], player.pos[1]] = player.id
        
        elif undo_info['type'] == 'wall':
            # Restore grid cells
            grid = self.board.board
            for cell, old_value in undo_info['old_values'].items():
                grid[cell[0], cell[1]] = old_value
            
            # Restore wall count
            undo_info['player'].available_walls += 1
    
    def _execute_move(self, move):
        """
        Execute the chosen move on the actual board.
        """
        move_type, move_data = move
        
        if move_type == "pawn":
            direction = move_data
            success = self.move(direction)
            if success:
                self.board.switch_turn()
            return success
        
        elif move_type == "wall":
            y, x = move_data
            success = place_wall(self.board, y, x, self)
            if success:
                self.board.switch_turn()
            return success
        
        return False
    
    def _is_game_over(self):
        """Check if game is over (either player reached objective)."""
        return (
            self.board.p1.pos[0] == self.board.p1.objective or
            self.board.p2.pos[0] == self.board.p2.objective
        )
    
    def _get_opponent(self):
        """Get the opponent player."""
        return self.board.p1 if self == self.board.p2 else self.board.p2
    
    def get_shortest_path_length(self, player=None):
        """
        Calculate shortest path length from player's position to objective.
        Uses BFS.
        """
        if player is None:
            player = self
        
        start = tuple(player.pos)
        target_row = player.objective
        
        dim = self.board.dimBoard
        grid = self.board.board
        
        q = deque([(start, 0)])  # (position, distance)
        visited = {start}
        
        moves = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        
        while q:
            (y, x), dist = q.popleft()
            
            if y == target_row:
                return dist // 2  # Convert grid distance to move count
            
            for dy, dx in moves:
                ny, nx = y + dy, x + dx
                
                if not (0 <= ny < dim and 0 <= nx < dim):
                    continue
                
                wall_y = y + dy // 2
                wall_x = x + dx // 2
                if grid[wall_y, wall_x] != 0:
                    continue
                
                if (ny, nx) not in visited and grid[ny, nx] in (0, player.id):
                    visited.add((ny, nx))
                    q.append(((ny, nx), dist + 2))
        
        return float('inf')  # No path found