import pygame, os
from time import sleep
import json
import game

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
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


settings = {}
ruta_settings = os.path.join(ruta_actual, "settings")
os.makedirs(ruta_settings, exist_ok=True)

submenu_active = False
options_menu_active = False
dificulty_menu_active = False

def change_menu_display(menu_type):
    global submenu_active, options_menu_active, dificulty_menu_active
    submenu_active = (menu_type == "submenu")
    options_menu_active = (menu_type == "options")
    dificulty_menu_active = (menu_type == "dificulty")


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


pygame.init()
FONT = pygame.font.SysFont("arial", 28)
load_settings()
screen_width, screen_high = screen.get_size()
pygame.display.flip()
clock = pygame.time.Clock()


ruta_saves = os.path.join(ruta_actual, "saves")
os.makedirs(ruta_saves, exist_ok=True)

def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, GRAY, rect)
    if callable(text):
        text_surface = font.render(text(), True, BLACK)  # Ejecutar lambda si es callable
    else:
        text_surface = font.render(text, True, BLACK)
    
    screen.blit(
        text_surface,
        (rect.x + (rect.width - text_surface.get_width()) // 2,
         rect.y + (rect.height - text_surface.get_height()) // 2)
    )


estado_juego_inicial = {
    "objetos": {
        "comida": {
            "bizcochitos don satur": 0,
            "medialunas": 0,
            "lata de duraznos": 0,
            "lata de atun": 0,
            "empanadas de carne": 0
        },
        "agua": 0,
        "medicina": {
            "vendas": 0,
            "botiquin": 0,
            "jarabe": 0,
            "capsula": 0,
            "pastilla": 0
        }
    },
    "dia": 0,
    "dificultad": "Easy"
}

estado_juego = {}
indice_partida = 1

def delete_game(indice_partida):

    global estado_juego
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    if os.path.exists(partida_root):
        os.remove(partida_root)

    estado_juego = {}

def start_game():
    global estado_juego
    global screen
    estado_juego = game.start_game(estado_juego, screen)


def load_game(indice_partida, start_immediately=True):
    global screen
    global estado_juego
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    if os.path.exists(partida_root):
        with open(partida_root, "r") as archivo:
            estado_juego = json.load(archivo)
        if start_immediately:
            start_game()
    else:
        change_menu_display("dificulty")

def get_state_game(indice):
    partida_root = os.path.join(ruta_saves, f"partida{indice}.json")
    if os.path.exists(partida_root):
        return f"Game {indice}"
    else:
        return "New Game"
    
def get_dificulty_game(indice):
    partida_root = os.path.join(ruta_saves, f"partida{indice}.json")
    if os.path.exists(partida_root):
        try:
            with open(partida_root, "r") as archivo:
                estado = json.load(archivo)
            return estado.get("dificultad", "Desconocida")
        except Exception as e:
            print(f"[ERROR] No se pudo leer partida {indice}: {e}")
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
    return pygame.Rect((screen_width - w) // 2, y, w, h)


def recenter_buttons():
    global buttons_main, buttons_options, buttons_sub
    # Main menu
    buttons_main = [
        (center_rect(290, 200, 50), "Empezar", lambda: change_menu_display("submenu")),
        (center_rect(420, 200, 50), "Opciones", lambda: change_menu_display("options")),
        (center_rect(570, 200, 50), "Salir", lambda: exit_game()),
    ]

    # Options menu
    buttons_options = [
        (center_rect(290, 200, 50), settings["display_mode"], lambda: modify_settings(1)),
        (center_rect(420, 200, 50), f"resolution: {resolutions_available[settings['resolution_index']]}", lambda: modify_settings(2)),
        (center_rect(570, 200, 50), "Opcion3", lambda: print("opcion3")),
        (center_rect(720, 200, 50), "Volver", lambda: change_menu_display("main")),
    ]

    # Submenu
    buttons_sub = [
        (center_rect(290, 200, 50), lambda: get_state_game(1), ("load", 1)),
        (center_rect(290, 200, 50).move(220, 0).inflate(-150, 0), "X", ("delete", 1)),
        (center_rect(390, 200, 50), lambda: get_state_game(2), ("load", 2)),
        (center_rect(390, 200, 50).move(220, 0).inflate(-150, 0), "X", ("delete", 2)),
        (center_rect(490, 200, 50), lambda: get_state_game(3), ("load", 3)),
        (center_rect(490, 200, 50).move(220, 0).inflate(-150, 0), "X", ("delete", 3)),
        (center_rect(590, 200, 50), "Volver", lambda: change_menu_display("main")),
    ]


buttons_main = [
    (center_rect(290, 200, 50), "Empezar", lambda: change_menu_display("submenu")),
    (center_rect(420, 200, 50), "Opciones", lambda: change_menu_display("options")),
    (center_rect(570, 200, 50), "Salir", lambda: exit_game()),
]


buttons_options = [
    (center_rect(150, 200, 50), settings["display_mode"], lambda: modify_settings(1)),
    (center_rect(290, 200, 50), f"resolution: {resolutions_available[settings['resolution_index']]}", lambda: modify_settings(2)),
    (center_rect(420, 200, 50), "Opcion3", lambda: print("opcion3")),
    (center_rect(560, 200, 50), "Volver", lambda: change_menu_display("main")),
]

buttons_sub = [
    (center_rect(290, 200, 50), lambda: get_state_game(1), ("load", 1)),
    (center_rect(290, 200, 50).move(220, 0).inflate(-150, 0), "X", ("delete", 1)),
    (center_rect(390, 200, 50), lambda: get_state_game(2), ("load", 2)),
    (center_rect(390, 200, 50).move(220, 0).inflate(-150, 0), "X", ("delete", 2)),
    (center_rect(490, 200, 50), lambda: get_state_game(3), ("load", 3)),
    (center_rect(490, 200, 50).move(220, 0).inflate(-150, 0), "X", ("delete", 3)),
    (center_rect(590, 200, 50), "Volver", lambda: change_menu_display("main")),
]

def get_labels_sub():
    return [
        (FONT.render(get_dificulty_game(1), True, BLACK), (160, 260)),
        (FONT.render(get_dificulty_game(2), True, BLACK), (260, 260)),
        (FONT.render(get_dificulty_game(3), True, BLACK), (360, 260)),
    ]



buttons_choose_dificulty = [
    (center_rect(150, 200, 50), "Easy", ("create", 1)),

    (center_rect(250, 200, 50), "Medium", ("create", 2)),

    (center_rect(350, 200, 50), "Hard", ("create", 3)),

    (center_rect(450, 200, 50), "Volver", lambda: change_menu_display("main"))
]


            

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()

            if submenu_active:
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

            elif options_menu_active:
                for rect, text, action in buttons_options:
                    if rect.collidepoint(pos):
                        action()
                        recenter_buttons()

            elif dificulty_menu_active:
                for rect, text, action in buttons_choose_dificulty:
                    if rect.collidepoint(pos):
                        if callable(action):
                            action()
                            recenter_buttons()
                        else:
                            tipo, indice = action
                            if tipo == "create":
                                estado_juego = estado_juego_inicial.copy()
                                estado_juego["dificultad"] = text  # "Easy", "Medium", "Hard"
                                save_game(indice)
                                load_game(indice)

            else:  # main menu
                for rect, text, action in buttons_main:
                    if rect.collidepoint(pos):
                        action()
                        recenter_buttons()


    # Dibujar botones del menú activo
    if submenu_active:
        botones = buttons_sub
    elif options_menu_active:
        botones = buttons_options
    elif dificulty_menu_active:
        botones = buttons_choose_dificulty
    else:
        botones = buttons_main

    if submenu_active:
        for label_surface, position in get_labels_sub():
            screen.blit(label_surface, position)

    screen.fill(WHITE)
    for rect, text, _ in botones:
        draw_button(screen, rect, text, FONT)

    pygame.display.flip()
    clock.tick(60)
