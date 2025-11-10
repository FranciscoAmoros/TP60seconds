import json
import random
import pygame
import os
from typing import Dict, List, Tuple
estado_juego: Dict = {}
def total_comida(estado: Dict) -> int:
    try:
        return sum(int(v) for v in estado["objetos"]["comida"].values())
    except Exception:
        return 0
def consumir_comida(estado: Dict, cantidad: int) -> int:
    faltantes = 0
    if cantidad <= 0:
        return 0
    if "objetos" not in estado or "comida" not in estado["objetos"]:
        return cantidad
    tipos = list(estado["objetos"]["comida"].keys())
    for _ in range(cantidad):
        disponibles = [t for t in tipos if estado["objetos"]["comida"].get(t, 0) > 0]
        if not disponibles:
            faltantes += 1
            continue
        t = random.choice(disponibles)
        estado["objetos"]["comida"][t] -= 1
    return faltantes
def agregar_comida(estado: Dict, cantidad: int) -> None:
    if cantidad <= 0:
        return
    tipos = list(estado.get("objetos", {}).get("comida", {}).keys())
    if not tipos:
        return
    for _ in range(cantidad):
        t = random.choice(tipos)
        estado["objetos"]["comida"][t] = estado["objetos"]["comida"].get(t, 0) + 1
def consumir_agua(estado: Dict, cantidad: int) -> int:
    faltantes = 0
    agua = int(estado.get("objetos", {}).get("agua", 0))
    if agua >= cantidad:
        estado["objetos"]["agua"] = agua - cantidad
        return 0
    else:
        estado["objetos"]["agua"] = 0
        faltantes = cantidad - agua
        return faltantes
def agregar_agua(estado: Dict, cantidad: int) -> None:
    if cantidad <= 0:
        return
    estado.setdefault("objetos", {})
    estado["objetos"]["agua"] = int(estado["objetos"].get("agua", 0)) + cantidad

def total_medicina(estado: Dict) -> Dict[str, int]:
    try:
        return {k: int(v) for k, v in estado["objetos"]["medicina"].items()}
    except Exception:
        return {}

def asegurar_min_medicina(estado: Dict, minimos: Dict[str, int] | None = None) -> None:
    if minimos is None:
        minimos = {"botiquin": 2, "vendas": 4, "pastilla": 4}
    estado.setdefault("objetos", {})
    estado["objetos"].setdefault("medicina", {})
    for k, v in minimos.items():
        actual = int(estado["objetos"]["medicina"].get(k, 0))
        if actual < v:
            estado["objetos"]["medicina"][k] = v

def usar_medicina(estado: Dict, tipo: str, nombre: str) -> str:
    meds = total_medicina(estado)
    if meds.get(tipo, 0) <= 0:
        return "No hay esa medicina."
    if not nombre or nombre not in estado.get("personajes", {}):
        return "Personaje invalido."
    pj = estado["personajes"][nombre]
    if not pj.get("vivo"):
        return f"{nombre} no esta con vida."

    efecto = ""
    if tipo == "vendas":
        pj["herido"] = False
        pj["salud"] = min(100, pj["salud"] + 15)
        efecto = "Vendado y estabilizado."
    elif tipo == "botiquin":
        pj["herido"] = False
        pj["enfermo"] = False
        pj["salud"] = min(100, pj["salud"] + 30)
        efecto = "Tratamiento completo aplicado."
    elif tipo == "jarabe":
        pj["enfermo"] = False
        pj["salud"] = min(100, pj["salud"] + 10)
        efecto = "Alivia enfermedad."
    elif tipo == "pastilla":
        pj["enfermo"] = False
        pj["salud"] = min(100, pj["salud"] + 5)
        efecto = "Cura enfermedad y +5 de vida."
    elif tipo == "capsula":
        pj["salud"] = min(100, pj["salud"] + 10)
        efecto = "Recupera algo de salud."
    else:
        return "Medicina desconocida."

    estado["objetos"]["medicina"][tipo] = meds[tipo] - 1
    return f"{nombre}: {efecto}"
