import pygame, os, random, datetime
from time import sleep
import json
import game

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()


ruta_actual = os.path.dirname(__file__)
ruta_saves = os.path.join(ruta_actual, "saves")
os.makedirs(ruta_saves, exist_ok=True)


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
        game.start_game(estado_juego)
            

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    keys = pygame.key.get_pressed()