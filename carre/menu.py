import pygame
import sys
from juego import crear_partida, load_game, niveles_dificultad
import seconds_game
from recoleccion import fase_recoleccion

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, GRAY, rect)
    text_surface = font.render(text, True, BLACK)
    screen.blit(
        text_surface,
        (rect.x + (rect.width - text_surface.get_width()) // 2,
         rect.y + (rect.height - text_surface.get_height()) // 2)
    )

def elegir_dificultad():
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    FONT = pygame.font.SysFont("arial", 28)
    opciones = [
        (pygame.Rect(200, 150, 200, 50), "Fácil", "facil"),
        (pygame.Rect(200, 220, 200, 50), "Normal", "normal"),
        (pygame.Rect(200, 290, 200, 50), "Difícil", "dificil"),
    ]

    while True:
        screen.fill(WHITE)
        draw_button(screen, pygame.Rect(150, 80, 300, 50), "Elige dificultad", FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                for rect, _, diff in opciones:
                    if rect.collidepoint(pos):
                        return diff

        for rect, text, _ in opciones:
            draw_button(screen, rect, text, FONT)

        pygame.display.flip()
        clock.tick(60)

def main_menu(screen):
    pygame.font.init()
    FONT = pygame.font.SysFont("arial", 36)
    clock = pygame.time.Clock()
    submenu_active = False

    def start_game_menu():
        nonlocal submenu_active
        submenu_active = True

    def options():
        print("Opciones en construcción...")

    def exit_game():
        pygame.quit()
        sys.exit()

    def new_game():
        dificultad = elegir_dificultad()
        estado = crear_partida(0, dificultad)

        inventario_guardado, resultado = fase_recoleccion(niveles_dificultad[dificultad])
        if resultado == "perdiste":
            print("¡Perdiste! No llegaste al sótano.")
            return
        else:
            estado["objetos"] = inventario_guardado
            seconds_game.start_game(estado, 0)

    def load_existing_game():
        estado = load_game(0)
        if estado:
            seconds_game.start_game(estado, 0)
        else:
            new_game()

    def back_to_main():
        nonlocal submenu_active
        submenu_active = False

    buttons_main = [
        (pygame.Rect(200, 150, 200, 50), "Empezar", start_game_menu),
        (pygame.Rect(200, 220, 200, 50), "Opciones", options),
        (pygame.Rect(200, 290, 200, 50), "Salir", exit_game),
    ]

    buttons_sub = [
        (pygame.Rect(200, 150, 250, 50), "Nueva partida", new_game),
        (pygame.Rect(200, 220, 250, 50), "Cargar partida", load_existing_game),
        (pygame.Rect(200, 290, 250, 50), "Volver", back_to_main),
    ]

    while True:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                botones = buttons_sub if submenu_active else buttons_main
                for rect, _, action in botones:
                    if rect.collidepoint(pos):
                        action()

        botones = buttons_sub if submenu_active else buttons_main
        for rect, text, _ in botones:
            draw_button(screen, rect, text, FONT)

        pygame.display.flip()
        clock.tick(60)
