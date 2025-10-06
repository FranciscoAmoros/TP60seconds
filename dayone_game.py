import pygame, random, os, datetime

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORIGINAL_TILE_SIZE = 32
SCALE_FACTOR = 1
TILE_SIZE = ORIGINAL_TILE_SIZE * SCALE_FACTOR  # 64x64
SOLID_TILES = [2]
TILE_FOLDER = 'imagenes/tiles'
MAP_FILE = 'map.txt'
BUNKER_IMG = None

BUNKER = None

player_pos = [0, 0]

inventory=[]

OBJECTS = "imagenes_objs/"

objects = []

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

                # Verificar si la posición está libre
                is_valid_position = True

                # Verificar colisión con los rectángulos de los colliders (si existen)
                for collider in collision_rects:
                    if rect.colliderect(collider):
                        is_valid_position = False
                        break  # Salir si se encuentra colisión

                # Verificar si la posición choca con algún objeto
                if is_valid_position:
                    for item in objects:
                        if item["rect"].colliderect(rect):
                            is_valid_position = False
                            break  # Salir si se encuentra colisión con un objeto

                # Si la posición es válida, agregarla a la lista
                if is_valid_position:
                    valid_positions.append((px, py))

    # Retornar una posición aleatoria válida si existe alguna
    if valid_positions:
        return random.choice(valid_positions)
    return None  # Si no hay posiciones válidas disponibles



def get_objects(estado_juego, tilemap):
    global objects
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

    global BUNKER, BUNKER_IMG

    can_spawn_bunker = False

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
                if player_pos[0] in range(x-2, x+2) and player_pos[1] in range(y-2, y+2):
                    screen.blit(tiles[tile_id], (x * tile_size + offset_x, y * tile_size + offset_y))

            if x == 17 and y == 6:
                if player_pos[0] in range(x-2, x+2) and player_pos[1] in range(y-2, y+2):
                    can_spawn_bunker = True
                
                tile_center_x = x * tile_size + offset_x
                tile_center_y = y * tile_size + offset_y

    # Ajuste para centrar la imagen más grande
                bunker_width, bunker_height = BUNKER_IMG.get_size()
                draw_x = tile_center_x + (tile_size - bunker_width) // 2
                draw_y = tile_center_y + (tile_size - bunker_height) // 2
                
                if can_spawn_bunker and BUNKER is None:
                    BUNKER = pygame.Rect(draw_x, draw_y, bunker_width, bunker_height)

    if can_spawn_bunker and BUNKER is not None:
        screen.blit(BUNKER_IMG, (draw_x, draw_y))


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


def get_player_tile_position(player, tilemap, tile_size, screen):
    # Tamaño de la ventana
    screen_width, screen_height = screen.get_size()

    # Calcular el offset para centrar el mapa
    map_width = len(tilemap[0]) * tile_size
    map_height = len(tilemap) * tile_size
    offset_x = (screen_width - map_width) // 2
    offset_y = (screen_height - map_height) // 2

    # Convertir las coordenadas del jugador en píxeles a coordenadas de tiles
    player_tile_x = (player.x - offset_x) // tile_size
    player_tile_y = (player.y - offset_y) // tile_size

    return player_tile_x, player_tile_y

            


def main(estado, screen1):
    global screen, BUNKER_IMG, BUNKER
    global player_pos
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
    speed = 3

    start_ticks = pygame.time.get_ticks()
    countdown_time = 60 

    NEGRO = (0, 0, 0)
    ROJO = (255, 0, 0)

    player = pygame.Rect(550, 350, 16, 16)

    BUNKER_IMG = pygame.image.load("bunker.png").convert_alpha()
    BUNKER_IMG = pygame.transform.scale(BUNKER_IMG, (64, 64))

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
        if BUNKER is not None:
            if player.colliderect(BUNKER):
                for item in inventory:
                    if not item["type"] == "agua":
                        estado_juego["objetos"][item["type"]][item["name"]][0] += 1 #agregar 1 a la cantidad del item
                    else:
                        estado_juego["objetos"][item["type"]][0] += 1 #agregar 1 a la cantidad del item
                    inventory.remove(item) #remover item del inventario

        screen.fill(BLACK)

        player_pos[0], player_pos[1] = get_player_tile_position(player, tilemap, TILE_SIZE, screen)
        draw_map(screen, tilemap, tiles, TILE_SIZE)

        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = countdown_time - seconds_passed
        pygame.draw.rect(screen, ROJO, player)
        for obj in objects:
            obj_pos = [0, 0]
            obj_pos[0], obj_pos[1] = get_player_tile_position(obj["rect"], tilemap, TILE_SIZE, screen)
            if not obj_pos[0] in range(player_pos[0]-2, player_pos[0]+2) or not obj_pos[1] in range(player_pos[1]-2, player_pos[1]+2):
                continue
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

        if time_left <= 0:
            done = True

        pygame.display.flip()
        clock.tick(60)

    return estado_juego
