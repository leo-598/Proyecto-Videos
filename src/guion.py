"""Lee guion.md y lo separa en bloques (B1..B6), frases y palabras.

Marcas del guion:
  [B1 – GANCHO]  encabezado de bloque
  [pausa]        pausa corta
  *palabra*      énfasis
"""
import re
import unicodedata
from pathlib import Path

ENCABEZADO = re.compile(r"^\[(B\d+)\s*[–-]\s*([^\]]+)\]\s*$")


def normalizar(palabra):
    """Minúsculas, sin tildes ni signos: sirve para comparar palabras."""
    sin_tildes = unicodedata.normalize("NFD", palabra.lower())
    sin_tildes = "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", sin_tildes)


def leer(carpeta):
    """Devuelve una lista de bloques:
    {id, nombre, frases: [texto para la voz], palabras: [{texto, enfasis}]}"""
    lineas = (Path(carpeta) / "guion.md").read_text(encoding="utf-8").splitlines()
    bloques, actual = [], None
    for linea in lineas:
        linea = linea.strip()
        m = ENCABEZADO.match(linea)
        if m:
            actual = {"id": m.group(1), "nombre": m.group(2).strip(), "texto": ""}
            bloques.append(actual)
        elif actual is not None and linea and not linea.startswith("---"):
            actual["texto"] += " " + linea

    for b in bloques:
        texto = b.pop("texto").strip()
        # Frases separadas por [pausa]; sin asteriscos para la voz
        b["frases"] = [f.replace("*", "").strip() for f in texto.split("[pausa]") if f.strip()]
        # Palabras con su marca de énfasis y el número de frase (para tiempos y subtítulos)
        b["palabras"] = []
        trozos = [f for f in texto.split("[pausa]") if f.strip()]
        for n_frase, trozo in enumerate(trozos):
            for token in trozo.split():
                b["palabras"].append({"texto": token.replace("*", ""), "enfasis": "*" in token, "frase": n_frase})
    return bloques
