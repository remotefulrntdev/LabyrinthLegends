import pygame
from other.cons import WHITE
class Wall(pygame.sprite.Sprite):
    def __init__(self,pos,color) -> None:
        super().__init__()
        self.image = pygame.Surface((50, 50)).convert_alpha()
        self.image.fill(color)
        if color == WHITE:
            self.image.set_alpha(0)
        self.color = color  
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self, player) -> None:
        # make walls moving instead of player
        if player.canimoveleft:
            self.rect.x += player.rect.width
        if player.canimoveright:
            self.rect.x -= player.rect.width
        if player.canimoveup:
            self.rect.y += player.rect.height
        if player.canimovedown:
            self.rect.y -= player.rect.height