# ai/evaluation.py

"""
Board evaluation function for Quoridor AI.

The evaluation considers:
1. Path length difference (most important)
2. Wall availability
3. Central control
4. Blocking potential
"""

from collections import deque


def evaluate_board(board, ai_player):
    """
    Evaluate the board state from AI player's perspective.
    
    Returns a score where:
    - Positive values favor the AI
    - Negative values favor the opponent
    - Higher magnitude = stronger position
    
    Args:
        board: Board object
        ai_player: AIPlayer instance
    
    Returns:
        float: evaluation score
    """
    
    # Get opponent
    opponent = board.p1 if ai_player == board.p2 else board.p2
    
    # Check for immediate win/loss
    if ai_player.pos[0] == ai_player.objective:
        return 10000  # AI wins
    if opponent.pos[0] == opponent.objective:
        return -10000  # Opponent wins
    
    # Calculate component scores
    path_score = _evaluate_path_difference(board, ai_player, opponent)
    wall_score = _evaluate_walls(ai_player, opponent)
    position_score = _evaluate_position(board, ai_player, opponent)
    blocking_score = _evaluate_blocking_potential(board, ai_player, opponent)
    
    # Weighted combination
    total_score = (
        path_score * 100 +      # Path difference is most important
        wall_score * 10 +       # Wall advantage matters
        position_score * 5 +    # Central position is helpful
        blocking_score * 15     # Blocking opportunities are valuable
    )
    
    return total_score


def _evaluate_path_difference(board, ai_player, opponent):
    """
    Calculate the difference in shortest path lengths.
    Negative difference means AI is closer to winning.
    
    Returns:
        float: opponent_path - ai_path (positive is good for AI)
    """
    
    ai_path = _shortest_path_length(board, ai_player)
    opponent_path = _shortest_path_length(board, opponent)
    
    # If either path is infinite, heavily penalize
    if ai_path == float('inf'):
        return -1000
    if opponent_path == float('inf'):
        return 1000
    
    # Return difference (positive means AI is closer)
    return opponent_path - ai_path


def _evaluate_walls(ai_player, opponent):
    """
    Evaluate wall advantage.
    More walls = more strategic options.
    
    Returns:
        float: wall advantage score
    """
    
    wall_difference = ai_player.available_walls - opponent.available_walls
    
    # Having walls when opponent doesn't is very valuable
    if ai_player.available_walls > 0 and opponent.available_walls == 0:
        return wall_difference + 5
    
    return wall_difference


def _evaluate_position(board, ai_player, opponent):
    """
    Evaluate positional advantage.
    Central columns are generally better.
    
    Returns:
        float: position score
    """
    
    center = board.dimBoard // 2
    
    # Distance from center column
    ai_center_dist = abs(ai_player.pos[1] - center)
    opponent_center_dist = abs(opponent.pos[1] - center)
    
    # Closer to center is better (negative distance is good)
    return opponent_center_dist - ai_center_dist


def _evaluate_blocking_potential(board, ai_player, opponent):
    """
    Evaluate how well positioned the AI is to block opponent.
    
    Considers:
    - Proximity to opponent
    - Ability to place blocking walls
    
    Returns:
        float: blocking potential score
    """
    
    if ai_player.available_walls == 0:
        return 0
    
    # Calculate distance between players
    ai_y, ai_x = ai_player.pos
    opp_y, opp_x = opponent.pos
    
    distance = abs(ai_y - opp_y) + abs(ai_x - opp_x)
    
    # Being closer to opponent when you have walls is advantageous
    # But not too close (you need space to maneuver)
    if distance < 8:  # Very close
        return 2
    elif distance < 16:  # Moderate distance
        return 1
    else:
        return 0


def _shortest_path_length(board, player):
    """
    BFS to find shortest path from player's current position to objective.
    
    Args:
        board: Board object
        player: Player object
    
    Returns:
        int: number of moves to reach objective (or inf if no path)
    """
    
    start = tuple(player.pos)
    target_row = player.objective
    
    dim = board.dimBoard
    grid = board.board
    
    q = deque([(start, 0)])  # (position, distance)
    visited = {start}
    
    # Pawn moves: up, down, left, right (on even-even grid)
    moves = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    
    while q:
        (y, x), dist = q.popleft()
        
        # Reached objective row
        if y == target_row:
            return dist // 2  # Convert grid distance to move count
        
        for dy, dx in moves:
            ny, nx = y + dy, x + dx
            
            # Bounds check
            if not (0 <= ny < dim and 0 <= nx < dim):
                continue
            
            # Wall check (between current and next position)
            wall_y = y + dy // 2
            wall_x = x + dx // 2
            if grid[wall_y, wall_x] != 0:
                continue
            
            # Visit if empty or contains current player
            if (ny, nx) not in visited and grid[ny, nx] in (0, player.id):
                visited.add((ny, nx))
                q.append(((ny, nx), dist + 2))
    
    return float('inf')  # No path exists


def _count_reachable_cells(board, player):
    """
    Count how many cells are reachable from player's position.
    More mobility = better position.
    
    Returns:
        int: number of reachable cells
    """
    
    start = tuple(player.pos)
    dim = board.dimBoard
    grid = board.board
    
    q = deque([start])
    visited = {start}
    
    moves = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    
    while q:
        y, x = q.popleft()
        
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
                q.append((ny, nx))
    
    return len(visited)


def debug_evaluation(board, ai_player):
    """
    Print detailed evaluation breakdown for debugging.
    """
    
    opponent = board.p1 if ai_player == board.p2 else board.p2
    
    print("=== Evaluation Breakdown ===")
    print(f"AI Path Length: {_shortest_path_length(board, ai_player)}")
    print(f"Opponent Path Length: {_shortest_path_length(board, opponent)}")
    print(f"Path Difference: {_evaluate_path_difference(board, ai_player, opponent)}")
    print(f"Wall Score: {_evaluate_walls(ai_player, opponent)}")
    print(f"Position Score: {_evaluate_position(board, ai_player, opponent)}")
    print(f"Blocking Score: {_evaluate_blocking_potential(board, ai_player, opponent)}")
    print(f"Total Score: {evaluate_board(board, ai_player)}")
    print("===========================")