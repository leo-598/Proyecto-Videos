"""Etapa 6 — Subtítulos ASS palabra por palabra.

- Grupos de hasta 3 palabras (se corta también en comas, puntos y signos).
- La palabra que suena va en amarillo #FFC832 y un poco más grande; las demás en #F7F4EE.
- Centro hacia el 62 % de la altura, corrido a la izquierda para no tocar el 15 % derecho.
- El bloque de cierre (último) no lleva subtítulos: la tarjeta ya muestra la frase.
"""
import json
from pathlib import Path

from src import config

SIGNOS_CORTE = (".", ",", ":", ";", "?", "!")


def color_ass(hex_color):
    r, g, b = config.hex_a_rgb(hex_color)
    return f"&H00{b:02X}{g:02X}{r:02X}"


def tiempo_ass(seg):
    seg = max(0.0, seg)
    h, resto = divmod(seg, 3600)
    m, s = divmod(resto, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def agrupar(palabras, maximo):
    grupos, actual = [], []
    for p in palabras:
        actual.append(p)
        if len(actual) >= maximo or p["texto"].endswith(SIGNOS_CORTE):
            grupos.append(actual)
            actual = []
    if actual:
        grupos.append(actual)
    return grupos


def generar(carpeta):
    carpeta = Path(carpeta)
    m = config.marca()
    pal, st, fmt = m["paleta"], m["subtitulos"], m["formato"]
    tiempos = json.loads((carpeta / "tiempos.json").read_text(encoding="utf-8"))
    ultimo_bloque = tiempos["bloques"][-1]["id"]

    margen_izq = 90
    margen_der = int(fmt["ancho"] * m["zonas_seguras"]["derecha"]) + 30  # 15 % + respiro
    x = (margen_izq + fmt["ancho"] - margen_der) // 2
    y = int(fmt["alto"] * st["altura"])
    amarillo, blanco = color_ass(pal["acento"]), color_ass(pal["texto"])

    cabecera = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {fmt['ancho']}
PlayResY: {fmt['alto']}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{m['fuentes']['subtitulos_ass']},{st['tamano']},{blanco},{blanco},{color_ass(pal['fondo'])},&H64000000,0,0,0,0,100,100,0,0,1,{st['borde']},2,5,{margen_izq},{margen_der},0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    eventos = []
    palabras = [p for p in tiempos["palabras"] if p["bloque"] != ultimo_bloque]
    for bloque in [b["id"] for b in tiempos["bloques"]]:
        del_bloque = [p for p in palabras if p["bloque"] == bloque]
        grupos = agrupar(del_bloque, st["max_palabras"])
        for gi, grupo in enumerate(grupos):
            # El grupo se queda en pantalla hasta que empieza el siguiente (máx. 0,4 s de más)
            siguiente = grupos[gi + 1][0]["inicio"] if gi + 1 < len(grupos) else grupo[-1]["fin"] + 0.4
            fin_grupo = min(siguiente, grupo[-1]["fin"] + 0.4)
            for k, actual in enumerate(grupo):
                ini = actual["inicio"]
                fin = grupo[k + 1]["inicio"] if k + 1 < len(grupo) else fin_grupo
                trozos = []
                for p in grupo:
                    if p is actual:
                        trozos.append(f"{{\\c&H{amarillo[4:]}&\\fscx108\\fscy108}}{p['texto']}{{\\r}}")
                    else:
                        trozos.append(p["texto"])
                texto = f"{{\\an5\\pos({x},{y})}}" + " ".join(trozos)
                eventos.append(f"Dialogue: 0,{tiempo_ass(ini)},{tiempo_ass(fin)},Sub,,0,0,0,,{texto}")

    (carpeta / "subtitulos.ass").write_text(cabecera + "\n".join(eventos) + "\n", encoding="utf-8-sig")
    print(f"  subtitulos.ass listo: {len(eventos)} eventos")
