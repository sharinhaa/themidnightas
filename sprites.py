import pygame
import math
from config import *

#CLASSES ANCESTRAIS (classes pai)
class Entidade (pygame.sprite.Sprite):
    """Classe Pai para todos os seres móveis/vivos do jogo."""
    def __init__(self, game, x, y, cor):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.x = x * tilesize
        self.y = y * tilesize
        self.rect.x = self.x
        self.rect.y = self.y

class ObjetoCenario(pygame.sprite.Sprite):
    """Classe Pai para estruturas estáticas e itens do mapa."""
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize

#CLASSES HERDEIRAS (classes filhas)
class player(Entidade):
    """Classe Filha que controla o Estudante (Carlos Eugênio)."""
    def __init__(self, game, x, y, avatar_type):
        super().__init__(game, x, y, white)
        self.avatar_type = avatar_type 
        self.vx, self.vy = 0, 0
        self.is_crouching = False

        #customização baseada no Polimorfismo de inicialização
        if avatar_type == "Carlos Eugênio":
            pygame.draw.circle(self.image, purple, (tilesize//2, tilesize//2), tilesize//2 - 2)
            pygame.draw.rect(self.immage, white,  (tilesize//4, tilesize//4, tilesize//2, tilesize//2))
        else:
            pygame.draw.circle(self.image, green, (tilesize//2, tilesize//2), tilesize//2 -2)
            pygame.draw.rect(self.image, black, (tilesize//3, tilesize//3, tilesize//3, tilesize//3))

        self.hitbox = self.rect.inflate(-tilesize * 0.2, -tilesize * 0.2)

    def get_input(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()

        #gerenciamento de passos silenciosos (agachar)
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_crouching = True
            current_speed = player_speed_crouch
        else:
            self.is_crouching = False 
            current_speed = player_speed_base

        #entradas híbridas 


