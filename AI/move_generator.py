# AI/move_generator.py 

from collections import deque


def generate_all_moves(board, player):
    """Generate all valid moves for a player on the real board."""
    moves = []
    moves.extend(generate_pawn_moves(board, player))
    if player.available_walls > 0:
        moves.extend(generate_wall_moves(board, player))
    return moves


def generate_pawn_moves(board, player):
    """Generate pawn moves on real board."""
    moves = []
    y, x = player.pos
    dim = board.dimBoard
    grid = board.board
    
    opponent = board.p1 if player == board.p2 else board.p2
    oy, ox = opponent.pos
    
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
    for dy, dx, wy, wx in directions:
        ny, nx = y + dy, x + dx
        wall_y, wall_x = y + wy, x + wx
        
        if not (0 <= wall_y < dim and 0 <= wall_x < dim):
            continue
        if grid[wall_y, wall_x] != 0:
            continue
        if not (0 <= ny < dim and 0 <= nx < dim):
            continue
        
        if (ny, nx) == (oy, ox):
            # Jump logic
            jy, jx = ny + dy, nx + dx
            jwy, jwx = ny + wy, nx + wx
            
            if (0 <= jy < dim and 0 <= jx < dim and
                0 <= jwy < dim and 0 <= jwx < dim and
                grid[jwy, jwx] == 0 and grid[jy, jx] == 0):
                moves.append(("pawn", (jy, jx)))
            else:
                # Diagonal jumps
                if dy != 0:
                    sides = [(0, -2, 0, -1), (0, 2, 0, 1)]
                else:
                    sides = [(-2, 0, -1, 0), (2, 0, 1, 0)]
                
                for sdy, sdx, swy, swx in sides:
                    sy, sx = ny + sdy, nx + sdx
                    sw_y, sw_x = ny + swy, nx + swx
                    if (0 <= sy < dim and 0 <= sx < dim and
                        0 <= sw_y < dim and 0 <= sw_x < dim and
                        grid[sw_y, sw_x] == 0 and grid[sy, sx] == 0):
                        moves.append(("pawn", (sy, sx)))
        else:
            if grid[ny, nx] == 0:
                moves.append(("pawn", (ny, nx)))
    
    return moves


def generate_wall_moves(board, player):
    """Generate wall placements on real board."""
    moves = []
    dim = board.dimBoard
    grid = board.board
    
    for cy in range(1, dim - 1, 2):
        for cx in range(1, dim - 1, 2):
            if grid[cy, cx] != 0:
                continue
            
            # Horizontal
            if cx - 1 >= 0 and cx + 1 < dim:
                cells = ((cy, cx - 1), (cy, cx), (cy, cx + 1))
                if all(grid[y, x] == 0 for y, x in cells):
                    if _paths_exist_after_wall(board, cells):
                        moves.append(("wall", cells))
            
            # Vertical
            if cy - 1 >= 0 and cy + 1 < dim:
                cells = ((cy - 1, cx), (cy, cx), (cy + 1, cx))
                if all(grid[y, x] == 0 for y, x in cells):
                    if _paths_exist_after_wall(board, cells):
                        moves.append(("wall", cells))
    
    return moves


def _paths_exist_after_wall(board, cells):
    """Check both players have paths after wall placement."""
    grid = board.board
    
    for y, x in cells:
        grid[y, x] = 1
    
    p1_ok = _has_path(board, board.p1)
    p2_ok = _has_path(board, board.p2)
    
    for y, x in cells:
        grid[y, x] = 0
    
    return p1_ok and p2_ok


def _has_path(board, player):
    """BFS to check if player can reach goal."""
    start = tuple(player.pos)
    target = player.objective
    dim = board.dimBoard
    grid = board.board
    
    visited = set([start])
    queue = deque([start])
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
    while queue:
        y, x = queue.popleft()
        if y == target:
            return True
        
        for dy, dx, wy, wx in directions:
            ny, nx = y + dy, x + dx
            wall_y, wall_x = y + wy, x + wx
            
            if not (0 <= ny < dim and 0 <= nx < dim):
                continue
            if grid[wall_y, wall_x] != 0:
                continue
            if (ny, nx) not in visited:
                visited.add((ny, nx))
                queue.append((ny, nx))
    
    return False