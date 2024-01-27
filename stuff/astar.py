import heapq
import pygame


class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start node to current node
        self.h = 0  # Heuristic cost from current node to end node
        self.f = 0  # Total cost

    def __lt__(self, other):
        return self.f < other.f


def astar_search(start_pos, end_pos, obstacles):
    open_list = []
    closed_set = set()

    start_node = Node(start_pos)
    end_node = Node(end_pos)

    open_list.append(start_node)
    a = 0
    while open_list:
        a += 1
        current_node = heapq.heappop(open_list)
        closed_set.add(current_node.position)
        print("ITERATION ", a, " CURRENT NODE: ", current_node.position)
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            print("FOUND PATH IN ", a, " ITERATIONS")
            return path[::-1]  # Return reversed path

        neighbors = get_neighbors(current_node, obstacles)

        for neighbor in neighbors:
            if neighbor.position in closed_set:
                continue

            neighbor.g = current_node.g + 1
            neighbor.h = calculate_heuristic(neighbor, end_node)
            neighbor.f = neighbor.g + neighbor.h
            print("NEIGHBOR: ", neighbor.position, " F: ", neighbor.f)
            if neighbor in open_list:
                open_node = next((node for node in open_list if node == neighbor), None)
                if neighbor.g < open_node.g:
                    open_node.g = neighbor.g
                    open_node.parent = current_node
            else:
                heapq.heappush(open_list, neighbor)

    return None  # No path found


def get_neighbors(node, obstacles):
    neighbors = []
    positions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Adjacent positions

    for position in positions:
        neighbor_pos = (node.position[0] + position[0], node.position[1] + position[1])

        if not is_valid_position(neighbor_pos, obstacles):
            continue

        neighbor_node = Node(neighbor_pos, parent=node)
        neighbors.append(neighbor_node)

    return neighbors


def is_valid_position(position, obstacles):
    for obstacle in obstacles:
        if pygame.Rect(obstacle).colliderect(pygame.Rect(position[0] - 25, position[1] - 25, 50, 50)):
            return False
    return True


def calculate_heuristic(node, end_node):
    return abs(node.position[0] - end_node.position[0]) + abs(node.position[1] - end_node.position[1])
