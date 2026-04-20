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
Na distribuição de itens, as folhas de papel são objetos do tipo sprite posicionados em coordenadas (x, y) que coincidem com os centros dos tiles do tipo 0. inicialmente, os locais são fixos para garantir que o nível seja "vencível" e equilibrado
