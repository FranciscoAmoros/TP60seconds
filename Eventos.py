# Diccionario de eventos básicos simplificados
eventos = {
    "exploracion": {
        "personaje": "Todos",
        "dia_min": 1,
        "resultados": {
            "recursos": 0.5,
            "radiacion_enfermedad": 0.2,
            "ataque": 0.15,
            "nada": 0.15
        }
    },
    "ataque_externo": {
        "personaje": "Todos",
        "dia_min": 8,
        "resultados": {
            "pierde_recursos": 0.4,
            "herido": 0.3,
            "defensa_aliada": 0.2,
            "fallo_ataque": 0.1
        }
    },
    "salud": {
        "personaje": "Todos",
        "dia_min": 2,
        "resultados": {
            "pierde_salud_moral": 0.4,
            "muerte": 0.3,
            "sobrevive": 0.3
        }
    },
    "mascotas": {
        "personaje": "Todos con perro o gato",
        "dia_min": 5,
        "resultados": {
            "trae_recursos": 0.5,
            "defiende_refugio": 0.3,
            "desaparece_temporal": 0.2
        }
    },
    "trueques": {
        "personaje": "Todos",
        "dia_min": 10,
        "resultados": {
            "intercambio_exitoso": 0.5,
            "nada": 0.3,
            "negativo": 0.2
        }
    },
    "mutaciones": {
        "personaje": "Mary Jane u otros irradiados",
        "dia_min": 25,
        "resultados": {
            "resistente_fuerza": 0.4,
            "pierde_moral": 0.3,
            "nada": 0.3
        }
    },
    "rescate": {
        "personaje": "Todos",
        "dia_min": 35,
        "resultados": {
            "rescate_exitoso": 0.4,
            "rescate_parcial": 0.3,
            "rescate_falla": 0.3
        }
    },
    "desastres": {
        "personaje": "Todos",
        "dia_min": 15,
        "resultados": {
            "pierde_recursos": 0.5,
            "daño_personajes": 0.3,
            "nada": 0.2
        }
    },
    "timmy_explora": {
        "personaje": "Timmy",
        "dia_min": 15,
        "resultados": {
            "recursos": 0.5,
            "herido": 0.2,
            "nada": 0.2,
            "desaparece": 0.1
        }
    },
    "ted_explora": {
        "personaje": "Ted",
        "dia_min": 12,
        "resultados": {
            "colapsa": 0.5,
            "recursos": 0.3,
            "desaparece": 0.2
        }
    },
    "madre": {
        "personaje": "Dolores",
        "dia_min": 7,
        "resultados": {
            "pierde_moral": 0.4,
            "accion_util": 0.3,
            "explora_recursos": 0.2,
            "accidente_leve": 0.1
        }
    },
    "hija": {
        "personaje": "Mary Jane",
        "dia_min": 10,
        "resultados": {
            "recursos": 0.4,
            "daño": 0.3,
            "nada": 0.2,
            "muta": 0.1
        }
    }
}

import random
import os
os.system('cls' if os.name == 'nt' else 'clear')
def simular_evento(nombre_evento):
    event = eventos[nombre_evento]
    resultados = event["resultados"]
    elecciones = list(resultados.keys())
    probabilidades = list(resultados.values())
    resultado = random.choices(elecciones, probabilidades)[0]
    return resultado

