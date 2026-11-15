import pygame
import sys
import random 
import copy
from config import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("The Midnight Assignment")

        self.clock = pygame.time.Clock()
        self.running = True

        self.original_map_data = copy.deepcopy(map_data)
        self.gerador = BibliotecaGerador(tilesize)

        self.font_title = pygame.font.SysFont("Courier New", 32, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 16, bold=True)

        # CARREGAMENTO DOS FUNDOS (Menu, Vitória e Derrota) 
        try:
            self.menu_bg = pygame.image.load("imagens/menu_bg.png").convert()
            self.menu_bg = pygame.transform.scale(self.menu_bg, (width, height))
        except (pygame.error, FileNotFoundError):
            self.menu_bg = pygame.Surface((width, height))
            self.menu_bg.fill((15, 15, 25))

        try:
            self.vitoria_bg = pygame.image.load("imagens/vitoria_bg.png").convert()
            self.vitoria_bg = pygame.transform.scale(self.vitoria_bg, (width, height))
        except (pygame.error, FileNotFoundError):
            try:
                self.vitoria_bg = pygame.image.load("imagens/vitoria_bg.jpg").convert()
                self.vitoria_bg = pygame.transform.scale(self.vitoria_bg, (width, height))
            except (pygame.error, FileNotFoundError):
                self.vitoria_bg = None

        try:
            self.derrota_bg = pygame.image.load("imagens/game_over.png").convert()
            self.derrota_bg = pygame.transform.scale(self.derrota_bg, (width, height))
        except (pygame.error, FileNotFoundError):
            self.derrota_bg = None

        # CARREGAMENTO DA IMAGEM DO GUARDIÃO DA SABEDORIA (EASTER EGG)
        try:
            img = pygame.image.load("imagens/Guardião_da_Sabedoria.png").convert_alpha()
            self.guardiao_img = pygame.transform.scale(img, (170, 226))
        except (pygame.error, FileNotFoundError):
            self.guardiao_img = None

        self.state = 'MENU'
        self.menu_index = 0
        self.avatar_selecao = "Carlos Eugênio"

        self.score = 0
        self.lives = 3 
        self.papers_collected = 0
        self.total_papers_needed = 5
        self.exit_unlocked = False 
        
        self.secoes_mapa = {}
        self.letras_coords = {}
        self.pistas_coletadas = set()
        self.easter_egg_sequence = []
        self.correct_sequence = ["I", "F", "R", "N"]
        self.pistas_spawned = False
        self.msg_feedback = ""
        self.msg_timer = 0

    def mapear_blocos_estantes(self, grid):
        """Agrupa blocos conectados e ordena de A até Z seguindo a leitura natural (por fileira e coluna)."""
        visitados = set()
        blocos = []

        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == 1 and (col, row) not in visitados:
                    fila = deque([(col, row)])
                    visitados.add((col, row))
                    while fila:
                        c, r = fila.popleft()
                        for dc, dr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nc, nr = c + dc, r + dr
                            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                                if grid[nr][nc] == 1 and (nc, nr) not in visitados:
                                    visitados.add((nc, nr))
                                    fila.append((nc, nr))
                    blocos.append((col, row))

        blocos.sort(key=lambda pos: (pos[1] // 2, pos[0]))

        secoes = {}
        letras_coords = {}
        alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        for idx, (col, row) in enumerate(blocos):
            if idx < len(alfabeto):
                letra = alfabeto[idx]
                secoes[(col, row)] = letra
                letras_coords[letra] = (col, row)

        return secoes, letras_coords

    def init_level(self):
        global map_data
        map_data = copy.deepcopy(self.original_map_data)
        
        self.secoes_mapa, self.letras_coords = self.mapear_blocos_estantes(map_data)
        self.cenario_bg = self.gerador.gerar_cenario_completo(map_data, width, height, self.secoes_mapa)

        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.papers = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.quadro_group = pygame.sprite.Group()
        
        self.spawn_pos = (26, 16)
        self.librarian_spawn_pos = (27, 11)
        self.exit_rect = None
        self.exit_coords = None
        self.quadro_pos_coords = None

        self.pistas_spawned = False
        self.pistas_coletadas.clear()
        self.easter_egg_sequence = []
        self.msg_feedback = ""

        for row, tiles in enumerate(map_data):
            for col, tile in enumerate(tiles):
                if tile in [0, 3, 4, 6, 7, 8]:
                    bg = ObjetoCenario(col, row, tilesize, tilesize)
                    bg.image.set_alpha(0) 
                    self.background_tiles.add(bg)

                if tile in [1, 2, 4, 5, 9]:
                    letter = self.secoes_mapa.get((col, row), "")
                    obs = Obstaculo(col, row, tile, letter)
                    self.walls.add(obs)
                    self.all_sprites.add(obs)

                if tile == 3:
                    self.spawn_pos = (col, row)
                elif tile == 4:
                    self.exit_coords = (col, row)
                    self.exit_rect = pygame.Rect(col * tilesize, row * tilesize, tilesize, tilesize)
                elif tile == 6:
                    folha = ItemColetavel(col, row, em_cima_de_móvel=False)
                    self.papers.add(folha)
                    self.all_sprites.add(folha)
                elif tile == 7:
                    self.librarian_spawn_pos = (col, row)
                elif tile == 8:
                    self.quadro_pos_coords = (col, row)

        self.player = Player(self, self.spawn_pos[0], self.spawn_pos[1])
        self.all_sprites.add(self.player)
        
        self.librarian = Librarian(self, self.librarian_spawn_pos[0], self.librarian_spawn_pos[1])
        self.all_sprites.add(self.librarian)

    def spawn_pistas_easter_egg(self):
        estantes_disponiveis = [
            letra for letra in self.letras_coords.keys()
            if letra not in self.correct_sequence
        ]

        if len(estantes_disponiveis) >= len(self.correct_sequence):
            estantes_esconderijo = random.sample(estantes_disponiveis, len(self.correct_sequence))
        else:
            estantes_esconderijo = list(self.letras_coords.keys())[:len(self.correct_sequence)]

        for letra_pista, estante_alvo in zip(self.correct_sequence, estantes_esconderijo):
            cx, cy = self.letras_coords[estante_alvo]
            pista = ItemColetavel(cx, cy, is_easter_egg=True, letter_hint=letra_pista, em_cima_de_móvel=True)
            pista.image.set_alpha(0)
            self.papers.add(pista)
            self.all_sprites.add(pista)
        
        self.pistas_spawned = True

    def unlock_exit_door(self):
        """Abre a porta de saída na parede para fora da biblioteca e libera a passagem."""
        self.exit_unlocked = True
        tile_porta_saida_aberta = self.gerador.criar_textura_porta_aberta(para_fora=True)

        if self.exit_coords:
            col, row = self.exit_coords
            self.cenario_bg.blit(tile_porta_saida_aberta, (col * tilesize, row * tilesize))

        for wall in list(self.walls):
            if wall.tile_type == 4:
                wall.kill()

        self.set_feedback("PORTA DE SAÍDA ABERTA!")

    def set_feedback(self, msg):
        self.msg_feedback = msg
        self.msg_timer = 210

    def trigger_catch(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = 'GAMEOVER'
        else:
            self.player.x = float(self.spawn_pos[0] * tilesize)
            self.player.y = float(self.spawn_pos[1] * tilesize)
            self.player.hitbox.center = (int(self.player.x) + tilesize // 2, int(self.player.y) + tilesize // 2)
            self.player.rect.center = self.player.hitbox.center

            lx, ly = self.librarian_spawn_pos
            self.librarian.reset_to_grid(lx, ly)
            self.librarian.choose_next_cell()

    def trigger_easter_egg_unlock(self):
        tile_porta_aberta = self.gerador.criar_textura_porta_aberta(para_fora=False)

        for row in range(len(map_data)):
            for col in range(len(map_data[0])):
                if map_data[row][col] == 9:
                    map_data[row][col] = 0
                    self.cenario_bg.blit(tile_porta_aberta, (col * tilesize, row * tilesize))

        for wall in list(self.walls):
            if wall.tile_type == 9:
                wall.kill()

        if self.quadro_pos_coords:
            col, row = self.quadro_pos_coords
            self.quadro_secreto = QuadroSecreto(col, row)
            self.quadro_group.add(self.quadro_secreto)
            self.all_sprites.add(self.quadro_secreto)
        
        self.set_feedback("PASSAGEM SECRETA DESBLOQUEADA!")

    def check_bookshelf_interaction(self):
        player_box = self.player.hitbox.inflate(32, 32)
        
        # 1. Coleta de Folhas (Normais no chão ou Pistas escondidas dentro das estantes)
        for paper in list(self.papers):
            if player_box.colliderect(paper.rect):
                if getattr(paper, 'is_easter_egg', False):
                    self.score += 50
                    letra_pista = getattr(paper, 'letter_hint', '?')
                    self.pistas_coletadas.add(letra_pista)
                    
                    qtd_pistas = len(self.pistas_coletadas)
                    if qtd_pistas >= len(self.correct_sequence):
                        self.set_feedback(f"Papel [{letra_pista}] encontrado! (4/4) Agora siga a ordem nas estantes!")
                    else:
                        self.set_feedback(f"Você achou um papel escondido com a letra [{letra_pista}]! ({qtd_pistas}/4)")
                else:
                    self.papers_collected += 1
                    self.score += 100
                    if self.papers_collected >= self.total_papers_needed:
                        if not self.exit_unlocked:
                            self.unlock_exit_door()
                        if not self.pistas_spawned:
                            self.spawn_pistas_easter_egg()
                
                paper.kill()
                return

        # 2. Exploração das Estantes e Ativação Secreta (Só ativa após coletar as 4 pistas)
        for wall in self.walls:
            if hasattr(wall, 'letter_id') and wall.letter_id:
                if player_box.colliderect(wall.hitbox):
                    letra = wall.letter_id

                    if len(self.pistas_coletadas) < len(self.correct_sequence):
                        self.set_feedback(f"Estante [{letra}]")
                        return

                    proxima_esperada = self.correct_sequence[len(self.easter_egg_sequence)]
                    
                    if letra == proxima_esperada:
                        self.easter_egg_sequence.append(letra)
                        qtd = len(self.easter_egg_sequence)
                        
                        if self.easter_egg_sequence == self.correct_sequence:
                            self.trigger_easter_egg_unlock()
                        else:
                            self.set_feedback(f"Estante [{letra}] (*clique* {qtd}/4)")
                    else:
                        self.easter_egg_sequence = []
                        self.set_feedback(f"Estante [{letra}]")
                    return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == 'MENU':
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.menu_index = (self.menu_index - 1) % 3
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.menu_index = (self.menu_index + 1) % 3
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        if self.menu_index == 0:   self.state = 'SELECT_AVATAR'
                        elif self.menu_index == 1: self.state = 'CREDITS'
                        elif self.menu_index == 2: self.running = False

                elif self.state == 'CREDITS':
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                        self.state = 'MENU'

                elif self.state == 'SELECT_AVATAR':
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.score = 0
                        self.lives = 3
                        self.papers_collected = 0
                        self.exit_unlocked = False
                        self.init_level()
                        self.state = 'PLAYING'
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'

                elif self.state == 'PLAYING':
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_e]:
                        self.check_bookshelf_interaction()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'

                elif self.state in ['GAMEOVER', 'VICTORY']:
                    if event.key in [pygame.K_r, pygame.K_SPACE, pygame.K_RETURN]:
                        self.state = 'SELECT_AVATAR'
                    elif event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        self.state = 'MENU'

                elif self.state == 'EASTER_EGG':
                    if event.key in [pygame.K_r, pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                        self.player.y += tilesize
                        self.player.hitbox.centery = int(self.player.y) + tilesize // 2
                        self.player.rect.center = self.player.hitbox.center
                        self.state = 'PLAYING'

    def update(self, dt):
        if self.state == 'PLAYING':
            self.all_sprites.update(dt)

            if self.msg_timer > 0:
                self.msg_timer -= 1

            if hasattr(self, 'quadro_secreto'):
                if self.player.hitbox.colliderect(self.quadro_secreto.rect):
                    self.state = "EASTER_EGG"

            if self.exit_unlocked and self.exit_rect:
                if self.player.hitbox.colliderect(self.exit_rect):
                    self.score += 300
                    self.state = "VICTORY"

    def draw_hud(self):
        txt = f"PONTOS: {self.score:04d}   FOLHAS: {self.papers_collected}/{self.total_papers_needed}"
        self.screen.blit(self.font_hud.render(txt, True, white), (15, 8))

        radar_text, radar_color, _ = self.librarian.get_radar_status()
        self.screen.blit(self.font_hud.render(radar_text, True, radar_color), (500, 8))

        if self.msg_timer > 0:
            lbl = self.font_hud.render(self.msg_feedback, True, yellow)
            self.screen.blit(lbl, (width // 2 - lbl.get_width() // 2, height - 35))

        for i in range(3):
            cad_rect = pygame.Rect(width - 110 + (i * 26), 8, 16, 20)
            if i < self.lives:
                pygame.draw.rect(self.screen, white, cad_rect)
                pygame.draw.rect(self.screen, blue, (cad_rect.x+2, cad_rect.y+2, 12, 16), 1)
            else:
                pygame.draw.rect(self.screen, dark_gray, cad_rect)
                pygame.draw.line(self.screen, red, (cad_rect.left, cad_rect.top), (cad_rect.right, cad_rect.bottom), 2)

    def draw_victory_screen(self):
        """Tela de VITÓRIA — mantém as posições originais da arte de vitória."""
        if self.vitoria_bg:
            self.screen.blit(self.vitoria_bg, (0, 0))
        else:
            self.screen.fill((15, 15, 25))
            t_surf = self.font_title.render("TRABALHO RECUPERADO!", True, green)
            self.screen.blit(t_surf, (width // 2 - t_surf.get_width() // 2, 150))

        # Pontuação da Vitória
        score_surf = self.font_hud.render(f"PONTOS: {self.score}", True, yellow)
        score_rect = score_surf.get_rect(center=(width // 2 + 16, 415))
        self.screen.blit(score_surf, score_rect)

        # Caixa Esquerda: [R] NOVO JOGO
        r_surf = self.font_hud.render("[R] NOVO JOGO", True, white)
        r_rect = r_surf.get_rect(center=(385, 501))
        self.screen.blit(r_surf, r_rect)

        # Caixa Direita: [Q] MENU
        q_surf = self.font_hud.render("[Q] MENU", True, white)
        q_rect = q_surf.get_rect(center=(648, 501))
        self.screen.blit(q_surf, q_rect)

    def draw_gameover_screen(self):
        """Tela de DERROTA (Game Over) — coordenadas independentes para a imagem game_over.png."""
        if self.derrota_bg:
            self.screen.blit(self.derrota_bg, (0, 0))
        else:
            self.screen.fill((15, 15, 25))
            t_surf = self.font_title.render("EXPULSO DA BIBLIOTECA!", True, red)
            self.screen.blit(t_surf, (width // 2 - t_surf.get_width() // 2, 150))

        # Pontuação da Derrota (acima das caixas)
        score_surf = self.font_hud.render(f"PONTOS: {self.score}", True, yellow)
        score_rect = score_surf.get_rect(center=(width // 2, 355))
        self.screen.blit(score_surf, score_rect)

        # Caixa Esquerda da Derrota: [R] NOVO JOGO
        r_surf = self.font_hud.render("[R] NOVO JOGO", True, white)
        r_rect = r_surf.get_rect(center=(365, 452))
        self.screen.blit(r_surf, r_rect)

        # Caixa Direita da Derrota: [Q] MENU
        q_surf = self.font_hud.render("[Q] MENU", True, white)
        q_rect = q_surf.get_rect(center=(645, 452))
        self.screen.blit(q_surf, q_rect)

    def draw(self):
        self.screen.fill(black)

        if self.state == 'MENU':
            self.screen.blit(self.menu_bg, (0, 0))

            opcoes = ["Jogar", "Créditos", "Sair"]
            posicoes_x = [355, 519, 690]
            posicao_y = 510

            for i, opt in enumerate(opcoes):
                cor = yellow if i == self.menu_index else (220, 220, 230)
                opt_surf = self.font_menu.render(opt, True, cor)
                opt_rect = opt_surf.get_rect(center=(posicoes_x[i], posicao_y))
                
                if i == self.menu_index:
                    seta_surf = self.font_hud.render("▼", True, yellow)
                    seta_rect = seta_surf.get_rect(center=(posicoes_x[i], posicao_y - 20))
                    self.screen.blit(seta_surf, seta_rect)
                    
                self.screen.blit(opt_surf, opt_rect)

        elif self.state == 'CREDITS':
            t_surf = self.font_title.render("CRÉDITOS DO JOGO", True, white)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, 100))

            c1 = self.font_hud.render("Desenvolvido para avaliação do 2º bimestre - IFRN", True, white)
            c2 = self.font_hud.render("GDD e Mecânicas: estilo arcade stealth", True, light_gray)
            c3 = self.font_hud.render("Pressione [ESPAÇO] ou [ESC] para retornar", True, yellow)
            self.screen.blit(c1, (width//2 - c1.get_width()//2, 220))
            self.screen.blit(c2, (width//2 - c2.get_width()//2, 260))
            self.screen.blit(c3, (width//2 - c3.get_width()//2, 340))

        elif self.state == 'SELECT_AVATAR':
            t_surf = self.font_title.render("SELEÇÃO DE AVATAR", True, white)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, 60))

            pygame.draw.rect(self.screen, purple, (width//2 - 100, 140, 200, 200), 4)
            pygame.draw.circle(self.screen, purple, (width//2, 220), 50)
            pygame.draw.rect(self.screen, white, (width//2 - 25, 195, 50, 50))

            self.screen.blit(self.font_hud.render("Carlos Eugênio", True, white), (width//2 - 55, 360))
            self.screen.blit(self.font_hud.render("Especialidade: Camuflagem em sombras", True, light_gray), (width//2 - 140, 395))

            inst = self.font_hud.render("Pressione [ENTER] ou [ESPAÇO] para iniciar", True, yellow)
            self.screen.blit(inst, (width//2 - inst.get_width()//2, 480))

        elif self.state == 'PLAYING':
            self.screen.blit(self.cenario_bg, (0, 0))
            self.librarian.draw_vision_cone(self.screen)
            self.all_sprites.draw(self.screen)
            self.draw_hud()

        elif self.state == 'VICTORY':
            self.draw_victory_screen()

        elif self.state == 'GAMEOVER':
            self.draw_gameover_screen()

        elif self.state == 'EASTER_EGG':
            self.screen.fill((25, 15, 45))

            quadro_w, quadro_h = 182, 238
            quadro_x = width // 2 - quadro_w // 2
            quadro_y = 55
            pygame.draw.rect(self.screen, yellow, (quadro_x, quadro_y, quadro_w, quadro_h), 5)

            if self.guardiao_img:
                self.screen.blit(self.guardiao_img, (quadro_x + 6, quadro_y + 6))
            else:
                pygame.draw.circle(self.screen, purple, (width // 2, quadro_y + quadro_h // 2), 50)

            t1 = self.font_title.render("O GUARDIÃO DA SABEDORIA", True, yellow)
            t2 = self.font_hud.render('"Dizem que ele sabe quando você usa ChatGPT..."', True, white)

            self.screen.blit(t1, (width//2 - t1.get_width()//2, 320))
            self.screen.blit(t2, (width//2 - t2.get_width()//2, 380))
            self.screen.blit(self.font_hud.render("Pressione [ESPAÇO] ou [ESC] para retornar", True, light_gray), (width//2 - 170, 460))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(fps) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()