def init_personajes_si_faltan(estado: Dict) -> None:
    if "personajes" in estado:
        return
    estado["personajes"] = {
        "Ted": {"vivo": True, "salud": 100, "moral": 100, "herido": False, "enfermo": False, "desaparece_hasta": 0, "comida_bar": 5, "agua_bar": 5},
        "Dolores": {"vivo": True, "salud": 100, "moral": 100, "herido": False, "enfermo": False, "desaparece_hasta": 0, "comida_bar": 5, "agua_bar": 5},
        "Timmy": {"vivo": True, "salud": 100, "moral": 100, "herido": False, "enfermo": False, "desaparece_hasta": 0, "comida_bar": 5, "agua_bar": 5},
        "Mary Jane": {"vivo": True, "salud": 100, "moral": 100, "herido": False, "enfermo": False, "desaparece_hasta": 0, "comida_bar": 5, "agua_bar": 5},
    }


def normalizar_barras_iniciales(estado: Dict) -> None:
    """Asegura que cada personaje tenga barras llenas (5) si no existen."""
    if "personajes" not in estado:
        return
    for pj in estado["personajes"].values():
        if "comida_bar" not in pj:
            pj["comida_bar"] = 5
        if "agua_bar" not in pj:
            pj["agua_bar"] = 5
def vivos_presentes(estado: Dict) -> List[str]:
    return [n for n, p in estado.get("personajes", {}).items() if p.get("vivo")]
def cargar_eventos(ruta: str = "eventos.json") -> Dict:
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
def elegir_evento(eventos: Dict, estado: Dict) -> Tuple[str, str, str]:
    if not eventos:
        return ("ninguno", "nada", "")
    dia = int(estado.get("dia", 1))
    candidatos = []
    for eid, data in eventos.items():
        dia_min = int(data.get("dia_min", 1))
        if dia < dia_min:
            continue
        candidatos.append(eid)
    if not candidatos:
        return ("ninguno", "nada", "")
    evento_id = random.choice(candidatos)
    data = eventos[evento_id]
    res = data.get("resultados", {})
    if not res:
        return (evento_id, "nada", "")
    opciones = list(res.keys())
    pesos = [float(res[k]) for k in opciones]
    total = sum(pesos)
    if total <= 0:
        return (evento_id, random.choice(opciones), "")
    pesos = [p / total for p in pesos]
    resultado = random.choices(opciones, weights=pesos, k=1)[0]
    # Si el evento menciona personaje, elegimos uno válido
    personaje_cond = str(data.get("personaje", "Todos"))
    elegido = ""
    if personaje_cond in ("Ted", "Dolores", "Timmy", "Mary Jane"):
        if estado["personajes"].get(personaje_cond, {}).get("vivo"):
            elegido = personaje_cond
    elif personaje_cond.startswith("Todos"):
        vivos = vivos_presentes(estado)
        elegido = random.choice(vivos) if vivos else ""
    else:
        # Por defecto, cualquiera vivo
        vivos = vivos_presentes(estado)
        elegido = random.choice(vivos) if vivos else ""
    return (evento_id, resultado, elegido)
