import json
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

import random
from other.utilz import Utilz
s1 = pygame.transform.scale(pygame.image.load('res/villager.png'), (50,100))
inter = pygame.transform.scale(pygame.image.load('res/inter.png'), (100,50))
def load_js(fil):
    with open(fil, "r") as f:
        return json.load(f)
class Trader(pygame.sprite.Sprite):
    def __init__(self,pos,s,w) -> None:
        super().__init__()
        self.image = s1 
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.coll = False
        self.stars = s 
        self.walls = w 

        self.level = 1
        sw = load_js("swords.json")
        pt = load_js("potions.json")
        pz = load_js("pets.json")
        ar = load_js("artifacts.json")
        self.selling = {"Swords":random.sample(sw, random.randint((0 if len(sw) <= 0 else 1),min(len(sw), 5))), "Potions":random.sample(pt, random.randint((0 if len(pt) <= 0 else 1),min(len(pt),5))),"Artifacts":random.sample(ar, random.randint((0 if len(ar) <= 0 else 1),min(len(ar),5))),"Pets":random.sample(pz, random.randint((0 if len(pz) <= 0 else 1),min(len(pz),5)))}
    def update(self, player,world) -> None:
        if world == 2: 
            self.level = 2
        if player.canimoveleft:
            self.rect.x += player.rect.width
        if player.canimoveright:
            self.rect.x -= player.rect.width
        if player.canimoveup:
            self.rect.y += player.rect.height
        if player.canimovedown:
            self.rect.y -= player.rect.height
    def get_distance(self, obj2):
        return Utilz.get_distance(self, obj2)
    def blit_img(self,screen:pygame.Surface):
        screen.blit(inter, self.rect.topright)
