import heapq
import logging
import pygame 
from other.cons import CELL_SIZE
# Heuristic
def heuristic(node, goal):
    x1, y1 = node
    x2, y2 = goal
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

class Finder:
    def __init__(self, start, end,walls) -> None:
        logging.debug("SLAVE STARTED PATHFINDING")
        self.path = None 
        self.start = start
        self.end = end 
        self.walls = walls
    def run(self, r):
        if not r: 
            while True:
                self.path = astar(self.start.rect.topleft, self.end.rect.topleft, self.walls)
                pygame.time.wait(70)
# A*
def astar(start_pos, end_pos, obstacles: pygame.sprite.Group):
    open_set = []
    heapq.heappush(open_set, (0, start_pos))
    came_from = {}

    # cost and movement dictionaries
    g_score = {obstacle.rect.topleft: float('inf') for obstacle in obstacles}
    g_score[start_pos] = 0

    while len(open_set) > 0:
        current = heapq.heappop(open_set)[1]

        if current == end_pos:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path

        for dx, dy in [(0, CELL_SIZE), (0, -CELL_SIZE), (CELL_SIZE, 0), (-CELL_SIZE, 0)]:
            next_pos = current[0] + dx, current[1] + dy
            next_rect = pygame.Rect(next_pos[0], next_pos[1], CELL_SIZE, CELL_SIZE)

            if any(next_rect.colliderect(obstacle.rect) for obstacle in obstacles.sprites()):
                continue

            new_cost = g_score[current] + 1

            if new_cost < g_score.get(next_pos, float('inf')):
                g_score[next_pos] = new_cost
                f_score = new_cost + heuristic(next_pos, end_pos)
                heapq.heappush(open_set, (f_score, next_pos))
                came_from[next_pos] = current
if __name__ == "__main__":

    class Obstacle(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image.fill((0, 0, 0))
            self.rect = self.image.get_rect(topleft=(x, y))


    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Pathfinding")

 
    obstacle_group = pygame.sprite.Group()
    obstacle_group.add(Obstacle(90, 90), Obstacle(120, 90), Obstacle(150, 90), Obstacle(180, 90), Obstacle(210, 90))

    start_pos = (30, 30)
    end_pos = (570, 570)
    path = astar(start_pos, end_pos, obstacle_group)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))


        obstacle_group.draw(screen)

        if path:
            pygame.draw.lines(screen, (255, 0, 0), False, path, 3)

        pygame.display.flip()

    pygame.quit()
