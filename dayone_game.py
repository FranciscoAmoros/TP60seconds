import pygame, random, os, datetime

BLACK = (0, 0, 0)

pygame.init()

estado_juego = {}

def main(estado, screen):
    global estado_juego
    estado_juego = estado
    done = False
    back_to_menu = False
    screen.fill(BLACK)
    pygame.display.flip()
    clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get():
            pass

        clock.tick(60)
        pygame.display.flip()

    
    return estado_juego, back_to_menu