import dayone_game
import seconds_game

estado_juego = {}
etapa_recoleccion = True

def start_game(estado, screen):
    global estado_juego, etapa_recoleccion
    estado_juego = estado

    if not estado_juego["dia"] == 0:
        etapa_recoleccion = False

    if etapa_recoleccion:
        estado_juego, back_to_menu = dayone_game.main(estado_juego, screen)
        if not back_to_menu:
            estado_juego = seconds_game.main(estado_juego, screen)
        estado_juego["dia"] = 1
    else:
        estado_juego = seconds_game.main(estado_juego, screen)

    return estado_juego
    