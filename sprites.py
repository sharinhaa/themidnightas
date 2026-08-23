# sprites.py
import pygame
import math
import random
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


class Librarian(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        
        self.image = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 30, 30), (tilesize // 2, tilesize // 2), tilesize // 2 - 2)
        
        self.rect = self.image.get_rect()
        self.reset_to_grid(x, y)
        
        self.speed = 110  # Velocidade levemente ajustada
        self.direction = pygame.math.Vector2(0, 0)
        self.choose_next_cell()

    def reset_to_grid(self, x, y):
        self.grid_x = int(x)
        self.grid_y = int(y)
        self.pos = pygame.math.Vector2(
            self.grid_x * tilesize + tilesize // 2, 
            self.grid_y * tilesize + tilesize // 2
        )
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.hitbox = self.rect.inflate(-8, -8)
        self.target_grid = (self.grid_x, self.grid_y)
        self.target_pos = pygame.math.Vector2(self.pos)
        self.last_grid = (self.grid_x, self.grid_y)

    def is_walkable(self, col, row):
        if 0 <= row < len(map_data) and 0 <= col < len(map_data[0]):
            return map_data[row][col] in [0, 3, 4, 6, 7]
        return False

    def get_valid_neighbors(self):
        col, row = self.grid_x, self.grid_y
        candidates = []
        directions = [(col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)]
        
        for c, r in directions:
            if self.is_walkable(c, r):
                candidates.append((c, r))
        return candidates

    def choose_next_cell(self):
        neighbors = self.get_valid_neighbors()
        if not neighbors:
            return

        unvisited = [n for n in neighbors if n != self.last_grid]
        next_cell = random.choice(unvisited) if unvisited else random.choice(neighbors)

        self.last_grid = (self.grid_x, self.grid_y)
        self.target_grid = next_cell
        
        target_x = next_cell[0] * tilesize + tilesize // 2
        target_y = next_cell[1] * tilesize + tilesize // 2
        self.target_pos = pygame.math.Vector2(target_x, target_y)

    def update(self, dt):
        target_vector = self.target_pos - self.pos
        distance = target_vector.length()

        if distance < 3:
            self.pos = pygame.math.Vector2(self.target_pos)
            self.grid_x, self.grid_y = self.target_grid
            self.choose_next_cell()
            target_vector = self.target_pos - self.pos
            distance = target_vector.length()

        if distance > 0:
            self.direction = target_vector.normalize()
            self.pos += self.direction * self.speed * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self.hitbox.center = self.rect.center

        self.check_player_detection()

    def has_line_of_sight(self, target_pos):
        start = self.pos
        end = pygame.math.Vector2(target_pos)
        dist = start.distance_to(end)
        
        if dist == 0:
            return True

        steps = int(dist / 10)
        for i in range(1, steps):
            check_point = start.lerp(end, i / steps)
            for wall in self.game.walls:
                if wall.rect.collidepoint(check_point.x, check_point.y):
                    return False
        return True

    def check_player_detection(self):
        to_player = pygame.math.Vector2(self.game.player.rect.center) - self.pos
        dist_to_player = to_player.length()

        # 1. CAPTURA POR TRÁS OU LADOS (Toque físico bem próximo)
        if dist_to_player < 20:
            self.game.trigger_catch()
            return

        # 2. CAPTURA PELA FRENTE (Curta distância dentro do cone de visão)
        if self.direction.length() > 0 and dist_to_player < 35:
            angle_to_player = self.direction.angle_to(to_player)
            
            # Dentro do ângulo da lanterna (-35° a +35°)
            if -35 <= angle_to_player <= 35:
                if self.has_line_of_sight(self.game.player.rect.center):
                    self.game.trigger_catch()

    def draw_vision_cone(self, surface):
        if self.direction.length() == 0:
            return

        # Mantém a luz vermelha exatamente no alcance da imagem (75 pixels)
        cone_length = 75
        cone_angle = 40

        base_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))

        p1 = self.pos
        left_angle = math.radians(base_angle - cone_angle)
        right_angle = math.radians(base_angle + cone_angle)

        p2 = self.pos + pygame.math.Vector2(math.cos(left_angle), math.sin(left_angle)) * cone_length
        p3 = self.pos + pygame.math.Vector2(math.cos(right_angle), math.sin(right_angle)) * cone_length

        cone_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surface, (255, 0, 0, 60), [p1, p2, p3])
        surface.blit(cone_surface, (0, 0))
                        
    def draw_vision_cone(self, surface):
        if self.direction.length() == 0:
            return

        cone_length = 75
        cone_angle = 40

        base_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))

        p1 = self.pos
        left_angle = math.radians(base_angle - cone_angle)
        right_angle = math.radians(base_angle + cone_angle)

        p2 = self.pos + pygame.math.Vector2(math.cos(left_angle), math.sin(left_angle)) * cone_length
        p3 = self.pos + pygame.math.Vector2(math.cos(right_angle), math.sin(right_angle)) * cone_length

        cone_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surface, (255, 0, 0, 60), [p1, p2, p3])
        surface.blit(cone_surface, (0, 0))

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