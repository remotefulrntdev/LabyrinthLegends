import pygame
from player.player import Player
import random
from other.utilz import Utilz
from other.cons import CELL_SIZE
s1 = pygame.transform.scale(pygame.image.load('res/star.png'), (50,50))
s2 = pygame.transform.scale(pygame.image.load('res/star2.png'), (50,50))
class Star(pygame.sprite.Sprite):
    def __init__(self,pos,s,w) -> None:
        super().__init__()
        self.image = s1 
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.coll = False
        self.stars = s 
        self.walls = w 
        self.my_sound =pygame.mixer.Sound("res/music/loot/star.ogg")
    def update(self, player:Player,world) -> None:
        if Utilz.get_distance(self, player) > CELL_SIZE*50:
            self.kill()
        if world == 2: 
            self.image = s2
        if player.rect.colliderect(self.rect):
            self.my_sound.play()
            mod = 2 if player.equipped_artifact!= None and player.equipped_artifact["name"]== "The Artifact of Looting" else 1
            mod *= 2 if "Star Doubler" in player.potions.keys() else 1
            player.score += 1 * (3 if world == 2 else 1) * mod 
            self.kill() # F
        if player.canimoveleft:
            self.rect.x += player.rect.width
        if player.canimoveright:
            self.rect.x -= player.rect.width
        if player.canimoveup:
            self.rect.y += player.rect.height
        if player.canimovedown:
            self.rect.y -= player.rect.height

        if not self.coll: 
            asp = pygame.sprite.collide_rect(self, player)
            wll = pygame.sprite.spritecollideany(self, self.walls)
            st = pygame.sprite.spritecollideany(self, self.stars)
            if not asp and wll is None and st == self:
                self.coll = True
            else: 
                self.rect.x += random.choice([50,0])
                self.rect.y += random.choice([50,0])