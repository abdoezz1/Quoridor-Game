# AI/search.py - OPTIMIZED VERSION

import math
import heapq
from collections import deque


# Move codes
PAWN_MOVE_CODE = "pawn"
WALL_MOVE_CODE = "wall"
VERTICAL_CONNECTOR_CODE = 2
HORIZONTAL_CONNECTOR_CODE = 3

# Performance tuning
MAX_WALL_CANDIDATES = 15  # Only evaluate top N wall moves


def find_best_move(board, ai_player, search_depth, wall_bonus_weight=1.0):
    """
    Find best move using Alpha-Beta search.
    """
    virtual_board = _create_virtual_board(board)
    valid_moves = _get_valid_moves_virtual(board, virtual_board, maximizing=True)
    
    if not valid_moves:
        return None
    
    # Instant win check
    for move in valid_moves:
        if move[0] == PAWN_MOVE_CODE and move[1][0] == ai_player.objective:
            return move
    
    # Move ordering: pawn moves first (faster to evaluate)
    valid_moves.sort(key=lambda m: (0 if m[0] == PAWN_MOVE_CODE else 1))
    
    best_move = None
    best_value = -math.inf
    
    for move in valid_moves:
        new_virtual_board = _apply_move_virtual(board, virtual_board, move, maximizing=True)
        
        value = _alpha_beta(
            board,
            new_virtual_board,
            search_depth - 1,
            -math.inf,
            math.inf,
            False,
            wall_bonus_weight
        )
        
        if value > best_value or best_move is None:
            best_value = value
            best_move = move
        
        # Early exit if we found a winning move
        if value == math.inf:
            break
    
    return best_move


def _alpha_beta(board, virtual_board, depth, alpha, beta, maximizing, wall_bonus_weight):
    """
    Alpha-Beta pruning with optimizations.
    """
    # Terminal checks
    if virtual_board[0][0][0] == board.p1.objective:
        return -math.inf if maximizing else math.inf
    
    if virtual_board[1][0][0] == board.p2.objective:
        return math.inf if maximizing else -math.inf
    
    # Depth limit
    if depth == 0:
        return _heuristic(board, virtual_board, wall_bonus_weight)
    
    valid_moves = _get_valid_moves_virtual(board, virtual_board, maximizing)
    
    if not valid_moves:
        return _heuristic(board, virtual_board, wall_bonus_weight)
    
    # Move ordering: winning moves first, then pawn moves, then walls
    target_row = board.p2.objective if maximizing else board.p1.objective
    valid_moves.sort(key=lambda m: _move_priority(m, target_row))
    
    if maximizing:
        max_eval = -math.inf
        for move in valid_moves:
            new_board = _apply_move_virtual(board, virtual_board, move, maximizing=True)
            eval_score = _alpha_beta(board, new_board, depth - 1, alpha, beta, False, wall_bonus_weight)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in valid_moves:
            new_board = _apply_move_virtual(board, virtual_board, move, maximizing=False)
            eval_score = _alpha_beta(board, new_board, depth - 1, alpha, beta, True, wall_bonus_weight)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def _move_priority(move, target_row):
    """
    Assign priority for move ordering. Lower = evaluated first.
    """
    move_type, move_data = move
    
    if move_type == PAWN_MOVE_CODE:
        # Winning move = highest priority
        if move_data[0] == target_row:
            return -100
        # Other pawn moves = high priority
        return 0
    else:
        # Wall moves = lower priority
        return 10


def _heuristic(board, virtual_board, wall_bonus_weight):
    """
    Fast evaluation function.
    """
    p1_path = _astar_path(virtual_board, virtual_board[0][0], board.p1.objective, board.dimBoard)
    p2_path = _astar_path(virtual_board, virtual_board[1][0], board.p2.objective, board.dimBoard)
    
    if p1_path == 0:
        return -math.inf
    if p2_path == 0:
        return math.inf
    
    path_diff = (p1_path - p2_path) * 4
    wall_bonus = virtual_board[1][1] * wall_bonus_weight
    
    return path_diff + wall_bonus


def _astar_path(virtual_board, start_pos, target_row, dim):
    """
    A* pathfinding - optimized.
    """
    grid = virtual_board[2]
    
    # Convert numpy types to int
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
                if not grid[wall_y][wall_x] and (ny, nx) not in visited:
                    h = abs(ny - target_row)
                    heapq.heappush(heap, (g + 1 + h, g + 1, ny, nx))
    
    return math.inf