def aplicar_resultado(estado: Dict, evento: str, resultado: str, personaje: str) -> str:
    """Aplica efectos al estado y devuelve una descripción breve."""
    desc = []
    def baja_salud(nombre: str, v: int):
        if not nombre:
            return
        pj = estado["personajes"][nombre]
        pj["salud"] = max(0, pj["salud"] - v)
        if pj["salud"] == 0:
            pj["vivo"] = False
    def sube_salud(nombre: str, v: int):
        if not nombre:
            return
        pj = estado["personajes"][nombre]
        pj["salud"] = min(100, pj["salud"] + v)
    # Mapeo simple de resultados a efectos
    if resultado in ("recursos", "explora_recursos", "trae_recursos"):
        comida = random.randint(1, 3)
        agua = random.randint(1, 2)
        agregar_comida(estado, comida)
        agregar_agua(estado, agua)
        # Medicina al explorar
        estado.setdefault("objetos", {})
        estado["objetos"].setdefault("medicina", {})
        meds_text = []
        v_add = random.randint(0, 2)
        p_add = random.randint(0, 2)
        b_add = 1 if random.random() < 0.25 else 0
        if v_add:
            estado["objetos"]["medicina"]["vendas"] = int(estado["objetos"]["medicina"].get("vendas", 0)) + v_add
            meds_text.append(f"vendas x{v_add}")
        if p_add:
            estado["objetos"]["medicina"]["pastilla"] = int(estado["objetos"]["medicina"].get("pastilla", 0)) + p_add
            meds_text.append(f"pastilla x{p_add}")
        if b_add:
            estado["objetos"]["medicina"]["botiquin"] = int(estado["objetos"]["medicina"].get("botiquin", 0)) + b_add
            meds_text.append(f"botiquin x{b_add}")
        extra = (" y medicinas: " + ", ".join(meds_text)) if meds_text else ""
        desc.append(f"Hallaron comida x{comida} y agua x{agua}{extra}.")
    elif resultado in ("radiacion_enfermedad",):
        if personaje:
            estado["personajes"][personaje]["enfermo"] = True
            baja_salud(personaje, 10)
            desc.append(f"{personaje} enfermó por radiación.")
    elif resultado in (
        "ataque",
        "daño_personajes",
        "da��o_personajes",
        "herido",
        "accidente_leve",
        "daño",
        "da��o",
    ):
        if personaje:
            estado["personajes"][personaje]["herido"] = True
            baja_salud(personaje, 15)
            desc.append(f"{personaje} resultó herido.")
        # Pérdida de recursos ligera
        perd = random.randint(0, 2)
        falt = consumir_comida(estado, perd)
        perd_agua = random.randint(0, 2)
        consumir_agua(estado, perd_agua)
        if perd or perd_agua:
            desc.append("Se perdieron algunos recursos en el caos.")
    elif resultado in ("pierde_recursos", "negativo"):
        perd = random.randint(1, 3)
        falt = consumir_comida(estado, perd)
        perd_agua = random.randint(1, 3)
        consumir_agua(estado, perd_agua)
        desc.append("Parte de los suministros desapareció.")
    elif resultado in ("fallo_ataque", "defensa_aliada", "nada", "sobrevive"):
        desc.append("No ocurrió nada grave.")
    elif resultado in ("pierde_salud_moral", "pierde_moral"):
        if personaje:
            baja_salud(personaje, 10)
            desc.append(f"{personaje} se siente peor hoy.")
    elif resultado in ("muerte",):
        if personaje:
            estado["personajes"][personaje]["salud"] = 0
            estado["personajes"][personaje]["vivo"] = False
            desc.append(f"{personaje} no sobrevivió.")
    elif resultado in ("desaparece", "desaparece_temporal"):
        if personaje:
            dias = random.randint(2, 5)
            estado["personajes"][personaje]["desaparece_hasta"] = int(estado.get("dia", 1)) + dias
            desc.append(f"{personaje} desaparece por {dias} días.")
    elif resultado in ("resistente_fuerza",):
        if personaje:
            sube_salud(personaje, 10)
            desc.append(f"{personaje} parece más resistente.")
    elif resultado in ("rescate_exitoso", "rescate_parcial", "rescate_falla"):
        # Marcamos una bandera simple
        estado.setdefault("meta_rescate", {})
        estado["meta_rescate"][resultado] = estado["meta_rescate"].get(resultado, 0) + 1
        desc.append("Se escuchan señales en la radio…")
    else:
        desc.append("El día pasó sin novedades destacables.")
    return " ".join(desc)

def enviar_exploracion(estado: Dict, nombre: str, dias: int) -> str:
    if nombre not in estado.get("personajes", {}):
        return "Personaje invalido."
    pj = estado["personajes"][nombre]
    if not pj.get("vivo"):
        return f"{nombre} no puede salir."
    if int(estado.get("dia", 1)) <= pj.get("desaparece_hasta", 0):
        return f"{nombre} ya esta fuera."
    pj["desaparece_hasta"] = int(estado.get("dia", 1)) + dias
    pj["explorando"] = True
    pj["vuelve_dia"] = int(estado.get("dia", 1)) + dias
    return f"{nombre} sale a explorar por {dias} dias."

