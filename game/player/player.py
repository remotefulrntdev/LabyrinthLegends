import logging
from other.cons import *
import pygame
from other.utilz import Utilz
from environment.wall import Wall
import json 
import random
from environment.pet import Pet

def load_js(fil):
    with open(fil, "r") as f:
        return json.load(f)

pz:list = load_js("pets.json")

class Hitbox(pygame.sprite.Sprite):
    def __init__(self,pos,player) -> None:
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = pos 
        self.player = player
    def coll(self,en):
        hits = pygame.sprite.spritecollide(self, en, False) 
        if self.player.equipped_artifact != None:
            if self.player.equipped_artifact["name"] == "The Artifact of Masters":
                return None
        for hit in hits:
            if type(hit) == Wall:
                print(hit.color)
                if hit.color == (0,0,0) or hit.color == (255,255,255):
                    self.player.swap()
                    hits.remove(hit)
        return hits
    def chck_right(self, enemies):
        self.rect.x += self.rect.width
        hits = self.coll(enemies)
        self.rect.x -= self.rect.width
        return hits

    def chck_left(self, enemies):
        self.rect.x -= self.rect.width
        hits = self.coll(enemies)
        self.rect.x += self.rect.width
        return hits

    def chck_up(self, enemies):
        self.rect.y -= self.rect.height
        hits = self.coll(enemies)
        
        self.rect.y += self.rect.height
        return hits
    def check_collide(self, en):
        hits = pygame.sprite.collide_rect(self, en)
        return hits
    def chck_down(self, enemies):
        self.rect.y += self.rect.height
        hits = self.coll(enemies)
        self.rect.y -= self.rect.height
        return hits


class Player(pygame.sprite.Sprite):
    def __init__(self,walls,swap_callback,pet_group:pygame.sprite.Group,shadow,traders):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.Surface((50, 50))
        # self.image.fill(GREEN)
        self.image = pygame.image.load("res/cube.png").convert_alpha()
        self.rect = self.image.get_rect()
        # set player to the center of the screen but rounded to the nearest 50
        self.rect.center =  Utilz.place_spawn_point(walls)
        self.walls = walls
        self.hitbox = Hitbox(self.rect.center,self)
        self.lefty = False
        self.righty = False
        self.swap = swap_callback
        self.uppy = False
        self.pet_group = pet_group
        self.downy = False
        self.canimoveleft = False
        self.canimoveright = False
        self.canimoveup = False
        self.shadow = shadow
        self.canimovedown = False
        self.move_count = 0
        self.health = 100
        self.trader_group = traders
        self.moves = []
        self.won = False
        self.score = 999
        self.equipped_sword = 0
        self.potions = {}
        self.equipped_sword_i = None
        self.equipped_artifact = None
        self.backpack_turned_on = False
        self.died = False
        self.unlocked = []
        self.dmgmult = 1
        self.last_remembered_pet = None
        def is_rock(x):
            return x["name"] == "Rock"
        self.equipped_pet = list(filter(is_rock, pz))[0]
        self.equipped_pet["is_rock"] = True
        self.pet = None 
        self.walks = []
        for i in range(20):
            ns =        self.start_sound = pygame.mixer.Sound("res/music/move/1.mp3")
            ns.set_volume(1)
            self.walks.append(ns)

    def take_damage(self,amount):
        mod = 2 if "Defender" in self.potions.keys() else 1
        self.health -= round(amount/mod)
    def update(self):
        self.dmgmult = 1

        for pot_n in self.potions.keys():
            try:
                self.potions[pot_n] -= 2
                if self.potions[pot_n] == 0:
                    self.potions.pop(pot_n)
                if pot_n == "The Potion Of Skill":
                    self.dmgmult *= 2
                if self.equipped_artifact != None and self.equipped_artifact["name"] == "The Artifact of Potions God":
                    if self.potions[pot_n] > FPS*60*7:
                        self.potions[pot_n] = -(self.potions[pot_n])
                elif self.potions[pot_n] < 0:
                    self.potions[pot_n] = -(self.potions[pot_n])
            except RuntimeError:
                logging.error("runtime error")
        self.canimovedown = False
        self.canimoveup = False
        self.canimoveright = False
        self.canimoveleft = False
        keys = pygame.key.get_pressed()
        for key in keys:
            if keys[pygame.K_LEFT]:
                random.choice(self.walks).play()
                self.lefty = True
            elif keys[pygame.K_RIGHT]:
                random.choice(self.walks).play()
                self.righty = True
            elif keys[pygame.K_UP]:
                random.choice(self.walks).play()
                self.uppy = True
            elif keys[pygame.K_DOWN]:
                random.choice(self.walks).play()
                self.downy = True
            if not keys[pygame.K_LEFT] and not self.lefty:
                self.lefty = False
            if not keys[pygame.K_RIGHT] and not self.righty:
                self.righty = False
            if not keys[pygame.K_UP] and not self.uppy:
                self.uppy = False
            if not keys[pygame.K_DOWN] and not self.downy:
                self.downy = False
        if self.equipped_pet != self.last_remembered_pet:
            self.last_remembered_pet = self.equipped_pet
            # pet got updates 
            
            for sprt in self.pet_group.sprites():
                sprt.kill()
            self.pet = Pet(self.equipped_pet["name"],self.shadow.groups()[0], self.groups()[0],self.trader_group, self.walls, self.rect.topleft,pygame.transform.scale(pygame.image.load(self.equipped_pet["image"]), (50,50)), self.equipped_pet["damage_cd"], self.equipped_pet["speed"], self,self.shadow, self.equipped_pet["reach"], self.equipped_pet["stun_chance"], self.equipped_pet["damage"],self.equipped_pet["is_rock"])
            self.pet_group.add(self.pet)
        if self.rect.left > WIDTH:
            self.rect.right = 0

        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        # check vars lefty righty etc and move accordingly only if hitbox doesnt collide with wall
        if self.lefty:
            if not self.hitbox.chck_left(self.walls):
                self.canimoveleft = True
                self.moves.append("left")
        if self.righty:
            if not self.hitbox.chck_right(self.walls):
                self.canimoveright = True
                self.moves.append("right")
        if self.uppy:
            if not self.hitbox.chck_up(self.walls):
                self.canimoveup = True
                self.moves.append("up")

        if self.downy:
            if not self.hitbox.chck_down(self.walls):
                self.canimovedown = True
                self.moves.append("down")
        self.hitbox.rect.center = self.rect.center
        self.lefty = False
        self.righty = False
        self.uppy = False
        self.downy = False
