import pygame
import heapq

# Define the dimensions of the screen
WIDTH = 800
HEIGHT = 600

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define the size of each cell
CELL_SIZE = 50

# Create the start and end positions
start_pos = (2 * CELL_SIZE, 2 * CELL_SIZE)
end_pos = (WIDTH - 3 * CELL_SIZE, HEIGHT - 3 * CELL_SIZE)

# Add obstacles
obstacles = [
    pygame.Rect(4 * CELL_SIZE, 4 * CELL_SIZE, CELL_SIZE, CELL_SIZE),
    pygame.Rect(5 * CELL_SIZE, 4 * CELL_SIZE, CELL_SIZE, CELL_SIZE),
    pygame.Rect(6 * CELL_SIZE, 4 * CELL_SIZE, CELL_SIZE, CELL_SIZE),
    pygame.Rect(7 * CELL_SIZE, 4 * CELL_SIZE, CELL_SIZE, CELL_SIZE),
    pygame.Rect(8 * CELL_SIZE, 4 * CELL_SIZE, CELL_SIZE, CELL_SIZE),
    pygame.Rect(9 * CELL_SIZE, 4 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
]

# Create the sprite
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)

    def update(self):
        pass

# Create the sprite group
all_sprites = pygame.sprite.Group()
sprite = Sprite(start_pos)
all_sprites.add(sprite)

# Heuristic function (Euclidean distance)
def heuristic(node, goal):
    x1, y1 = node
    x2, y2 = goal
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

# A* algorithm
def astar():
    # Initialize the open and closed sets
    open_set = []
    heapq.heappush(open_set, (0, start_pos))
    came_from = {}

    # Initialize the cost and movement dictionaries
    g_score = {tuple(obstacle.topleft): float('inf') for obstacle in obstacles}
    g_score[start_pos] = 0

    # Start the A* algorithm
    while len(open_set) > 0:
        current = heapq.heappop(open_set)[1]

        if current == end_pos:
            # Reconstruct the path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path

        for dx, dy in [(0, CELL_SIZE), (0, -CELL_SIZE), (CELL_SIZE, 0), (-CELL_SIZE, 0)]:
            next_pos = current[0] + dx, current[1] + dy
            next_rect = pygame.Rect(next_pos[0], next_pos[1], CELL_SIZE, CELL_SIZE)

            if next_rect.collidelist(obstacles) != -1:
                continue

            # Calculate the new cost to move to the next position
            new_cost = g_score[current] + 1

            if new_cost < g_score.get(next_pos, float('inf')):
                # Update the cost and movement dictionaries
                g_score[next_pos] = new_cost
                f_score = new_cost + heuristic(next_pos, end_pos)
                heapq.heappush(open_set, (f_score, next_pos))
                came_from[next_pos] = current

        # Update the screen
        draw(path)

# Function to draw the objects
def draw(path):

    screen.fill(BLACK)

    for obstacle in obstacles:
        pygame.draw.rect(screen, RED, obstacle)

    pygame.draw.rect(screen, BLUE, (end_pos[0], end_pos[1], CELL_SIZE, CELL_SIZE))

    all_sprites.update()
    all_sprites.draw(screen)
    if path:
        for p in path: 
            pygame.draw.circle(screen, WHITE, p, 20)

    pygame.display.update()

# Main game loop
running = True

path = astar()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if path:
        # Move the sprite along the path
        print(path)
        position = path.pop(0)
        
        dx = position[0] - sprite.rect.x
        dy = position[1] - sprite.rect.y
        sprite.move(dx, dy)
    clock.tick(100)  # Adjust the movement speed here
    print(path)
    # Draw the objects
    draw()
    clock.tick(60)

# Quit the game
pygame.quit()