def resolver_vueltas_de_exploracion(estado: Dict, eventos: Dict) -> List[str]:
    mensajes: List[str] = []
    hoy = int(estado.get("dia", 1))
    for nombre, pj in estado.get("personajes", {}).items():
        if pj.get("explorando") and pj.get("vuelve_dia") == hoy:
            if nombre == "Timmy" and "timmy_explora" in eventos:
                eid = "timmy_explora"
            elif nombre == "Ted" and "ted_explora" in eventos:
                eid = "ted_explora"
            else:
                eid = "exploracion" if "exploracion" in eventos else None
            if eid:
                data = eventos[eid]
                res = data.get("resultados", {})
                if res:
                    opciones = list(res.keys())
                    pesos = [float(res[k]) for k in opciones]
                    tot = sum(pesos)
                    pesos = [p / tot for p in pesos] if tot > 0 else None
                    r = random.choices(opciones, weights=pesos, k=1)[0]
                    if r in ("desaparece", "desaparece_temporal"):
                        r = "nada"
                    m = aplicar_resultado(estado, eid, r, nombre)
                    mensajes.append(f"{nombre} regresa: {r}. {m}")
            pj["explorando"] = False
            pj["vuelve_dia"] = 0
            pj["desaparece_hasta"] = 0
    return mensajes


def pasar_dia_manual(estado: Dict, eventos: Dict) -> str:
    # Avanzar día manual con raciones por personaje
    estado["dia"] = int(estado.get("dia", 1)) + 1

    vivos = [n for n, p in estado["personajes"].items() if p.get("vivo")]
    presentes = [n for n in vivos if int(estado.get("dia", 1)) > estado["personajes"][n].get("desaparece_hasta", 0)]

    texto_consumo: List[str] = []
    alguien_con_hambre_o_sed = False
    for n in presentes:
        pj = estado["personajes"][n]
        penal = 0
        if int(pj.get("comida_bar", 0)) <= 0:
            penal += 5
            alguien_con_hambre_o_sed = True
        if int(pj.get("agua_bar", 0)) <= 0:
            penal += 5
            alguien_con_hambre_o_sed = True
        if penal:
            pj["salud"] = max(0, pj.get("salud", 0) - penal)
            if pj["salud"] == 0:
                pj["vivo"] = False

    if alguien_con_hambre_o_sed:
        texto_consumo.append("Alguien pasó hambre o sed hoy.")

    # Regresos de expedición el día actual
    eventos_regreso = resolver_vueltas_de_exploracion(estado, eventos)

    # Elegir y resolver evento del día
    evento_id, resultado_id, personaje = elegir_evento(eventos, estado)
    # Ajustar frecuencia de eventos segun dia
    mod_resultado = resultado_id
    dia_act = int(estado.get("dia", 1))
    if resultado_id == "muerte" and dia_act < 50:
        mod_resultado = "herido"
    if resultado_id in ("pierde_salud_moral", "pierde_moral") and dia_act < 25:
        mod_resultado = "nada"
    if resultado_id in ("desaparece", "desaparece_temporal"):
        mod_resultado = "nada"
    texto_evento = aplicar_resultado(estado, evento_id, mod_resultado, personaje)

    # Decaimiento natural al final del día (baja 1 sin ir por debajo de 0)
    for n in estado.get("personajes", {}).keys():
        pj = estado["personajes"][n]
        pj["comida_bar"] = max(0, int(pj.get("comida_bar", 0)) - 1)
        pj["agua_bar"] = max(0, int(pj.get("agua_bar", 0)) - 1)

    texto = [f"Día {estado['dia']}:", *texto_consumo]
    texto.extend(eventos_regreso)
    if evento_id != "ninguno":
        texto.append(f"Evento: {evento_id} → {resultado_id}.")
    if texto_evento:
        texto.append(texto_evento)
    return "\n".join([t for t in texto if t])


