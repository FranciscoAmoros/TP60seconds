import pygame


pygame.init()
pantalla = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Movimiento en 8 direcciones")

NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)

jugador = pygame.Rect(300, 220, 40, 40)
velocidad = 5

reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    teclas = pygame.key.get_pressed()

    dx, dy = 0, 0 

    if teclas[pygame.K_w]: 
        dy = -velocidad
    if teclas[pygame.K_s]: 
        dy = velocidad
    if teclas[pygame.K_a]: 
        dx = -velocidad
    if teclas[pygame.K_d]: 
        dx = velocidad

    jugador.x += dx
    jugador.y += dy

    if jugador.left < 0: jugador.left = 0
    if jugador.right > 640: jugador.right = 640
    if jugador.top < 0: jugador.top = 0
    if jugador.bottom > 480: jugador.bottom = 480

    pantalla.fill(NEGRO)
    pygame.draw.rect(pantalla, ROJO, jugador)
    pygame.display.flip()

    reloj.tick(60)

pygame.quit()
