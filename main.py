#main.py
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

        gerador = BibliotecaGerador(tilesize)
        self.cenario_bg = gerador.gerar_cenario_completo(self.original_map_data, width, height)

        self.font_title = pygame.font.SysFont("Courier New", 36, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_menu = pygame.font.SysFont("Arial", 16, bold=True)

        self.menu_bg = pygame.image.load("imagens/menu_bg.png").convert()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (width, height))

        self.state = 'MENU'
        self.menu_index = 0
        self.avatar_selecao = "Carlos Eugênio"

        self.score = 0
        self.lives = 3 
        self.papers_collected = 0
        self.total_papers_needed = 5
        self.exit_unlocked = False 
        
        #Controles do easter egg
        self.pistas_coletadas = set()
        self.easter_egg_sequence = []
        self.correct_sequence = ["I", "F", "R", "N"]
        self.pistas_spawned = False
        self.msg_feedback = ""
        self.msg_timer = 0

    def init_level(self):
        global map_data
        map_data = copy.deepcopy(self.original_map_data)

        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.papers = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.quadro_group = pygame.sprite.Group()
        self.exit_rect = None

        self.quadro_pos_coords = None 

        self.librarian_spawn_pos = (27, 1)
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

                if tile in [1, 2, 9]:
                    letter = ""
                    if row == 2 and col == 2: letter = "I"
                    elif row == 2 and col == 9: letter = "F"
                    elif row == 5 and col == 12: letter = "R"
                    elif row == 8 and col == 6: letter = "N"

                    obs = Obstaculo(col, row, tile, letter)
                    obs.image.set_alpha(0) 
                    self.walls.add(obs)
                    self.all_sprites.add(obs)
                elif tile == 3:
                    self.spawn_pos = (col, row)
                elif tile == 4:
                    self.exit_rect = pygame.Rect(col * tilesize, row * tilesize, tilesize * 2, tilesize * 2)
                elif tile == 6:
                    papr = ItemColetavel(col, row)
                    self.papers.add(papr)
                    self.all_sprites.add(papr)
                elif tile == 8:
                    self.quadro_pos_coords = (col, row)

        self.player = Player(self, self.spawn_pos[0], self.spawn_pos[1])
        self.all_sprites.add(self.player)
        
        self.librarian = Librarian(self, self.librarian_spawn_pos[0], self.librarian_spawn_pos[1])
        self.all_sprites.add(self.librarian)

    def spawn_pistas_easter_egg(self):
        pistas_pos = [("I", 1, 4), ("F", 4, 11), ("R", 7, 4), ("N", 10, 1)]
        for letra, cx, cy in pistas_pos: 
            pista = ItemColetavel(cx, cy, is_easter_egg=True, letter_hint=letra)
            self.papers.add(pista)
            self.all_sprites.add(pista)
        self.pistas_spawned = True
        self.set_feedback("As 4 pistas apareceram no mapa!")

    def set_feedback(self, msg):
        self.msg_feedback = msg
        self.msg_timer = 180

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
        for row in range(len(map_data)):
            for col in range(len(map_data[0])):
                if map_data[row][col] == 9:
                    map_data[row][col] = 0

        for wall in list(self.walls):
            if wall.tile_type == 9:
                wall.kill()

        if self.quadro_pos_coords:
            col, row = self.quadro_pos_coords
            self.quadro_secreto = QuadroSecreto(col, row)
            self.quadro_secreto.image.set_alpha(0)  
            self.quadro_group.add(self.quadro_secreto)
            self.all_sprites.add(self.quadro_secreto)

        self.set_feedback("PASSAGEM SECRETA E SALA REVELADAS!")

    def check_bookshelf_interaction(self):
        if not self.exit_unlocked:
            self.set_feedback("Pegue as 5 folhas principais primeiro!")
            return

        if len(self.pistas_coletadas) < 4:
            self.set_feedback(f"Faltam pistas no chão! ({len(self.pistas_coletadas)}/4)")
            return

        player_box = self.player.hitbox.inflate(20, 20)
        
        for wall in self.walls:
            if hasattr(wall, 'letter_id') and wall.letter_id:
                if player_box.colliderect(wall.rect):
                    proxima_esperada = self.correct_sequence[len(self.easter_egg_sequence)]
                    
                    if wall.letter_id == proxima_esperada:
                        self.easter_egg_sequence.append(wall.letter_id)
                        self.set_feedback(f"Sequencia: {'-'.join(self.easter_egg_sequence)}")
                        
                        if self.easter_egg_sequence == self.correct_sequence:
                            self.trigger_easter_egg_unlock()
                    else:
                        self.easter_egg_sequence = []
                        self.set_feedback(f"Ordem incorreta! Reseta para [I]. Pressionou: {wall.letter_id}")
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
                    if event.key == pygame.K_r:
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

            collected = pygame.sprite.spritecollide(self.player, self.papers, True)
            for item in collected:
                if not item.is_easter_egg:
                    self.papers_collected += 1
                    self.score += 100
                    if self.papers_collected >= self.total_papers_needed:
                        self.exit_unlocked = True 
                        if not self.pistas_spawned:
                            self.spawn_pistas_easter_egg()
                else:
                    self.score += 50
                    if hasattr(item, 'letter_hint'):
                        self.pistas_coletadas.add(item.letter_hint)
                        self.set_feedback(f"Pegou pista [{item.letter_hint}] ({len(self.pistas_coletadas)}/4)")

            if hasattr(self, 'quadro_secreto'):
                if self.player.hitbox.colliderect(self.quadro_secreto.rect):
                    self.state = "EASTER_EGG"

            if self.exit_unlocked and self.exit_rect:
                if self.player.hitbox.colliderect(self.exit_rect):
                    self.score += 300
                    self.state = "VICTORY"

    def draw_hud(self):
        txt = f"PONTOS: {self.score:04d}   FOLHAS: {self.papers_collected}/{self.total_papers_needed}   PISTAS: {len(self.pistas_coletadas)}/4"
        self.screen.blit(self.font_hud.render(txt, True, white), (15, 8))

        radar_text, radar_color, _ = self.librarian.get_radar_status()
        self.screen.blit(self.font_hud.render(radar_text, True, radar_color), (500, 8))

        if self.msg_timer > 0:
            lbl = self.font_hud.render(self.msg_feedback, True, yellow)
            self.screen.blit(lbl, (width // 2 - lbl.get_width() // 2, height - 30))

        for i in range(3):
            cad_rect = pygame.Rect(width - 110 + (i * 26), 8, 16, 20)
            if i < self.lives:
                pygame.draw.rect(self.screen, white, cad_rect)
                pygame.draw.rect(self.screen, blue, (cad_rect.x+2, cad_rect.y+2, 12, 16), 1)
            else:
                pygame.draw.rect(self.screen, dark_gray, cad_rect)
                pygame.draw.line(self.screen, red, (cad_rect.left, cad_rect.top), (cad_rect.right, cad_rect.bottom), 2)

        if self.exit_unlocked and self.exit_rect:
            pygame.draw.rect(self.screen, blue, self.exit_rect, 2)

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

        elif self.state in ['GAMEOVER', 'VICTORY']:
            texto = "TRABALHO RECUPERADO COM SUCESSO!" if self.state == 'VICTORY' else "EXPULSO DA BIBLIOTECA!"
            color = green if self.state == 'VICTORY' else red 
            
            t_surf = self.font_title.render(texto, True, color)
            self.screen.blit(t_surf, (width//2 - t_surf.get_width()//2, height//3))
            
            res = self.font_hud.render(f"Pontuação Final: {self.score} pontos.", True, white)
            self.screen.blit(res, (width//2 - res.get_width()//2, height//2))
            self.screen.blit(self.font_hud.render("Pressione [R] para reiniciar ou [Q] para sair", True, light_gray), (width//2 - 170, height//2 + 50))

        elif self.state == 'EASTER_EGG':
            self.screen.fill((25, 15, 45))
            pygame.draw.rect(self.screen, yellow, (width//2 - 90, 80, 180, 200), 5)
            pygame.draw.circle(self.screen, purple, (width//2, 170), 50)

            t1 = self.font_title.render("O GUARDIÃO DO CONHECIMENTO", True, yellow)
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