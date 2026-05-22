#main.py
import pygame
import sys
import random 
from config import *
from sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.diaplay.set_caption("The Midnight Assignment")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Courier New", 36, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 22, bold=True)

        self.state = 'MENU'
        self.score = 0
        self.lives = 3 
        self.papers_collected = 0
        self.total_papers_needed = 5
        self.exit_unlocked = False 

    def init_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.papers = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()

        self.exit_rect = None

#processamento e montagem da matriz do cenário 
        for row, tiles in enumerate(map_data):
            for col, tile in enumerate(tiles):
                if tile in [0, 3, 4, 5, 6]:
                    bg = ObjetoCenario(col, row, tilesize, tilesize)
                    bg.image.fill(noise_color if tile == 5 else floor_color)
                    self.background_tiles.add(bg)

                if tile == 1 or tile == 2:
                    obs = Obstaculo(col, row, tile)
                    self.walls.add(obs)
                    self.all_sprites.add(obs)
                elif tile == 3:
                    self.spaw_pos = (col, row)
                elif tile == 4:
                    self.exit_rect = pygame.Rect(col * tilesize, row * tilesize, tilesize)
                elif tile == 6:
                    papr = ItemColetavel(col, row)
                    self.papers.add(papr)
                    self.all_sprites.add(papr)

#inicializa o personagem único padrão ("Carlos Eugênio")
        self.player = player(self, self.spawn_pos[0], self.spawn_pos[1], "Carlos Eugênio")
        self.all_sprites.add(self.player)

        self.librarian = Librarian(self,  6, 1)
        self.all_sprites.add(self.librarian)

    def trigger_catch(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = 'GAMEOVER'
        else:
            #reseta as posições no mapa se for pego, sem perder o progesso das folhas
            self.player.x = self.spawn_pos[0] *tilesize
            self.player.y = self.spawn_pos[1] * tilesize
            self.player.rect.topleft = (self.player.x, self.player.y)
            self.librarian.pos = pygame.math.Vector2(6 * tilesize, 1 * tilesize)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == 'MENU':
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.score = 0
                        self.lives = 3
                        self.papers_collected = 0
                        self.exit_unlocked  = False
                        self.init_level()
                        self.state = 'PLAYING'
                    elif event.key in [pygame.K_ESCAPE, pygame.k_q]:
                        pygame.quit()
                        sys.exit()

                    elif self.state in ['GAMEOVER', 'VICTORY']:
                        if event.key == pygame.K_r:
                            #reinicia a partida direto
                            self.score = 0
                            self.lives = 3
                            self.papers_collected = 0
                            self.exit_unlocked = False
                            self.init_level()
                            self.state = 'PLAYING'
                        elif event.key in [pygame.K_ESCAPE, pygame.K_q]:
                            self.state = 'MENU'

                def update(self):
                    if self.state == 'PLAYING':
                        self.all_sprites.update()

                        collected = pygame.sprite.spritecollide(self.player, self.papers, True)
                        for _ in collected:
                            self.papers_collected += 1
                            self.score += 100
                            if self.papers_collected >= self.total_papers_needed:
                                self.exit_unlocked = True  

                        if self.exit_unlocked and self.exit_rect:
                            if self.player.hitbox.colliderect(self.exit_rect):
                                self.score += 300
                                self.state = 'VICTORY'

                def draw_hud(self):
                    hud_text = f"PONTOS: {self.score:04d}   FOLHAS: {self.papers_collected}/{self.total_papers_needed}"
                    hud_surf = self.font_hud.render(hud_text, True, white)
                    self.screen.blit(hud_surf, (20, 15))

                    for i in range(3):
                        book_rect = pygame.Rect(width - 140 + (i * 35), 15, 22, 26)
                        if i < self.lives:
                            pygame.draw.rect(self.screen, white, book_rect)
                            pygame.draw.rect(self.screen, red, (book_rect.left, book_rect.top), (book_rect.right, book_rect.bottom), 2)
                        else:
                            pygame.draw.rect(self.screen, dark_gray, book_rect)
                            pygame.draw.line(self.screen, red, (book_rect.left, book_rect.top), (book_rect.right, book_rect.bottom), 2)

                    if self.exit_unlocked:
                        pygame.draw.rect(self.screen, blue, self.exit_rect)

                def draw(self):
                    self.screen.fill(black)

                    if self.state == 'MENU':
                        offset_x = random.randint(-2, 2) if random.random() > 0.85 else 0
                        title_surf = self.font_title.render("THE MIDNIGHT ASSIGNMENT", True, red if offset_x else white)
                        self.screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2 + offset_x, height // 3))

                        sub_surf = self.font_hud.render("Pressione ESPAÇO para iniciar ou Q para sair", True, light_gray)
                        self.screen.blit(sub_surf, (width // 2 - sub_surf.get_width() // 2, height // 2))

                    elif self.state == 'PLAYING':
                        self.background_tiles.draw(self.screen)
                        self.all_sprites.draw(self.screen)
                        self.draw_hud()

                    elif self.state in ['GAMEOVER', 'VICTORY']:
                        text = "TRABALHO RECUPERADO COM SUCESSO!" if self.state == 'VICTORY' else "EXPULSO DA BIBLIOTECA!"
                        color = green if self.state == 'VICTORY' else red 
                        surf = self.font_title.render(text, True, color)
                        self.screen.blit(surf, (width // 2 - surf.get_width() // 2, height // 3))

                        score_surf = self.font_hud.render(f"Pontuação Final: {self.score} pontos", True, white)
                        self.screen.blit(score_surf, (width // 2 - score_surf.get_width() // 2, height // 2))

                        retry_surf = self.font_hud.render("Pressione [R]  para jogar novamente ou [Q] para ir ao menu", True, light_gray)
                        self.screen.blit(retry_surf, (width // 2 - retry_surf.get_width() // 2, height // 2 + 60))

                    pygame.display.flip()

                def run(self):
                    while True:
                        self.clock.tick(fps)
                        self.handle_events()
                        self.update()
                        self.draw()

            if __name__ == '__main__':
                game = Game()
                game.run()



                    



            