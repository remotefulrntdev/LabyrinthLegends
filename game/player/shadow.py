import pygame
from other.cons import *
import os
import random
from stuff.astar import get_neighbors
from player.player import Player

hurt_sounds  = [pygame.mixer.Sound(os.path.join("res/music/hurt", file)) for file in os.listdir("res/music/hurt") if file.endswith(('.mp3', '.wav', '.ogg', '.flac'))]

class PlayersShadow(pygame.sprite.Sprite):
    def __init__(self, player, walls, grid, d):
        super().__init__()
        self.image = pygame.image.load("res/cube.png").convert_alpha()
        self.image.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect(center=player.rect.center)
        self.move_speeds = [1.8, 2.4, 4, 0]
        self.speed_type = 3
        self.player = player
        self.walls = walls
        self.an = False
        self.grid = grid
        self.path = None
        self.cooldown = 0
        self.sleep_counter = 0
        self.max_sleep = 10
        self.max_damage_cd = FPS * 0.1
        self.damage_cd = 0
        self.disabled = d
        self.paused = False
        self.health = 100
        self.max_health = self.health
        self.state = ""
        self.dream_timer = 0
        self.darkness_animation_progress = 0
        self.increase_alpha = True
        self.rebirths = 0
        self.damage = 4
    def start_darkness_animation(self):
        self.darkness_animation_progress = 1
        self.increase_alpha = True

    def is_animation_finished(self):
        return self.darkness_animation_progress > FPS * 4.25 * 2 + 1

    def update(self, player:Player):
        self.move_speed = self.move_speeds[self.speed_type]
        if "The Potion Of Slowness" in player.potions.keys():
             self.move_speed /= 2
        if player.equipped_artifact != None and "The Artifact of Slowness" == player.equipped_artifact["name"]:
            self.move_speed /= 2
        if 0 < self.darkness_animation_progress <= FPS * 4.25 * 2 + 1:
            self.health = self.max_health
            alpha_value = min(self.darkness_animation_progress, 255)
            self.image.set_alpha(alpha_value)

            if self.increase_alpha:
                self.darkness_animation_progress += 1
                if self.darkness_animation_progress > FPS * 4.25 * 2 + 1:
                    self.increase_alpha = False
            else:
                self.darkness_animation_progress -= 1
                if self.darkness_animation_progress == 1:
                    self.increase_alpha = True

        if self.is_animation_finished() and self.disabled:
            self.disabled = False
            self.speed_type = 3
            self.increase_alpha = True 
            self.move_speed = self.move_speeds[self.speed_type]
            self.rebirths += 1
            self.darkness_animation_progress = 0
            if self.rebirths >= 5:
                self.player.won = True
        self.cooldown -= 1
        self.damage_cd += 1


        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if self.speed_type == 3:
            self.dream_timer = FPS
        if self.health <= 0 and self.darkness_animation_progress <= 0:
            self.max_health *= 2 
            self.max_damage_cd //= 2
            self.damage *= 2
            self.health = self.max_health
            self.disabled = True
            self.start_darkness_animation()

        for direction, can_move in zip(directions, (player.canimoveleft, player.canimoveright, player.canimoveup, player.canimovedown)):
            if can_move:
                self.rect.x += direction[0] * player.rect.width
                self.rect.y += direction[1] * player.rect.height
                self.an = True
        if self.disabled:
            return 
        self.sleep_counter += 1
        if self.sleep_counter / FPS >= self.max_sleep:
            self.sleep_counter = 0
            self.speed_type = (self.speed_type - 1) % len(self.move_speeds)
 
            self.move_speed = self.move_speeds[self.speed_type]

        if self.damage_cd >= self.max_damage_cd and player.hitbox.check_collide(self) and self.speed_type != 3:
            player.take_damage(self.damage)
            rc = random.choice(hurt_sounds)

            if rc.get_num_channels() == 0:
                rc.play()
            self.damage_cd = 0

        if self.speed_type != 3:
            if self.cooldown <= 0 and len(player.moves) >= 1:
                # MOVE
                poped = player.moves.pop(0)
                move_amount = 50
                self.rect.x += move_amount * (poped == "right") - move_amount * (poped == "left")
                self.rect.y += move_amount * (poped == "down") - move_amount * (poped == "up")
                self.cooldown = int(self.move_speeds[self.speed_type] * 10)

        speed_desc = ["SLEEPING", "MOVING SLOWLY", "MOVING MEDIUM", "MOVING FAST"]
        speed_desc.reverse()
        self.state = f"IS {speed_desc[self.speed_type]} {round(self.max_sleep * FPS - self.sleep_counter)}t"
