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
    "display_mode": "fullscreen",
    "resolution_index": 2,
    "brightness": 100  # porcentaje (50-150)
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
    # Migración/normalización de brillo: aceptar antiguo rango [-100..100] como offset
    b = settings.get("brightness")
    if b is None:
        settings["brightness"] = 100
    else:
        try:
            if 50 <= b <= 150:
                pass
            elif -100 <= b <= 100:
                settings["brightness"] = max(50, min(150, 100 + int(b)))
            else:
                settings["brightness"] = 100
        except Exception:
            settings["brightness"] = 100
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
    # Si existen recursos/UI dependientes de resolución, actualizarlos
    try:
        if 'rescale_assets' in globals():
            rescale_assets()
        if 'recenter_buttons' in globals():
            recenter_buttons()
    except Exception:
        pass


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

fondo_menu_raw = pygame.image.load(os.path.join(ruta_actual, "fondomenu.jpg"))
fondo_menu = pygame.transform.scale(fondo_menu_raw, (screen_width, screen_high))
def rescale_assets():
    global fondo_menu
    try:
        fondo_menu = pygame.transform.scale(fondo_menu_raw, (screen_width, screen_high))
    except Exception:
        pass


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
    return pygame.Rect((screen_width - w) // 2, y, w, h)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def change_brightness(delta):
    global settings
    # Ajuste en pasos del 25% con límites 50%-150%
    current = settings.get("brightness", 100)
    settings["brightness"] = clamp(current + delta, 50, 150)
    save_settings()
    load_settings()
    try:
        rescale_assets()
        recenter_buttons()
    except Exception:
        pass
    try:
        rescale_assets()
    except Exception:
        pass

def recenter_buttons():
    global buttons_main, buttons_options, buttons_sub, buttons_choose_dificulty

    btn_w, btn_h = botones_images_escalados["blue"].get_size()
    small_w, small_h = botones_images_escalados["x"].get_size()

    gap = max(16, int(screen_high * 0.04))

    # Main menu
    n_main = 3
    total_h_main = n_main * btn_h + (n_main - 1) * gap
    start_y_main = (screen_high - total_h_main) // 2
    buttons_main = [
        (center_rect(start_y_main + (btn_h + gap) * 0, btn_w, btn_h), "Empezar", lambda: change_menu_display("submenu")),
        (center_rect(start_y_main + (btn_h + gap) * 1, btn_w, btn_h), "Opciones", lambda: change_menu_display("options")),
        (center_rect(start_y_main + (btn_h + gap) * 2, btn_w, btn_h), "Salir", lambda: exit_game()),
    ]

    # Opciones con brillo
    opt_text_res = f"resolution: {resolutions_available[settings['resolution_index']]}"
    opt_text_mode = settings.get("display_mode", "windowed")
    opt_text_brightness = f"Brillo: {settings.get('brightness', 100)}%"

    n_opt = 6
    total_h_opt = n_opt * btn_h + (n_opt - 1) * gap
    start_y_opt = (screen_high - total_h_opt) // 2
    buttons_options = [
        (center_rect(start_y_opt + (btn_h + gap) * 0, btn_w, btn_h), opt_text_mode, lambda: modify_settings(1)),
        (center_rect(start_y_opt + (btn_h + gap) * 1, btn_w, btn_h), opt_text_res, lambda: modify_settings(2)),
        (center_rect(start_y_opt + (btn_h + gap) * 2, btn_w, btn_h), "Brillo -", lambda: change_brightness(-25)),
        (center_rect(start_y_opt + (btn_h + gap) * 3, btn_w, btn_h), "Brillo +", lambda: change_brightness(+25)),
        (center_rect(start_y_opt + (btn_h + gap) * 4, btn_w, btn_h), opt_text_brightness, lambda: None),
        (center_rect(start_y_opt + (btn_h + gap) * 5, btn_w, btn_h), "Volver", lambda: change_menu_display("main")),
    ]

    # Submenú partidas
    n_sub_rows = 3
    total_h_sub = n_sub_rows * btn_h + (n_sub_rows - 1) * gap
    start_y_sub = (screen_high - total_h_sub) // 2
    buttons_sub = []
    for i in range(3):
        y = start_y_sub + (btn_h + gap) * i
        load_btn = (center_rect(y, btn_w, btn_h), (lambda idx=i+1: (lambda: get_state_game(idx)))(), ("load", i+1))
        load_rect = load_btn[0]
        x_rect = pygame.Rect(load_rect.x + btn_w + 20, load_rect.y + (btn_h - small_h)//2, small_w, small_h)
        x_btn = (x_rect, "X", ("delete", i+1))
        buttons_sub.extend([load_btn, x_btn])
    buttons_sub.append((center_rect(start_y_sub + (btn_h + gap) * 3, btn_w, btn_h), "Volver", lambda: change_menu_display("main")))

    # Elegir dificultad
    n_diff = 4
    total_h_diff = n_diff * btn_h + (n_diff - 1) * gap
    start_y_diff = (screen_high - total_h_diff) // 2
    buttons_choose_dificulty = [
        (center_rect(start_y_diff + (btn_h + gap) * 0, btn_w, btn_h), "Easy", ("create", 1)),
        (center_rect(start_y_diff + (btn_h + gap) * 1, btn_w, btn_h), "Medium", ("create", 2)),
        (center_rect(start_y_diff + (btn_h + gap) * 2, btn_w, btn_h), "Hard", ("create", 3)),
        (center_rect(start_y_diff + (btn_h + gap) * 3, btn_w, btn_h), "Volver", lambda: change_menu_display("main"))
    ]


def get_labels_sub():
    labels = []
    try:
        slot_rects = [buttons_sub[0][0], buttons_sub[2][0], buttons_sub[4][0]]
        for i, rect in enumerate(slot_rects, start=1):
            surf = FONT.render(get_dificulty_game(i), True, BLACK)
            pos = (rect.centerx - surf.get_width() // 2, rect.bottom + 10)
            labels.append((surf, pos))
    except Exception:
        pass
    return labels


# Inicializar botones centrados
recenter_buttons()


            

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
                            estado_juego["dificultad"] = text  

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

    screen.blit(fondo_menu, (0, 0))
    if current_display == "submenu":
        for label_surface, position in get_labels_sub():
            screen.blit(label_surface, position)
    for rect, text, _ in botones:
        draw_button(screen, rect, text, FONT)
    # Overlay de brillo basado en porcentaje (50-150)
    p = settings.get("brightness", 100)
    diff = p - 100
    if diff != 0:
        overlay = pygame.Surface((screen_width, screen_high))
        if diff < 0:
            overlay.fill((0, 0, 0))
            overlay.set_alpha(min(255, int(-diff * 2.55)))  # 50% -> ~127
        else:
            overlay.fill((255, 255, 255))
            overlay.set_alpha(min(255, int(diff * 2.55)))   # 150% -> ~127
        screen.blit(overlay, (0, 0))
    pygame.display.flip()
    clock.tick(60)
