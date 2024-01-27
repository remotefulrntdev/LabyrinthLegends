
# import heapq
# def heuristic(a, b):
#     # Calculate the Manhattan distance between two points
#     return abs(a[0] - b[0]) + abs(a[1] - b[1])


# def astar_search(grid, start, goal, CELLS_X, CELLS_Y):
#     # Initialize the open and closed sets
#     open_set = []
#     closed_set = set()

#     # Create a dictionary to store the parent of each cell
#     parent = {}

#     # Create a dictionary to store the cost of reaching each cell
#     g_score = {cell: float('inf') for row in grid for cell in row}
#     g_score[start] = 0

#     # Create a dictionary to store the total cost of reaching each cell
#     f_score = {cell: float('inf') for row in grid for cell in row}
#     f_score[start] = heuristic(start, goal)

#     # Add the start cell to the open set
#     heapq.heappush(open_set, (f_score[start], start))

#     while open_set:
#         # Get the cell with the lowest f-score from the open set
#         current = heapq.heappop(open_set)[1]

#         # Check if the current cell is the goal
#         if current == goal:
#             # Reconstruct the path from the goal to the start
#             path = []
#             while current in parent:
#                 path.append(current)
#                 current = parent[current]
#             path.append(start)
#             return path[::-1]  # Return the reversed path
#         print(current, goal, parent, g_score, f_score)
#         # Add the current cell to the closed set
#         closed_set.add(current)

#         # Get the neighbors of the current cell
#         neighbors = [(current[0] - 1, current[1]),  # Left
#                      (current[0] + 1, current[1]),  # Right
#                      (current[0], current[1] - 1),  # Up
#                      (current[0], current[1] + 1)]  # Down

#         for neighbor in neighbors:
#             x, y = neighbor

#             # Check if the neighbor is valid (within the grid) and not a wall
#             if 0 <= x < CELLS_X and 0 <= y < CELLS_Y and grid[x][y]:
#                 # Calculate the tentative g-score for the neighbor
#                 tentative_g_score = g_score[current] + 1

#                 if tentative_g_score < g_score[neighbor]:
#                     # Update the parent and g-score of the neighbor
#                     parent[neighbor] = current
#                     g_score[neighbor] = tentative_g_score
#                     f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)

#                     if neighbor not in closed_set:
#                         # Add the neighbor to the open set
#                         heapq.heappush(open_set, (f_score[neighbor], neighbor))

#     return None
