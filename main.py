import pygame, os
from time import sleep
import json
import dayone_game, seconds_game

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
pygame.init()
FUENTE = pygame.font.SysFont("arial", 36)
ruta_actual = os.path.dirname(__file__)

settings_default = {
    "display_mode": "windowed",
    "resolution_index": 2
}

resolutions_available = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1600, 900),
    (1920, 1080)
]

current_display = "main"


settings = {}
ruta_settings = os.path.join(ruta_actual, "settings")
os.makedirs(ruta_settings, exist_ok=True)


def change_menu_display(display):
    global current_display
    current_display = display


def load_settings():
    global settings_root
    global settings
    settings_root = os.path.join(ruta_settings, "settings.json")

    if os.path.exists(settings_root):
        with open(settings_root, "r") as archivo:
            settings = json.load(archivo)
    else:
        settings = settings_default.copy()
        with open(settings_root, "w") as archivo:
            json.dump(settings, archivo, indent=4)
    update_config()

def update_config():
    global screen, screen_width, screen_high
    global settings

    try:
        resolution = resolutions_available[settings["resolution_index"]]
    except (IndexError, KeyError):
        resolution = resolutions_available[0]
        settings["resolution_index"] = 0

    if settings["display_mode"] == "fullscreen":
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(resolution)

    screen_width, screen_high = screen.get_size()


def save_settings():
    global settings
    with open(settings_root, "w") as archivo:
        json.dump(settings, archivo, indent=4)

def modify_settings(indice):
    global settings

    if indice == 1:
        settings["display_mode"] = (
            "fullscreen" if settings["display_mode"] == "windowed" else "windowed"
        )

    elif indice == 2:
        # Cambiar al siguiente índice de resolución
        current_index = settings.get("resolution_index", 0)
        new_index = (current_index + 1) % len(resolutions_available)
        settings["resolution_index"] = new_index

    save_settings()
    load_settings()

botones_images = {
    "green": pygame.image.load(os.path.join(ruta_actual, "UI", "button_green.png")),
    "blue": pygame.image.load(os.path.join(ruta_actual, "UI", "button_blue.png")),
    "red": pygame.image.load(os.path.join(ruta_actual, "UI", "button_red.png")),
    "x": pygame.image.load(os.path.join(ruta_actual, "UI", "button_x.png")),
}

# Escalar las imágenes por un factor de 4
botones_images_escalados = {
    clave: pygame.transform.scale(img, (img.get_width() * 7, img.get_height() * 7))
    for clave, img in botones_images.items()
}

botones_text_colors = {
    "Empezar": "green",
    "Opciones": "blue",
    "Salir": "red",
    "Volver": "red",
    "X": "x",
    "Easy": "green",
    "Medium": "blue",
    "Hard": "red"
}

FONT = pygame.font.SysFont("arial", 28)
load_settings()
screen_width, screen_high = screen.get_size()
pygame.display.flip()
clock = pygame.time.Clock()

fondo_menu = pygame.image.load("fondomenu.jpg")
fondo_menu = pygame.transform.scale(fondo_menu, (screen_width, screen_high))


ruta_saves = os.path.join(ruta_actual, "saves")
os.makedirs(ruta_saves, exist_ok=True)

