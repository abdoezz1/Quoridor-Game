# AI/search.py - OPTIMIZED with smart wall selection

import math
import heapq
from collections import deque, Counter


# Move codes
PAWN_MOVE_CODE = "pawn"
WALL_MOVE_CODE = "wall"
VERTICAL_CONNECTOR_CODE = 2
HORIZONTAL_CONNECTOR_CODE = 3

# Performance tuning
MAX_WALL_CANDIDATES = 30  # Evaluate top N strategic walls






# =============================================================================
# VIRTUAL BOARD
# =============================================================================

def _create_virtual_board(board):
    """Create virtual board state for search."""
    dim = board.dimBoard
    grid_copy = [[board.board[y, x] for x in range(dim)] for y in range(dim)]
    
    return [
        [[int(board.p1.pos[0]), int(board.p1.pos[1])], board.p1.available_walls],
        [[int(board.p2.pos[0]), int(board.p2.pos[1])], board.p2.available_walls],
        grid_copy
    ]


def _apply_move_virtual(board, virtual_board, move, maximizing):
    """Apply move to virtual board and return new state."""
    new_virtual_board = [
        [virtual_board[0][0].copy(), virtual_board[0][1]],
        [virtual_board[1][0].copy(), virtual_board[1][1]],
        [row.copy() for row in virtual_board[2]]
    ]
    
    player_idx = 1 if maximizing else 0
    player_id = board.p2.id if maximizing else board.p1.id
    
    move_type, move_data = move
    
    if move_type == PAWN_MOVE_CODE:
        old_pos = virtual_board[player_idx][0]
        new_virtual_board[2][old_pos[0]][old_pos[1]] = 0
        
        new_y, new_x = int(move_data[0]), int(move_data[1])
        new_virtual_board[player_idx][0] = [new_y, new_x]
        new_virtual_board[2][new_y][new_x] = player_id
    else:
        coord1, coord2, coord3 = move_data
        
        new_virtual_board[2][coord1[0]][coord1[1]] = 1
        new_virtual_board[2][coord3[0]][coord3[1]] = 1
        
        if coord1[0] == coord2[0]:
            new_virtual_board[2][coord2[0]][coord2[1]] = HORIZONTAL_CONNECTOR_CODE
        else:
            new_virtual_board[2][coord2[0]][coord2[1]] = VERTICAL_CONNECTOR_CODE
        
        new_virtual_board[player_idx][1] -= 1
    
    return new_virtual_board


def apply_move_to_board(board, move, player):
    """Apply move to actual game board."""
    move_type, move_data = move
    grid = board.board
    
    if move_type == PAWN_MOVE_CODE:
        grid[player.pos[0], player.pos[1]] = 0
        
        new_y, new_x = int(move_data[0]), int(move_data[1])
        player.pos = [new_y, new_x]
        grid[new_y, new_x] = player.id
    else:
        coord1, coord2, coord3 = move_data
        
        grid[coord1[0], coord1[1]] = 1
        grid[coord3[0], coord3[1]] = 1
        
        if coord1[0] == coord2[0]:
            grid[coord2[0], coord2[1]] = HORIZONTAL_CONNECTOR_CODE
        else:
            grid[coord2[0], coord2[1]] = VERTICAL_CONNECTOR_CODE
        
        player.available_walls -= 1


# =============================================================================
# PATHFINDING
# =============================================================================

def _astar_path(virtual_board, start_pos, target_row, dim):
    """A* pathfinding to find shortest path to goal row."""
    grid = virtual_board[2]
    
    start_y = int(start_pos[0])
    start_x = int(start_pos[1])
    
    if start_y == target_row:
        return 0
    
    visited = set()
    heap = [(abs(start_y - target_row), 0, start_y, start_x)]
    
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
    while heap:
        f, g, y, x = heapq.heappop(heap)
        
        if y == target_row:
            return g
        
        if (y, x) in visited:
            continue
        visited.add((y, x))
        
        for dy, dx, wy, wx in directions:
            ny, nx = y + dy, x + dx
            wall_y, wall_x = y + wy, x + wx
            
            if 0 <= ny < dim and 0 <= nx < dim:
                if 0 <= wall_y < dim and 0 <= wall_x < dim:
                    if not grid[wall_y][wall_x] and (ny, nx) not in visited:
                        h = abs(ny - target_row)
                        heapq.heappush(heap, (g + 1 + h, g + 1, ny, nx))
    
    return math.inf


