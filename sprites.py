import pygame
import math
from config import *

#CLASSES ANCESTRAIS (classes pai)
class Entidade (pygame.sprite.Sprite):
    """Classe Pai para todos os seres dinâmicos do jogo."""
    def __init__(self, game, x, y):
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
    """Classe Filha que controlada pelo usuário."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.vx, self.vy = 0, 0
        self.is_crouching = False

        #customização baseada no Polimorfismo de inicialização
        pygame.draw.circle(self.image, purple, (tilesize//2, tilesize//2), tilesize//2 - 2)
        pygame.draw.rect(self.immage, white, (tilesize//4, tilesize//4, tilesize//2, tilesize//2))
        
        self.hitbox = self.rect.inflate(-tilesize * 0.2, -tilesize * 0.2)

    def get_input(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()

        #gerenciamento de passos silenciosos (agachar)
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_crouching = True
            speed = player_speed_crouch
        else:
            self.is_crouching = False 
            speed = player_speed_base

 #entradas híbridas (WASD/SETAS)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  self.vx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = speed
        if keys [pygame.K_UP] or keys[pygame.K_w]:   self.vy = -speed
        if keys [pygame.K_DOWN] or keys[pygame.K_s]: self.vy = speed

        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def move_and_collide(self, dt):
        self.x += self.vx * dt
        self.hitbox.x = self.x + (self.rect.width - self.hitbox.width) // 2
        hits = pygame.sprite.spritecollide(self, self.game.walls, False, lambda s, o: s.hitbox.colliderect(o.rect))
        if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.hitbox.width - (self.hitbox.width - self.hitbox.width) // 2
                if self.vx < 0:
                    self.x = hits[0].rect.right - (self.rect.width - self.hitbox.width) // 2
                self.vx = 0
                self.hitbox.x = self.x + (self.rect.width - self.hitbox.width) // 2 

                self.y += self.vy * dt
                self.hitbox.y = self.y + (self.rect.height - self.hitbox.height) // 2
        hits = pygame.sprite.spritecollide(self, self.game.walls, False, lambda s, o: s.hitbox.colliderect(o.rect))
        if hits:
                    if self.vy > 0:
                        self.y = hits[0].rect.top - self.hitbox.height - (self.rect.height - self.hitbox.height) // 2
                    if self.vy < 0:
                        self.vy = hits[0].rect.bottom - (self.rect.height - self.hitbox.height) // 2 
                    self.vy = 0
                    self.hitbox.y = self.y + (self.rect.height - self.hitbox.height) // 2

                    self.rect.x = self.x
                    self.rect.y = self.y

    def update(self, dt):
        self.get_input()
        self.move_and_collide(dt)

class Librarian(Entidade):
    """Classe filha que controla o bibliotecário e suas propriedades."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        pygame.draw.circle(self.image, red, (tilesize//2, tilesize//2), tilesize//2 -2)
        pygame.draw.circle(self.image, black, (tilesize//2, tilesize//2), tilesize//5)

        self.pos = pygame.math.Vector2(self.x, self.y)
        self.waypoints = [(x, y), (x + 10, y), (x + 10, y + 5), (x, y + 5)]
        self.current_waypoint = 0
        self.facing_angle = 0.0

    def update(self, dt):
        #movimentação baseada nos waypoints da patrulha 
        target = pygame.math.Vector2(self.waypoints[self.current_waypoint]) * tilesize
        direction = target - self.pos 

        if direction.length() > 3:
            direction = direction.normalize()
            self.pos += direction * librarian_speed * dt
            self.facing_angle = math.atan2(-direction.y, direction.x)
        else:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

        self.rect.topleft = self.pos
        self.check_player_detection() 

    def check_player_detection(self):
        player = self.game.player
        vec = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        distance = vec.length()

        if distance < detection_radius:
            px = int(player.rect.centerx // tilesize)
            py = int(player.rect.centery // tilesize)
            if 0 <= py < len(map_data) and 0 <= px < len(map_data[0]):
                if map_data[py][px] == 5 and not player.is_crouching:
                    self.game.trigger_catch()
                return
            
            if distance > 0:
                angle_to_player = math.atan2(vec.y, vec.x)
                angle_diff = (angle_to_player - self.facing_angle + math.pi) % (2 * math.pi) - math.pi

                if abs(angle_diff) < math.pi / 4:
                    if self.has_line_of_sight(pygame.math.Vector2(self.rect.center), pygame.math.Vector2(player.rect.center)):
                        self.game.trigger_catch()

        def has_line_of_sight(self, start, end):
            steps = int(start.distance_to(end) / 8)
            if steps == 0: return True
            for i in range(1, steps):
                point = start.lerp(end, i / steps)
                tx, ty = int(point.x // tilesize), int(point.y  // tilesize)
                if 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0]):
                    if map_data[ty][tx] == 1: #estannte obstrui totalmente 
                        return False 
            return True 
        
        def draw_vision_cone(self, surface):
            cone_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            center = pygame.math.Vector2(self.rect.center)

            p1 = center + pygame.math.Vector2(math.cos(self.facing_angle - math.pi/4), -math.sin(self.facing_angle - math.pi/4)) * detection_radius
            p2 = center + pygame.math.Vector2(math.cos(self.facing_angle + math.pi/4), -math.sin(self.facing_angle + math.pi/4)) * detection_radius

            pygame.draw.polygon(cone_surf, (250, 40, 40, 40), [center, p1, p2])
            surface.blit(cone_surf, (0, 0))   


class Obstaculo(ObjetoCenario):
    """Classe filha para elementos fixos.""" 
    def __init__(self, col, row, tile_type, letter_id=""):
        super().__init__(col, row, tilesize, tilesize)
        self.tile_type = tile_type
        self.letter_id = letter_id
        self.col = col
        self.row = row
        self.render_visual()

    def render_visual(self):
        if self.tile_type == 1:
            self.image.fill(dark_gray)
            pygame.draw.rect(self.image, yellow, (4, 4, 6, 32))
            pygame.draw.rect(self.image, blue, (14, 4, 6, 32))
            if self.letter_id:
                font = pygame.font.SysFont("Arial", 14, bold=True)
                let_surf = font.render(self.letter_id, True, white)
                self.image.blit(let_surf, (25, 12))
        elif self.tile_type == 2:
            self.image.fill(light_gray)
            pygame.draw.rect(self.image, black, (3, 3, tilesize-6, tilesize-6), 2)

class ItemColetavel(ObjetoCenario):
    """Classe filha para as folhas do projeto final."""
    def __init__(self, col, row, is_easter_egg=False, letter_hint=""):
        super().__init__(col, row, 18, 24)
        self.rect.center = (col * tilesize + tilesize // 2, row *tilesize + tilesize // 2)
        self.is_easter_egg = is_easter_egg
        self.letter_hint = self.letter_hint

        self.image.fill(white)
        pygame.draw.rect(self.image, black, (0, 0, 18, 24), 1)
        cor_linha = red if is_easter_egg else blue
        pygame.draw.line(self.image, cor_linha, (3, 6), (15, 6), 1)
        pygame.draw.line(self.image, cor_linha, (3, 14), (12, 14), 1)