def dar_comida(estado: Dict, nombre: str) -> str:
    if nombre not in estado.get("personajes", {}):
        return "Personaje inválido."
    pj = estado["personajes"][nombre]
    if not pj.get("vivo"):
        return f"{nombre} no está con vida."
    if int(estado.get("dia", 1)) <= pj.get("desaparece_hasta", 0):
        return f"{nombre} está ausente."
    if int(pj.get("comida_bar", 0)) >= 5:
        return f"{nombre} ya está saciado."
    falt = consumir_comida(estado, 1)
    if falt:
        return "No hay comida suficiente."
    pj["comida_bar"] = int(pj.get("comida_bar", 0)) + 1
    return f"Le diste comida a {nombre}."


def dar_agua(estado: Dict, nombre: str) -> str:
    if nombre not in estado.get("personajes", {}):
        return "Personaje inválido."
    pj = estado["personajes"][nombre]
    if not pj.get("vivo"):
        return f"{nombre} no está con vida."
    if int(estado.get("dia", 1)) <= pj.get("desaparece_hasta", 0):
        return f"{nombre} está ausente."
    if int(pj.get("agua_bar", 0)) >= 5:
        return f"{nombre} ya está hidratado."
    falt = consumir_agua(estado, 1)
    if falt:
        return "No hay agua suficiente."
    pj["agua_bar"] = int(pj.get("agua_bar", 0)) + 1
    return f"Le diste agua a {nombre}."
def pasar_dia(estado: Dict, eventos: Dict) -> str:
    # Avanzar día
    estado["dia"] = int(estado.get("dia", 1)) + 1
    # Personas presentes (no desaparecidas)
    vivos = [n for n, p in estado["personajes"].items() if p["vivo"]]
    presentes = [n for n in vivos if int(estado.get("dia", 1)) > estado["personajes"][n]["desaparece_hasta"]]
    # Consumo diario (1 agua + 1 comida por presente)
    falt_agua = consumir_agua(estado, len(presentes))
    falt_comida = consumir_comida(estado, len(presentes))
    texto_consumo = []
    if falt_agua or falt_comida:
        texto_consumo.append("Faltaron raciones: hambre/sed afectan a la familia.")
        for n in presentes:
            pj = estado["personajes"][n]
            pj["salud"] = max(0, pj["salud"] - 5)
            if pj["salud"] == 0:
                pj["vivo"] = False
    # Elegir y resolver evento
    evento_id, resultado_id, personaje = elegir_evento(eventos, estado)
    texto_evento = aplicar_resultado(estado, evento_id, resultado_id, personaje)
    # Texto final del día
    texto = [f"Día {estado['dia']}:", *texto_consumo]
    if evento_id != "ninguno":
        texto.append(f"Evento: {evento_id} → {resultado_id}.")
    if texto_evento:
        texto.append(texto_evento)
    return "\n".join([t for t in texto if t])
