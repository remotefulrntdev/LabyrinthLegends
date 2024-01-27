import heapq

def astar_search(grid, start, end, num_cells_x, num_cells_y):
    heap = []

    heapq.heappush(heap, (0, start))
    visited = set()
    came_from = {}
    g_score = {start: 0}

    while heap:
        current = heapq.heappop(heap)[1]

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        visited.add(current)
        neighbors = get_neighbors(current, num_cells_x, num_cells_y, grid)

        for neighbor in neighbors:
            neighbor_cost = g_score[current] + 1  # Assuming each movement cost is 1
            if neighbor not in g_score or neighbor_cost < g_score[neighbor]:
                g_score[neighbor] = neighbor_cost
                priority = neighbor_cost + heuristic(neighbor, end)
                heapq.heappush(heap, (priority, neighbor))
                came_from[neighbor] = current

    return None

def get_neighbors(node, num_cells_x, num_cells_y, grid):
    x, y = node
    neighbors = [(x-50, y), (x+50, y), (x, y-50), (x, y+50)]
    valid_neighbors = []

    for neighbor in neighbors:
        if is_valid_neighbor(neighbor, num_cells_x, num_cells_y, grid):
            valid_neighbors.append(neighbor)

    return valid_neighbors

def is_valid_neighbor(neighbor, num_cells_x, num_cells_y, grid):
    x, y = neighbor
    return 0 <= x < num_cells_x * 50 and 0 <= y < num_cells_y * 50 and not grid[y // 50][x // 50]

def heuristic(node, goal):
    x1, y1 = node
    x2, y2 = goal
    return abs(x2 - x1) + abs(y2 - y1)
