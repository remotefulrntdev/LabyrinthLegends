import logging
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from other.cons import CELL_SIZE, FPS, WHITE
from other.astar import Finder
import random
import threading
from other.utilz import Utilz

water_drop = pygame.transform.scale(pygame.image.load("res/gfx/water.png"), (35,35))
fire = pygame.transform.scale(pygame.image.load("res/gfx/fire.png"), (35,35))

class Pet(pygame.sprite.Sprite):
    def __init__(self,uuid, shadow_group, player_group,trader_group, walls, pos,img, damage_cd, speed,player,shadow,reach,stun_chance,damage,is_rock) -> None:
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
        self.uuid = uuid 
        self.finder = Finder(self, self.shadow, walls)
        finder_thrd = threading.Thread(target=self.finder.run,args=[self.is_rock])
        finder_thrd.start()
        self.colliders = [walls, shadow_group, player_group, trader_group]
        self.moves = []
    def update(self, player) -> None:
        self.tick += 1
        p = self.finder.path 
        rx = 0
        ry = 0
        if player.canimoveleft:
            self.rect.x += player.rect.width
            rx += player.rect.width
        if player.canimoveright:
            self.rect.x -= player.rect.width
            rx += -player.rect.width
        if player.canimoveup:
            self.rect.y += player.rect.height
            ry += player.rect.height
        if player.canimovedown:
            self.rect.y -= player.rect.height
            ry += -player.rect.height
        for i in range(len(self.moves)):
            self.moves[i] = Utilz.a_tuples(self.moves[i], (rx,ry)) 
        if self.is_rock:
            if Utilz.get_distance(self.shadow, self) < self.reach*CELL_SIZE and self.shadow.speed_type != 3 and self.tick % FPS*2.5 == 0:
                self.shadow.health -= 30
            return 
        if self.uuid == "Amogus":
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
        if len(self.moves) > 0 and self.moves[-1] == self.rect.topleft:
            pass 
        else: 
            self.moves.append(self.rect.center)
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
        if self.tick % 10 == 0 and len(self.moves) > 0:

            self.moves.pop(0)
    def after_draw(self,screen):
        if self.player.equipped_pet["uuid"] == "4567defg-89ab-hijk-de45-67890123defg": # water thing 
            water_drop_r = water_drop.get_rect()
            for move in self.moves:
                water_drop_r.center = move 
                screen.blit(water_drop, water_drop_r)
        elif self.player.equipped_pet["uuid"] == "5678efgh-9abc-ijkl-ef56-78901234efgh": # fire guy
            fire_r = fire.get_rect()
            for move in self.moves:
                fire_r.center = move 
                screen.blit(fire, fire_r)