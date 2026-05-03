TÍTULO: The Midnight Assignment - fuja do bibliotecário!

DESCRIÇÃO GERAL: o jogo terá tipo Acarde/Stealth 2D/ Dungeon Crawler Urbano; o ambiente do game será em uma biblioteca escolar durante o período da madrugada, tendo seu cenário composto por corredores estreitos formados por estantes gigantescas e áreas de leitura com mesas que oferecem cobertura parcial.
A ideia principal do jogo se dará quando o jogador assume o papel de um estudante que, em um momento de desespero, invade a escola à noite para recuperar os originais de um trabalho acadêmico vital. O desafio não é apenas encontrar as folhas, mas gerenciar o som dos seus passos e a visibilidade em relação à visão "aguçada" do biblotecário, que segue padrões de busca inteligentes. 

OBJETIVO: o principal objetivo pensado é a recuperação das folhas de um projeto. O jogador deve localizar e recuperar as 5 folhas manuscritas do seu projeto final, que foram deixadas em locais distintos da Biblioteca Central; o jogo tem como desafio o fato de que as folhas não são visíveis desde do início, sendo preciso o player explorar o labirinto de estantes para revelá-vas no mapa. Após coletar a última folha, um sinal sonoro discreto indica que a saída de emergência foi destrancada, fazendo com que o jogador retorne ao ponto de extração para vencer a partida. 

PERSONAGENS PRINCIPAIS: o jogador tem a liberdade de escolher entre dois avatares no início da partida, cada um com identidades visuais distintas, mas compartilhando a mesma técnica rigorosa. Dentre as identidades, temos a ideia de colocar docentes do IFRN como os avatares -nos quais seriam Carlos Eugênio (possuindo um traje formal escuro, com camuflagem nas sombras) e Romerito (possuindo traje esportivo, focado em agilidade e visibilidade clara)-. 
Nas movimentações técnicas, teremos os EIXOS: movimentação em 4 direções cardinais; LÓGICA DE GRID: embora o movimento seja livre em pixels, o personagem respeita uma "caixa de colisão" 10% menor que o seu sprite para evitar que ele fique preso em cantos de estantes; VELOCIDADE BASE: 5 pixels por frame (o qual é ajustável para garantir consistência em diferentes computadores).

INIMIGOS E OBSTÁCULOS: O bibliotecário não será apenas um obstáculo móvel, mas uma entidade com estado de comportamento:
- Mecânica de campo de visão/proximidade - implementação de detecção baseada em raio de alcance e linha de visão direta, que respeita a obstrução de objetos sólidos (estantes);
- Obstáculos Ambientais - inclusão de "zonas de ruído" que forçam o jogador a alternar entre caminhar e agachar para evitar detecção acústica
  
CENÁRIO/MAPA E LEVEL DESIGN: em sua estrutura técnica, o mapa é interpretado como uma malha de tiles (ladrilhos). Cada número na matriz corresponde a um tipo de objeto:
0: piso - caminho livre;
1: estante de livros - bloqueio total de movimento e campo de visão;
2: mesa de estudo - bloqueio de movimento, mas permite a o campo de visão do inimigo sem dificuldades;
3: ponto de spaw - onde o avatar começam;
4: saída -só se torna ativa após coletar os itenso. 
Na distribuição de itens, as folhas de papel são objetos do tipo sprite posicionados em coordenadas (x, y) que coincidem com os centros dos tiles do tipo 0. inicialmente, os locais são fixos para garantir que o nível seja "vencível" e equilibrado.

SISTEMA DE PONTUAÇÃO: o sistema de pontuação é gerenciado por uma variável de global ou um atributo de classe. Os pontos são acumulados durante a partida e exibidos em tempo real na interface (HUD). 
*Item "folha de trabalho": +100 pontos por unidades;
*Conclusão da missão (fuga): +300 pontos

SISTEMA DE VIDA E DANO: na estrutura visual dos cadernos, em vez de um número genérico, a vida é representada por ícones de cadernos no canto superior da tela. As vidas iniciais serão de três cadernos, sendo assim, cada vez que o jogador for pego, um caderno se fecha ou "rasga". 

CONTROLES E ENTREDAS DE SISTEMA: o jogo utiliza um sistema de entrada híbrido para garantr acessibilidade e conforto
-Setas ou WASD- movimentação cardeal durante a exploção 
-R- reiniciar partida; tela de game over ou pausa
-Q ou ESC- sair do jogo/voltar para o menu ou gameplay
-Espaço/Enter- confirmar seleção para menus ou seleção de personagens 