def _draw_book_panel(screen: pygame.Surface, estado: Dict, fuente: pygame.font.Font, comida_icon: pygame.Surface, agua_icon: pygame.Surface, seleccionado: str | None):
    # Panel (libro) en esquina inferior derecha
    sw, sh = screen.get_size()
    panel_w, panel_h = 380, 320
    x = sw - panel_w - 20
    y = sh - panel_h - 20

    # Fondo y borde del "libro"
    bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    bg.fill((210, 190, 160, 240))
    screen.blit(bg, (x, y))
    pygame.draw.rect(screen, (80, 60, 40), (x, y, panel_w, panel_h), 3)

    # Título opcional
    titulo = fuente.render("Registro", True, (50, 40, 30))
    screen.blit(titulo, (x + 12, y + 8))

    # Listado de personajes
    fila_y = y + 40
    icon_size = 18
    gap = 4
    face = pygame.Surface((36, 36))
    face.fill((120, 120, 120))

    face_rects = {}
    comida_btn = None
    agua_btn = None
    meds_btns = {}

    for nombre, pj in estado.get("personajes", {}).items():
        # Cara (placeholder cuadrado) y borde si seleccionado
        rect_face = pygame.Rect(x + 12, fila_y, face.get_width(), face.get_height())
        screen.blit(face, rect_face)
        if nombre == seleccionado:
            pygame.draw.rect(screen, (20, 120, 220), rect_face, 3)
        face_rects[nombre] = rect_face

        # Nombre
        nombre_txt = fuente.render(nombre, True, (30, 30, 30))
        screen.blit(nombre_txt, (x + 12 + 44, fila_y))

        # Barras como filas de iconos (comida arriba, agua abajo) en base a contadores del PJ
        llenos_comida = max(0, min(5, int(pj.get("comida_bar", 0))))
        llenos_agua = max(0, min(5, int(pj.get("agua_bar", 0))))

        # Fila comida (latas)
        fila1_y = fila_y + 18
        for i in range(llenos_comida):
            screen.blit(comida_icon, (x + 12 + 44 + i * (icon_size + gap), fila1_y))

        # Fila agua (botellas)
        fila2_y = fila1_y + icon_size + 2
        for i in range(llenos_agua):
            screen.blit(agua_icon, (x + 12 + 44 + i * (icon_size + gap), fila2_y))

        # Si este es el seleccionado, dibujar botones de acción
        if nombre == seleccionado:
            # Botón dar comida
            comida_btn = pygame.Rect(x + panel_w - 100, fila_y + 2, 32, 32)
            pygame.draw.rect(screen, (230, 230, 230), comida_btn)
            pygame.draw.rect(screen, (80, 80, 80), comida_btn, 2)
            screen.blit(pygame.transform.smoothscale(comida_icon, (28, 28)), (comida_btn.x + 2, comida_btn.y + 2))

            # Botón dar agua
            agua_btn = pygame.Rect(x + panel_w - 60, fila_y + 2, 32, 32)
            pygame.draw.rect(screen, (230, 230, 230), agua_btn)
            pygame.draw.rect(screen, (80, 80, 80), agua_btn, 2)
            screen.blit(pygame.transform.smoothscale(agua_icon, (28, 28)), (agua_btn.x + 2, agua_btn.y + 2))

        # Ajuste de altura de fila para que entren controles
        # Agregar botones de medicinas por fila seleccionada
        if nombre == seleccionado:
            r_v = pygame.Rect(x + panel_w - 200, fila_y + 2, 32, 32)
            pygame.draw.rect(screen, (230, 230, 230), r_v)
            pygame.draw.rect(screen, (80, 80, 80), r_v, 2)
            try:
                screen.blit(pygame.transform.smoothscale(vendas_icon, (28, 28)), (r_v.x + 2, r_v.y + 2))
            except Exception:
                pass
            meds_btns["vendas"] = r_v

            r_p = pygame.Rect(x + panel_w - 160, fila_y + 2, 32, 32)
            pygame.draw.rect(screen, (230, 230, 230), r_p)
            pygame.draw.rect(screen, (80, 80, 80), r_p, 2)
            try:
                screen.blit(pygame.transform.smoothscale(pastilla_icon, (28, 28)), (r_p.x + 2, r_p.y + 2))
            except Exception:
                pass
            meds_btns["pastilla"] = r_p

            r_b = pygame.Rect(x + panel_w - 120, fila_y + 2, 32, 32)
            pygame.draw.rect(screen, (230, 230, 230), r_b)
            pygame.draw.rect(screen, (80, 80, 80), r_b, 2)
            try:
                screen.blit(pygame.transform.smoothscale(botiquin_icon, (28, 28)), (r_b.x + 2, r_b.y + 2))
            except Exception:
                pass
            meds_btns["botiquin"] = r_b

        fila_y += 68

    return {"faces": face_rects, "btn_comida": comida_btn, "btn_agua": agua_btn, "btn_meds": meds_btns}


