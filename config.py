#config.py
width = 800
height = 600
fps = 60
tilesize = 40

# PALETAS DE CORES 
black = (10, 10, 15)
white = (245, 245, 250)
dark_gray = (32, 32, 40)       # estantes (bloqueio físico e visão)
light_gray = (90, 95, 110)     # mesas (bloqueio unicamente físico)
floor_color = (18, 18, 24)     # piso normal
noise_color = (55, 30, 30)     # zonas de ruído
yellow = (255, 210, 0)         # folhas normais / seleção / alertas
red = (230, 40, 40)            # bibliotecário / alertas críticos  
blue = (0, 100, 255)           # saída destrancada
purple = (130, 60, 200)        # Carlos Eugênio (avatar)
green = (40, 200, 80)          # texto de vitória

# MODIFICADORES DE VELOCIDADE
player_speed_base = 160
player_speed_crouch = 75
librarian_speed = 70
detection_radius = 180   # alcance máximo de visão do bibliotecário

# MATRIZ DO CENÁRIO 
# 0: piso | 1: estante | 2: mesa | 3: spawn player | 4: saída | 5: ruído | 6: folha | 7: spawn bibliotecário
map_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 2, 2, 0, 1, 1, 0, 1],
    [1, 0, 1, 6, 1, 0, 1, 1, 0, 1, 1, 0, 1, 6, 1, 0, 2, 2, 0, 1],
    [1, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 6, 6, 6, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 2, 2, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 6, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 4, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]