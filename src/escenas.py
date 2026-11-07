"""Etapa 5 — Visuales: dibuja con Pillow las escenas de escenas.yaml y las manda a FFmpeg.

- Nada de imágenes externas: todo son formas (arcos, gotas, muñecos, sol, avión, textos).
- Cada escena dura lo que dura su bloque según tiempos.json; la última (cierre) dura
  hasta el final de la voz + 2 s.
- Las animaciones se enganchan a palabras del guion (ej. el círculo se completa
  cuando la voz dice "círculo").
- Se dibuja al doble de tamaño y se reduce (bordes suaves). Los fotogramas van por
  tubería a FFmpeg: no se guardan PNG.
- Siempre visibles: sello de serie arriba. Texto de fuentes en B2–B5.
Salida: visuales/escenas.mp4 (sin audio ni subtítulos).
"""
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src import config, guion

SS = 2                      # factor de sobremuestreo (dibuja a 2x y reduce)
CENTRO = (500, 780)         # centro del área visual (corrido a la izquierda por el 15 % derecho)
ESPECTRO = ["#E8505B", "#FF8A3D", "#FFC832", "#58C470", "#2F6BFF", "#4B3FD6", "#9B5DE5"]
BANDA = 14                  # grosor de cada color del arcoíris

M = config.marca()
FONDO = M["paleta"]["fondo"]
AMARILLO = M["paleta"]["acento"]
AZUL = M["paleta"]["dato"]
TEXTO = M["paleta"]["texto"]
ANCHO, ALTO, FPS = M["formato"]["ancho"], M["formato"]["alto"], M["formato"]["fps"]


# ---------- utilidades ----------

def mezclar(color, otro, t):
    """Mezcla dos colores hex. t=0 -> color, t=1 -> otro. Sirve para fundidos sobre el fondo."""
    a, b = config.hex_a_rgb(color), config.hex_a_rgb(otro)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def visible(color, alfa):
    """Color con 'opacidad' alfa sobre el fondo plano (0 = invisible)."""
    return mezclar(FONDO, color, max(0.0, min(1.0, alfa)))