def _has_path_fast(grid, start, goal_row, dim):
    """Fast BFS path check."""
    start_y, start_x = int(start[0]), int(start[1])
    
    if start_y == goal_row:
        return True
    
    visited = set()
    visited.add((start_y, start_x))
    queue = deque([(start_y, start_x)])
    
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
    while queue:
        y, x = queue.popleft()
        
        for dy, dx, wy, wx in directions:
            ny, nx = y + dy, x + dx
            wall_y, wall_x = y + wy, x + wx
            
            if not (0 <= ny < dim and 0 <= nx < dim):
                continue
            if not (0 <= wall_y < dim and 0 <= wall_x < dim):
                continue
            if grid[wall_y][wall_x]:
                continue
            if (ny, nx) in visited:
                continue
            
            if ny == goal_row:
                return True
            
            visited.add((ny, nx))
            queue.append((ny, nx))
    
    return False


# =============================================================================
# MOVE GENERATION
# =============================================================================

def _get_valid_moves_virtual(board, virtual_board, maximizing):
    """Generate all valid moves for current player."""
    moves = []
    dim = board.dimBoard
    grid = virtual_board[2]
    
    player_idx = 1 if maximizing else 0
    opponent_idx = 0 if maximizing else 1
    
    py, px = virtual_board[player_idx][0]
    oy, ox = virtual_board[opponent_idx][0]
    remaining_walls = virtual_board[player_idx][1]
    
    py, px = int(py), int(px)
    oy, ox = int(oy), int(ox)
    
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
    # Generate pawn moves
    for dy, dx, wy, wx in directions:
        ny, nx = py + dy, px + dx
        wall_y, wall_x = py + wy, px + wx
        
        if not (0 <= wall_y < dim and 0 <= wall_x < dim):
            continue
        if grid[wall_y][wall_x]:
            continue
        
        if (ny, nx) == (oy, ox):
            # Jump over opponent
            jy, jx = ny + dy, nx + dx
            jwy, jwx = ny + wy, nx + wx
            
            if (0 <= jy < dim and 0 <= jx < dim and
                0 <= jwy < dim and 0 <= jwx < dim and
                not grid[jwy][jwx] and not grid[jy][jx]):
                moves.append((PAWN_MOVE_CODE, (jy, jx)))
                continue
            
            # Diagonal jumps
            if dy != 0:
                for sdx, swx in [(-2, -1), (2, 1)]:
                    sy, sx = ny, nx + sdx
                    swy, swx_pos = ny, nx + swx
                    if (0 <= sx < dim and 0 <= swx_pos < dim and
                        not grid[swy][swx_pos] and not grid[sy][sx]):
                        moves.append((PAWN_MOVE_CODE, (sy, sx)))
            else:
                for sdy, swy in [(-2, -1), (2, 1)]:
                    sy, sx = ny + sdy, nx
                    swy_pos, swx = ny + swy, nx
                    if (0 <= sy < dim and 0 <= swy_pos < dim and
                        not grid[swy_pos][swx] and not grid[sy][sx]):
                        moves.append((PAWN_MOVE_CODE, (sy, sx)))
        else:
            if 0 <= ny < dim and 0 <= nx < dim and not grid[ny][nx]:
                moves.append((PAWN_MOVE_CODE, (ny, nx)))
    
    # Generate wall moves with smart selection
    if remaining_walls > 0:
        wall_moves = _get_wall_moves_smart(virtual_board, dim, board, maximizing)
        moves.extend(wall_moves)
    
    return moves


