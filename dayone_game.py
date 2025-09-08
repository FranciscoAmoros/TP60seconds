import pygame, random, os, datetime

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORIGINAL_TILE_SIZE = 32
SCALE_FACTOR = 2
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR  # 64x64
SOLID_TILES = [2]
TILE_FOLDER = 'imagenes/tiles'
MAP_FILE = 'map.txt'

collision_rects = []

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

def draw_colliders(screen, tilemap):
    global collision_rects

    map_width = len(tilemap[0]) * TILE_SIZE
    map_height = len(tilemap) * TILE_SIZE
    screen_width, screen_height = screen.get_size()
    offset_x = (screen_width - map_width) // 2
    offset_y = (screen_height - map_height) // 2

    for y, row in enumerate(tilemap):
        for x, tile_id in enumerate(row):
            if tile_id in SOLID_TILES:
                rect = pygame.Rect(x * TILE_SIZE + offset_x, y * TILE_SIZE + offset_y, TILE_SIZE, TILE_SIZE)
                collision_rects.append(rect)
            


def main(estado, screen1):
    global screen
    screen = screen1
    global estado_juego
    estado_juego = estado
    done = False
    back_to_menu = False
    tiles = load_tiles(TILE_FOLDER)
    tilemap = load_map(MAP_FILE)
    draw_colliders(screen, tilemap)
    clock = pygame.time.Clock()



    font = pygame.font.SysFont(None, 72)
    speed = 5

    start_ticks = pygame.time.get_ticks()
    countdown_time = 60 

    NEGRO = (0, 0, 0)
    ROJO = (255, 0, 0)

    player = pygame.Rect(300, 220, 40, 40)

    screen_w, screen_h = screen.get_size()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0

        if teclas[pygame.K_w]: 
            dy = -speed
        if teclas[pygame.K_s]: 
            dy = speed
        if teclas[pygame.K_a]: 
            dx = -speed
        if teclas[pygame.K_d]: 
            dx = speed

        if teclas[pygame.K_LEFT]:
            dx = -speed
        if teclas[pygame.K_RIGHT]:
            dx = speed
        if teclas[pygame.K_UP]:
            dy = -speed
        if teclas[pygame.K_DOWN]:
            dy = speed
        
        player.x += dx
        player.y += dy

        if player.left < 0: player.left = 0
        if player.right > screen_w: player.right = screen_w
        if player.top < 0: player.top = 0
        if player.bottom > screen_h: player.bottom = screen_h

        for collider in collision_rects:
            if player.colliderect(collider):
                player.x -= dx
                break

        for collider in collision_rects:
            if player.colliderect(collider):
                player.y -= dy
                break



        screen.fill(BLACK)

        draw_map(screen, tilemap, tiles, TILE_SIZE)

        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = countdown_time - seconds_passed
        pygame.draw.rect(screen, ROJO, player)

        if time_left >= 0:
            text = font.render(str(time_left), True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, 40))  
            screen.blit(text, text_rect)
        else:
  
            done = True
            back_to_menu = True

        pygame.display.flip()
        clock.tick(60)

    return estado_juego, back_to_menu
