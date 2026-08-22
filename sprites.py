# sprites.py
import pygame
import math
from config import *

class Entidade(pygame.sprite.Sprite):
    """Classe base para objetos móveis."""
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.x = float(x * tilesize)
        self.y = float(y * tilesize)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

class ObjetoCenario(pygame.sprite.Sprite):
    """Classe base para elementos estáticos do cenário."""
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize

class Player(Entidade):
    """Jogador: Carlos Eugênio com física suave de deslize pelas quinas."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.vx, self.vy = 0, 0
        self.is_crouching = False
        
        pygame.draw.circle(self.image, purple, (tilesize//2, tilesize//2), tilesize//2 - 2)
        pygame.draw.rect(self.image, white, (tilesize//4, tilesize//4, tilesize//2, tilesize//2))

        self.hitbox = pygame.Rect(0, 0, tilesize - 12, tilesize - 12)
        self.hitbox.center = self.rect.center

    def get_input(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_crouching = True
            speed = player_speed_crouch
        else:
            self.is_crouching = False
            speed = player_speed_base

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  self.vx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:    self.vy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  self.vy = speed

        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def move_and_collide(self, dt):
        self.x += self.vx * dt
        self.hitbox.centerx = int(self.x) + tilesize // 2
        
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.rect):
                if self.vx > 0: self.hitbox.right = wall.rect.left
                elif self.vx < 0: self.hitbox.left = wall.rect.right
                self.x = self.hitbox.centerx - tilesize // 2
                self.vx = 0

        self.y += self.vy * dt
        self.hitbox.centery = int(self.y) + tilesize // 2
        
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.rect):
                if self.vy > 0: self.hitbox.bottom = wall.rect.top
                elif self.vy < 0: self.hitbox.top = wall.rect.bottom
                self.y = self.hitbox.centery - tilesize // 2
                self.vy = 0

        self.rect.center = self.hitbox.center

    def update(self, dt):
        self.get_input()
        self.move_and_collide(dt)


class Librarian(Entidade):
    """Inimigo: Nasce distante e patrulha corredores limpos do mapa."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        
        pygame.draw.circle(self.image, red, (tilesize//2, tilesize//2), tilesize//2 - 2)
        pygame.draw.circle(self.image, black, (tilesize//2, tilesize//2), tilesize//5)

        self.hitbox = pygame.Rect(0, 0, tilesize - 14, tilesize - 14)

        # Waypoints configurados sob medida para os corredores abertos do seu map_data
        grid_waypoints = [
            (17, 10), # Ponto inicial (Perto da saída)
            (1, 10),  # Corredor inferior esquerdo
            (1, 4),   # Subida pelo lado esquerdo
            (18, 4),  # Corredor central totalmente limpo
            (18, 10)  # Retorno ao canto inferior direito
        ]

        self.waypoints = [
            pygame.math.Vector2(col * tilesize + tilesize//2, row * tilesize + tilesize//2)
            for col, row in grid_waypoints
        ]

        self.current_waypoint = 0
        self.pos = pygame.math.Vector2(x * tilesize + tilesize//2, y * tilesize + tilesize//2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center = self.rect.center
        self.facing_angle = 0.0

    def update(self, dt):
        target = self.waypoints[self.current_waypoint]
        direction = target - self.pos
        dist = direction.length()

        if dist < 8:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)
            return

        direction = direction.normalize()
        self.facing_angle = math.atan2(-direction.y, direction.x)
        
        step = direction * librarian_speed * dt
        self.pos += step

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.hitbox.center = self.rect.center

        self.check_player_detection()

    def check_player_detection(self):
        player = self.game.player
        vec = pygame.math.Vector2(player.hitbox.center) - pygame.math.Vector2(self.rect.center)
        distance = vec.length()

        # Toque direto
        if self.hitbox.colliderect(player.hitbox):
            self.game.trigger_catch()
            return

        # Raio de visão
        if 0 < distance < detection_radius:
            angle_to_player = math.atan2(-vec.y, vec.x)
            angle_diff = (angle_to_player - self.facing_angle + math.pi) % (2 * math.pi) - math.pi
            
            if abs(angle_diff) < math.pi / 4:
                if self.has_line_of_sight(pygame.math.Vector2(self.rect.center), pygame.math.Vector2(player.hitbox.center)):
                    self.game.trigger_catch()

    def has_line_of_sight(self, start, end):
        steps = int(start.distance_to(end) / 8)
        if steps == 0: return True
        for i in range(1, steps):
            point = start.lerp(end, i / steps)
            tx, ty = int(point.x // tilesize), int(point.y // tilesize)
            if 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0]):
                if map_data[ty][tx] in [1, 2]: # Estantes e mesas bloqueiam a visão
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
    def __init__(self, col, row, is_easter_egg=False, letter_hint=""):
        super().__init__(col, row, 18, 24)
        self.rect.center = (col * tilesize + tilesize // 2, row * tilesize + tilesize // 2)
        self.is_easter_egg = is_easter_egg
        self.letter_hint = letter_hint
        
        self.image.fill(white)
        pygame.draw.rect(self.image, black, (0, 0, 18, 24), 1)
        cor_linha = red if is_easter_egg else blue
        pygame.draw.line(self.image, cor_linha, (3, 6), (15, 6), 1)
        pygame.draw.line(self.image, cor_linha, (3, 14), (12, 14), 1)