def prog(t, t0, t1):
    """Avance de 0 a 1 entre t0 y t1, con frenado suave al final."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    x = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
    return 1 - (1 - x) ** 3


_fuentes = {}


def fuente(tipo, tam):
    tam = max(8, int(round(tam)))
    clave = (tipo, tam)
    if clave not in _fuentes:
        if tipo == "titulo":
            f = ImageFont.truetype(str(config.ruta(M["fuentes"]["titulos"])), tam)
        else:
            f = ImageFont.truetype(str(config.ruta(M["fuentes"]["subtitulos"])), tam)
            f.set_variation_by_name(M["fuentes"]["subtitulos_grosor"])
        _fuentes[clave] = f
    return _fuentes[clave]


class Lienzo:
    """Lienzo a 2x con un zoom de cámara suave alrededor de CENTRO. Coordenadas en píxeles 1080x1920."""

    def __init__(self, zoom=1.0):
        self.img = Image.new("RGB", (ANCHO * SS, ALTO * SS), FONDO)
        self.d = ImageDraw.Draw(self.img)
        self.zoom = zoom

    def p(self, x, y):
        cx, cy = CENTRO
        return ((cx + (x - cx) * self.zoom) * SS, (cy + (y - cy) * self.zoom) * SS)

    def s(self, v):
        return v * self.zoom * SS

    def circulo(self, c, r, relleno=None, borde=None, ancho=0):
        x, y = self.p(*c)
        rr = self.s(r)
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=relleno, outline=borde,
                       width=max(1, round(self.s(ancho))) if ancho else 0)

    def arco(self, c, r, a0, a1, color, ancho):
        if a1 - a0 >= 359.5:   # círculo completo: sin costura donde se unen las puntas
            a0, a1 = 0, 360
        if a1 <= a0:
            return
        x, y = self.p(*c)
        rr = self.s(r)
        self.d.arc([x - rr, y - rr, x + rr, y + rr], a0, a1, fill=color, width=max(1, round(self.s(ancho))))

    def linea(self, a, b, color, ancho, puntas=True):
        self.d.line([self.p(*a), self.p(*b)], fill=color, width=max(1, round(self.s(ancho))))
        if puntas:  # extremos redondeados
            for q in (a, b):
                self.circulo(q, ancho / 2, relleno=color)

    def poligono(self, puntos, color):
        self.d.polygon([self.p(*q) for q in puntos], fill=color)

    def texto(self, c, partes, tipo, tam, ancla="mm"):
        """partes = [(texto, color), ...] en una sola línea, centrada en c."""
        f = fuente(tipo, self.s(tam))
        total = sum(f.getlength(t) for t, _ in partes)
        x, y = self.p(*c)
        if ancla == "mm":
            x -= total / 2
        for t, color in partes:
            self.d.text((x, y), t, font=f, fill=color, anchor="lm")
            x += f.getlength(t)


def linea_que_crece(L, puntos, avance, color, ancho):
    """Dibuja una polilínea hasta el 'avance' (0..1) de su largo total."""
    tramos = list(zip(puntos, puntos[1:]))
    largos = [math.dist(a, b) for a, b in tramos]
    falta = sum(largos) * avance
    for (a, b), largo in zip(tramos, largos):
        if falta <= 0:
            break
        f = min(1.0, falta / largo)
        L.linea(a, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), color, ancho)
        falta -= largo


def discontinua(L, a, b, avance, color, ancho, trazo=18, hueco=13):
    largo = math.dist(a, b) * avance
    ux, uy = (b[0] - a[0]) / math.dist(a, b), (b[1] - a[1]) / math.dist(a, b)
    d = 0.0
    while d < largo:
        e = min(d + trazo, largo)
        L.linea((a[0] + ux * d, a[1] + uy * d), (a[0] + ux * e, a[1] + uy * e), color, ancho, puntas=False)
        d += trazo + hueco


def arcoiris(L, c, r, a0, a1, alfa=1.0, colores=ESPECTRO, banda=BANDA):
    for i, col in enumerate(colores):
        L.arco(c, r - i * banda, a0, a1, visible(col, alfa), banda + 1)


def muneco(L, cabeza, alfa=1.0, escala=1.0, color=TEXTO):
    """Muñeco simple de espaldas: cabeza, cuerpo, brazos y piernas."""
    x, y = cabeza
    c = visible(color, alfa)
    e = escala
    L.circulo((x, y), 34 * e, relleno=c)
    L.linea((x, y + 40 * e), (x, y + 170 * e), c, 14 * e)
    L.linea((x - 48 * e, y + 120 * e), (x, y + 70 * e), c, 12 * e)
    L.linea((x + 48 * e, y + 120 * e), (x, y + 70 * e), c, 12 * e)
    L.linea((x, y + 170 * e), (x - 34 * e, y + 270 * e), c, 13 * e)
    L.linea((x, y + 170 * e), (x + 34 * e, y + 270 * e), c, 13 * e)


def gota(L, c, r, alfa=1.0):
    L.circulo(c, r, relleno=visible(AZUL, 0.28 * alfa), borde=visible(AZUL, alfa), ancho=max(3, r * 0.05))
    L.circulo((c[0] - r * 0.38, c[1] - r * 0.38), r * 0.14, relleno=visible("#FFFFFF", 0.55 * alfa))


def sol(L, c, r, alfa, giro=0.0):
    col = visible(AMARILLO, alfa)
    L.circulo(c, r, relleno=col)
    for k in range(8):
        a = math.radians(k * 45 + giro)
        L.linea((c[0] + math.cos(a) * r * 1.35, c[1] + math.sin(a) * r * 1.35),
                (c[0] + math.cos(a) * r * 1.8, c[1] + math.sin(a) * r * 1.8), col, 8)


def avion(L, c, escala, alfa):
    """Avión simple apuntando hacia arriba a la derecha."""
    col = visible(TEXTO, alfa)
    ang = math.radians(-50)

    def rot(px, py):
        return (c[0] + (px * math.cos(ang) - py * math.sin(ang)) * escala,
                c[1] + (px * math.sin(ang) + py * math.cos(ang)) * escala)

    L.poligono([rot(60, 0), rot(-50, -9), rot(-50, 9)], col)                     # fuselaje
    L.poligono([rot(15, 0), rot(-15, -55), rot(-28, -55), rot(-10, 0)], col)      # ala
    L.poligono([rot(15, 0), rot(-15, 55), rot(-28, 55), rot(-10, 0)], col)
    L.poligono([rot(-38, 0), rot(-52, -22), rot(-58, -22), rot(-50, 0)], col)     # cola
    L.poligono([rot(-38, 0), rot(-52, 22), rot(-58, 22), rot(-50, 0)], col)


# ---------- escenas (t = segundos desde que empieza el bloque) ----------

def escena_b1(L, t, dur, cuando, ctx):
    t_circulo = cuando("circulo", 0.6)
    c, r = (500, 820), 300
    a = 180 + 180 * prog(t, 0.1, max(0.6, min(1.6, t_circulo - 0.2)))
    a += 180 * prog(t, t_circulo, t_circulo + 0.9)
    arcoiris(L, c, r, 180, a)
    alfa = prog(t, 0.3, 0.8)
    L.texto((500, 420 + 30 * (1 - alfa)), [("¿Por qué es ", visible(TEXTO, alfa)), ("CURVO?", visible(AMARILLO, alfa))],
            "titulo", 64)


def escena_b2(L, t, dur, cuando, ctx):
    c, r = (520, 720), 250
    gota(L, c, r * (0.6 + 0.4 * prog(t, 0.0, 0.6)), prog(t, 0.0, 0.5))
    y_e = c[1] - 110
    entrada = (c[0] - math.sqrt(r * r - 110 * 110), y_e)
    fondo_gota = (c[0] + r * math.cos(math.radians(25)), c[1] + r * math.sin(math.radians(25)))
    salida = (c[0] + r * math.cos(math.radians(125)), c[1] + r * math.sin(math.radians(125)))
    t_rayo = 0.6
    t_abanico = max(t_rayo + 2.0, cuando("separada", 0.7) - 0.3)
    linea_que_crece(L, [(40, y_e), entrada, fondo_gota, salida], prog(t, t_rayo, t_abanico), "#FFFFFF", 8)
    alfa_et = prog(t, 0.8, 1.3)
    L.texto((150, y_e - 45), [("luz del sol", visible(TEXTO, 0.8 * alfa_et))], "texto", 34)
    a = prog(t, t_abanico, t_abanico + 1.0)
    if a > 0:
        for i, col in enumerate(ESPECTRO):
            ang = math.radians(112 + i * 6)
            largo = 210 * a
            L.linea(salida, (salida[0] + math.cos(ang) * largo, salida[1] + math.sin(ang) * largo), col, 9)
        L.texto((150, 1060), [("colores", visible(AMARILLO, prog(t, t_abanico + 0.5, t_abanico + 1.0)))], "texto", 34)


def geometria_b3():
    sol_c, cabeza = (110, 560), (330, 760)
    u = ((cabeza[0] - sol_c[0]), (cabeza[1] - sol_c[1]))
    n = math.hypot(*u)
    u = (u[0] / n, u[1] / n)
    antisolar = (cabeza[0] + u[0] * 400, cabeza[1] + u[1] * 400)
    ang_u = math.degrees(math.atan2(u[1], u[0]))
    ang_g = ang_u - 42
    gota_c = (cabeza[0] + math.cos(math.radians(ang_g)) * 420, cabeza[1] + math.sin(math.radians(ang_g)) * 420)
    return sol_c, cabeza, antisolar, ang_u, ang_g, gota_c


def escena_b3(L, t, dur, cuando, ctx):
    sol_c, cabeza, antisolar, ang_u, ang_g, gota_c = geometria_b3()
    t_42 = cuando("cuarenta", 0.5)
    L.linea((60, cabeza[1] + 275), (900, cabeza[1] + 275), visible("#5A606B", prog(t, 0.0, 0.4)), 4)  # suelo
    sol(L, sol_c, 50, prog(t, 0.0, 0.5), giro=t * 20)
    a_m = prog(t, 0.3, 0.9)
    muneco(L, (cabeza[0], cabeza[1] + 40 * (1 - a_m)), a_m)
    # Línea punteada sol -> cabeza -> punto antisolar
    discontinua(L, sol_c, antisolar, prog(t, 1.0, max(1.6, t_42 - 0.6)), visible(TEXTO, 0.7), 5)
    a_x = prog(t, t_42 - 0.6, t_42 - 0.2)
    if a_x > 0:
        L.circulo(antisolar, 12, borde=visible(TEXTO, a_x), ancho=4)
    # Línea de la mirada hacia la gota + cuña de 42°
    a_g = prog(t, t_42 - 0.4, t_42 + 0.3)
    if a_g > 0:
        linea_que_crece(L, [cabeza, gota_c], a_g, visible(AMARILLO, 0.9), 5)
        gota(L, gota_c, 26, a_g)
        L.arco(cabeza, 120, ang_g, ang_g + 42 * a_g, visible(AMARILLO, a_g), 6)
    a_t = prog(t, t_42, t_42 + 0.35)
    if a_t > 0:
        mitad = math.radians(ang_g + 21)
        L.texto((cabeza[0] + math.cos(mitad) * 185, cabeza[1] + math.sin(mitad) * 185),
                [("≈42°", visible(AMARILLO, a_t))], "titulo", 40 + 12 * a_t)


def escena_b4(L, t, dur, cuando, ctx):
    t_cada = cuando("cada", 0.6)
    fuera = 1 - prog(t, t_cada - 0.3, t_cada + 0.1)   # la fase 1 se desvanece
    A, R, n = (500, 720), 280, 28
    if fuera > 0:
        L.circulo(A, 26, relleno=visible("#2A2E36", fuera))
        L.circulo(A, 8, relleno=visible(TEXTO, fuera))
        L.texto((A[0], A[1] + 62), [("sombra de tu cabeza", visible(TEXTO, 0.75 * fuera * prog(t, 0.2, 0.7)))],
                "texto", 32)
        t_aro = min(2.4, t_cada - 1.2)
        for k in range(n):
            ang = math.radians(-90 + k * 360 / n)
            q = (A[0] + math.cos(ang) * R, A[1] + math.sin(ang) * R)
            aparece = prog(t, 0.2 + (t_aro - 0.2) * k / n, 0.2 + (t_aro - 0.2) * k / n + 0.25)
            if aparece > 0:
                L.circulo(q, 15, relleno=visible(AMARILLO, aparece * fuera))
        brillo = prog(t, t_aro, t_aro + 0.6) * fuera
        if brillo > 0:
            arcoiris(L, A, R + 40, 0, 360, alfa=brillo * 0.9, banda=10)
    entra = prog(t, t_cada, t_cada + 0.5)
    if entra > 0:
        otros = [mezclar(c, "#FFFFFF", 0.3) for c in ESPECTRO]
        for x, colores, t0, etiqueta in ((320, ESPECTRO, t_cada + 0.2, "tú"),
                                         (680, otros, t_cada + 0.8, "tu parce")):
            muneco(L, (x, 830), entra, escala=0.8)
            arcoiris(L, (x, 830), 220, 180, 180 + 180 * prog(t, t0, t0 + 0.8), banda=10, colores=colores)
            L.texto((x, 1075), [(etiqueta, visible(TEXTO, 0.8 * prog(t, t0, t0 + 0.4)))], "texto", 34)


def escena_b5(L, t, dur, cuando, ctx):
    t_avion = cuando("avion", 0.55)
    c, r = (500, 815), 290
    baja = prog(t, t_avion, t_avion + 1.2)               # el suelo se va hacia abajo
    y_suelo = 860 + 460 * baja
    suelo_alfa = 1 - baja
    # Mitad tapada: suelo oscuro y arcoíris tenue
    L.d.rectangle([0, L.p(0, y_suelo)[1], ANCHO * SS, ALTO * SS], fill=visible("#0B0C0F", suelo_alfa))
    crece = prog(t, 0.0, 1.2)
    arcoiris(L, c, r, 0, 360 * crece, alfa=0.25)
    # Parte visible (por encima del suelo) con brillo completo
    capa = Lienzo(L.zoom)
    arcoiris(capa, c, r, 0, 360 * crece)
    mascara = Image.new("L", L.img.size, 0)
    ImageDraw.Draw(mascara).rectangle([0, 0, ANCHO * SS, L.p(0, y_suelo)[1]], fill=255)
    L.img.paste(capa.img, (0, 0), mascara)
    resalta = 1.0 + 0.6 * math.sin(math.pi * prog(t, cuando("suelo", 0.35), cuando("suelo", 0.35) + 0.6))
    L.linea((40, y_suelo), (920, y_suelo), visible("#8A909B", suelo_alfa * min(1.0, 0.6 * resalta)), 5)
    a = prog(t, t_avion - 0.2, t_avion + 1.6)
    if t >= t_avion - 0.2:
        avion(L, (140 + 560 * a, 1200 - 820 * a), 1.0, min(1.0, 4 * a) * (1 - prog(t, t_avion + 1.6, t_avion + 2.0)))


def escena_b6(L, t, dur, cuando, ctx):
    a = prog(t, 0.0, 0.45)
    tam = 100 * (0.85 + 0.15 * a)
    L.texto((520, 830), [("Parchan", visible(TEXTO, a)), ("Col", visible(AMARILLO, a))], "titulo", tam)
    b = prog(t, 0.25, 0.9)
    L.linea((520 - 180 * b, 905), (520 + 180 * b, 905), visible(AMARILLO, b), 8)
    L.texto((520, 990), [(ctx["frase_cierre"], visible(TEXTO, prog(t, 0.4, 0.9)))], "texto", 54)


ESCENAS = {"B1": escena_b1, "B2": escena_b2, "B3": escena_b3, "B4": escena_b4, "B5": escena_b5, "B6": escena_b6}
CON_FUENTES = {"B2", "B3", "B4", "B5"}


# ---------- capas fijas (sello y fuentes), a tamaño final ----------

def capa_sello(texto):
    img = Image.new("RGBA", (ANCHO, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = fuente("titulo", 50)
    w = f.getlength(texto)
    x0, x1, y0, y1 = 540 - w / 2 - 34, 540 + w / 2 + 34, 40, 130
    d.rounded_rectangle([x0, y0, x1, y1], radius=45, fill=mezclar(FONDO, "#FFFFFF", 0.06), outline=AMARILLO, width=4)
    d.text((540, (y0 + y1) / 2), texto, font=f, fill=AMARILLO, anchor="mm")
    return img, (0, 150)


def capa_fuentes(texto):
    img = Image.new("RGBA", (ANCHO, 60), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((60, 30), texto, font=fuente("texto", 30), fill=mezclar(FONDO, TEXTO, 0.7) + (255,),
                             anchor="lm")
    return img, (0, 1450)


# ---------- programa principal ----------

def generar(carpeta):
    carpeta = Path(carpeta)
    diseno = config.leer_yaml(carpeta / "escenas.yaml")
    tiempos = json.loads((carpeta / "tiempos.json").read_text(encoding="utf-8"))
    total = tiempos["duracion_voz"] + M["cierre"]["segundos"]
    n_frames = math.ceil(total * FPS)

    # Tramos: cada escena empieza con su bloque; la primera en 0 y la última va hasta el final
    bloques = tiempos["bloques"]
    tramos = []
    for i, b in enumerate(bloques):
        ini = 0.0 if i == 0 else b["inicio"]
        fin = bloques[i + 1]["inicio"] if i + 1 < len(bloques) else total
        palabras = [p for p in tiempos["palabras"] if p["bloque"] == b["id"]]
        tramos.append((b["id"], ini, fin, palabras))

    sello, pos_sello = capa_sello(diseno["sello_serie"])
    fuentes_img, pos_fuentes = capa_fuentes(diseno["texto_fuentes"])
    ctx = {"frase_cierre": M["frase_cierre"]}

    salida = carpeta / "visuales"
    salida.mkdir(exist_ok=True)
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{ANCHO}x{ALTO}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
         str(salida / "escenas.mp4")],
        stdin=subprocess.PIPE)

    print(f"  Dibujando {n_frames} fotogramas ({total:.2f} s)...")
    for n in range(n_frames):
        t = n / FPS
        bid, ini, fin, palabras = next(tr for tr in tramos if tr[1] <= t < tr[2]) if t < total else tramos[-1]
        local, dur = t - ini, fin - ini

        def cuando(raiz, fraccion, _p=palabras, _ini=ini, _dur=dur):
            """Momento (relativo a la escena) en que suena la primera palabra que empieza por 'raiz'."""
            for p in _p:
                if p["norm"].startswith(raiz):
                    return p["inicio"] - _ini
            return fraccion * _dur

        zoom = 1.0 + 0.045 * (local / dur) if bid != "B6" else 1.0   # cámara que se acerca despacio
        L = Lienzo(zoom)
        ESCENAS[bid](L, local, dur, cuando, ctx)
        cuadro = L.img.resize((ANCHO, ALTO), Image.BOX)
        if local < 0.2 and bid != bloques[0]["id"]:                   # fundido corto al cambiar de escena
            cuadro = Image.blend(Image.new("RGB", (ANCHO, ALTO), FONDO), cuadro, local / 0.2)
        cuadro.paste(sello, pos_sello, sello)
        if bid in CON_FUENTES:
            cuadro.paste(fuentes_img, pos_fuentes, fuentes_img)
        ffmpeg.stdin.write(cuadro.tobytes())
        if n % 150 == 0:
            print(f"    {n}/{n_frames}")

    ffmpeg.stdin.close()
    if ffmpeg.wait() != 0:
        raise RuntimeError("FFmpeg falló al codificar las escenas")
    print("  visuales/escenas.mp4 listo")
