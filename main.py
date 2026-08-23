# main.py
import pygame
import sys
import random 
from config import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("The Midnight Assignment")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Courier New", 38, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 20, bold=True)

        self.state = 'MENU'
        self.menu_index = 0
        self.avatar_selecao = "Carlos Eugênio"

        # Atributos gerais do jogo 
        self.score = 0
        self.lives = 3 
        self.papers_collected = 0
        self.total_papers_needed = 5
        self.exit_unlocked = False 

        # Estruturas easter egg
        self.easter_egg_sequence = []
        self.correct_sequence = ["I", "F", "R", "N"]

    def init_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.papers = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.exit_rect = None
        self.librarian_spawn_pos = (17, 10)  # Padrão de segurança longe do jogador

        for row, tiles in enumerate(map_data):
            for col, tile in enumerate(tiles):
                # Desenha o piso base para posições onde há caminhada ou itens
                if tile in [0, 3, 4, 6, 7]:
                    bg = ObjetoCenario(col, row, tilesize, tilesize)
                    bg.image.fill(floor_color)
                    self.background_tiles.add(bg)

                if tile in [1, 2]:
                    letter = ""
                    if row == 2 and col == 2: letter = "I"
                    if row == 2 and col == 10: letter = "F"
                    if row == 5 and col == 13: letter = "R"
                    if row == 9 and col == 4: letter = "N"

                    obs = Obstaculo(col, row, tile, letter)
                    self.walls.add(obs)
                    self.all_sprites.add(obs)
                elif tile == 3:
                    self.spawn_pos = (col, row)
                elif tile == 4:
                    self.exit_rect = pygame.Rect(col * tilesize, row * tilesize, tilesize, tilesize)
                elif tile == 6:
                    papr = ItemColetavel(col, row)
                    self.papers.add(papr)
                    self.all_sprites.add(papr)
                elif tile == 7:
                    self.librarian_spawn_pos = (col, row)

        # Dispersão das pistas do Easter Egg em posições livres
        pistas_pos = [("I", 2, 8), ("F", 4, 12), ("R", 8, 3), ("N", 10, 11)]
        for letra, cx, cy in pistas_pos: 
            pista = ItemColetavel(cx, cy, is_easter_egg=True, letter_hint=letra)
            self.papers.add(pista)
            self.all_sprites.add(pista)

        # Injeção das instâncias do Player e Librarian nas posições corretas
        self.player = Player(self, self.spawn_pos[0], self.spawn_pos[1])
        self.all_sprites.add(self.player)
        
        self.librarian = Librarian(self, self.librarian_spawn_pos[0], self.librarian_spawn_pos[1])
        self.all_sprites.add(self.librarian)

    def trigger_catch(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = 'GAMEOVER'
        else:
            # Reseta a posição do jogador
            self.player.x = float(self.spawn_pos[0] * tilesize)
            self.player.y = float(self.spawn_pos[1] * tilesize)
            self.player.hitbox.center = (int(self.player.x) + tilesize // 2, int(self.player.y) + tilesize // 2)
            self.player.rect.center = self.player.hitbox.center

            # Reseta o Bibliotecário no spawn
            lx, ly = self.librarian_spawn_pos
            self.librarian.reset_to_grid(lx, ly)
            self.librarian.choose_next_cell()

    def draw(self):
        self.screen.fill(black)

        if self.state == 'MENU':
            offset = random.randint(-3, 3) if random.random() > 0.88 else 0
            cor_titulo = red if offset != 0 else white
            t_surf = self.font_title.render("THE MIDNIGHT ASSIGNMENT", True, cor_titulo)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2 + offset, height//4))

            opcoes = ["Jogar", "Créditos", "Sair"]
            for i, opt in enumerate(opcoes):
                cor = yellow if i == self.menu_index else light_gray
                prefixo = "> " if i == self.menu_index else " "
                opt_surf = self.font_hud.render(prefixo + opt, True, cor)
                self.screen.blit(opt_surf, (width//2 - 60, height//2 + (i * 40)))

        elif self.state == 'CREDITS':
            t_surf = self.font_title.render("CRÉDITOS DO JOGO", True, white)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, 100))

            c1 = self.font_hud.render("Desenvolvido para avaliação do 2 bimestre - IFRN", True, white)
            c2 = self.font_hud.render("GDD e Mecânicas: estilo arcade", True, light_gray)
            c3 = self.font_hud.render("Pressione [ESPAÇO] ou [ESC] para retornar ao menu", True, yellow)
            self.screen.blit(c1, (width//2 - c1.get_width()//2, 220))
            self.screen.blit(c2, (width//2 - c2.get_width()//2, 260))
            self.screen.blit(c3, (width//2 - c3.get_width()//2, 340))

        elif self.state == 'SELECT_AVATAR':
            t_surf = self.font_title.render("SELEÇÃO DE AVATAR", True, white)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, 70))

            pygame.draw.rect(self.screen, purple, (width//2 - 120, 160, 240, 240), 5)
            pygame.draw.circle(self.screen, purple, (width//2, 260), 60)
            pygame.draw.rect(self.screen, white, (width//2 - 30, 230, 60, 60))

            self.screen.blit(self.font_hud.render("Carlos Eugênio", True, white), (width//2 - 60, 415))
            self.screen.blit(self.font_hud.render("Especialidade: camuflagem e movimentação em sombras", True, light_gray), (width//2 - 215, 455))

            inst = self.font_hud.render("Pressione [ENTER] ou [ESPAÇO] para iniciar a missão", True, yellow)
            self.screen.blit(inst, (width//2 - inst.get_width()//2, 540))

        elif self.state == 'PLAYING':
            self.background_tiles.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.librarian.draw_vision_cone(self.screen)
            self.draw_hud()

        elif self.state == 'GAMEOVER':
            t_surf = self.font_title.render("EXPULSO DA BIBLIOTECA!", True, red)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, height//3))
            
            res = self.font_hud.render(f"Pontuação Final Consolidada: {self.score} pontos.", True, white)
            self.screen.blit(res, (width//2 - res.get_width()//2, height//2))
            
            inst = self.font_hud.render("Pressione [R] para Novo Jogo ou [Q] para sair", True, light_gray)
            self.screen.blit(inst, (width//2 - inst.get_width()//2, height//2 + 60))

        elif self.state == 'VICTORY':
            t_surf = self.font_title.render("TRABALHO RECUPERADO COM SUCESSO!", True, green)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, height//3))
            
            res = self.font_hud.render(f"Pontuação Final Consolidada: {self.score} pontos.", True, white)
            self.screen.blit(res, (width//2 - res.get_width()//2, height//2))
            
            inst = self.font_hud.render("Pressione [R] para Novo Jogo ou [Q] para sair", True, light_gray)
            self.screen.blit(inst, (width//2 - inst.get_width()//2, height//2 + 60))

        elif self.state == 'EASTER_EGG':
            self.screen.fill((25, 15, 45))
            pygame.draw.rect(self.screen, yellow, (width//2 - 100, 100, 200, 240), 6)
            pygame.draw.circle(self.screen, purple, (width//2, 210), 60)

            t1 = self.font_title.render("O GUARDIÃO DO CONHECIMENTO", True, yellow)
            t2 = self.font_hud.render('"Dizem que ele sabe quando você usa ChatGPT..."', True, white)

            self.screen.blit(t1, (width//2 - t1.get_width()//2, 380))
            self.screen.blit(t2, (width//2 - t2.get_width()//2, 440))
            self.screen.blit(self.font_hud.render("Segredo Revelado! Pressione [R] para retornar", True, light_gray), (width//2 - 190, 520))

        pygame.display.flip()
    def trigger_easter_egg_unlock(self):
        for row in range(len(map_data)):
            for col in range(len(map_data[0])):
                if row == 10 and col == 17:
                    map_data[row][col] = 0
                    for wall in self.walls:
                        if wall.rect.x == col * tilesize and wall.rect.y == row * tilesize:
                            wall.kill()
        self.state = 'EASTER_EGG'

    def check_bookshelf_interaction(self):
        for wall in self.walls:
            if wall.letter_id:
                if self.player.hitbox.inflate(12, 12).colliderect(wall.rect):
                    if not self.easter_egg_sequence or self.easter_egg_sequence[-1] != wall.letter_id:
                        self.easter_egg_sequence.append(wall.letter_id)

                        if self.easter_egg_sequence == self.correct_sequence:
                            self.trigger_easter_egg_unlock()
                        elif len(self.easter_egg_sequence) >= 4:
                            self.easter_egg_sequence = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == 'MENU':
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.menu_index = (self.menu_index - 1) % 3
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.menu_index = (self.menu_index + 1) % 3
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        if self.menu_index == 0:   self.state = 'SELECT_AVATAR'
                        elif self.menu_index == 1: self.state = 'CREDITS'
                        elif self.menu_index == 2: pygame.quit(); sys.exit()

                elif self.state == 'CREDITS':
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                        self.state = 'MENU'

                elif self.state == 'SELECT_AVATAR':
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.score = 0
                        self.lives = 3
                        self.papers_collected = 0
                        self.exit_unlocked = False
                        self.easter_egg_sequence = []
                        self.init_level()
                        self.state = 'PLAYING'
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'

                elif self.state == 'PLAYING':
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.check_bookshelf_interaction()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'MENU'

                elif self.state in ['GAMEOVER', 'VICTORY', 'EASTER_EGG']:
                    if event.key == pygame.K_r:
                        self.state = 'SELECT_AVATAR'
                    elif event.key in [pygame.K_ESCAPE, pygame.K_q]:
                        self.state = 'MENU'

    def update(self, dt):
        if self.state == 'PLAYING':
            self.all_sprites.update(dt)

            collected = pygame.sprite.spritecollide(self.player, self.papers, False)
            for item in collected:
                if self.player.hitbox.colliderect(item.rect):
                    item.kill()
                    if not item.is_easter_egg:
                        self.papers_collected += 1
                        self.score += 100
                        if self.papers_collected >= self.total_papers_needed:
                            self.exit_unlocked = True 
                    else:
                        self.score += 25

            if self.exit_unlocked and self.exit_rect:
                if self.player.hitbox.colliderect(self.exit_rect):
                    self.score += 300
                    self.state = 'VICTORY'

    def draw_hud(self):
        txt = f"PONTOS: {self.score:04d}   FOLHAS: {self.papers_collected}/{self.total_papers_needed}"
        self.screen.blit(self.font_hud.render(txt, True, white), (20, 15)) 

        distancia_minima = 9999.0
        for paper in self.papers:
            d = pygame.math.Vector2(self.player.rect.center).distance_to(paper.rect.center)
            if d < distancia_minima: distancia_minima = d

        radar_label = "RADAR: SEM SINAL"
        radar_color = light_gray
        if distancia_minima < 80:       radar_label = "RADAR: PROXIMIDADE CRÍTICA"; radar_color = red
        elif distancia_minima < 160:    radar_label = "RADAR: DETECTANDO SINAL"; radar_color = yellow 

        self.screen.blit(self.font_hud.render(radar_label, True, radar_color), (410, 15))

        for i in range(3):
            cad_rect = pygame.Rect(width - 120 + (i * 30), 14, 18, 22)
            if i < self.lives:
                pygame.draw.rect(self.screen, white, cad_rect)
                pygame.draw.rect(self.screen, blue, (cad_rect.x+2, cad_rect.y+2, 14, 18), 1)
            else:
                pygame.draw.rect(self.screen, dark_gray, cad_rect)
                pygame.draw.line(self.screen, red, (cad_rect.left, cad_rect.top), (cad_rect.right, cad_rect.bottom), 2)

        if self.exit_unlocked and self.exit_rect:
            pygame.draw.rect(self.screen, blue, self.exit_rect)

    def draw(self):
        self.screen.fill(black)

        if self.state == 'MENU':
            offset = random.randint(-3, 3) if random.random() > 0.88 else 0
            cor_titulo = red if offset != 0 else white
            t_surf = self.font_title.render("THE MIDNIGHT ASSIGNMENT", True, cor_titulo)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2 + offset, height//4))

            opcoes = ["Jogar", "Créditos", "Sair"]
            for i, opt in enumerate(opcoes):
                cor = yellow if i == self.menu_index else light_gray
                prefixo = "> " if i == self.menu_index else " "
                opt_surf = self.font_hud.render(prefixo + opt, True, cor)
                self.screen.blit(opt_surf, (width//2 - 60, height//2 + (i * 40)))

        elif self.state == 'CREDITS':
            t_surf = self.font_title.render("CRÉDITOS DO JOGO", True, white)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, 100))

            c1 = self.font_hud.render("Desenvolvido para avaliação do 2 bimestre - IFRN", True, white)
            c2 = self.font_hud.render("GDD e Mecânicas: estilo arcade", True, light_gray)
            c3 = self.font_hud.render("Pressione [ESPAÇO] ou [ESC] para retornar ao menu", True, yellow)
            self.screen.blit(c1, (width//2 - c1.get_width()//2, 220))
            self.screen.blit(c2, (width//2 - c2.get_width()//2, 260))
            self.screen.blit(c3, (width//2 - c3.get_width()//2, 340))

        elif self.state == 'SELECT_AVATAR':
            t_surf = self.font_title.render("SELEÇÃO DE AVATAR", True, white)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, 70))

            pygame.draw.rect(self.screen, purple, (width//2 - 120, 160, 240, 240), 5)
            pygame.draw.circle(self.screen, purple, (width//2, 260), 60)
            pygame.draw.rect(self.screen, white, (width//2 - 30, 230, 60, 60))

            self.screen.blit(self.font_hud.render("Carlos Eugênio", True, white), (width//2 - 60, 415))
            self.screen.blit(self.font_hud.render("Especialidade: camuflagem e movimentação em sombras", True, light_gray), (width//2 - 215, 455))

            inst = self.font_hud.render("Pressione [ENTER] ou [ESPAÇO] para iniciar a missão", True, yellow)
            self.screen.blit(inst, (width//2 - inst.get_width()//2, 540))

        elif self.state == 'PLAYING':
            self.background_tiles.draw(self.screen)
            self.all_sprites.draw(self.screen)
            # Desenha o cone de visão vermelho em cima do cenário
            self.librarian.draw_vision_cone(self.screen)
            self.draw_hud()

        elif self.state in ['GAMEOVER', 'VICTORY']:
            texto = "TRABALHO RECUPERADO COM SUCESSO!" if self.state == 'VICTORY' else "EXPULSO DA BIBLIOTECA!"
            color = green if self.state == 'VICTORY' else red 
            
            t_surf = self.font_title.render(texto, True, color)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, height//3))
            
            res = self.font_hud.render(f"Pontuação Final Consolidada: {self.score} pontos.", True, white)
            self.screen.blit(res, (width//2 - res.get_width()//2, height//2))
            self.screen.blit(self.font_hud.render("Pressione [R] para Novo Jogo ou [Q] para sair", True, light_gray), (width//2 - 190, height//2 + 60))

        elif self.state == 'EASTER_EGG':
            self.screen.fill((25, 15, 45))
            pygame.draw.rect(self.screen, yellow, (width//2 - 100, 100, 200, 240), 6)
            pygame.draw.circle(self.screen, purple, (width//2, 210), 60)

            t1 = self.font_title.render("O GUARDIÃO DO CONHECIMENTO", True, yellow)
            t2 = self.font_hud.render('"Dizem que ele sabe quando você usa ChatGPT..."', True, white)

            self.screen.blit(t1, (width//2 - t1.get_width()//2, 380))
            self.screen.blit(t2, (width//2 - t2.get_width()//2, 440))
            self.screen.blit(self.font_hud.render("Segredo Revelado! Pressione [R] para retornar", True, light_gray), (width//2 - 190, 520))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(fps) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

if __name__ == '__main__':
    game = Game()
    game.run()