def draw_button(screen, rect, text, font):
    if not text in botones_text_colors:
        color_key = "blue"  # Color por defecto si no está en el diccionario
    else:
        color_key = botones_text_colors[text]
    screen.blit(botones_images_escalados[color_key], rect)
    if callable(text):
        text_surface = font.render(text(), True, BLACK)  # Ejecutar lambda si es callable
    else:
        text_surface = font.render(text, True, BLACK)
    
    if not text == "X":
        screen.blit(
            text_surface,
            (rect.x + (rect.width - text_surface.get_width()) // 2,
            rect.y + (rect.height - text_surface.get_height()) // 2)
        )


estado_juego_inicial = {
    "objetos": {
        "comida": {
            "bizcochitos don satur": [0, 1],
            "medialunas": [0, 1],
            "lata de duraznos": [0, 1],
            "lata de atun": [0, 1],
            "empanadas de carne": [0, 1]
        },
        "agua": [0,1],
        "medicina": {
            "vendas": [0,1],
            "botiquin": [0, 2],
            "jarabe": [0,1],
            "capsula": [0,1],
            "pastilla": [0,1]
        }
    },
    "dia": 0,
    "dificultad": "Easy"
}

estado_juego = {}


def delete_game(indice_partida):

    global estado_juego
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    if os.path.exists(partida_root):
        os.remove(partida_root)

    estado_juego = {}

def clear_levels_60unfinished():
    archivos = os.listdir(ruta_saves)
    
    for archivo_nombre in archivos:
        ruta_completa = os.path.join(ruta_saves, archivo_nombre)
        if os.path.isfile(ruta_completa):
            # Abrimos y leemos el archivo
            with open(ruta_completa, "r") as f:
                contenido = json.load(f)
            
            # Si "dia" es 0, borramos la partida
            if contenido.get("dia", 1) == 0:
                # Extraemos el índice completo del nombre del archivo
                # Suponiendo que el nombre es "partidaX.json"
                indice_str = ''.join(c for c in archivo_nombre if c.isdigit())
                if indice_str:
                    indice = int(indice_str)
                    delete_game(indice)


clear_levels_60unfinished()

def start_game(indice_partida):
    global estado_juego
    global screen
    if estado_juego["dia"] == 0:
        estado_juego = dayone_game.main(estado_juego, screen)
        change_menu_display("main")
        estado_juego["dia"] = 1
        if estado_juego["dia"] == 1:
            save_game(indice_partida)
            load_game(indice_partida, start_immediately=False)
            estado_juego = seconds_game.main(estado_juego, screen)
    else:
        estado_juego = seconds_game.main(estado_juego, screen)


def load_game(indice_partida, start_immediately=True):
    global screen
    global estado_juego
    global aux_indice
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    if os.path.exists(partida_root):
        with open(partida_root, "r") as archivo:
            estado_juego = json.load(archivo)
        if start_immediately:
            start_game(indice_partida)
    else:
        change_menu_display("dificulty")
        aux_indice = indice_partida

def get_state_game(indice_partida):
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")
    if os.path.exists(partida_root):
        return f"Game {indice_partida}"
    else:
        return "New Game"
    
def get_dificulty_game(indice_partida):
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")
    if os.path.exists(partida_root):
        try:
            with open(partida_root, "r") as archivo:
                estado = json.load(archivo)
            return estado.get("dificultad", "Desconocida")
        except Exception as e:
            print(f"[ERROR] No se pudo leer partida {indice_partida}: {e}")
            return "Error"
    else:
        return "N/A"

        
def save_game(indice_partida):
    global estado_juego
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    with open(partida_root, "w") as archivo:
        json.dump(estado_juego, archivo, indent=4)


def exit_game():
    pygame.quit()
    exit()


def center_rect(y, w, h):
    """Devuelve un Rect centrado horizontalmente en la pantalla"""
    return pygame.Rect((screen_width - w) // 2 - 450, y, w, h)


def recenter_buttons():
    global buttons_main, buttons_options, buttons_sub, buttons_choose_dificulty
    # Main menu
    buttons_main = [
        (center_rect(290, 224, 112), "Empezar", lambda: change_menu_display("submenu")),
        (center_rect(440, 224, 112), "Opciones", lambda: change_menu_display("options")),
        (center_rect(590, 224, 112), "Salir", lambda: exit_game()),
    ]

    # Options menu
    buttons_options = [
        (center_rect(290, 224, 112), settings["display_mode"], lambda: modify_settings(1)),
        (center_rect(440, 224, 112), f"resolution: {resolutions_available[settings['resolution_index']]}", lambda: modify_settings(2)),
        (center_rect(590, 224, 112), "Opcion3", lambda: print("opcion3")),
        (center_rect(740, 224, 112), "Volver", lambda: change_menu_display("main")),
    ]

    # Submenu
    buttons_sub = [
        (center_rect(290, 224, 112), lambda: get_state_game(1), ("load", 1)),
        (center_rect(290, 126, 126).move(220, 0), "X", ("delete", 1)),
        (center_rect(440, 224, 112), lambda: get_state_game(2), ("load", 2)),
        (center_rect(440, 126, 126).move(220, 0), "X", ("delete", 2)),
        (center_rect(590, 224, 112), lambda: get_state_game(3), ("load", 3)),
        (center_rect(590, 126, 126).move(220, 0), "X", ("delete", 3)),
        (center_rect(740, 224, 112), "Volver", lambda: change_menu_display("main")),
    ]

    buttons_choose_dificulty = [
        (center_rect(290, 224, 112), "Easy", ("create", 1)),

        (center_rect(440, 224, 112), "Medium", ("create", 2)),

        (center_rect(590, 224, 112), "Hard", ("create", 3)),

        (center_rect(740, 224, 112), "Volver", lambda: change_menu_display("main"))
    ]


buttons_main = [
    (center_rect(290, 224, 112), "Empezar", lambda: change_menu_display("submenu")),
    (center_rect(440, 224, 112), "Opciones", lambda: change_menu_display("options")),
    (center_rect(590, 224, 112), "Salir", lambda: exit_game()),
]


buttons_options = [
    (center_rect(290, 224, 112), settings["display_mode"], lambda: modify_settings(1)),
    (center_rect(440, 224, 112), f"resolution: {resolutions_available[settings['resolution_index']]}", lambda: modify_settings(2)),
    (center_rect(590, 224, 112), "Opcion3", lambda: print("opcion3")),
    (center_rect(740, 224, 112), "Volver", lambda: change_menu_display("main")),
]

buttons_sub = [
    (center_rect(290, 224, 112), lambda: get_state_game(1), ("load", 1)),
    (center_rect(290, 126, 126).move(220, 0), "X", ("delete", 1)),
    (center_rect(440, 224, 112), lambda: get_state_game(2), ("load", 2)),
    (center_rect(440, 126, 126).move(220, 0), "X", ("delete", 2)),
    (center_rect(590, 224, 112), lambda: get_state_game(3), ("load", 3)),
    (center_rect(590, 126, 126).move(220, 0), "X", ("delete", 3)),
    (center_rect(740, 224, 112), "Volver", lambda: change_menu_display("main")),
]

def get_labels_sub():
    return [
        (FONT.render(get_dificulty_game(1), True, BLACK), (160, 260)),
        (FONT.render(get_dificulty_game(2), True, BLACK), (260, 260)),
        (FONT.render(get_dificulty_game(3), True, BLACK), (360, 260)),
    ]



buttons_choose_dificulty = [
    (center_rect(290, 224, 112), "Easy", None),

    (center_rect(440, 224, 112), "Medium", None),

    (center_rect(590, 224, 112), "Hard", None),

    (center_rect(740, 224, 112), "Volver", lambda: change_menu_display("main"))
]


            

running = True

aux_indice = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()

            if current_display == "submenu":
                for rect, text, action in buttons_sub:
                    if rect.collidepoint(pos):
                        if callable(action):
                            action()
                            recenter_buttons()
                        else:
                            tipo, indice = action
                            if tipo == "delete":
                                delete_game(indice)

                                recenter_buttons()
                            elif tipo == "load":
                                load_game(indice)

                            else:
                                change_menu_display("main")
                                recenter_buttons()

            elif current_display == "options":
                for rect, text, action in buttons_options:
                    if rect.collidepoint(pos):
                        action()
                        recenter_buttons()

            elif current_display == "dificulty":
                for rect, text, action in buttons_choose_dificulty:
                    if rect.collidepoint(pos):
                        if callable(action):
                            action()
                            recenter_buttons()
                        else:
                            estado_juego = estado_juego_inicial.copy()
                            estado_juego["dificultad"] = text  # "Easy", "Medium", "Hard"

                            save_game(aux_indice)
                            load_game(aux_indice)

            else:  # main menu
                for rect, text, action in buttons_main:
                    if rect.collidepoint(pos):
                        action()
                        recenter_buttons()


    # Dibujar botones del menú activo
    if current_display == "submenu":
        botones = buttons_sub
    elif current_display == "options":
        botones = buttons_options
    elif current_display == "dificulty":
        botones = buttons_choose_dificulty
    else:
        botones = buttons_main

    if current_display == "submenu":
        for label_surface, position in get_labels_sub():
            screen.blit(label_surface, position)

    screen.blit(fondo_menu, (0, 0))
    for rect, text, _ in botones:
        draw_button(screen, rect, text, FONT)
    pygame.display.flip()
    clock.tick(60)
