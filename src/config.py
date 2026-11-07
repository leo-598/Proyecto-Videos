"""Carga la configuración de marca y series, y utilidades comunes (rutas, estado)."""
import re
from pathlib import Path

import yaml

# Carpeta raíz del proyecto (la que contiene CLAUDE.md)
RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "modelos"


def leer_yaml(ruta):
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def marca():
    return leer_yaml(RAIZ / "config" / "marca.yaml")


def series():
    return leer_yaml(RAIZ / "config" / "series.yaml")


def ruta(rel):
    """Convierte una ruta relativa del proyecto (ej. assets/fonts/x.ttf) en absoluta."""
    return RAIZ / rel


def hex_a_rgb(color):
    if isinstance(color, tuple):  # ya viene en RGB
        return color
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def cambiar_estado(carpeta, estado):
    """Cambia la línea 'estado:' de metadata.yaml sin borrar los comentarios."""
    archivo = Path(carpeta) / "metadata.yaml"
    texto = archivo.read_text(encoding="utf-8")
    texto = re.sub(r"^estado:[ \t]*\S+", f"estado: {estado}", texto, count=1, flags=re.M)
    archivo.write_text(texto, encoding="utf-8")
