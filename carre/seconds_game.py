import pygame
from juego import guardar_partida

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

estado_juego_global = {}

def draw_text(screen, text, x, y, font, color=BLACK):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, GRAY, rect)
    text_surface = font.render(text, True, BLACK)
    screen.blit(
        text_surface,
        (rect.x + (rect.width - text_surface.get_width()) // 2,
         rect.y + (rect.height - text_surface.get_height()) // 2)
    )

def start_game(estado, indice_partida: int):
    global estado_juego_global
    estado_juego_global = estado

    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 28)

    next_day_button = pygame.Rect(200, 400, 200, 50)

    corriendo = True
    fin_juego = False

    while corriendo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if next_day_button.collidepoint(event.pos) and not fin_juego:
                    avanzar_dia(indice_partida)

        screen.fill(WHITE)

        # Dibujar información del juego
        draw_text(screen, f"Día {estado_juego_global['dia']}", 50, 50, font)
        draw_text(screen, f"Inventario: {estado_juego_global['objetos']}", 50, 100, font)
        draw_text(screen, f"Eventos: {estado_juego_global['eventos']}", 50, 150, font)

        if estado_juego_global["dia"] > 5:  # Demo: 5 días
            draw_text(screen, "Fin del juego (demo)", 200, 300, font)
            fin_juego = True
        else:
            draw_button(screen, next_day_button, "Siguiente día", font)

        pygame.display.flip()
        clock.tick(60)

def avanzar_dia(indice_partida: int):
    estado_juego_global["dia"] += 1
    estado_juego_global["eventos"].append(f"Evento del día {estado_juego_global['dia']}")
    guardar_partida(indice_partida, estado_juego_global)
