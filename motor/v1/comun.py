"""Utilidades comunes del motor v1: rutas, ajustes, lectura de guion.md y tiempos.

Formato de guion.md (el mismo del MVP, más dos marcas):
  [B1 – GANCHO]      encabezado de bloque (opcional)
  [pausa]            pausa corta entre frases (ajustes: voz.pausa)
  [pausa:0.6]        pausa de 0,6 s
  *palabra*          énfasis
  {G|ge}             se muestra "G" en el subtítulo pero la voz dice "ge" (una palabra)
  Cada frase (separada por [pausa], por salto de línea o por bloque) se genera aparte.
  Las líneas que empiezan con '#', '>' o '---' y las que van antes del primer texto de voz se ignoran
  si hay bloques; sin bloques, todo lo que no sea encabezado cuenta como voz.
"""
import json
import re
import subprocess
import unicodedata
from pathlib import Path

V1 = Path(__file__).resolve().parent
MOTOR = V1.parent
RAIZ = MOTOR.parent
MODELOS = MOTOR / "modelos"
FONTS = RAIZ / "assets" / "fonts"

AJUSTES = {
    "fps": 30,
    "voz": {
        "modelo": "kokoro-multi-lang-v1_0", "sid": 29, "lang": "es", "escala_tiempo": 0.95,  # duración relativa de la voz (0.95 = 5 % más rápida)
        "hilos": 4, "inicio": 0.15, "pausa": 0.40, "pausa_bloque": 0.50, "final": 0.60,
        "parecido_minimo": 0.90, "reintentos_escala": [1.0, 0.9],
    },
    "whisper": {"modelo": "small", "carpeta": str(RAIZ / "modelos" / "whisper")},
    "cierre": {"segundos": 0},  # sin tarjeta ParchanCol al final (decisión del dueño, 2026-11-07)
}


def ajustes(carpeta=None):
    """Ajustes del motor; un video puede cambiar algunos con <video>/ajustes.json (mismas claves)."""
    a = json.loads(json.dumps(AJUSTES))
    if carpeta and (Path(carpeta) / "ajustes.json").exists():
        extra = json.loads((Path(carpeta) / "ajustes.json").read_text(encoding="utf-8"))
        for k, v in extra.items():
            if isinstance(v, dict):
                a.setdefault(k, {}).update(v)
            else:
                a[k] = v
    return a


def marca():
    import yaml
    with open(RAIZ / "config" / "marca.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalizar(palabra):
    """Minúsculas, sin tildes ni signos: sirve para comparar palabras (copiada de src/guion.py)."""
    sin_tildes = unicodedata.normalize("NFD", palabra.lower())
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", sin_tildes)


ENCABEZADO = re.compile(r"^\[(B\d+)\s*[–-]\s*([^\]]+)\]\s*$")
PAUSA = re.compile(r"\[pausa(?::\s*([0-9.]+))?\]")
CAMBIO = re.compile(r"\{([^|{}]+)\|([^|{}]+)\}")


def leer_guion(carpeta, aj=None):
    """Devuelve la lista de frases: {bloque, texto (subtítulo), voz (lo que dice el TTS),
    palabras: [{texto, voz, enfasis}], pausa (s de silencio DESPUÉS)}."""
    aj = aj or ajustes(carpeta)
    lineas = (Path(carpeta) / "guion.md").read_text(encoding="utf-8").splitlines()
    hay_bloques = any(ENCABEZADO.match(l.strip()) for l in lineas)
    frases, bloque = [], (None if hay_bloques else "B1")
    for linea in lineas:
        linea = linea.strip()
        m = ENCABEZADO.match(linea)
        if m:
            bloque = m.group(1)
            if frases:
                frases[-1]["pausa"] = max(frases[-1]["pausa"], aj["voz"]["pausa_bloque"])
            continue
        if bloque is None or not linea or linea.startswith(("#", ">", "---", "Serie:", "Marcas")):
            continue
        # trozos separados por [pausa]
        pos = 0
        for mp in list(PAUSA.finditer(linea)) + [None]:
            trozo = linea[pos: mp.start()] if mp else linea[pos:]
            pausa = float(mp.group(1)) if (mp and mp.group(1)) else aj["voz"]["pausa"]
            pos = mp.end() if mp else len(linea)
            trozo = trozo.strip()
            if not trozo:
                if mp and frases:
                    frases[-1]["pausa"] = pausa
                continue
            palabras = []
            for tok in trozo.split():
                c = CAMBIO.search(tok)
                ver = CAMBIO.sub(lambda x: x.group(1), tok)
                dic = CAMBIO.sub(lambda x: x.group(2), tok)
                palabras.append({"texto": ver.replace("*", ""), "voz": dic.replace("*", ""), "enfasis": "*" in tok, "cambio": bool(c)})
            frases.append({"bloque": bloque, "texto": " ".join(p["texto"] for p in palabras),
                           "voz": " ".join(p["voz"] for p in palabras), "palabras": palabras, "pausa": pausa})
    if frases:
        frases[-1]["pausa"] = aj["voz"]["final"]
    return frases


def total_cuadros(carpeta):
    """TOTAL del story.js; si no está, sale de phrases.json."""
    s = Path(carpeta) / "story.js"
    if s.exists():
        m = re.search(r"\bTOTAL\s*=\s*(\d+)", s.read_text(encoding="utf-8"))
        if m:
            return int(m.group(1))
    p = Path(carpeta) / "phrases.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))["frames"]
    raise SystemExit("No sé cuántos cuadros tiene el video: falta TOTAL en story.js y no hay phrases.json")


def ffmpeg(*args, capturar=False, cwd=None):
    r = subprocess.run(["ffmpeg", "-hide_banner", *map(str, args)], capture_output=True, text=True, cwd=cwd,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("ffmpeg falló:\n" + r.stderr[-2000:])
    return r.stderr if capturar else None
