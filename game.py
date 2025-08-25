import dayone_game
import seconds_game

estado_juego = {}
etapa_recoleccion = True

def start_game(estado):
    global estado_juego, etapa_recoleccion
    estado_juego = estado

    if not estado_juego["dia"] == 0:
        etapa_recoleccion = False

    if etapa_recoleccion:
        estado_juego = dayone_game.main(estado_juego)
    else:
        estado_juego = seconds_game.main(estado_juego)
    