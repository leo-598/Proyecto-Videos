"""Orquestador: produce un video de punta a punta.

Uso:
    .venv\\Scripts\\python -m src.producir videos/<carpeta> [--forzar]

Corre las etapas en orden. Si una etapa ya tiene su archivo de salida, la salta
(salvo con --forzar). Actualiza el estado en metadata.yaml y anota el tiempo de
cada etapa en metricas/tiempos_produccion.csv.
"""
import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from src import config, escenas, render, subtitulos, tiempos, voz

# (nombre, función, archivo de salida, estado al terminar o None)
ETAPAS = [
    ("voz", voz.generar, "voz.wav", "voz"),
    ("tiempos", tiempos.generar, "tiempos.json", None),
    ("subtitulos", subtitulos.generar, "subtitulos.ass", None),
    ("escenas", escenas.generar, "visuales/escenas.mp4", None),
    ("render", render.generar, "final.mp4", "render"),
]


def registrar(video, etapa, segundos, saltada):
    archivo = config.RAIZ / "metricas" / "tiempos_produccion.csv"
    nuevo = not archivo.exists()
    with open(archivo, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "video", "etapa", "segundos", "saltada"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), video, etapa, f"{segundos:.1f}",
                    "si" if saltada else "no"])


def main():
    parser = argparse.ArgumentParser(description="Produce un video de ParchanCol")
    parser.add_argument("carpeta", help="carpeta del video, ej. videos/2026-11-07_porque_arcoiris-curvo")
    parser.add_argument("--forzar", action="store_true", help="rehacer todas las etapas")
    args = parser.parse_args()

    carpeta = Path(args.carpeta).resolve()
    meta = config.leer_yaml(carpeta / "metadata.yaml")
    if meta.get("estado") == "idea":
        raise SystemExit("El guion no tiene el CONTROL 1 aprobado (estado: idea). No se produce.")

    total = time.time()
    for nombre, funcion, salida, estado in ETAPAS:
        if (carpeta / salida).exists() and not args.forzar:
            print(f"[{nombre}] ya existe {salida}: la salto")
            registrar(carpeta.name, nombre, 0, True)
            continue
        print(f"[{nombre}] empezando...")
        inicio = time.time()
        funcion(carpeta)
        segundos = time.time() - inicio
        registrar(carpeta.name, nombre, segundos, False)
        print(f"[{nombre}] listo en {segundos:.1f} s")
        if estado:
            config.cambiar_estado(carpeta, estado)
    print(f"Terminado en {time.time() - total:.1f} s. Siguiente paso: CONTROL 2 (revisión humana).")


if __name__ == "__main__":
    main()
