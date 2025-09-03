import pygame, random, os, datetime

BLACK = (0, 0, 0)
ORIGINAL_TILE_SIZE = 32
SCALE_FACTOR = 2
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR  # 96x96
TILE_FOLDER = 'imagenes/tiles'
MAP_FILE = 'map.txt'



pygame.init()

estado_juego = {}

def load_tiles(folder):
    tiles = {}
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            tile_id = int(filename.split('.')[0])  # Ej: "1.png" -> 1
            path = os.path.join(folder, filename)
            
            # Cargar la imagen con transparencia
            image = pygame.image.load(path).convert_alpha()

            # Escalar a 96x96
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
    screen.fill(BLACK)
    pygame.display.flip()
    clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get():
            pass   
        draw_map(screen, tilemap, tiles, TILE_SIZE)

        clock.tick(60)
        pygame.display.flip()

    
    return estado_juego, back_to_menu