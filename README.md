TÍTULO: The Midnight Assignment - fuja do bibliotecário!

DESCRIÇÃO GERAL: o jogo terá tipo Acarde/Stealth 2D/ Dungeon Crawler Urbano; o ambiente do game será em uma biblioteca escolar durante o período da madrugada, tendo seu cenário composto por corredores estreitos formados por estantes gigantescas, áreas de leitura com mesas que oferecem cobertura parcial e setores proibidos com uma "péssima" iluminação.
A ideia principal do jogo se dará quando o jogador assume o papel de um estudante que, em um momento de desespero, invade a escola à noite para recuperar os originais de um trabalho acadêmico vital. O desafio não é apenas encontrar as folhas, mas gerenciar o som dos seus passos e a visibilidade em relação à lanterna do biblotecário, que segue padrões de busca inteligentes. 

OBJETIVO: o principal objetivo pensado é a recuperação das folhas de um projeto. O jogador deve localizar e recuperar as 5 folhas manuscritas do seu projeto final, que foram deixadas em locais distintos da Biblioteca Central; o jogo tem como desafio o fato de que as folhas não são visíveis desde do início, sendo preciso o player explorar o labirinto de estantes para revelá-vas no mapa. Após coletar a última folha, um sinal sonoro discreto indica que a saída de emergência foi destrancada, fazendo com que o jogador retorne ao ponto de extração para vencer a partida. 

PERSONAGENS PRINCIPAIS: o jogador tem a liberdade de escolher entre dois avatares no início da partida, cada um com identidades visuais distintas, mas compartilhando a mesma técnica rigorosa. Dentre as identidades, temos a ideia de colocar docentes do IFRN como os avatares -nos quais seriam Carlos Eugênio (possuindo um traje formal escuro, com camuflagem nas sombras) e Romerito (possuindo traje esportivo, focado em agilidade e visibilidade clara)-. 
Nas movimentações técnicas, teremos os EIXOS: movimentação em 4 direções cardinais; LÓGICA DE GRID: embora o movimento seja livre em pixels, o personagem respeita uma "caixa de colisão" 10% menor que o seu sprite para evitar que ele fique preso em cantos de estantes; VELOCIDADE BASE: 5 pixels por frame (o qual é ajustável para garantir consistência em diferentes computadores).

INIMIGOS E OBSTÁCULOS: O bibliotecário não será apenas um obstáculo móvel, mas uma entidade com estado de comportamento:         -Estados de patrulha- segue uma rota predefinida (quadrada ou em L), possuindo também cor amarela/branca suaves em seu cone de luz;
Estado de alerta- se o jogador, fizer barulho ou for visto de relance, o bibliotecário para por 2/3 segundos e gira a lanterna por 360° para procurar o invasor; 
Estado de perseguição- se o jogador entrar totalmente no cone de luz, a mesma fica vermelha,  a velocidade do inimigo aumenta em 30% e ele persegue o jogador até perdê-lo de vista por 5 segundos. 
O cone de luz- o mesmo serve como um "sensor" do inimigo, sendo bloqueado por estantes (objetos opacos).O visual do cone deve ser semitransparente, permitindo que o jogador veja o que está atrás da luz, ma sinta o perigo de cruzá-la. 

CENÁRIO/MAPA E LEVEL DESIGN: em sua estrutura técnica, o mapa é interpretado como uma malha de tiles (ladrilhos). Cada número na matriz corresponde a um tipo de objeto:
0: piso -caminho livre-;
1: estante de livros -bloqueio total de movimento e luz-;
2: mesa de estudo -bloqueio de movimento, mas permite a passagem de luz da lanterna-;
3: ponto de spaw -onde o avatar começam-;
4: saída -só se torna ativa após coletar os itens-. 
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
