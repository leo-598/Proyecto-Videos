"""Etapa 7 — Render final con FFmpeg.

Une visuales/escenas.mp4 + voz.wav + subtitulos.ass (quemados en la imagen).
- Audio: volumen a -14 LUFS en dos pasadas (primero mide, luego corrige), AAC 192k.
  La voz se rellena con silencio durante los 2 s del cierre.
- Video: 1080x1920, 30 fps, H.264 yuv420p, preset veryfast.
Salida: final.mp4
"""
import json
import re
import subprocess
from pathlib import Path

from src import config


def medir_volumen(wav, lufs, pico):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af",
                        f"loudnorm=I={lufs}:TP={pico}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])


def generar(carpeta):
    carpeta = Path(carpeta)
    m = config.marca()
    lufs, pico, fps = m["audio"]["lufs"], m["audio"]["pico_maximo"], m["formato"]["fps"]

    medido = medir_volumen(carpeta / "voz.wav", lufs, pico)
    loudnorm = (f"loudnorm=I={lufs}:TP={pico}:LRA=11:measured_I={medido['input_i']}"
                f":measured_TP={medido['input_tp']}:measured_LRA={medido['input_lra']}"
                f":measured_thresh={medido['input_thresh']}:offset={medido['target_offset']}:linear=true")

    # FFmpeg corre dentro de la carpeta del video: así las rutas del filtro ass no llevan "C:\"
    fuentes = Path(config.ruta(m["fuentes"]["carpeta"])).relative_to(config.RAIZ)
    subir = "/".join([".."] * len(carpeta.resolve().relative_to(config.RAIZ).parts))
    filtro = (f"[0:v]ass=subtitulos.ass:fontsdir={subir}/{fuentes.as_posix()}[v];"
              f"[1:a]{loudnorm},aresample=48000,apad[a]")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", "visuales/escenas.mp4", "-i", "voz.wav", "-filter_complex", filtro,
           "-map", "[v]", "-map", "[a]", "-r", str(fps),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "final.mp4"]
    subprocess.run(cmd, cwd=carpeta, check=True)
    print("  final.mp4 listo")
