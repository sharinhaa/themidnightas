import pygame
import math
import random
from config import *
from collections import deque

SECOES_ESTANTES = {}

class Entidade(pygame.sprite.Sprite):
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
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize

class ChaveSecreta(pygame.sprite.Sprite):
    """Chave dourada que surge na sala do bibliotecário após concluir o ritual."""
    def __init__(self, col, row):
        super().__init__()
        self.col = col
        self.row = row
        self.timer = 0.0
        self.base_y = row * tilesize + tilesize // 2
        self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(col * tilesize + tilesize // 2, self.base_y))
        self.desenhar_chave()

    def desenhar_chave(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (255, 225, 80, 65), (13, 13), 12)
        pygame.draw.circle(self.image, (245, 200, 45), (8, 13), 5, 2)
        pygame.draw.circle(self.image, (165, 115, 20), (8, 13), 5, 1)
        pygame.draw.rect(self.image, (245, 200, 45), (12, 12, 10, 3))
        pygame.draw.rect(self.image, (245, 200, 45), (17, 15, 2, 3))
        pygame.draw.rect(self.image, (245, 200, 45), (20, 15, 2, 4))
        self.image.set_at((7, 11), (255, 255, 220))

    def update(self, dt):
        self.timer += dt * 4.0
        self.rect.centery = int(self.base_y + math.sin(self.timer) * 2.5)

class TotemColecao(pygame.sprite.Sprite):
    """Totem/Relíquia de coleção (Coruja Dourada da Sabedoria) que surge na sala secreta ao abrir a porta."""
    def __init__(self, col, row):
        super().__init__()
        self.col = col
        self.row = row
        self.timer = 0.0
        self.image = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(col * tilesize, row * tilesize))
        self.desenhar_totem(0.0)

    def desenhar_totem(self, offset_y):
        self.image.fill((0, 0, 0, 0))
        cx = tilesize // 2

        # Pedestal de pedra/mármore (fixo no chão)
        pygame.draw.rect(self.image, (75, 70, 90), (7, 24, 18, 6), border_radius=2)
        pygame.draw.rect(self.image, (130, 125, 150), (9, 21, 14, 4))
        pygame.draw.line(self.image, (235, 195, 65), (8, 24), (24, 24), 1)

        ty = int(offset_y)
        # Corpo dourado da Coruja/Totem (sem brilho/halo ao redor)
        pygame.draw.ellipse(self.image, (240, 190, 45), (cx - 6, 8 + ty, 12, 13))
        pygame.draw.ellipse(self.image, (175, 120, 20), (cx - 6, 8 + ty, 12, 13), 1)
        # Orelhas / Coroa do totem
        pygame.draw.polygon(self.image, (245, 205, 60), [(cx - 5, 9 + ty), (cx - 3, 5 + ty), (cx - 1, 9 + ty)])
        pygame.draw.polygon(self.image, (245, 205, 60), [(cx + 1, 9 + ty), (cx + 3, 5 + ty), (cx + 5, 9 + ty)])
        # Olhos de rubi
        pygame.draw.circle(self.image, (255, 55, 75), (cx - 2, 11 + ty), 1)
        pygame.draw.circle(self.image, (255, 55, 75), (cx + 2, 11 + ty), 1)
        # Gema central no peito
        pygame.draw.polygon(self.image, (90, 220, 255), [(cx, 14 + ty), (cx + 2, 16 + ty), (cx, 18 + ty), (cx - 2, 16 + ty)])

    def update(self, dt):
        self.timer += dt * 4.5
        offset_y = math.sin(self.timer) * 2.0
        self.desenhar_totem(offset_y)

