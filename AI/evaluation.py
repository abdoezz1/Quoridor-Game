import heapq
import math


def evaluate_board(board, ai_player, wall_bonus_weight=1.0):    
    opponent = board.p1 if ai_player == board.p2 else board.p2
    
    if ai_player.pos[0] == ai_player.objective:
        return math.inf
    if opponent.pos[0] == opponent.objective:
        return -math.inf
    
    ai_path = astar_path_length(board, ai_player)
    opp_path = astar_path_length(board, opponent)
    
    if ai_path == 0:
        return math.inf
    if opp_path == 0:
        return -math.inf
    

    path_diff = (opp_path - ai_path) * 4
    wall_bonus = ai_player.available_walls * wall_bonus_weight
    
    return path_diff + wall_bonus


def astar_path_length(board, player):
    start = tuple(player.pos)
    target_row = player.objective
    dim = board.dimBoard
    grid = board.board
    
    visited = [[False] * dim for _ in range(dim)]
    heap = [(abs(start[0] - target_row), 0, start[0], start[1])]
    
    directions = [(-2, 0, -1, 0), (2, 0, 1, 0), (0, -2, 0, -1), (0, 2, 0, 1)]
    
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
            
            if not (0 <= ny < dim and 0 <= nx < dim):
                continue
            if grid[wall_y, wall_x] != 0:
                continue
            if visited[ny][nx]:
                continue
            
            h = abs(ny - target_row)
            heapq.heappush(heap, (g + 1 + h, g + 1, ny, nx))
    
    return math.inf