def dibujar_ui(screen: pygame.Surface, estado: Dict, fuente: pygame.font.Font, mensaje: str, comida_icon: pygame.Surface, agua_icon: pygame.Surface, seleccionado):
    screen.fill((25, 25, 25))
    # Cabecera
    dia_txt = fuente.render(f"Día: {estado.get('dia', 1)}", True, (255, 255, 255))
    screen.blit(dia_txt, (20, 20))
    agua = int(estado.get("objetos", {}).get("agua", 0))
    comida = total_comida(estado)
    inv_txt = fuente.render(f"Agua: {agua}  |  Comida: {comida}", True, (200, 200, 200))
    screen.blit(inv_txt, (20, 60))
    # Personajes
    y = 100
    for nombre, pj in estado.get("personajes", {}).items():
        status = "Vivo" if pj.get("vivo") else "Muerto"
        extra = []
        if pj.get("herido"):
            extra.append("Herido")
        if pj.get("enfermo"):
            extra.append("Enfermo")
        if int(estado.get("dia", 1)) <= pj.get("desaparece_hasta", 0):
            extra.append("Ausente")
        linea = f"{nombre}: {status} • Salud {pj.get('salud',0)}"
        if extra:
            linea += " • " + ", ".join(extra)
        txt = fuente.render(linea, True, (230, 230, 230))
        screen.blit(txt, (20, y))
        y += 30
    # Mensaje del día
    y += 10
    for linea in mensaje.split("\n"):
        txt = fuente.render(linea, True, (255, 215, 180))
        screen.blit(txt, (20, y))
        y += 28
    instr = fuente.render("Enter: siguiente día • Esc: salir", True, (180, 180, 180))
    screen.blit(instr, (20, screen.get_height() - 40))

    # Panel tipo libro en esquina inferior derecha
    ui_rects = _draw_book_panel(screen, estado, fuente, comida_icon, agua_icon, seleccionado)

    # Boton de Exploracion centrado abajo
    sw, sh = screen.get_size()
    exp_w, exp_h = 200, 44
    exp_rect = pygame.Rect((sw - exp_w) // 2, sh - exp_h - 18, exp_w, exp_h)
    pygame.draw.rect(screen, (40, 110, 160), exp_rect)
    pygame.draw.rect(screen, (20, 50, 80), exp_rect, 3)
    exp_txt = fuente.render("Exploracion", True, (255, 255, 255))
    screen.blit(exp_txt, (exp_rect.centerx - exp_txt.get_width() // 2, exp_rect.centery - exp_txt.get_height() // 2))
    ui_rects["btn_explorar"] = exp_rect

    pygame.display.flip()
    return ui_rects
def _draw_exploration_modal(screen: pygame.Surface, estado: Dict, fuente: pygame.font.Font):
    sw, sh = screen.get_size()
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    mw, mh = 520, 320
    mx = (sw - mw) // 2
    my = (sh - mh) // 2
    pygame.draw.rect(screen, (235, 235, 235), (mx, my, mw, mh))
    pygame.draw.rect(screen, (30, 30, 30), (mx, my, mw, mh), 4)
    title = fuente.render("Elige quien explorar", True, (20, 20, 20))
    screen.blit(title, (mx + (mw - title.get_width()) // 2, my + 16))

    rects = {}
    disabled = {}
    names = list(estado.get("personajes", {}).keys())
    cols = 2
    bw, bh = 200, 60
    gapx, gapy = 32, 28
    start_x = mx + (mw - (cols * bw + (cols - 1) * gapx)) // 2
    start_y = my + 70
    for i, nombre in enumerate(names):
        cx = i % cols
        cy = i // cols
        r = pygame.Rect(start_x + cx * (bw + gapx), start_y + cy * (bh + gapy), bw, bh)
        pj = estado["personajes"][nombre]
        unusable = (not pj.get("vivo")) or pj.get("herido") or pj.get("enfermo")
        color = (180, 60, 60) if unusable else (60, 160, 80)
        pygame.draw.rect(screen, color, r)
        pygame.draw.rect(screen, (30, 30, 30), r, 3)
        txt = fuente.render(nombre, True, (255, 255, 255))
        screen.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))
        rects[nombre] = r
        disabled[nombre] = unusable

    note = fuente.render("Heridos o enfermos no pueden explorar.", True, (20, 20, 20))
    screen.blit(note, (mx + (mw - note.get_width()) // 2, my + mh - 30))
    pygame.display.flip()
    return {"rects": rects, "disabled": disabled}
def main(estado: Dict, screen: pygame.Surface) -> Dict:
    global estado_juego
    estado_juego = estado
    # Inicialización
    init_personajes_si_faltan(estado_juego)
    normalizar_barras_iniciales(estado_juego)
    eventos = cargar_eventos()
    fuente = pygame.font.SysFont("arial", 20)

    # Cargar iconos para barras (Don Satur y Agua)
    def _load_icon(path: str, size: int = 18) -> pygame.Surface:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (size, size))
        except Exception:
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((200, 200, 200, 255))
            pygame.draw.rect(s, (80, 80, 80), s.get_rect(), 1)
            return s

    comida_icon = _load_icon(os.path.join("imagenes_objs", "bizcochitos don satur.png"), 18)
    agua_icon = _load_icon(os.path.join("imagenes_objs", "agua.png"), 18)
    # Iconos de medicinas
    vendas_icon = _load_icon(os.path.join("imagenes_objs", "vendas.png"), 18)
    pastilla_icon = _load_icon(os.path.join("imagenes_objs", "pastilla.png"), 18)
    botiquin_icon = _load_icon(os.path.join("imagenes_objs", "botiquin.png"), 18)
    # Exponer para panel de libro
    globals()["vendas_icon"] = vendas_icon
    globals()["pastilla_icon"] = pastilla_icon
    globals()["botiquin_icon"] = botiquin_icon
    # Asegurar mnimo de medicinas al iniciar supervivencia
    asegurar_min_medicina(estado_juego, {"botiquin": 2, "vendas": 4, "pastilla": 4})
    # Mensaje inicial si no existe
    estado_juego.setdefault("dia", max(1, int(estado_juego.get("dia", 1))))
    mensaje = "Presiona Enter para avanzar el día."
    seleccionado = None
    last_ui = None
    clock = pygame.time.Clock()
    done = False
    show_explore_modal = False
    last_modal = None
    while not done:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                done = True
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    done = True
                elif ev.key == pygame.K_RETURN:
                    mensaje = pasar_dia_manual(estado_juego, eventos)
                elif ev.key == pygame.K_e:
                    show_explore_modal = True
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                # Modal de exploracion activo
                if show_explore_modal and last_modal:
                    for nombre, r in last_modal.get("rects", {}).items():
                        if r.collidepoint(mx, my):
                            if last_modal.get("disabled", {}).get(nombre, False):
                                mensaje = f"{nombre} no puede explorar (herido o enfermo)."
                            else:
                                dias = random.randint(1, 3)
                                mensaje = enviar_exploracion(estado_juego, nombre, dias)
                                show_explore_modal = False
                                last_modal = None
                            break
                # Seleccion de caras
                elif last_ui and "faces" in last_ui:
                    for nombre, r in last_ui["faces"].items():
                        if r.collidepoint(mx, my):
                            seleccionado = nombre
                            mensaje = f"Seleccionado: {nombre}"
                            break
                # Acciones de item/agua/comida
                if seleccionado and last_ui:
                    btn_c = last_ui.get("btn_comida")
                    btn_a = last_ui.get("btn_agua")
                    btn_meds = last_ui.get("btn_meds", {})
                    clicked = False
                    for tipo, r in btn_meds.items():
                        if r.collidepoint(mx, my):
                            mensaje = usar_medicina(estado_juego, tipo, seleccionado)
                            clicked = True
                            break
                    if not clicked and btn_c and btn_c.collidepoint(mx, my):
                        mensaje = dar_comida(estado_juego, seleccionado)
                        clicked = True
                    if not clicked and btn_a and btn_a.collidepoint(mx, my):
                        mensaje = dar_agua(estado_juego, seleccionado)
                        clicked = True
                # Abrir modal desde boton explorar
                if last_ui and last_ui.get("btn_explorar") and last_ui["btn_explorar"].collidepoint(mx, my):
                    show_explore_modal = True
        last_ui = dibujar_ui(screen, estado_juego, fuente, mensaje, comida_icon, agua_icon, seleccionado)
        if show_explore_modal:
            last_modal = _draw_exploration_modal(screen, estado_juego, fuente)
        clock.tick(60)
    return estado_juego
