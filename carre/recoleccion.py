import pygame
import random
import time

ANCHO, ALTO = 640, 640
FILAS, COLUMNAS = 4, 4
TAM_HAB = ANCHO // COLUMNAS

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (100, 100, 100)
AZUL = (0, 0, 255)
VERDE = (0, 200, 0)
ROJO = (200, 0, 0)
AMARILLO = (255, 255, 0)

def crear_casa(filas, columnas):
    return [[{"objetos": [], "visitada": False} for _ in range(columnas)] for _ in range(filas)]

def repartir_objetos(casa, objetos):
    lista_obj = []

    for _ in range(objetos.get("agua", 0)):
        lista_obj.append("agua")

    for nombre, cantidad in objetos.get("comida", {}).items():
        lista_obj.extend([nombre] * cantidad)

    for nombre, cantidad in objetos.get("medicina", {}).items():
        if isinstance(cantidad, list):
            lista_obj.extend([nombre] * len(cantidad))
        else:
            lista_obj.extend([nombre] * cantidad)

    for _ in range(objetos.get("radio", 0)):
        lista_obj.append("radio")

    for obj in lista_obj:
        f = random.randint(0, FILAS - 1)
        c = random.randint(0, COLUMNAS - 1)
        casa[f][c]["objetos"].append(obj)

def fase_recoleccion(objetos):
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Fase de Recolección")

    fuente = pygame.font.SysFont("Arial", 20)

    casa = crear_casa(FILAS, COLUMNAS)
    repartir_objetos(casa, objetos)

    sotano = (3, 3)
    jugador = pygame.Rect(10, 10, 40, 40)
    velocidad = 5
    inventario = []
    inventario_guardado = []

    tiempo_max = 60
    tiempo_inicio = time.time()

    reloj = pygame.time.Clock()
    ejecutando = True
    game_over = False

    while ejecutando:
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - tiempo_inicio
        tiempo_restante = max(0, tiempo_max - int(tiempo_transcurrido))

        if tiempo_restante == 0:
            if (jugador.y // TAM_HAB, jugador.x // TAM_HAB) == sotano:
                inventario_guardado.extend(inventario)
                inventario = []
            else:
                game_over = True
            ejecutando = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                game_over = True

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w]: jugador.y -= velocidad
        if teclas[pygame.K_s]: jugador.y += velocidad
        if teclas[pygame.K_a]: jugador.x -= velocidad
        if teclas[pygame.K_d]: jugador.x += velocidad

        jugador.x = max(0, min(jugador.x, ANCHO - jugador.width))
        jugador.y = max(0, min(jugador.y, ALTO - jugador.height))

        fila = jugador.y // TAM_HAB
        col = jugador.x // TAM_HAB
        casa[fila][col]["visitada"] = True

        nuevos_objetos = []
        for i, obj in enumerate(casa[fila][col]["objetos"]):
            obj_rect = pygame.Rect(col * TAM_HAB + 20 + i * 25, fila * TAM_HAB + 20, 20, 20)
            if jugador.colliderect(obj_rect):
                if len(inventario) < 5:
                    inventario.append(obj)
                else:
                    nuevos_objetos.append(obj)
            else:
                nuevos_objetos.append(obj)
        casa[fila][col]["objetos"] = nuevos_objetos

        if (fila, col) == sotano and inventario:
            inventario_guardado.extend(inventario)
            inventario = []

        pantalla.fill(NEGRO)
        for f in range(FILAS):
            for c in range(COLUMNAS):
                x, y = c * TAM_HAB, f * TAM_HAB
                rect = pygame.Rect(x, y, TAM_HAB, TAM_HAB)
                if casa[f][c]["visitada"]:
                    pygame.draw.rect(pantalla, GRIS, rect, 0)
                else:
                    pygame.draw.rect(pantalla, NEGRO, rect, 0)
                pygame.draw.rect(pantalla, BLANCO, rect, 2)
                if casa[f][c]["visitada"]:
                    for i, obj in enumerate(casa[f][c]["objetos"]):
                        obj_rect = pygame.Rect(x + 20 + i * 25, y + 20, 20, 20)
                        pygame.draw.rect(pantalla, ROJO, obj_rect)

        x_s, y_s = sotano[1] * TAM_HAB, sotano[0] * TAM_HAB
        pygame.draw.rect(pantalla, AMARILLO, (x_s + 5, y_s + 5, TAM_HAB - 10, TAM_HAB - 10), 3)

        pygame.draw.rect(pantalla, AZUL, jugador)

        texto_inv = fuente.render(f"Inventario: {inventario}", True, VERDE)
        texto_guardado = fuente.render(f"Sótano: {inventario_guardado}", True, VERDE)
        texto_tiempo = fuente.render(f"Tiempo: {tiempo_restante}s", True, VERDE)
        pantalla.blit(texto_inv, (10, ALTO - 70))
        pantalla.blit(texto_guardado, (10, ALTO - 50))
        pantalla.blit(texto_tiempo, (10, ALTO - 30))

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()

    if game_over:
        return [], "perdiste"
    else:
        return inventario_guardado, "ganaste"
