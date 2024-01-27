import logging
import pygame
from other.cons import CELL_SIZE, FPS, WHITE
from other.astar import Finder
import random
import threading
from other.utilz import Utilz

class Pet(pygame.sprite.Sprite):
    def __init__(self,name, shadow_group, player_group,trader_group, walls, pos,img, damage_cd, speed,player,shadow,reach,stun_chance,damage,is_rock) -> None:
        super().__init__()
        self.or_img = img.copy()
        self.stun_img:pygame.Surface = img.copy()
        self.stun_img.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)

        self.image = img 
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.stun_timer = 0
        self.disabled = False 
        self.player = player
        self.walls = walls 
        self.path = []
        self.damage_cooldown = damage_cd
        self.speed = speed
        self.damage = damage
        self.tick = 0
        self.shadow = shadow
        self.reach = reach 
        self.is_rock = is_rock
        self.stun_chance = stun_chance # 0.005 * 10 = 0.05 * 10
        self.max_speed =speed
        self.name = name 
        self.finder = Finder(self, self.shadow, walls)
        finder_thrd = threading.Thread(target=self.finder.run,args=[self.is_rock])
        finder_thrd.start()
        self.colliders = [walls, shadow_group, player_group, trader_group]
    def update(self, player) -> None:
        self.tick += 1
        p = self.finder.path 
        if player.canimoveleft:
            self.rect.x += player.rect.width
        if player.canimoveright:
            self.rect.x -= player.rect.width
        if player.canimoveup:
            self.rect.y += player.rect.height
        if player.canimovedown:
            self.rect.y -= player.rect.height
        if self.is_rock:
            if Utilz.get_distance(self.shadow, self) < self.reach*CELL_SIZE and self.shadow.speed_type != 3 and self.tick % FPS*2.5 == 0:
                self.shadow.health -= 30
            return 
        if self.name == "Amogus":
            for g in self.colliders:
                for sp in g.sprites():
                    if Utilz.get_distance(self, sp) < CELL_SIZE*2:
                        sp.image = self.image.copy()
        if self.stun_timer > 0:
            
            self.stun_timer -= 1
            if self.stun_timer==1:
                self.disabled = False
                self.image = self.or_img
            return 
        if self.tick % self.damage_cooldown == 0 and self.shadow.speed_type != 3 and Utilz.get_distance(self.shadow, self) < self.reach*CELL_SIZE:
            self.shadow.health -= self.damage
            c = random.random()
            if c < self.stun_chance*100:
                self.stun_timer = FPS*1.5
                self.disabled = True 
                logging.info("Your pet was stunned during the attack")
                self.image = self.stun_img
        if p!= None and len(p) > 0:
            self.path = p 
        elif p == None:
            self.rect.center = self.player.rect.center
        c = random.random()
        if c < self.stun_chance:
            self.stun_timer = FPS*1.5
            self.disabled = True 
            logging.info("Your pet was stunned")
            self.image = self.stun_img
        if self.tick % self.speed == 0: 
            if len(self.path) > 0:
                self.rect.topleft = self.path.pop()
