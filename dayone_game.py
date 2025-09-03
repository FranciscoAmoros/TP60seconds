import pygame, random, os, datetime

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORIGINAL_TILE_SIZE = 32
SCALE_FACTOR = 2
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR  # 64x64
TILE_FOLDER = 'imagenes/tiles'
MAP_FILE = 'map.txt'

pygame.init()

estado_juego = {}

def load_tiles(folder):
    tiles = {}
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            tile_id = int(filename.split('.')[0])
            path = os.path.join(folder, filename)
            
            # Cargar la imagen con transparencia
            image = pygame.image.load(path).convert_alpha()

            # Escalar a 64x64
            image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

            tiles[tile_id] = image
    return tiles


# Cargar el mapa
def load_map(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [[int(cell) for cell in line.strip().split(',')] for line in lines]


def draw_map(screen, tilemap, tiles, tile_size):
    # Tamaño del mapa en píxeles
    map_width = len(tilemap[0]) * tile_size
    map_height = len(tilemap) * tile_size

    # Tamaño de la ventana
    screen_width, screen_height = screen.get_size()

    # Calcular offset para centrar
    offset_x = (screen_width - map_width) // 2
    offset_y = (screen_height - map_height) // 2

    # Dibujar tiles
    for y, row in enumerate(tilemap):
        for x, tile_id in enumerate(row):
            if tile_id in tiles:
                screen.blit(tiles[tile_id], (x * tile_size + offset_x, y * tile_size + offset_y))


def main(estado, screen1):
    global screen
    screen = screen1
    global estado_juego
    estado_juego = estado
    done = False
    back_to_menu = False
    tiles = load_tiles(TILE_FOLDER)
    tilemap = load_map(MAP_FILE)
    clock = pygame.time.Clock()

    # Fuente para el contador
    font = pygame.font.SysFont(None, 72)  # un poco más grande

    # Tiempo inicial (en milisegundos)
    start_ticks = pygame.time.get_ticks()
    countdown_time = 60  # segundos

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # 1. Borrar pantalla
        screen.fill(BLACK)

        # 2. Dibujar mapa
        draw_map(screen, tilemap, tiles, TILE_SIZE)

        # 3. Calcular tiempo restante
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = countdown_time - seconds_passed

        # 4. Dibujar contador (centrado arriba)
        if time_left >= 0:
            text = font.render(str(time_left), True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, 40))  
            screen.blit(text, text_rect)
        else:
            # Se terminó el tiempo
            done = True
            back_to_menu = True

        # 5. Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)

    return estado_juego, back_to_menu


