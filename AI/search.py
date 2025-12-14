# AI/search.py 

import math
import heapq
from AI.move_generator import generate_all_moves


# Wall codes (should match your Config.py)
PAWN_MOVE_CODE = "pawn"
WALL_MOVE_CODE = "wall"
VERTICAL_CONNECTOR_CODE = 2
HORIZONTAL_CONNECTOR_CODE = 3


def find_best_move(board, ai_player, search_depth, wall_bonus_weight=1.0):
    """
    Find best move using Alpha-Beta search.
    Same logic as colleague's ai_move().
    
    Args:
        board: Board object
        ai_player: AIPlayer instance
        search_depth: how deep to search
        wall_bonus_weight: weight for wall count in evaluation
    
    Returns:
        (move_type, move_data) tuple or None
    """
    # Create virtual board state
    virtual_board = _create_virtual_board(board)
    
    # Generate valid moves for AI (maximizing player)
    valid_moves = generate_all_moves(board, ai_player)
    
    if not valid_moves:
        return None
    
    # Check for immediate winning move (same as colleague's fast_win_move)
    for move in valid_moves:
        if move[0] == PAWN_MOVE_CODE and move[1][0] == ai_player.objective:
            return move  # Instant win!
    
    # Find best move via alpha-beta
    best_move = None
    best_value = -math.inf
    
    for move in valid_moves:
        # Apply move to virtual board
        new_virtual_board = _apply_move_virtual(board, virtual_board, move, maximizing=True)
        
        # Evaluate with alpha-beta (opponent's turn next, so maximizing=False)
        value = _alpha_beta(
            board, 
            new_virtual_board, 
            search_depth, 
            -math.inf, 
            math.inf, 
            False,  # Opponent's turn
            wall_bonus_weight
        )
        
        if value > best_value:
            best_value = value
            best_move = move
    
    return best_move


def _alpha_beta(board, virtual_board, depth, alpha, beta, maximizing, wall_bonus_weight):
    """
    Alpha-Beta pruning - same logic as colleague's alpha_beta().
    
    Args:
        board: Board object (for dimension info)
        virtual_board: [p1_state, p2_state, grid]
        depth: remaining search depth
        alpha: best for maximizer
        beta: best for minimizer
        maximizing: True if AI's turn
        wall_bonus_weight: evaluation weight
    
    Returns:
        evaluation score
    """
    # Terminal check: Player 1 reached objective
    if virtual_board[0][0][0] == board.p1.objective:
        return -math.inf if maximizing else math.inf
    
    # Terminal check: Player 2 (AI) reached objective
    if virtual_board[1][0][0] == board.p2.objective:
        return math.inf if maximizing else -math.inf
    
    # Depth limit reached - evaluate
    if depth == 0:
        return _heuristic(board, virtual_board, wall_bonus_weight)
    
    # Generate valid moves
    valid_moves = _get_valid_moves_virtual(board, virtual_board, maximizing)
    
    if not valid_moves:
        return _heuristic(board, virtual_board, wall_bonus_weight)
    
    # Move ordering: prioritize winning moves (same as colleague)
    valid_moves.sort(key=lambda m: 0 if m[0] == PAWN_MOVE_CODE and (
        (maximizing and m[1][0] == board.p2.objective) or
        (not maximizing and m[1][0] == board.p1.objective)
    ) else 1)
    
    if maximizing:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = _apply_move_virtual(board, virtual_board, move, maximizing=True)
            eval_score = _alpha_beta(board, new_board, depth - 1, alpha, beta, False, wall_bonus_weight)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = _apply_move_virtual(board, virtual_board, move, maximizing=False)
            eval_score = _alpha_beta(board, new_board, depth - 1, alpha, beta, True, wall_bonus_weight)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval


def _heuristic(board, virtual_board, wall_bonus_weight):
    """
    Evaluation function - EXACTLY matches colleague's heuristic().
    """
    p1_path = _astar_path(board, virtual_board, virtual_board[0][0], board.p1.objective)
    p2_path = _astar_path(board, virtual_board, virtual_board[1][0], board.p2.objective)
    
    # Terminal states
    if p1_path == 0:
        return -math.inf
    if p2_path == 0:
        return math.inf
    
    # Same formula as colleague
    path_diff = (p1_path - p2_path) * 4
    wall_bonus = virtual_board[1][1] * wall_bonus_weight  # AI (p2) wall count
    
    return path_diff + wall_bonus


