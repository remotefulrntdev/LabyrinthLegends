import math
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

from environment.wall import Wall 
from other.cons import *
import random
import json 
def load_js(fil):
    with open(fil, "r") as f:
        return json.load(f)
sw:list = load_js("swords.json")
pt:list  = load_js("potions.json")
pz:list  = load_js("pets.json")
ar:list  = load_js("artifacts.json")

all_items =sw 
all_items.extend(pt)
all_items.extend(ar)
all_items.extend(pz)
class Utilz:
    @staticmethod
    def interpolate_color(start_color, end_color, progress, contrast):
        r = int((start_color[0] + (end_color[0] - start_color[0]) * progress) * contrast)
        g = int((start_color[1] + (end_color[1] - start_color[1]) * progress) * contrast)
        b = int((start_color[2] + (end_color[2] - start_color[2]) * progress) * contrast)
        return (min(255, r), min(255, g), min(255, b))
    @staticmethod
    def generate_labyrinth(CELLS_X, CELLS_Y, start = (191, 38, 38),end = (216, 186, 70),gr = None):
        # мій щоденник:
        #
        # 
        # 10.03.2023:
        # я робив цей алгоритм вже більше 6 годин
        #
        #
        # 13.03.2023:
        # не може бути воно працює
        #
        #
        # 20.01.2024:
        # подальші записи знищено бо мене з'їв скібіді туалет
        #
        #
        # 28.01.2024:
        # rip

        exits = []
        grid = [[False] * CELLS_Y for _ in range(CELLS_X)]

        stack = []


        start_x = random.randint(0, CELLS_X - 1)
        start_y = random.randint(0, CELLS_Y - 1)


        grid[start_x][start_y] = True


        stack.append((start_x, start_y))


        while stack:

            current_x, current_y = stack[-1]

            neighbors = []
            if current_x > 1 and not grid[current_x - 2][current_y]:
                neighbors.append((-2, 0))
            if current_x < CELLS_X - 2 and not grid[current_x + 2][current_y]:
                neighbors.append((2, 0))
            if current_y > 1 and not grid[current_x][current_y - 2]:
                neighbors.append((0, -2))
            if current_y < CELLS_Y - 2 and not grid[current_x][current_y + 2]:
                neighbors.append((0, 2))

            if neighbors:
                dx, dy = random.choice(neighbors)

                grid[current_x + dx // 2][current_y + dy // 2] = True

                grid[current_x + dx][current_y + dy] = True

                stack.append((current_x + dx, current_y + dy))

            else:
                if (current_x == 0 or current_x == CELLS_X - 1 or current_y == 0 or current_y == CELLS_Y - 1):
                    nw = Wall((current_x*50, current_y * 50+50), WHITE)
                    exits.append(nw)



                stack.pop()
        if gr != None:
            walls = gr
        else:
            walls = pygame.sprite.Group()
        for x in range(CELLS_X):
            for y in range(CELLS_Y):
                if not grid[x][y]:
                    start_color = start
                    end_color = end
                    progress = y / CELLS_Y
                    contrast = 1.5 
                    color = Utilz.interpolate_color(start_color, end_color, progress, contrast)
                    wall = Wall((x * CELL_SIZE, y * CELL_SIZE), color)
                    walls.add(wall)
        for w in exits: 
            walls.add(w) 
        return grid, walls, exits
    @staticmethod
    def place_spawn_point(walls):
        spawn_point = (WIDTH/2+25, HEIGHT/2+25)
        return spawn_point

    @staticmethod
    # draw text function
    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(pygame.font.match_font('arial'), size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        surf.blit(text_surface, text_rect)
    @staticmethod
    # draw text function
    def draw_text_with_next_line(surf, text, size, x, y, max_size=None):
        font = pygame.font.Font(pygame.font.match_font('arial'), size)
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line_test = current_line + [word] if current_line else [word]
            test_surface = font.render(' '.join(current_line_test), True, WHITE)
            test_width, test_height = test_surface.get_size()

            if max_size and test_width > max_size:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            lines.append(' '.join(current_line))

        y_offset = 0
        for line in lines:
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect()
            text_rect.midtop = (x, y + y_offset)
            surf.blit(text_surface, text_rect)
            y_offset += text_rect.height
    @staticmethod
    def get_exits(CELLS_X, CELLS_Y):
        walls = []

        # left
        for y in range(CELLS_Y):
            wall = Wall((-CELL_SIZE, y * CELL_SIZE), (0, 0, 0))
            walls.append(wall)

        # right
        for y in range(CELLS_Y):
            wall = Wall(((CELLS_X + 1) * CELL_SIZE, y * CELL_SIZE), (0, 0, 0))
            walls.append(wall)

        # top
        for x in range(CELLS_X):
            wall = Wall((x * CELL_SIZE, 0), (0, 0, 0))
            walls.append(wall)

        # bottom
        for x in range(CELLS_X):
            wall = Wall((x * CELL_SIZE, (CELLS_Y - 1) * CELL_SIZE), (0, 0, 0))
            walls.append(wall)

        return walls
    @staticmethod
    def get_distance(obj1, obj2):
        x1, y1 = obj1.rect.center  
        x2, y2 = obj2.rect.center
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance
    @staticmethod
    def a_tuples(a, b):
        return (a[0] + b[0], a[1]+b[1])
    @staticmethod
    def timeee(duration_frames):
        total_seconds = duration_frames / FPS
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    @staticmethod
    def mathcer(match, items):
        for item in items:
            if item["uuid"] == match["uuid"]:
                # print("Matched")
                return True
            # else:
            #     print(match["uuid"], "!=",item["uuid"])
        return False
    @staticmethod
    def uuid_to_item(uuid):
        return list(filter(lambda v: v["uuid"] == uuid,all_items))[0]