class PortaAutomatica(pygame.sprite.Sprite):
    """Porta de madeira com o mesmo visual da porta de saída, abrindo automaticamente ao passar."""
    def __init__(self, game, col, row):
        super().__init__()
        self.game = game
        self.col = col
        self.row = row
        self.is_open = False

        self.img_fechada = self.criar_sprite_fechada()
        self.img_aberta = self.criar_sprite_aberta()

        self.image = self.img_fechada
        self.rect = pygame.Rect(col * tilesize, row * tilesize, tilesize, tilesize)
        self.sensor_rect = self.rect.inflate(36, 24)

    def criar_sprite_fechada(self):
        surf = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)
        surf.fill((45, 25, 10))
        pygame.draw.rect(surf, (115, 65, 28), (3, 2, tilesize - 6, tilesize - 2))
        pygame.draw.rect(surf, (75, 40, 15), (6, 5, tilesize - 12, tilesize - 8), 2)
        pygame.draw.line(surf, (75, 40, 15), (tilesize // 2, 3), (tilesize // 2, tilesize - 2), 1)
        pygame.draw.rect(surf, (50, 50, 55), (3, 7, 4, 3))
        pygame.draw.rect(surf, (50, 50, 55), (3, tilesize - 10, 4, 3))
        pygame.draw.circle(surf, (235, 195, 55), (tilesize - 8, tilesize // 2), 3)
        pygame.draw.rect(surf, (25, 15, 5), (tilesize - 9, tilesize // 2 + 4, 2, 3))
        return surf

    def criar_sprite_aberta(self):
        surf = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)
        pygame.draw.rect(surf, (45, 25, 10), (0, 0, tilesize, 3))
        pygame.draw.rect(surf, (45, 25, 10), (tilesize - 3, 0, 3, tilesize))
        pygame.draw.polygon(surf, (115, 65, 28), [(0, 0), (8, 4), (8, tilesize - 2), (0, tilesize)])
        pygame.draw.polygon(surf, (45, 25, 10), [(0, 0), (8, 4), (8, tilesize - 2), (0, tilesize)], 1)
        pygame.draw.circle(surf, (235, 195, 55), (6, tilesize // 2), 2)
        return surf

    def update(self, dt):
        player_near = self.sensor_rect.colliderect(self.game.player.hitbox)
        librarian_near = self.sensor_rect.colliderect(self.game.librarian.hitbox)

        if player_near or librarian_near:
            if not self.is_open:
                self.is_open = True
                self.image = self.img_aberta
        else:
            if self.is_open:
                self.is_open = False
                self.image = self.img_fechada

class Player(Entidade):
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
            if self.hitbox.colliderect(wall.hitbox):
                if self.vx > 0: self.hitbox.right = wall.hitbox.left
                elif self.vx < 0: self.hitbox.left = wall.hitbox.right
                self.x = self.hitbox.centerx - tilesize // 2
                self.vx = 0

        self.y += self.vy * dt
        self.hitbox.centery = int(self.y) + tilesize // 2
        
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall.hitbox):
                if self.vy > 0: self.hitbox.bottom = wall.hitbox.top
                elif self.vy < 0: self.hitbox.top = wall.hitbox.bottom
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
            return map_data[row][col] in [0, 3, 6, 7, 8, 11, 12, 13]
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
                if wall.hitbox.collidepoint(check_point.x, check_point.y):
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
        self.col = col
        self.row = row
        self.tile_type = tile_type
        self.letter_id = letter_id
        
        self.rect = pygame.Rect(col * tilesize, row * tilesize, tilesize, tilesize)
        self.hitbox = pygame.Rect(col * tilesize, row * tilesize, tilesize, tilesize)
        self.image = pygame.Surface((tilesize, tilesize), pygame.SRCALPHA)

        if self.letter_id != "":
            placa_rect = pygame.Rect(5, 6, tilesize - 10, tilesize - 12)
            pygame.draw.rect(self.image, (32, 18, 8), placa_rect, border_radius=2)
            pygame.draw.rect(self.image, (215, 175, 85), placa_rect, 1, border_radius=2)
            for rx, ry in [(placa_rect.left + 2, placa_rect.top + 2),
                           (placa_rect.right - 3, placa_rect.top + 2),
                           (placa_rect.left + 2, placa_rect.bottom - 3),
                           (placa_rect.right - 3, placa_rect.bottom - 3)]:
                self.image.set_at((rx, ry), (245, 215, 120))

            fonte = pygame.font.SysFont("Courier New", 14, bold=True)
            texto_surf = fonte.render(self.letter_id, True, (250, 235, 185))
            texto_rect = texto_surf.get_rect(center=(tilesize // 2, tilesize // 2))
            self.image.blit(texto_surf, texto_rect)

class ItemColetavel(ObjetoCenario):
    def __init__(self, col, row, is_easter_egg=False, letter_hint="", em_cima_de_móvel=False):
        super().__init__(col, row, 20, 24)
        
        if em_cima_de_móvel:
            self.rect.x = col * tilesize + 6
            self.rect.y = row * tilesize + 2
        else:
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
        pygame.draw.rect(self.image, purple, (2, 2, tilesize - 4, tilesize - 4), 2)

        try:
            img_carregada = pygame.image.load("imagens/Guardião_da_Sabedoria.png").convert_alpha()
            mini = pygame.transform.scale(img_carregada, (tilesize - 8, tilesize - 8))
            self.image.blit(mini, (4, 4))
        except (pygame.error, FileNotFoundError):
            pygame.draw.rect(self.image, dark_gray, (8, 8, tilesize - 16, tilesize - 16))
            pygame.draw.circle(self.image, white, (tilesize // 2, tilesize // 2 - 2), 5)

class BibliotecaGerador:
    def __init__(self, tilesize):
        self.tilesize = tilesize
        self.COR_CHAO = (101, 67, 33)       
        self.COR_LINHA_CHAO = (80, 50, 20)
        self.COR_ESTANTE = (58, 32, 14)    
        self.COR_LIVROS = [
            (175, 42, 42),
            (42, 95, 165),
            (42, 130, 62),
            (195, 155, 48),
            (115, 55, 140),
            (150, 82, 38),
            (55, 130, 140),
        ]

    def criar_textura_chao(self):
        surface = pygame.Surface((self.tilesize, self.tilesize))
        surface.fill(self.COR_CHAO)
        pygame.draw.rect(surface, self.COR_LINHA_CHAO, (0, 0, self.tilesize, self.tilesize), 1)
        pygame.draw.line(surface, self.COR_LINHA_CHAO, (0, self.tilesize//2), (self.tilesize, self.tilesize//2), 1)
        return surface

    def criar_textura_parede(self, grid, col, row):
        """Parede clássica de biblioteca em mogno/boiserie com topo 2.5D, moldura e arandelas."""
        surface = pygame.Surface((self.tilesize, self.tilesize))

        top_wall = (row > 0 and grid[row - 1][col] in [2, 4, 9])
        bot_wall = (row < len(grid) - 1 and grid[row + 1][col] in [2, 4, 9])
        left_wall = (col > 0 and grid[row][col - 1] in [2, 4, 9])
        right_wall = (col < len(grid[0]) - 1 and grid[row][col + 1] in [2, 4, 9])

        if not bot_wall:
            pygame.draw.rect(surface, (36, 20, 11), (0, 0, self.tilesize, 8))
            pygame.draw.line(surface, (68, 40, 22), (0, 0), (self.tilesize, 0), 1)
            pygame.draw.rect(surface, (96, 56, 26), (0, 8, self.tilesize, 3))
            pygame.draw.line(surface, (140, 92, 45), (0, 8), (self.tilesize, 8), 1)

            pygame.draw.rect(surface, (66, 36, 18), (0, 11, self.tilesize, self.tilesize - 16))

            px0 = 0 if left_wall else 3
            px1 = self.tilesize if right_wall else self.tilesize - 3
            pygame.draw.rect(surface, (52, 27, 13), (px0 + 2, 13, max(2, px1 - px0 - 4), 11))
            pygame.draw.rect(surface, (112, 72, 34), (px0 + 2, 13, max(2, px1 - px0 - 4), 11), 1)

            if left_wall:
                pygame.draw.line(surface, (46, 24, 11), (0, 11), (0, self.tilesize - 6), 1)
                pygame.draw.line(surface, (86, 50, 25), (1, 11), (1, self.tilesize - 6), 1)

            if left_wall and right_wall and (col % 6 == 4) and row not in [3, 9]:
                halo = pygame.Surface((26, 22), pygame.SRCALPHA)
                pygame.draw.circle(halo, (255, 215, 100, 55), (13, 11), 11)
                surface.blit(halo, (self.tilesize // 2 - 13, 8))
                cx = self.tilesize // 2
                pygame.draw.rect(surface, (185, 145, 55), (cx - 2, 17, 4, 4))
                pygame.draw.polygon(surface, (250, 225, 135), [(cx - 3, 17), (cx + 3, 17), (cx + 2, 13), (cx - 2, 13)])

            pygame.draw.rect(surface, (42, 22, 10), (0, self.tilesize - 5, self.tilesize, 5))
            pygame.draw.line(surface, (118, 76, 36), (0, self.tilesize - 5), (self.tilesize, self.tilesize - 5), 1)

        else:
            surface.fill((38, 21, 11))
            pygame.draw.line(surface, (52, 30, 16), (0, self.tilesize // 2), (self.tilesize, self.tilesize // 2), 1)

            if not top_wall:
                pygame.draw.rect(surface, (74, 44, 24), (0, 0, self.tilesize, 3))
                pygame.draw.line(surface, (108, 68, 36), (0, 0), (self.tilesize, 0), 1)
            if not left_wall:
                pygame.draw.rect(surface, (74, 44, 24), (0, 0, 3, self.tilesize))
                pygame.draw.line(surface, (108, 68, 36), (0, 0), (0, self.tilesize), 1)
            if not right_wall:
                pygame.draw.rect(surface, (62, 35, 18), (self.tilesize - 3, 0, 3, self.tilesize))
                pygame.draw.line(surface, (24, 12, 6), (self.tilesize - 1, 0), (self.tilesize - 1, self.tilesize), 1)

        return surface

    def criar_textura_mesa(self, grid, col, row):
        surface = self.criar_textura_chao()

        top_mesa = (row > 0 and grid[row - 1][col] == 5)
        bot_mesa = (row < len(grid) - 1 and grid[row + 1][col] == 5)
        left_mesa = (col > 0 and grid[row][col - 1] == 5)
        right_mesa = (col < len(grid[0]) - 1 and grid[row][col + 1] == 5)

        if not top_mesa:
            pygame.draw.rect(surface, (85, 45, 18), (7, 0, self.tilesize - 14, 6))
            pygame.draw.rect(surface, (45, 22, 8), (7, 0, self.tilesize - 14, 3))
        if not bot_mesa:
            pygame.draw.rect(surface, (85, 45, 18), (7, self.tilesize - 6, self.tilesize - 14, 6))
            pygame.draw.rect(surface, (45, 22, 8), (7, self.tilesize - 3, self.tilesize - 14, 3))

        x0 = 0 if left_mesa else 3
        x1 = self.tilesize if right_mesa else self.tilesize - 3
        y0 = 0 if top_mesa else 5
        y1 = self.tilesize if bot_mesa else self.tilesize - 5

        pygame.draw.rect(surface, (150, 96, 44), (x0, y0, x1 - x0, y1 - y0))
        pygame.draw.line(surface, (125, 76, 32), (x0, (y0 + y1) // 2), (x1, (y0 + y1) // 2), 1)

        cor_borda = (75, 42, 16)
        if not top_mesa:
            pygame.draw.line(surface, cor_borda, (x0, y0), (x1 - 1, y0), 2)
        if not bot_mesa:
            pygame.draw.line(surface, cor_borda, (x0, y1 - 1), (x1 - 1, y1 - 1), 2)
        if not left_mesa:
            pygame.draw.line(surface, cor_borda, (x0, y0), (x0, y1 - 1), 2)
        if not right_mesa:
            pygame.draw.line(surface, cor_borda, (x1 - 1, y0), (x1 - 1, y1 - 1), 2)

        padrao = (col + row * 2) % 4
        if padrao == 0:
            pygame.draw.rect(surface, (40, 70, 140), (9, 10, 14, 11))
            pygame.draw.rect(surface, (245, 240, 225), (10, 11, 5, 9))
            pygame.draw.rect(surface, (245, 240, 225), (17, 11, 5, 9))
        elif padrao == 1:
            halo = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(halo, (255, 225, 90, 95), (12, 12), 11)
            surface.blit(halo, (4, 4))
            pygame.draw.circle(surface, (50, 50, 55), (16, 16), 4)
            pygame.draw.circle(surface, (245, 210, 70), (16, 16), 3)
        elif padrao == 2:
            pygame.draw.rect(surface, (240, 238, 230), (10, 9, 10, 13))
            pygame.draw.line(surface, (100, 100, 120), (12, 12), (18, 12), 1)
            pygame.draw.line(surface, (100, 100, 120), (12, 15), (17, 15), 1)
            pygame.draw.line(surface, (180, 40, 40), (21, 10), (23, 20), 2)
        else:
            pygame.draw.rect(surface, (165, 45, 45), (9, 12, 12, 8))
            pygame.draw.rect(surface, (45, 130, 70), (11, 9, 10, 7))

        return surface

    def criar_textura_escrivaninha_chefe(self, grid, col, row):
        surface = self.criar_textura_chao()
        top_mesa = (row > 0 and grid[row - 1][col] == 10)
        bot_mesa = (row < len(grid) - 1 and grid[row + 1][col] == 10)

        if not top_mesa and bot_mesa:
            pygame.draw.circle(surface, (45, 20, 25), (24, 18), 6)
            pygame.draw.rect(surface, (95, 25, 35), (25, 12, 5, 12), border_radius=2)

        y0 = 0 if top_mesa else 4
        y1 = self.tilesize if bot_mesa else self.tilesize - 4

        pygame.draw.rect(surface, (92, 42, 22), (4, y0, 18, y1 - y0))
        pygame.draw.rect(surface, (52, 22, 10), (4, y0, 18, y1 - y0), 2)

        if not top_mesa:
            halo = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(halo, (120, 255, 150, 75), (10, 10), 9)
            surface.blit(halo, (3, 6))
            pygame.draw.rect(surface, (30, 130, 75), (9, 11, 8, 5), border_radius=2)
            pygame.draw.rect(surface, (170, 50, 50), (8, 20, 10, 7))
        elif top_mesa and bot_mesa:
            pygame.draw.rect(surface, (240, 235, 220), (7, 9, 12, 14))
            pygame.draw.line(surface, (120, 110, 100), (13, 9), (13, 23), 1)
        else:
            pygame.draw.rect(surface, (235, 235, 230), (8, 8, 10, 11))
            pygame.draw.circle(surface, (190, 35, 35), (13, 22), 3)

        return surface

    def criar_textura_porta(self):
        surface = pygame.Surface((self.tilesize, self.tilesize))
        surface.fill((45, 25, 10))
        pygame.draw.rect(surface, (115, 65, 28), (3, 2, self.tilesize - 6, self.tilesize - 2))
        pygame.draw.rect(surface, (75, 40, 15), (6, 5, self.tilesize - 12, self.tilesize - 8), 2)
        pygame.draw.line(surface, (75, 40, 15), (self.tilesize // 2, 3), (self.tilesize // 2, self.tilesize - 2), 1)
        pygame.draw.rect(surface, (50, 50, 55), (3, 7, 4, 3))
        pygame.draw.rect(surface, (50, 50, 55), (3, self.tilesize - 10, 4, 3))
        pygame.draw.circle(surface, (235, 195, 55), (self.tilesize - 8, self.tilesize // 2), 3)
        pygame.draw.rect(surface, (25, 15, 5), (self.tilesize - 9, self.tilesize // 2 + 4, 2, 3))
        return surface

    def criar_textura_porta_aberta(self, para_fora=False):
        if para_fora:
            surface = pygame.Surface((self.tilesize, self.tilesize))
            surface.fill((12, 14, 28))
            pygame.draw.rect(surface, (85, 55, 25), (0, 0, 5, self.tilesize))
            pygame.draw.rect(surface, (45, 25, 10), (0, 0, self.tilesize, 3))
            pygame.draw.rect(surface, (45, 25, 10), (0, self.tilesize - 3, self.tilesize, 3))
            pygame.draw.polygon(surface, (115, 65, 28), [(4, 3), (self.tilesize - 2, 0), (self.tilesize - 2, 8), (4, 10)])
            pygame.draw.polygon(surface, (45, 25, 10), [(4, 3), (self.tilesize - 2, 0), (self.tilesize - 2, 8), (4, 10)], 1)
            pygame.draw.circle(surface, (235, 195, 55), (self.tilesize - 6, 5), 2)
        else:
            surface = self.criar_textura_chao()
            pygame.draw.rect(surface, (45, 25, 10), (0, 0, self.tilesize, 3))
            pygame.draw.rect(surface, (45, 25, 10), (self.tilesize - 3, 0, 3, self.tilesize))
            pygame.draw.polygon(surface, (115, 65, 28), [(0, 0), (8, 4), (8, self.tilesize - 2), (0, self.tilesize)])
            pygame.draw.polygon(surface, (45, 25, 10), [(0, 0), (8, 4), (8, self.tilesize - 2), (0, self.tilesize)], 1)
            pygame.draw.circle(surface, (235, 195, 55), (6, self.tilesize // 2), 2)
        return surface

    def criar_textura_estante(self, grid, col, row, letra=""):
        """Estante conectada (auto-tiling) com topo moldurado, livros variados e objetos decorativos."""
        surface = pygame.Surface((self.tilesize, self.tilesize))
        surface.fill((34, 18, 7))

        top_est = (row > 0 and grid[row - 1][col] == 1)
        bot_est = (row < len(grid) - 1 and grid[row + 1][col] == 1)
        left_est = (col > 0 and grid[row][col - 1] == 1)
        right_est = (col < len(grid[0]) - 1 and grid[row][col + 1] == 1)

        if not top_est:
            pygame.draw.rect(surface, (92, 54, 24), (0, 0, self.tilesize, 6))
            pygame.draw.line(surface, (128, 78, 38), (0, 1), (self.tilesize, 1), 1)
            pygame.draw.line(surface, (45, 24, 9), (0, 5), (self.tilesize, 5), 1)
            y_topo_nicho = 6
        else:
            pygame.draw.rect(surface, (68, 38, 15), (0, 0, self.tilesize, 3))
            y_topo_nicho = 3

        if not bot_est:
            pygame.draw.rect(surface, (75, 42, 16), (0, self.tilesize - 5, self.tilesize, 5))
            pygame.draw.line(surface, (110, 66, 28), (0, self.tilesize - 5), (self.tilesize, self.tilesize - 5), 1)
            y_base_nicho = self.tilesize - 5
        else:
            pygame.draw.rect(surface, (68, 38, 15), (0, self.tilesize - 3, self.tilesize, 3))
            y_base_nicho = self.tilesize - 3

        x_ini = 0 if left_est else 3
        x_fim = self.tilesize if right_est else self.tilesize - 3
        if not left_est:
            pygame.draw.rect(surface, (75, 42, 16), (0, 0, 3, self.tilesize))
        if not right_est:
            pygame.draw.rect(surface, (75, 42, 16), (self.tilesize - 3, 0, 3, self.tilesize))

        rng = random.Random(col * 97 + row * 31)
        tipo_nicho = rng.randint(0, 7)

        if not letra and tipo_nicho == 0:
            cx = (x_ini + x_fim) // 2
            pygame.draw.rect(surface, (160, 120, 45), (cx - 4, y_base_nicho - 3, 8, 3))
            pygame.draw.line(surface, (190, 150, 60), (cx, y_base_nicho - 3), (cx, y_base_nicho - 6), 2)
            pygame.draw.circle(surface, (45, 115, 165), (cx, y_base_nicho - 11), 6)
            pygame.draw.circle(surface, (70, 155, 85), (cx - 2, y_base_nicho - 12), 2)
            pygame.draw.circle(surface, (70, 155, 85), (cx + 2, y_base_nicho - 9), 2)
            pygame.draw.arc(surface, (210, 175, 75), (cx - 7, y_base_nicho - 18, 14, 14), -0.8, 2.2, 1)
        elif not letra and tipo_nicho == 1:
            cx = (x_ini + x_fim) // 2
            pygame.draw.rect(surface, (155, 45, 45), (cx - 8, y_base_nicho - 4, 16, 4))
            pygame.draw.rect(surface, (45, 95, 155), (cx - 7, y_base_nicho - 8, 14, 4))
            pygame.draw.rect(surface, (235, 225, 195), (cx - 2, y_base_nicho - 13, 4, 5))
            pygame.draw.circle(surface, (255, 210, 70), (cx, y_base_nicho - 15), 2)
        else:
            x = x_ini + 1
            while x < x_fim - 3:
                if rng.random() < 0.14:
                    x += rng.randint(3, 5)
                    continue

                larg = rng.choice([3, 4, 4, 5])
                if x + larg > x_fim:
                    larg = x_fim - x
                if larg < 2:
                    break

                alt_max = y_base_nicho - y_topo_nicho - 1
                alt = rng.randint(max(8, alt_max - 5), alt_max)
                y_livro = y_base_nicho - alt
                cor = rng.choice(self.COR_LIVROS)

                pygame.draw.rect(surface, cor, (x, y_livro, larg, alt))
                cor_escura = (max(0, cor[0] - 45), max(0, cor[1] - 45), max(0, cor[2] - 45))
                pygame.draw.line(surface, cor_escura, (x + larg - 1, y_livro), (x + larg - 1, y_base_nicho - 1), 1)

                if rng.random() < 0.45 and alt > 10:
                    pygame.draw.line(surface, (235, 200, 95), (x + 1, y_livro + 3), (x + larg - 2, y_livro + 3), 1)
                    if rng.random() < 0.5:
                        pygame.draw.line(surface, (235, 200, 95), (x + 1, y_base_nicho - 4), (x + larg - 2, y_base_nicho - 4), 1)

                x += larg + 1

        if letra:
            placa_rect = pygame.Rect(5, 6, self.tilesize - 10, self.tilesize - 12)
            pygame.draw.rect(surface, (32, 18, 8), placa_rect, border_radius=2)
            pygame.draw.rect(surface, (215, 175, 85), placa_rect, 1, border_radius=2)
            for rx, ry in [(placa_rect.left + 2, placa_rect.top + 2),
                           (placa_rect.right - 3, placa_rect.top + 2),
                           (placa_rect.left + 2, placa_rect.bottom - 3),
                           (placa_rect.right - 3, placa_rect.bottom - 3)]:
                surface.set_at((rx, ry), (245, 215, 120))

            font = pygame.font.SysFont("Courier New", 14, bold=True)
            txt = font.render(letra, True, (250, 235, 185))
            surface.blit(txt, (self.tilesize // 2 - txt.get_width() // 2, self.tilesize // 2 - txt.get_height() // 2))

        return surface

    def desenhar_tapete(self, cenario, col_ini, row_ini, largura_tiles, altura_tiles, cor_fundo, cor_borda):
        rect = pygame.Rect(
            col_ini * self.tilesize + 4,
            row_ini * self.tilesize + 4,
            largura_tiles * self.tilesize - 8,
            altura_tiles * self.tilesize - 8
        )
        pygame.draw.rect(cenario, cor_fundo, rect, border_radius=4)
        pygame.draw.rect(cenario, cor_borda, rect, 2, border_radius=4)
        pygame.draw.rect(cenario, cor_borda, rect.inflate(-8, -8), 1)

    def gerar_cenario_completo(self, map_data, width, height, secoes=None):
        cenario = pygame.Surface((width, height))
        if secoes is None:
            secoes = {}
        
        tile_chao = self.criar_textura_chao()
        tile_porta = self.criar_textura_porta()

        # 1. Piso base
        for row_idx, row in enumerate(map_data):
            for col_idx, tile in enumerate(row):
                cenario.blit(tile_chao, (col_idx * self.tilesize, row_idx * self.tilesize))

        # 2. Tapetes e Passadeiras nos corredores
        self.desenhar_tapete(cenario, 2, 4, 21, 1, (95, 38, 38), (185, 145, 70))
        self.desenhar_tapete(cenario, 2, 13, 21, 2, (95, 38, 38), (185, 145, 70))
        self.desenhar_tapete(cenario, 25, 10, 3, 4, (115, 32, 38), (205, 165, 70))
        self.desenhar_tapete(cenario, 25, 1, 4, 2, (58, 32, 95), (215, 180, 75))
        self.desenhar_tapete(cenario, 25, 16, 4, 3, (35, 75, 65), (180, 155, 85))

        # 3. Sombras 2.5D projetadas no piso abaixo de paredes e estantes
        sombra = pygame.Surface((self.tilesize, 7), pygame.SRCALPHA)
        sombra.fill((15, 8, 2, 95))
        for row_idx in range(len(map_data) - 1):
            for col_idx in range(len(map_data[0])):
                if map_data[row_idx][col_idx] in [1, 2] and map_data[row_idx + 1][col_idx] not in [1, 2]:
                    cenario.blit(sombra, (col_idx * self.tilesize, (row_idx + 1) * self.tilesize))

        # 4. Paredes, Estantes, Mesas e Portas
        for row_idx, row in enumerate(map_data):
            for col_idx, tile in enumerate(row):
                x = col_idx * self.tilesize
                y = row_idx * self.tilesize

                if tile == 2:
                    cenario.blit(self.criar_textura_parede(map_data, col_idx, row_idx), (x, y))
                elif tile == 1:
                    letter = secoes.get((col_idx, row_idx), "")
                    tile_est = self.criar_textura_estante(map_data, col_idx, row_idx, letter)
                    cenario.blit(tile_est, (x, y))
                elif tile == 5:
                    cenario.blit(self.criar_textura_mesa(map_data, col_idx, row_idx), (x, y))
                elif tile == 10:
                    cenario.blit(self.criar_textura_escrivaninha_chefe(map_data, col_idx, row_idx), (x, y))
                elif tile in [4, 9]:
                    cenario.blit(tile_porta, (x, y))

        return cenario