def _create_virtual_board(board):
    """
    Create virtual board state.
    """
    dim = board.dimBoard
    grid_copy = [[board.board[y, x] for x in range(dim)] for y in range(dim)]
    
    return [
        [[int(board.p1.pos[0]), int(board.p1.pos[1])], board.p1.available_walls],
        [[int(board.p2.pos[0]), int(board.p2.pos[1])], board.p2.available_walls],
        grid_copy
    ]


def _apply_move_virtual(board, virtual_board, move, maximizing):
    """
    Apply move to virtual board.
    """
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
        
        new_virtual_board[player_idx][1] -= 1  # FIXED: was -= 2
    
    return new_virtual_board


def _get_valid_moves_virtual(board, virtual_board, maximizing):
    """
    Generate valid moves - OPTIMIZED with limited wall moves.
    """
    moves = []
    dim = board.dimBoard
    grid = virtual_board[2]
    
    player_idx = 1 if maximizing else 0
    opponent_idx = 0 if maximizing else 1
    
    py, px = virtual_board[player_idx][0]
    oy, ox = virtual_board[opponent_idx][0]
    remaining_walls = virtual_board[player_idx][1]
    
    # Convert to int to avoid numpy issues
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
            # Jump logic
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
    
    # Generate LIMITED wall moves
    if remaining_walls > 0:
        wall_moves = _get_wall_moves_limited(virtual_board, dim, py, px, oy, ox, board)
        moves.extend(wall_moves)
    
    return moves


def _get_wall_moves_limited(virtual_board, dim, py, px, oy, ox, board):
    """
    Generate LIMITED wall placements - only strategic ones near players.
    """
    grid = virtual_board[2]
    p1_goal = board.p1.objective
    p2_goal = board.p2.objective
    
    # Collect wall candidates with priority scores
    candidates = []
    
    for y in range(1, dim - 1, 2):
        for x in range(1, dim - 1, 2):
            if grid[y][x]:
                continue
            
            # Priority: closer to opponent = more strategic
            dist_to_opp = abs(y - oy) + abs(x - ox)
            dist_to_self = abs(y - py) + abs(x - px)
            priority = dist_to_opp  # Lower = better
            
            # Horizontal wall
            if x - 1 >= 0 and x + 1 < dim:
                cells = ((y, x - 1), (y, x), (y, x + 1))
                if not any(grid[cy][cx] for cy, cx in cells):
                    candidates.append((priority, cells))
            
            # Vertical wall
            if y - 1 >= 0 and y + 1 < dim:
                cells = ((y - 1, x), (y, x), (y + 1, x))
                if not any(grid[cy][cx] for cy, cx in cells):
                    candidates.append((priority, cells))
    
    # Sort by priority and take top candidates only
    candidates.sort(key=lambda c: c[0])
    candidates = candidates[:MAX_WALL_CANDIDATES]
    
    # Validate only the top candidates
    moves = []
    for priority, cells in candidates:
        if _wall_valid_fast(virtual_board, cells, dim, p1_goal, p2_goal):
            moves.append((WALL_MOVE_CODE, cells))
    
    return moves


def _wall_valid_fast(virtual_board, cells, dim, p1_goal, p2_goal):
    """
    Fast wall validation using BFS.
    """
    grid = virtual_board[2]
    
    # Temporarily place wall
    for cy, cx in cells:
        grid[cy][cx] = 1
    
    # Check paths
    p1_ok = _has_path_fast(grid, virtual_board[0][0], p1_goal, dim)
    p2_ok = p1_ok and _has_path_fast(grid, virtual_board[1][0], p2_goal, dim)  # Short-circuit
    
    # Remove wall
    for cy, cx in cells:
        grid[cy][cx] = 0
    
    return p1_ok and p2_ok


def _has_path_fast(grid, start, goal_row, dim):
    """
    Fast BFS path check.
    """
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
            if grid[wall_y][wall_x]:
                continue
            if (ny, nx) in visited:
                continue
            
            if ny == goal_row:
                return True
            
            visited.add((ny, nx))
            queue.append((ny, nx))
    
    return False


def apply_move_to_board(board, move, player):
    """
    Apply move to actual board.
    """
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