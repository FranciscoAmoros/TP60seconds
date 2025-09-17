import pygame, random, os, datetime

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORIGINAL_TILE_SIZE = 32
SCALE_FACTOR = 1
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR  # 64x64
SOLID_TILES = [2]
TILE_FOLDER = 'imagenes/tiles'
MAP_FILE = 'map.txt'
BUNKER = None

inventory=[]

OBJECTS = "imagenes_objs/"

collision_rects = []

pygame.init()

estado_juego = {}

objects_quantity = {
    "Easy": {"comida": 6, "medicina": 3, "agua": 10},
    "Medium": {"comida": 5, "medicina": 1, "agua": 8},
    "Hard": {"comida": 3, "medicina": 0, "agua": 6}
}

def get_random_posible_position(tilemap):
    # Tamaño del mapa en píxeles
    map_width = len(tilemap[0]) * TILE_SIZE
    map_height = len(tilemap) * TILE_SIZE
    screen_width, screen_height = screen.get_size()

    # Offset para centrar
    offset_x = (screen_width - map_width) // 2
    offset_y = (screen_height - map_height) // 2

    # Obtener posiciones de tiles válidos (no sólidos)
    valid_positions = []
    for y, row in enumerate(tilemap):
        for x, tile_id in enumerate(row):
            if tile_id not in SOLID_TILES:
                px = x * TILE_SIZE + offset_x
                py = y * TILE_SIZE + offset_y
                rect = pygame.Rect(px, py, 40, 40)
                if not any(rect.colliderect(collider) for collider in collision_rects):
                    valid_positions.append((px, py))

    # Elegir una al azar
    if valid_positions:
        return random.choice(valid_positions)
    else:
        return 0, 0  # Fallback si no hay lugar


def get_objects(estado_juego, tilemap):
    objects = []

    for _ in range(objects_quantity[estado_juego["dificultad"]]["comida"]):
        llave = random.choice(list(estado_juego["objetos"]["comida"].keys()))
        value = estado_juego["objetos"]["comida"][llave]
        image_path = os.path.join(OBJECTS, f"{llave}.png")
        if not os.path.exists(image_path): continue

        objects.append({
            "type": "comida",
            "name": llave,
            "value": value,
            "image": pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (40, 40)),
            "rect": pygame.Rect(get_random_posible_position(tilemap), (40, 40)),
            
        })

    for _ in range(objects_quantity[estado_juego["dificultad"]]["medicina"]):

        llave = random.choice(list(estado_juego["objetos"]["medicina"].keys()))
        value = estado_juego["objetos"]["medicina"][llave]
        image_path = os.path.join(OBJECTS, f"{llave}.png")
        if not os.path.exists(image_path): continue

        objects.append({
            "type": "medicina",
            "name": llave,
            "value": value,
            "image": pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (40, 40)),
            "rect": pygame.Rect(get_random_posible_position(tilemap), (40, 40))
        
        })

    for _ in range(objects_quantity[estado_juego["dificultad"]]["agua"]):
        llave = "agua"
        value = estado_juego["objetos"]["agua"]
        image_path = os.path.join(OBJECTS, f"{llave}.png")
        if not os.path.exists(image_path): continue

        objects.append({
            "type": "agua",
            "name": llave,
            "value": value,
            "image": pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (40, 40)),
            "rect": pygame.Rect(get_random_posible_position(tilemap), (40, 40))
        })

    return objects


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

            if x == 17 and y == 6:
                tile_center_x = x * tile_size + offset_x
                tile_center_y = y * tile_size + offset_y

    # Ajuste para centrar la imagen más grande
                bunker_width, bunker_height = BUNKER.get_size()
                draw_x = tile_center_x + (tile_size - bunker_width) // 2
                draw_y = tile_center_y + (tile_size - bunker_height) // 2

    screen.blit(BUNKER, (draw_x, draw_y))


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
    global screen, BUNKER
    screen = screen1
    global estado_juego
    estado_juego = estado
    done = False
    tiles = load_tiles(TILE_FOLDER)
    tilemap = load_map(MAP_FILE)
    draw_colliders(screen, tilemap)
    objects = get_objects(estado_juego, tilemap)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 72)
    speed = 5

    start_ticks = pygame.time.get_ticks()
    countdown_time = 60 

    NEGRO = (0, 0, 0)
    ROJO = (255, 0, 0)

    player = pygame.Rect(550, 350, 16, 16)
    BUNKER = pygame.image.load("bunker.png").convert_alpha()
    BUNKER = pygame.transform.scale(BUNKER, (64, 64))

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
        for obj in objects:
            screen.blit(obj["image"], obj["rect"])
            if player.colliderect(obj["rect"]):
                if not len(inventory) == 4:
                    print(f"Has recogido: {obj['name']}")
                    obj["value"] = obj["value"][0] + 1
                    objects.remove(obj)
                    inventory.append(obj)

        # DIBUJAR INVENTARIO
        inventory_box_size = 50  # Tamaño de cada recuadro
        inventory_margin = 10    # Espacio entre recuadros
        inventory_x = 10         # Posición X donde inicia el inventario en pantalla
        inventory_y = screen.get_height() - inventory_box_size - 10  # Posición Y (abajo de la pantalla)

        for i, item in enumerate(inventory):
            rect_x = inventory_x + i * (inventory_box_size + inventory_margin)
            rect = pygame.Rect(rect_x, inventory_y, inventory_box_size, inventory_box_size)
            
            # Fondo gris semitransparente (blur simulado)
            s = pygame.Surface((inventory_box_size, inventory_box_size), pygame.SRCALPHA)
            s.fill((50, 50, 50, 180))  # Gris con alpha para transparencia
            screen.blit(s, (rect_x, inventory_y))
            
            # Borde blanco
            pygame.draw.rect(screen, WHITE, rect, 2)
            
            # Imagen escalada y centrada
            img = pygame.transform.scale(item["image"], (inventory_box_size - 10, inventory_box_size - 10))
            img_rect = img.get_rect(center=rect.center)
            screen.blit(img, img_rect)

        if time_left >= 0:
            text = font.render(str(time_left), True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, 40))  
            screen.blit(text, text_rect)
        else:
            done = True

        pygame.display.flip()
        clock.tick(60)

    return estado_juego