FLUXO DE JOGO (GAME LOOP & ESTADOS): o jogo é estruturado em um loop contínuo que processa entradas, atualiza a lógica e renderiza imagens, passando pelas seguites fases:
1. Inicialização e Menu (start state)
na abertura, temos a exibição do título animado (efeito de "glitch"); na interação, se tem a instrução "pressione qualquer tecla" ou botões "inicar" e "sair"; na seleção, têm-se a transição para a tela de escolha entre os avatares (Carlos Eugênio e Romerito).
2. Loop de Ação (play state)
na entrada, o jogador inicia na recepção da biblioteca; na exploração; a navegação furtiva entre as estantes, possuindo o radar de folhas (se implementando) indica a proximidade dos itens; por fim, na tensão escalonada, a cada folha coletada, a música do jogo ganha uma camada extra de percussão, aumentando o suspense.
3. Sistema de Verificação (check state)
no contador, o código verifica a cada frame; ao atingir o objetivo, um som de "porta destrancando" toca e uma seta indicadora aparece sutilmente apontando para a saída.
4. Conclusão (end state)
VITÓRIA - se o jogador tocar o portal de saída após o check; exibe pontuação e nota final.
DERROTA - se as vidas chegarem a zero; exibe a tela de "expulso".

REGRAS DO JOGO E MACÂNICAS DE COLISÃO
*Colisão com o cenário (paredes e estantes) -> na mecânica estrita, o jogador possui uma hitbox ligeiramente menor que o sprite visual. Isso evita que o personagem "tranque" nos cantos ao passar por corredores estreitos. 
*Sistema de Detecção (inimigo e jogador) -> o campo de visão será definido como uma área triangular ou poligonal que se projeta à frente do inimigo. A detecção ocorre através da intersecção entre o retângulo do jogador e o polígono de visão do inimigo. 

ESTRUTURA DO PROJETO (Arquitetura Python): A organização do projeto segue o princípio de moduralização; em vez de um arquivo único gigante, dividimos o código em módulos lógicos que conversam entre si. Na divisão atualizada, teremos:
-main.py- o "maestro" do jogo. Ele indica o pygame, contém o loop principal e gerencia a transição entre telas (menu -> jogo -> game over).
-sprites.py- contém as classes baseadas em pygame.sprites.Sprite. É aqui que reside a intelêngia dos avatares.
-settings.py- centraliza todas as constantes. Se você quiser mudar a velocidade do jogo ou a cor das paredes, muda aqui e o projeto todo se ajusta. 
-assets/- o repositório de mídia, organizado por tipo para facilitar o carregamento em massa. 

FUNCIONALIDADES MÍNIMAS (MVP): possui foco em 3 pilares fundamentais para que o jogo seja "jogável" do ínicio ao fim
1. Sistema de Movimentação e Colisão Reativa
o jogador deve se mover suavemente usando o teclado; ao encostar em uma estante, o personagem deve parar imediatamente sem "tremer" ou atravessar a parede
2. Inteligência Artificial ou Patrulha
um único inimigo que percorre um caminho retangular simples (indo de um ponto A para B, depois de C para D). Ele deve possuir uma área de detecção que represente o campo de visão do mesmo. 
3. Ciclo de Coleta e Interface (HUD)
o que deve funcionar no jogo são itens (folhas) que desaparecem ao toque do jogador (kill() no sprite) e incrementam para mudar de direção ao chegar no destino. 

EASTER EGG: Dentro da biblioteca, existe um easter egg escondido que pode ser desbloqueado através da observação e interação com o ambiente. Durante a exploração, o jogador pode encontrar algumas folhas especiais espalhadas pelo cenário. Diferente das demais, essas folhas contêm letras que funcionam como pistas. Essas letras correspondem às estantes da biblioteca, que estão identificandas com marcações visíveis. Ao interagir com as estantes na ordem correta, baseada nas letras encontradas nas folhas, um mecanismo secreto é ativado. 
Ao resolver o enigma: Uma estante se abre (ou desaparece), revelando uma área secreta escondida atrás dela. Dentro dessa área, o jogador encontra um quadro estilizado representando um professor apresentado como "O Guardião do Conhecimento". Além disso, o ambiente inclui um pequeno elemento narrativo: "Dizem que ele sabe quando você usa chat gpt para resolver as listas...". Este easter egg não é necessário para completar o jogo, mas recompensa jogadores curiosos com um momento secreto, reforçando a exploração e adicionando um toque de humor e mistério à experiência.
