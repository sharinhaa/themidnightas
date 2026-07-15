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
        
        # Desenha o Carlos Eugênio
        pygame.draw.circle(self.image, purple, (tilesize//2, tilesize//2), tilesize//2 - 2)
        pygame.draw.rect(self.image, white, (tilesize//4, tilesize//4, tilesize//2, tilesize//2))

        # Hitbox interna menor e centralizada para evitar prender nas quinas das paredes
        self.hitbox = pygame.Rect(0, 0, tilesize - 12, tilesize - 12)
        self.hitbox.center = self.rect.center

    def get_input(self):
        self.vx, self.vy = 0, 0
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_crouching = True
            speed =player_speed_crouch
        else:
            self.is_crouching = False
            speed = player_speed_base

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  self.vx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:    self.vy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  self.vy = speed

        # Normalização vetorial
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def move_and_collide(self, dt):
        """Movimentação robusta com verificação independente por eixo."""
        # --- EIXO X ---
        self.x += self.vx * dt
        self.hitbox.centerx = int(self.x) + tilesize // 2
        
        # Checa colisão apenas no eixo X
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.rect):
                if self.vx > 0: # Movendo para a direita, bateu na esquerda da parede
                    self.hitbox.right = wall.rect.left
                elif self.vx < 0: # Movendo para a esquerda, bateu na direita da parede
                    self.hitbox.left = wall.rect.right
                self.x = self.hitbox.centerx - tilesize // 2
                self.vx = 0

        # --- EIXO Y ---
        self.y += self.vy * dt
        self.hitbox.centery = int(self.y) + tilesize // 2
        
        # Checa colisão apenas no eixo Y
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.rect):
                if self.vy > 0: # Movendo para baixo, bateu no topo da parede
                    self.hitbox.bottom = wall.rect.top
                elif self.vy < 0: # Movendo para cima, bateu na base da parede
                    self.hitbox.top = wall.rect.bottom
                self.y = self.hitbox.centery - tilesize // 2
                self.vy = 0

        # Sincroniza a posição visual final do sprite
        self.rect.center = self.hitbox.center

    def update(self, dt):
        self.get_input()
        self.move_and_collide(dt)


class Librarian(Entidade):
    """Inimigo: Patrulha robusta com prevenção real de colisão física."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        pygame.draw.circle(self.image, red, (tilesize//2, tilesize//2), tilesize//2 - 2)
        pygame.draw.circle(self.image, black, (tilesize//2, tilesize//2), tilesize//5)
        
        # Waypoints reais baseados em pixels centrais
        self.waypoints = [
            pygame.math.Vector2(2 * tilesize + tilesize//2, 1 * tilesize + tilesize//2),
            pygame.math.Vector2(18 * tilesize + tilesize//2, 1 * tilesize + tilesize//2),
            pygame.math.Vector2(18 * tilesize + tilesize//2, 10 * tilesize + tilesize//2),
            pygame.math.Vector2(2 * tilesize + tilesize//2, 10 * tilesize + tilesize//2),
        ]
        self.current_waypoint = 0
        self.pos = pygame.math.Vector2(self.rect.center)
        self.facing_angle = 0.0

    def update(self, dt):
        target = self.waypoints[self.current_waypoint]
        direction = target - self.pos
        dist = direction.length()
        
        if dist > 5:
            direction = direction.normalize()
            self.facing_angle = math.atan2(-direction.y, direction.x)
            
            # Movimentação passo a passo do Bibliotecário com checagem de colisão real
            step_move = direction * librarian_speed * dt
            
            # Testa colisão no eixo X do Inimigo
            self.pos.x += step_move.x
            self.rect.centerx = int(self.pos.x)
            for wall in self.game.walls:
                if self.rect.colliderect(wall.rect):
                    if step_move.x > 0: self.rect.right = wall.rect.left
                    elif step_move.x < 0: self.rect.left = wall.rect.right
                    self.pos.x = self.rect.centerx

            # Testa colisão no eixo Y do Inimigo (Impede que ele atravesse estantes)
            self.pos.y += step_move.y
            self.rect.centery = int(self.pos.y)
            for wall in self.game.walls:
                if self.rect.colliderect(wall.rect):
                    if step_move.y > 0: self.rect.bottom = wall.rect.top
                    elif step_move.y < 0: self.rect.top = wall.rect.bottom
                    self.pos.y = self.rect.centery
        else:
            # Passa para o próximo ponto de patrulha ao chegar perto
            self.current_waypoint = (self.current_waypoint + 1) % len(self.waypoints)

        self.check_player_detection()

    def check_player_detection(self):
        player = self.game.player
        vec = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        distance = vec.length()

        if distance < detection_radius:
            # 1. Detecção Acústica em Piso Barulhento
            px = int(player.rect.centerx // tilesize)
            py = int(player.rect.centery // tilesize)
            if 0 <= py < len(map_data) and 0 <= px < len(map_data[0]):
                if map_data[py][px] == 5 and not player.is_crouching:
                    self.game.trigger_catch()
                    return

            # 2. Detecção Visual no Cone de Visão (Raycasting)
            if distance > 0:
                angle_to_player = math.atan2(-vec.y, vec.x)
                angle_diff = (angle_to_player - self.facing_angle + math.pi) % (2 * math.pi) - math.pi
                
                if abs(angle_diff) < math.pi / 4: # Cone de visão de 90°
                    if self.has_line_of_sight(pygame.math.Vector2(self.rect.center), pygame.math.Vector2(player.rect.center)):
                        self.game.trigger_catch()

    def has_line_of_sight(self, start, end):
        steps = int(start.distance_to(end) / 8)
        if steps == 0: return True
        for i in range(1, steps):
            point = start.lerp(end, i / steps)
            tx, ty = int(point.x // tilesize), int(point.y // tilesize)
            if 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0]):
                if map_data[ty][tx] == 1: # Estante obstrui totalmente a visão
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