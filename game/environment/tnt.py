import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from player.player import Player
import random
from other.utilz import Utilz
from other.cons import CELL_SIZE, WHITE, FPS 

s1 = pygame.transform.scale(pygame.image.load('res/tnt.png'), (50, 50))
s2 = pygame.Surface((50, 50))
s2.fill(WHITE)

class Tnt(pygame.sprite.Sprite):
    def __init__(self, pos, s, w,shadow,star_group) -> None:
        super().__init__()
        self.image = s1
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.coll = False
        self.stars = s
        self.walls = w
        self.tick = 0
        self.explosion_ticks = 0
        self.explosion_radius = CELL_SIZE * 4
        self.shadow = shadow
        self.star_group = star_group
        self.start_sound = pygame.mixer.Sound("res/music/boom/start.mp3")
        self.boom_sound = pygame.mixer.Sound("res/music/boom/finish.ogg")
        self.start_sound.play()
    def update(self, player: Player, world) -> None:
        if player.canimoveleft:
            self.rect.x += player.rect.width
        if player.canimoveright:
            self.rect.x -= player.rect.width
        if player.canimoveup:
            self.rect.y += player.rect.height
        if player.canimovedown:
            self.rect.y -= player.rect.height
        self.tick += 1


        if self.tick % 10 == 0:
            if self.image == s1:
                self.image = s2
            else:
                self.image = s1


        if self.tick % FPS*3 == 0:
            self.explode(player,world)

        if not self.coll:

            wll = pygame.sprite.spritecollideany(self, self.walls)
            # st = pygame.sprite.spritecollideany(self, self.stars)
            if wll is None:
                self.coll = True
            else:
                self.rect.x += random.choice([50, 0])
                self.rect.y += random.choice([50, 0])

    def explode(self, player: Player,w):
        if not ("TNT Immuner" in player.potions.keys()):
            if Utilz.get_distance(self, player) < self.explosion_radius:
                distance = Utilz.get_distance(self, player)
                damage = round(max(0, (self.explosion_radius - distance)//2.5))
                player.take_damage(damage*w)
        for star in self.star_group.sprites():
            if Utilz.get_distance(self, star) < self.explosion_radius:
                star.kill()
        if Utilz.get_distance(self, self.shadow) < self.explosion_radius:
            distance = Utilz.get_distance(self, player)
            damage = round(max(0, (self.explosion_radius - distance)//2))
            self.shadow.health -= damage*w
        self.boom_sound.play()
        self.kill()