def _astar_path(board, virtual_board, start_pos, target_row):
    """
    A* pathfinding - same as colleague's a_star_path().
    """
    dim = board.dimBoard
    grid = virtual_board[2]
    
    visited = [[False] * dim for _ in range(dim)]
    # (f_score, g_score, y, x)
    heap = [(abs(start_pos[0] - target_row), 0, start_pos[0], start_pos[1])]
    
    directions = [
        (-2, 0, -1, 0),  # Up
        (2, 0, 1, 0),    # Down
        (0, -2, 0, -1),  # Left
        (0, 2, 0, 1)     # Right
    ]
    
    while heap:
        f, g, y, x = heapq.heappop(heap)
        
        if y == target_row:
            return g
        
        if visited[y][x]:
            continue
        visited[y][x] = True
        
        for dy, dx, wy, wx in directions:
            ny, nx = y + dy, x + dx
            wall_y, wall_x = y + wy, x + wx
            
            if 0 <= ny < dim and 0 <= nx < dim:
                if not grid[wall_y][wall_x] and not visited[ny][nx]:
                    h = abs(ny - target_row)
                    heapq.heappush(heap, (g + 1 + h, g + 1, ny, nx))
    
    return math.inf  # No path


def _create_virtual_board(board):
    """
    Create virtual board state - same structure as colleague's.
    
    Structure:
    [
        [p1_pos, p1_walls],   # Player 1 state
        [p2_pos, p2_walls],   # Player 2 state  
        grid                  # 2D list copy
    ]
    """
    dim = board.dimBoard
    grid_copy = [[board.board[y, x] for x in range(dim)] for y in range(dim)]
    
    return [
        [list(board.p1.pos), board.p1.available_walls],
        [list(board.p2.pos), board.p2.available_walls],
        grid_copy
    ]


def _apply_move_virtual(board, virtual_board, move, maximizing):
    """
    Apply move to virtual board - EXACTLY matches colleague's apply_move().
    Returns new virtual board (doesn't modify original).
    """
    # Deep copy
    new_virtual_board = [
        [virtual_board[0][0].copy(), virtual_board[0][1]],
        [virtual_board[1][0].copy(), virtual_board[1][1]],
        [row.copy() for row in virtual_board[2]]
    ]
    
    # Player index: maximizing = AI = p2 = index 1
    player_idx = 1 if maximizing else 0
    player_id = board.p2.id if maximizing else board.p1.id
    
    move_type, move_data = move
    
    if move_type == PAWN_MOVE_CODE:
        # Clear old position
        old_pos = virtual_board[player_idx][0]
        new_virtual_board[2][old_pos[0]][old_pos[1]] = 0
        
        # Set new position
        new_pos = move_data
        new_virtual_board[player_idx][0] = list(new_pos)
        new_virtual_board[2][new_pos[0]][new_pos[1]] = player_id
    
    else:  # WALL_MOVE_CODE
        coord1, coord2, coord3 = move_data
        
        new_virtual_board[2][coord1[0]][coord1[1]] = 1
        new_virtual_board[2][coord3[0]][coord3[1]] = 1
        
        # Connector type based on orientation
        if coord1[0] == coord2[0]:  # Same row = horizontal
            new_virtual_board[2][coord2[0]][coord2[1]] = HORIZONTAL_CONNECTOR_CODE
        else:  # Same column = vertical
            new_virtual_board[2][coord2[0]][coord2[1]] = VERTICAL_CONNECTOR_CODE
        
        # Decrease wall count
        new_virtual_board[player_idx][1] -= 1
    
    return new_virtual_board


def _get_valid_moves_virtual(board, virtual_board, maximizing):
    """
    Generate valid moves from virtual board - matches colleague's get_valid_moves().
    """
    moves = []
    dim = board.dimBoard
    grid = virtual_board[2]
    
    # Current player info
    player_idx = 1 if maximizing else 0
    opponent_idx = 0 if maximizing else 1
    
    py, px = virtual_board[player_idx][0]
    oy, ox = virtual_board[opponent_idx][0]
    remaining_walls = virtual_board[player_idx][1]
    
    # Directions
    directions = {
        'up':    (-2, 0, -1, 0),
        'down':  (2, 0, 1, 0),
        'left':  (0, -2, 0, -1),
        'right': (0, 2, 0, 1),
    }
    
    # Generate pawn moves (same logic as colleague)
    for dy, dx, wy, wx in directions.values():
        ny, nx = py + dy, px + dx
        wall_y, wall_x = py + wy, px + wx
        
        # Check wall position bounds and blocking
        if not (0 <= wall_y < dim and 0 <= wall_x < dim):
            continue
        if grid[wall_y][wall_x]:
            continue
        
        # Opponent in the way - jump logic
        if (ny, nx) == (oy, ox):
            # Try straight jump
            jy, jx = ny + dy, nx + dx
            jwy, jwx = ny + wy, nx + wx
            
            if (0 <= jy < dim and 0 <= jx < dim and
                0 <= jwy < dim and 0 <= jwx < dim and
                not grid[jwy][jwx] and not grid[jy][jx]):
                moves.append((PAWN_MOVE_CODE, (jy, jx)))
                continue
            
            # Side steps (diagonal jumps)
            if dy != 0:  # Moving vertically, try horizontal sides
                for sdx, swx in [(-2, -1), (2, 1)]:
                    sy, sx = ny, nx + sdx
                    swy, swx_pos = ny, nx + swx
                    if (0 <= sx < dim and
                        not grid[swy][swx_pos] and not grid[sy][sx]):
                        moves.append((PAWN_MOVE_CODE, (sy, sx)))
            else:  # Moving horizontally, try vertical sides
                for sdy, swy in [(-2, -1), (2, 1)]:
                    sy, sx = ny + sdy, nx
                    swy_pos, swx = ny + swy, nx
                    if (0 <= sy < dim and
                        not grid[swy_pos][swx] and not grid[sy][sx]):
                        moves.append((PAWN_MOVE_CODE, (sy, sx)))
        else:
            # Regular move
            if 0 <= ny < dim and 0 <= nx < dim and not grid[ny][nx]:
                moves.append((PAWN_MOVE_CODE, (ny, nx)))
    
    # Generate wall moves if available
    if remaining_walls > 0:
        wall_moves = _get_wall_moves_virtual(board, virtual_board, dim)
        moves.extend(wall_moves)
    
    return moves


