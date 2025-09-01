import os
import json

ruta_actual = os.path.dirname(__file__)
ruta_saves = os.path.join(ruta_actual, "saves")
os.makedirs(ruta_saves, exist_ok=True)

estado_juego = {}

niveles_dificultad = {
    "facil": {
        "agua": 5,
        "comida": {
            "bizcochitos don satur": 3,
            "medialunas": 3,
            "lata de duraznos": 2,
            "lata de atun": 2,
            "empanadas de carne": 2
        },
        "medicina": {"vendas": 1, "botiquin": 1, "remedios": [1, 1, 1]},
        "radio": 1
    },
    "normal": {
        "agua": 3,
        "comida": {
            "bizcochitos don satur": 2,
            "medialunas": 2,
            "lata de duraznos": 1,
            "lata de atun": 1,
            "empanadas de carne": 1
        },
        "medicina": {"vendas": 0, "botiquin": 0, "remedios": [0, 0, 0]},
        "radio": 1
    },
    "dificil": {
        "agua": 1,
        "comida": {
            "bizcochitos don satur": 1,
            "medialunas": 0,
            "lata de duraznos": 0,
            "lata de atun": 0,
            "empanadas de carne": 0
        },
        "medicina": {"vendas": 0, "botiquin": 0, "remedios": [0, 0, 0]},
        "radio": 0
    }
}

def guardar_partida(indice_partida: int, estado):
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")
    with open(partida_root, "w") as archivo:
        json.dump(estado, archivo, indent=4)

def crear_partida(indice_partida: int, dificultad: str):
    estado = {
        "dia": 1,
        "dificultad": dificultad,
        "objetos": [],  # Se llenará desde recolección
        "eventos": []
    }
    guardar_partida(indice_partida, estado)
    return estado

def load_game(indice_partida: int):
    partida_root = os.path.join(ruta_saves, f"partida{indice_partida}.json")
    if os.path.exists(partida_root):
        with open(partida_root, "r") as archivo:
            estado = json.load(archivo)
    else:
        estado = None
    return estado