def _get_wall_moves_smart(virtual_board, dim, board, maximizing):
    """
    Generate wall placements prioritized by strategic value.
    Considers walls that:
    1. Block opponent's path to their goal
    2. Are near the action (both players)
    3. Protect AI's path
    """
    grid = virtual_board[2]
    p1_goal = board.p1.objective
    p2_goal = board.p2.objective
    
    # Positions
    ai_y, ai_x = virtual_board[1][0]
    opp_y, opp_x = virtual_board[0][0]
    
    ai_y, ai_x = int(ai_y), int(ai_x)
    opp_y, opp_x = int(opp_y), int(opp_x)
    
    candidates = []
    
    for y in range(1, dim - 1, 2):
        for x in range(1, dim - 1, 2):
            if grid[y][x]:
                continue
            
            # Calculate strategic priority (lower = better)
            priority = _calculate_wall_priority(
                y, x, ai_y, ai_x, opp_y, opp_x, p1_goal, p2_goal
            )
            
            # Horizontal wall
            if x - 1 >= 0 and x + 1 < dim:
                cells = ((y, x - 1), (y, x), (y, x + 1))
                if not any(grid[cy][cx] for cy, cx in cells):
                    # Horizontal walls block vertical movement
                    # Better for blocking opponent moving up/down
                    h_priority = priority
                    if p1_goal == 0:  # Opponent moving up
                        h_priority -= 5  # Horizontal walls help
                    else:
                        h_priority -= 5
                    candidates.append((h_priority, cells))
            
            # Vertical wall
            if y - 1 >= 0 and y + 1 < dim:
                cells = ((y - 1, x), (y, x), (y + 1, x))
                if not any(grid[cy][cx] for cy, cx in cells):
                    candidates.append((priority, cells))
    
    # Sort by priority and take top candidates
    candidates.sort(key=lambda c: c[0])
    candidates = candidates[:MAX_WALL_CANDIDATES]
    
    # Validate only top candidates
    moves = []
    for priority, cells in candidates:
        if _wall_valid_fast(virtual_board, cells, dim, p1_goal, p2_goal):
            moves.append((WALL_MOVE_CODE, cells))
    
    return moves


def _calculate_wall_priority(wall_y, wall_x, ai_y, ai_x, opp_y, opp_x, p1_goal, p2_goal):
    """
    Calculate strategic priority for a wall position.
    Lower priority = more valuable wall.
    """
    # Distance to opponent
    dist_to_opp = abs(wall_y - opp_y) + abs(wall_x - opp_x)
    
    # Distance to AI
    dist_to_ai = abs(wall_y - ai_y) + abs(wall_x - ai_x)
    
    # Is wall between opponent and their goal?
    if p1_goal == 0:  # Opponent moving up (decreasing row)
        blocks_opponent_path = wall_y < opp_y
        between_opp_and_goal = wall_y < opp_y
    else:  # Opponent moving down (increasing row)
        blocks_opponent_path = wall_y > opp_y
        between_opp_and_goal = wall_y > opp_y
    
    # Is wall between AI and AI's goal?
    if p2_goal == 16:  # AI moving down
        helps_ai = wall_y < ai_y  # Wall behind AI doesn't block us
    else:  # AI moving up
        helps_ai = wall_y > ai_y
    
    # Calculate priority
    priority = 0
    
    # Walls blocking opponent's path are valuable
    if blocks_opponent_path:
        # Closer to opponent = more immediately useful
        priority = dist_to_opp
        
        # Walls in opponent's column are extra valuable
        if abs(wall_x - opp_x) <= 2:
            priority -= 10
    else:
        # Walls behind opponent are less useful
        priority = 50 + dist_to_opp
    
    # Avoid walls that might block our own path
    if not helps_ai and dist_to_ai <= 4:
        priority += 20
    
    # Walls near center of action (between players) are good
    mid_y = (ai_y + opp_y) // 2
    dist_to_mid = abs(wall_y - mid_y)
    priority += dist_to_mid // 2
    
    return priority


def _wall_valid_fast(virtual_board, cells, dim, p1_goal, p2_goal):
    """Check if wall placement leaves valid paths for both players."""
    grid = virtual_board[2]
    
    # Temporarily place wall
    for cy, cx in cells:
        grid[cy][cx] = 1
    
    # Check paths
    p1_ok = _has_path_fast(grid, virtual_board[0][0], p1_goal, dim)
    p2_ok = p1_ok and _has_path_fast(grid, virtual_board[1][0], p2_goal, dim)
    
    # Remove wall
    for cy, cx in cells:
        grid[cy][cx] = 0
    
    return p1_ok and p2_ok


# =============================================================================
# EVALUATION
# =============================================================================