def _get_wall_moves_virtual(board, virtual_board, dim):
    """
    Generate wall placements - same as colleague's wall generation.
    """
    moves = []
    grid = virtual_board[2]
    
    # Goal rows for path checking
    p1_goal = board.p1.objective
    p2_goal = board.p2.objective
    
    for y in range(1, dim - 1, 2):
        for x in range(1, dim - 1, 2):
            # Try horizontal: (y, x-1), (y, x), (y, x+1)
            if x - 1 >= 0 and x + 1 < dim:
                cells = ((y, x - 1), (y, x), (y, x + 1))
                if not any(grid[cy][cx] for cy, cx in cells):
                    if _wall_valid_virtual(virtual_board, cells, dim, p1_goal, p2_goal):
                        moves.append((WALL_MOVE_CODE, cells))
            
            # Try vertical: (y-1, x), (y, x), (y+1, x)
            if y - 1 >= 0 and y + 1 < dim:
                cells = ((y - 1, x), (y, x), (y + 1, x))
                if not any(grid[cy][cx] for cy, cx in cells):
                    if _wall_valid_virtual(virtual_board, cells, dim, p1_goal, p2_goal):
                        moves.append((WALL_MOVE_CODE, cells))
    
    return moves


def _wall_valid_virtual(virtual_board, cells, dim, p1_goal, p2_goal):
    """
    Check wall doesn't block either player - same as colleague's has_path.
    """
    grid = virtual_board[2]
    
    # Temporarily place wall
    for cy, cx in cells:
        grid[cy][cx] = 1
    
    # Check both players have paths
    p1_ok = _has_path_virtual(grid, virtual_board[0][0], p1_goal, dim)
    p2_ok = _has_path_virtual(grid, virtual_board[1][0], p2_goal, dim)
    
    # Remove wall
    for cy, cx in cells:
        grid[cy][cx] = 0
    
    return p1_ok and p2_ok


def _has_path_virtual(grid, start, goal_row, dim):
    """
    BFS path check - same as colleague's has_path.
    """
    from collections import deque
    
    visited = [[False] * dim for _ in range(dim)]
    queue = deque([tuple(start)])
    visited[start[0]][start[1]] = True
    
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
    while queue:
        y, x = queue.popleft()
        
        if y == goal_row:
            return True
        
        for dy, dx, wy, wx in directions:
            ny, nx = y + dy, x + dx
            wall_y, wall_x = y + wy, x + wx
            
            if (0 <= ny < dim and 0 <= nx < dim and
                not grid[wall_y][wall_x] and not visited[ny][nx]):
                visited[ny][nx] = True
                queue.append((ny, nx))
    
    return False


def apply_move_to_board(board, move, player):
    """
    Apply move to actual board (not virtual) - same as colleague's apply_move with is_virtual=False.
    """
    move_type, move_data = move
    grid = board.board
    
    if move_type == PAWN_MOVE_CODE:
        # Clear old position
        grid[player.pos[0], player.pos[1]] = 0
        
        # Set new position
        new_y, new_x = move_data
        player.pos = [new_y, new_x]
        grid[new_y, new_x] = player.id
    
    else:  # WALL_MOVE_CODE
        coord1, coord2, coord3 = move_data
        
        grid[coord1[0], coord1[1]] = 1
        grid[coord3[0], coord3[1]] = 1
        
        # Connector type
        if coord1[0] == coord2[0]:  # Horizontal
            grid[coord2[0], coord2[1]] = HORIZONTAL_CONNECTOR_CODE
        else:  # Vertical
            grid[coord2[0], coord2[1]] = VERTICAL_CONNECTOR_CODE
        
        player.available_walls -= 2  # Each wall costs 2