import pygame
import math
import random
from config import *
from collections import deque

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
    """Jogador: Carlos Eugênio."""
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.vx, self.vy = 0, 0
        self.is_crouching = False
        
        pygame.draw.circle(self.image, purple, (tilesize//2, tilesize//2), tilesize//2 - 2)
        pygame.draw.rect(self.image, white, (tilesize//4, tilesize//4, tilesize//2, tilesize//2))

        self.hitbox = pygame.Rect(0, 0, tilesize - 10, tilesize - 10)
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
        
        self.speed = 110
        self.chase_speed = 130
        self.direction = pygame.math.Vector2(1, 0)
        self.radar_range = 240.0
        self.is_chasing = False
        self.chase_target_grid = None
        self.path = []
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
        self.is_chasing = False
        self.path = []

    def is_walkable(self, col, row):
        if 0 <= row < len(map_data) and 0 <= col < len(map_data[0]):
            return map_data[row][col] in [0, 3, 4, 6, 7]
        return False

    def get_valid_neighbors(self, col, row):
        candidates = []
        directions = [(col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)]
        
        for c, r in directions:
            if self.is_walkable(c, r):
                candidates.append((c, r))
        return candidates

    def choose_next_cell(self):
        neighbors = self.get_valid_neighbors(self.grid_x, self.grid_y)
        if not neighbors:
            return

        unvisited = [n for n in neighbors if n != self.last_grid]
        next_cell = random.choice(unvisited) if unvisited else random.choice(neighbors)

        self.last_grid = (self.grid_x, self.grid_y)
        self.target_grid = next_cell
        
        target_x = next_cell[0] * tilesize + tilesize // 2
        target_y = next_cell[1] * tilesize + tilesize // 2
        self.target_pos = pygame.math.Vector2(target_x, target_y)

    def find_path_bfs(self, start_grid, goal_grid):
        if start_grid == goal_grid:
            return []

        queue = deque([start_grid])
        came_from = {start_grid: None}

        while queue:
            current = queue.popleft()
            if current == goal_grid:
                break

            for nxt in self.get_valid_neighbors(current[0], current[1]):
                if nxt not in came_from:
                    queue.append(nxt)
                    came_from[nxt] = current

        if goal_grid not in came_from:
            return []

        curr = goal_grid
        path = []
        while curr != start_grid:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()
        return path

    def has_line_of_sight(self, target_pos):
        start = self.pos
        end = pygame.math.Vector2(target_pos)
        dist = start.distance_to(end)

        if dist == 0:
            return True

        steps = max(1, int(dist / 8))
        for i in range(1, steps):
            check_point = start.lerp(end, i / steps)
            for wall in self.game.walls:
                if wall.rect.collidepoint(check_point.x, check_point.y):
                    return False
        return True

    def is_player_in_cone(self, player_center):
        to_player = pygame.math.Vector2(player_center) - self.pos
        dist = to_player.length()

        if dist > 100:
            return False

        if self.direction.length() > 0:
            angle = self.direction.angle_to(to_player)
            if -45 <= angle <= 45:
                return self.has_line_of_sight(player_center)
        return False

    def update(self, dt):
        player_center = self.game.player.rect.center
        player_grid = (
            int(self.game.player.hitbox.centerx // tilesize),
            int(self.game.player.hitbox.centery // tilesize)
        )
        dist_to_player = self.pos.distance_to(player_center)
        has_los = self.has_line_of_sight(player_center)
        in_cone = self.is_player_in_cone(player_center)

        self.check_player_detection()

        if (in_cone or (has_los and dist_to_player <= self.radar_range)):
            self.is_chasing = True
            self.chase_target_grid = player_grid
            self.path = self.find_path_bfs((self.grid_x, self.grid_y), player_grid)
        elif self.is_chasing and not has_los:
            if not self.path:
                self.is_chasing = False
                self.choose_next_cell()

        current_speed = self.chase_speed if self.is_chasing else self.speed

        if self.is_chasing and self.path:
            next_step = self.path[0]
            target_x = next_step[0] * tilesize + tilesize // 2
            target_y = next_step[1] * tilesize + tilesize // 2
            self.target_pos = pygame.math.Vector2(target_x, target_y)

        target_vector = self.target_pos - self.pos
        distance = target_vector.length()

        if distance < 4:
            self.pos = pygame.math.Vector2(self.target_pos)
            self.grid_x = int(self.pos.x // tilesize)
            self.grid_y = int(self.pos.y // tilesize)

            if self.is_chasing and self.path:
                self.path.pop(0)
                if not self.path:
                    self.is_chasing = False
                    self.choose_next_cell()
            else:
                self.choose_next_cell()

            target_vector = self.target_pos - self.pos
            distance = target_vector.length()

        if distance > 0:
            self.direction = target_vector.normalize()
            self.pos += self.direction * current_speed * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self.hitbox.center = self.rect.center

    def check_player_detection(self):
        player_center = self.game.player.rect.center
        to_player = pygame.math.Vector2(player_center) - self.pos
        dist_to_player = to_player.length()

        if dist_to_player < 22:
            self.game.trigger_catch()

    def get_radar_status(self):
        player_center = self.game.player.rect.center
        dist = self.pos.distance_to(player_center)

        if dist > self.radar_range:
            return "Radar: Sem sinal", light_gray, False

        if not self.has_line_of_sight(player_center):
            return "Radar: Bloqueado(Estante)", light_gray, False

        if dist < 80:
            return "Radar: Perigo Iminente!", red, True
        elif dist < 150:
            return "Radar: Alvo Detectado", yellow, True
        else:
            return "Radar: Sinal Próximo...", yellow, True

    def draw_vision_cone(self, surface):
        if self.direction.length() == 0:
            return

        cone_length = 80
        cone_angle = 40

        base_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))

        p1 = (self.pos.x, self.pos.y)
        left_angle = math.radians(base_angle - cone_angle)
        right_angle = math.radians(base_angle + cone_angle)

        p2_vec = self.pos + pygame.math.Vector2(math.cos(left_angle), math.sin(left_angle)) * cone_length
        p3_vec = self.pos + pygame.math.Vector2(math.cos(right_angle), math.sin(right_angle)) * cone_length

        p2 = (p2_vec.x, p2_vec.y)
        p3 = (p3_vec.x, p3_vec.y)

        cone_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surface, (200, 0, 0, 90), [p1, p2, p3])
        surface.blit(cone_surface, (0, 0))

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, col, row, tile_type, letter_id=""):
        super().__init__()
        self.tile_type = tile_type
        self.letter_id = letter_id  # <--- Salva a identificacao da letra (I, F, R, N)
        self.image = pygame.Surface((tilesize, tilesize))

        if tile_type == 1:
            self.image.fill((70, 70, 80)) # Cor das estantes comuns
        elif tile_type == 2:
            self.image.fill(dark_gray)   # Paredes externas
        elif tile_type == 9:
            self.image.fill((40, 40, 60)) # Blocos da passagem secreta

        # Desenha a letra visível no topo da estante
        if self.letter_id:
            font = pygame.font.SysFont("Arial", 16, bold=True)
            text_surf = font.render(self.letter_id, True, (255, 215, 0))
            self.image.blit(text_surf, (8, 4))

        self.rect = self.image.get_rect()
        self.rect.x = col * tilesize
        self.rect.y = row * tilesize

class ItemColetavel(ObjetoCenario):
    def __init__(self, col, row, is_easter_egg=False, letter_hint=""):
        super().__init__(col, row, 20, 24)
        
        # Centraliza o sprite e sua hitbox exatamente na célula
        self.rect.center = (col * tilesize + tilesize // 2, row * tilesize + tilesize // 2)
        self.is_easter_egg = is_easter_egg
        self.letter_hint = letter_hint

        self.image.fill(white)
        pygame.draw.rect(self.image, black, (0, 0, 20, 24), 1)

        if is_easter_egg:
            pygame.draw.rect(self.image, yellow, (0, 0, 20, 24), 2)
            font = pygame.font.SysFont("Arial", 13, bold=True)
            letra_surf = font.render(self.letter_hint, True, red)
            self.image.blit(letra_surf, (5, 3))
        else:
            pygame.draw.line(self.image, blue, (3, 6), (17, 6), 1)
            pygame.draw.line(self.image, blue, (3, 14), (14, 14), 1)

class QuadroSecreto(ObjetoCenario):
    def __init__(self, col, row):
        super().__init__(col, row, tilesize, tilesize)
        self.image.fill(yellow)
        pygame.draw.rect(self.image, purple, (2, 2, tilesize - 4, tilesize - 4), 3)
        pygame.draw.rect(self.image, dark_gray, (8, 8, tilesize - 16, tilesize - 16))
        pygame.draw.circle(self.image, white, (tilesize // 2, tilesize // 2 - 2), 5)