def _heuristic(board, virtual_board, wall_bonus_weight):
    """Evaluate board position."""
    dim = board.dimBoard
    
    p1_path = _astar_path(virtual_board, virtual_board[0][0], board.p1.objective, dim)
    p2_path = _astar_path(virtual_board, virtual_board[1][0], board.p2.objective, dim)
    
    if p1_path == 0:
        return -math.inf
    if p2_path == 0:
        return math.inf
    
    # Path difference (main factor)
    path_diff = (p1_path - p2_path) * 4
    
    # Wall bonus
    wall_bonus = virtual_board[1][1] * wall_bonus_weight
    
    # Progress bonus for AI
    ai_row = int(virtual_board[1][0][0])
    ai_objective = board.p2.objective
    
    if ai_objective == 16:
        progress_bonus = ai_row / 16.0
    else:
        progress_bonus = (16 - ai_row) / 16.0
    
    return path_diff + wall_bonus + progress_bonus


# =============================================================================
# ALPHA-BETA SEARCH
# =============================================================================

def _alpha_beta(board, virtual_board, depth, alpha, beta, maximizing, wall_bonus_weight):
    """Alpha-Beta pruning minimax search."""
    # Terminal checks - ALWAYS from AI (P2) perspective
    if virtual_board[0][0][0] == board.p1.objective:
        return -math.inf  # P1 wins = bad for AI
    
    if virtual_board[1][0][0] == board.p2.objective:
        return math.inf   # P2 wins = good for AI
    
    # Depth limit
    if depth == 0:
        return _heuristic(board, virtual_board, wall_bonus_weight)
    
    valid_moves = _get_valid_moves_virtual(board, virtual_board, maximizing)
    
    if not valid_moves:
        return _heuristic(board, virtual_board, wall_bonus_weight)
    
    # Move ordering: winning moves first, then pawn moves, then walls
    target_row = board.p2.objective if maximizing else board.p1.objective
    valid_moves.sort(key=lambda m: (
        -100 if m[0] == PAWN_MOVE_CODE and m[1][0] == target_row else
        0 if m[0] == PAWN_MOVE_CODE else
        10
    ))
    
    if maximizing:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = _apply_move_virtual(board, virtual_board, move, True)
            eval_score = _alpha_beta(board, new_board, depth - 1, alpha, beta, False, wall_bonus_weight)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = _apply_move_virtual(board, virtual_board, move, False)
            eval_score = _alpha_beta(board, new_board, depth - 1, alpha, beta, True, wall_bonus_weight)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


# =============================================================================
# OSCILLATION DETECTION
# =============================================================================

def _detect_oscillation(position_history):
    """Detect if AI is stuck oscillating between positions."""
    if len(position_history) < 4:
        return False
    
    counts = Counter(position_history)
    return any(count >= 2 for count in counts.values())


# =============================================================================
# MAIN SEARCH FUNCTION
# =============================================================================

def find_best_move(board, ai_player, search_depth, wall_bonus_weight=1.0, position_history=None):
    """Find best move using Alpha-Beta search with oscillation prevention."""
    if position_history is None:
        position_history = []
    
    virtual_board = _create_virtual_board(board)
    valid_moves = _get_valid_moves_virtual(board, virtual_board, maximizing=True)
    
    if not valid_moves:
        return None
    
    # Instant win check
    for move in valid_moves:
        if move[0] == PAWN_MOVE_CODE and move[1][0] == ai_player.objective:
            return move
    
    # Sort: pawn moves first
    valid_moves.sort(key=lambda m: (0 if m[0] == PAWN_MOVE_CODE else 1))
    
    # Detect oscillation
    is_stuck = _detect_oscillation(position_history)
    

    
    best_move = None
    best_value = -math.inf
    
    for move in valid_moves:
        new_virtual_board = _apply_move_virtual(board, virtual_board, move, True)
        
        value = _alpha_beta(
            board,
            new_virtual_board,
            search_depth - 1,
            -math.inf,
            math.inf,
            False,
            wall_bonus_weight
        )
        
        # Oscillation penalty for pawn moves (escalating)
        if move[0] == PAWN_MOVE_CODE and position_history:
            move_pos = (int(move[1][0]), int(move[1][1]))
            visit_count = position_history.count(move_pos)
            if visit_count > 0:
                penalty = visit_count * (visit_count + 1) / 2
                value -= penalty
        
        # Wall bonus when stuck
        if move[0] == WALL_MOVE_CODE and is_stuck:
            value += 2.0
        

        
        if value > best_value or best_move is None:
            best_value = value
            best_move = move
        
        if value == math.inf:
            break
    

    
    return best_move