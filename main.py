import pygame, os
from time import sleep
import json
import game

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

pygame.init()
FONT = pygame.font.SysFont("arial", 28)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen.fill((50, 200, 255))
pygame.display.flip()
clock = pygame.time.Clock()


ruta_actual = os.path.dirname(__file__)
ruta_saves = os.path.join(ruta_actual, "saves")
os.makedirs(ruta_saves, exist_ok=True)

def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, GRAY, rect)
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
            "remedios": [0, 0, 0]
        }
    },
    "dia": 0
}

estado_juego = {}
indice_partida = 1

def load_game(indice_partida):
    global estado_juego
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    if os.path.exists(partida_root):
        with open(partida_root, "r") as archivo:
            estado_juego = json.load(archivo)
    else:
        estado_juego = estado_juego_inicial.copy()
        with open(partida_root, "w") as archivo:
            json.dump(estado_juego, archivo, indent=4)
    estado_juego = game.start_game(estado_juego, screen)
        
def save_game(indice_partida):
    global estado_juego
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")

    with open(partida_root, "w") as archivo:
        json.dump(estado_juego, archivo, indent=4)

def start_game_menu():
    global submenu_active
    submenu_active = True

def exit_game():
    pygame.quit()
    exit()


buttons_main = [
    (pygame.Rect(200, 150, 200, 50), "Empezar", start_game_menu),
    (pygame.Rect(200, 290, 200, 50), "Salir", exit_game),
]

buttons_sub = [
    (pygame.Rect(200, 150, 200, 50), "Game 1", 1),
    (pygame.Rect(200, 290, 200, 50), "Game 2", 2),
    (pygame.Rect(200, 430, 200, 50), "Game 3", 3),
]
            

running = True
submenu_active = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                botones = buttons_sub if submenu_active else buttons_main
                if botones == buttons_main:
                    for rect, _, action in botones:
                        if rect.collidepoint(pos):
                            action()
                else:
                    for rect, _, index in botones:
                        if rect.collidepoint(pos):
                            indice_partida = index
                            load_game(index)

        botones = buttons_sub if submenu_active else buttons_main
        for rect, text, _ in botones:
            draw_button(screen, rect, text, FONT)

       
    pygame.display.flip()
    clock.tick(60)