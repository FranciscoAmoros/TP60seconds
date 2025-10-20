import pygame, random

estado_juego = {}

def main(estado, screen):
    global estado_juego
    estado_juego = estado
    
    done = False

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            screen.fill((100, 100, 100))
            pygame.display.flip()


    return estado_juego