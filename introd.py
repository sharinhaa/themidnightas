import pygame
from config import *

class IntroManager:
    def __init__(self):
        self.pages = [
            # PÁGINA 1: O Conflito Inicial
            "CAMPUS IFRN - 23:30 PM\n\n"
            "É a noite que precede a entrega da lista final do ano letivo.\n"
            "Carlos Eugênio passou a semana inteira no laboratório organizando o código.\n"
            "Faltando meia hora para a meia-noite, ele percebe com horror:\n"
            "as 5 FOLHAS DE RASCUNHO com a arquitetura do projeto e os cálculos\n"
            "de colisão ficaram esquecidas sobre as mesas da Biblioteca Central!",

            # PÁGINA 2: A Armadilha
            "SEM ESSAS FOLHAS, O PROJETO SERÁ CONSIDERADO INCOMPLETO!\n\n"
            "Carlos consegue deslizar para dentro da biblioteca minutos antes das luzes\n"
            "principais se apagarem na escuridão...\n\n"
            "Mas ouve o estalo seco da tranca da porta principal:\n"
            "ELE FICOU PRESO LÁ DENTRO!",
            
            # PÁGINA 3: A Ameaça
            "NAS SOMBRAS DA BIBLIOTECA...\n\n"
            "Uma figura misteriosa patrulha os corredores com passos pesados.\n"
            "É o BIBLIOTECÁRIO NOTURNO: um funcionário inflexível conhecido por aplicar\n"
            "punições severas e zerar sem piedade o trabalho de quem desrespeita\n"
            "as regras e o horário da instituição.",

            # PÁGINA 4: O Mito da Aprovação (Easter Egg)
            "A LENDA DO GABARITO DO GUARDIÃO\n\n"
            "Circula entre os alunos um rumor: um professor lendário deixou um mapa\n"
            "de respostas e notas extras escondido em uma sala oculta na biblioteca.\n"
            "Dizem que para a passagem se abrir, o aluno desesperado deve seguir\n"
            "o 'Mantra dos Aprovados' interagindo com as estantes na ordem: I - F - R - N.\n"
            "Nesta noite, Carlos pode testar se a maior lenda do campus é real!",

            # PÁGINA 5: Guia Prático de Gameplay
            "INSTRUÇÕES DA MISSÃO DE REGENERAÇÃO:\n\n"
            "• OBJETIVO: Colete as 5 FOLHAS do trabalho nas mesas da biblioteca.\n"
            "• RADAR DE PERIGO: Fique atento ao campo de visão vermelho do Bibliotecário.\n"
            "• SEGREDO: Teste a sequência 'I-F-R-N' nas estantes.\n"
            "• FUGA: Após pegar todas as folhas, escape pela PORTA DE SAÍDA!"
        ]

        self.current_index = 0

    def reset(self):
        """Reinicia o contador de páginas para quando a história for acessada novamente."""
        self.current_index = 0

    def next_page(self):
        """Avança para a próxima página. Retorna True quando terminar todas as páginas."""
        self.current_index += 1
        if self.current_index >= len(self.pages):
            return True
        return False

    def draw(self, screen, font_title, font_hud, font_menu):
        """Renderiza a interface gráfica da introdução sem erros de sobreposição."""
        # Fundo tom azul-escuro soturno
        screen.fill((12, 14, 22))

        # Moldura central decorativa com bordas arredondadas
        box_rect = pygame.Rect(40, 40, width - 80, height - 80)
        
        # Superfície interna translúcida
        surface_box = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        surface_box.fill((22, 26, 42, 230))
        screen.blit(surface_box, (box_rect.x, box_rect.y))
        
        # Borda externa amarela destacada
        pygame.draw.rect(screen, yellow, box_rect, 3, border_radius=10)

        # Cabeçalho da Tela
        header_text = font_title.render("--- O ARQUIVO PERDIDO ---", True, yellow)
        screen.blit(header_text, (width // 2 - header_text.get_width() // 2, 65))

        # Renderização do texto da página atual (alinhado e centralizado)
        texto_atual = self.pages[self.current_index]
        linhas = texto_atual.split("\n")
        
        pos_y = 135
        for linha in linhas:
            if linha.strip() == "":
                pos_y += 12
                continue

            # Se for um título interno na página, pinta de amarelo/dourado
            if linha in ["SEM ESSAS FOLHAS, O PROJETO SERÁ CONSIDERADO INCOMPLETO!", 
                         "NAS SOMBRAS DA BIBLIOTECA...", 
                         "A LENDA DO GABARITO DO GUARDIÃO", 
                         "INSTRUÇÕES DA MISSÃO DE REGENERAÇÃO:"]:
                lbl = font_hud.render(linha, True, yellow)
            else:
                lbl = font_hud.render(linha, True, white)
                
            screen.blit(lbl, (width // 2 - lbl.get_width() // 2, pos_y))
            pos_y += 28

        # Barra de rodapé com indicação de progresso e botões
        info_pag = f"Página {self.current_index + 1}/{len(self.pages)}   |   [ESPAÇO / ENTER] Avançar   •   [ESC] Pular Introdução"
        rodape = font_menu.render(info_pag, True, light_gray)
        screen.blit(rodape, (width // 2 - rodape.get_width() // 2, height - 75))