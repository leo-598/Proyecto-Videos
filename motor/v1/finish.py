"""Cierre del video: cuadros + audio -> videos/<carpeta>/final.mp4 (port de finish.sh a Python).

Uso:  .venv\\Scripts\\python.exe motor\\v1\\finish.py videos\\<carpeta> [--previa]

1. Revisa que estén todos los cuadros (out/frames/f0000.jpg ... f<TOTAL-1>.jpg).
2. Si falta out/mix_raw.wav, corre audio.py (sonidos.json).
3. Normaliza el audio a -14 LUFS en dos pasadas (ganancia fija + limitador) con pico <= -1,5 dB (config/marca.yaml).
4. Subtítulos palabra por palabra (ASS, Inter SemiBold; palabra que suena en #FFC832, resto #F7F4EE),
   lógica copiada de src/subtitulos.py. Nada en el 20 % de abajo ni en el 15 % derecho.
5. Tarjeta de cierre OPCIONAL (desde nov-2026 ya no se usa: cierre.segundos = 0 por defecto).
   Para un video que sí la lleve: ajustes.json {"cierre": {"segundos": 2}} -> fondo #14161A con
   "ParchanCol" ("Col" en amarillo) en Archivo Black.
   Los videos de caricatura NO llevan sello de serie.
6. Codifica (H.264 + AAC) a videos/<carpeta>/final.mp4 (fuera de out/, para subirlo al repo).
7. Control de calidad: duración, tamaño, sonoridad, cuadros congelados o negros, y out/qa_hoja.jpg.

--previa: junta out/previa/ (540x960, 1 de cada 3 cuadros) con la voz y los subtítulos -> out/previa.mp4.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

SIGNOS_CORTE = (".", ",", ":", ";", "?", "!")


# ---------------- subtítulos (de src/subtitulos.py) ----------------
def color_ass(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
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
        if len(actual) >= maximo or p["w"].endswith(SIGNOS_CORTE):
            grupos.append(actual)
            actual = []
    if actual:
        grupos.append(actual)
    return grupos


def subtitulos(carpeta, dur_historia, cierre):
    m = comun.marca()
    pal, st, fmt = m["paleta"], m["subtitulos"], m["formato"]
    words = json.loads((carpeta / "words.json").read_text(encoding="utf-8"))
    W, H = fmt["ancho"], fmt["alto"]
    margen_izq = 90
    margen_der = int(W * m["zonas_seguras"]["derecha"]) + 30  # 15 % + respiro
    x = (margen_izq + W - margen_der) // 2
    y = int(H * st["altura"])
    amarillo, blanco, fondo = color_ass(pal["acento"]), color_ass(pal["texto"]), color_ass(pal["fondo"])

    cabecera = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{m['fuentes']['subtitulos_ass']},{st['tamano']},{blanco},{blanco},{fondo},&H64000000,0,0,0,0,100,100,0,0,1,{st['borde']},2,5,{margen_izq},{margen_der},0,1
Style: Cierre,Archivo Black,150,{blanco},{blanco},{fondo},&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    eventos = []
    for bloque in dict.fromkeys(w["bloque"] for w in words):
        grupos = agrupar([w for w in words if w["bloque"] == bloque], st["max_palabras"])
        for gi, grupo in enumerate(grupos):
            # el grupo se queda hasta que empieza el siguiente (máx. 0,4 s de más) y nunca entra al cierre
            siguiente = grupos[gi + 1][0]["s"] if gi + 1 < len(grupos) else grupo[-1]["e"] + 0.4
            fin_grupo = min(siguiente, grupo[-1]["e"] + 0.4, dur_historia)
            for k, actual in enumerate(grupo):
                ini = actual["s"]
                fin = grupo[k + 1]["s"] if k + 1 < len(grupo) else fin_grupo
                if fin <= ini:
                    continue
                trozos = [f"{{\\c&H{amarillo[4:]}&\\fscx108\\fscy108}}{p['w']}{{\\r}}" if p is actual else p["w"] for p in grupo]
                eventos.append(f"Dialogue: 0,{tiempo_ass(ini)},{tiempo_ass(fin)},Sub,,0,0,0,,{{\\an5\\pos({x},{y})}}" + " ".join(trozos))
    # tarjeta de cierre: "Parchan" blanco + "Col" amarillo, centrada en la zona segura, con entrada suave
    nombre = m["nombre"]
    logo = f"{nombre[:-3]}{{\\c&H{amarillo[4:]}&}}{nombre[-3:]}"
    if cierre > 0:
        eventos.append(f"Dialogue: 1,{tiempo_ass(dur_historia)},{tiempo_ass(dur_historia + cierre)},Cierre,,0,0,0,,"
                   f"{{\\an5\\pos({x},{int(H * 0.45)})\\fad(250,0)}}{logo}")
    ruta = carpeta / "subtitulos.ass"
    ruta.write_text(cabecera + "\n".join(eventos) + "\n", encoding="utf-8-sig")
    print(f"  subtitulos.ass: {len(eventos)} eventos" + (" (incluye la tarjeta de cierre)" if cierre > 0 else ""))
    return ruta


# ---------------- audio ----------------
def normalizar_audio(entrada, salida, dur_total):
    """Mide, sube con una ganancia fija y un limitador recorta los picos; repite (método de la secante)
    hasta quedar a ±0,2 LU de -14, porque el limitador se come parte de la subida.
    (loudnorm en modo lineal baja la ganancia si el pico no cabe y el video queda por debajo de -14.)
    El limitador deja 1 dB extra de margen porque el AAC sube un poco los picos."""
    a = comun.marca()["audio"]
    lim = 10 ** ((a["pico_maximo"] - 1.0) / 20)

    def probar(g):
        filtro = f"volume={g:.2f}dB,alimiter=limit={lim:.4f}:level=false:attack=3:release=60:asc=1,apad=whole_dur={dur_total:.3f}"
        comun.ffmpeg("-y", "-i", entrada, "-af", filtro, "-ar", "48000", "-ac", "1", salida)
        return medir(salida)[0]

    obj = a["lufs"]
    g0, l0 = 0.0, medir(entrada)[0]
    g1 = obj - l0
    l1 = probar(g1)
    for _ in range(5):
        if abs(obj - l1) <= 0.2 or l1 == l0:
            break
        g0, l0, g1 = g1, l1, g1 + (obj - l1) * (g1 - g0) / (l1 - l0)
        l1 = probar(g1)
    print(f"  audio: {medir(entrada)[0]:.1f} -> {l1:.1f} LUFS (ganancia {g1:+.1f} dB)")


def medir(ruta):
    """Sonoridad integrada (LUFS) y pico real de un archivo."""
    txt = comun.ffmpeg("-i", ruta, "-af", "ebur128=peak=true", "-f", "null", "-", capturar=True)
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)


def probe(ruta):
    import subprocess
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                        "-of", "json", str(ruta)], capture_output=True, text=True)
    return json.loads(r.stdout)


def rel(p):
    """Ruta relativa a la raíz del proyecto con '/' (los filtros de ffmpeg no aceptan 'C:\\')."""
    return Path(p).resolve().relative_to(comun.RAIZ).as_posix()


# ---------------- previa ----------------
def previa(carpeta):
    aj = comun.ajustes(carpeta)
    fps = aj["fps"]
    cuadros = sorted(carpeta.glob("out/previa/f*.jpg"))
    if not cuadros:
        raise SystemExit("No hay cuadros en out/previa/: primero  node motor/v1/render.mjs <carpeta> --previa")
    total = comun.total_cuadros(carpeta)
    nums = [int(c.stem[1:]) for c in cuadros]
    lineas = []
    for k, (n, c) in enumerate(zip(nums, cuadros)):
        sig = nums[k + 1] if k + 1 < len(nums) else total
        lineas += [f"file '{c.name}'", f"duration {(sig - n) / fps:.4f}"]
    lineas.append(f"file '{cuadros[-1].name}'")
    (carpeta / "out" / "previa" / "lista.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    dur = total / fps
    ass = subtitulos(carpeta, dur, 0.0)
    audio = carpeta / "out" / "mix_raw.wav"
    if not audio.exists():
        audio = carpeta / "voz.wav"
    salida = carpeta / "out" / "previa.mp4"
    comun.ffmpeg("-y", "-f", "concat", "-safe", "0", "-i", rel(carpeta / "out" / "previa" / "lista.txt"), "-i", rel(audio),
                 "-vf", f"fps={fps},scale=540:960,ass={rel(ass)}:fontsdir=assets/fonts", "-t", f"{dur:.3f}",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", rel(salida), cwd=comun.RAIZ)
    print(f"  previa lista: {salida}  ({len(cuadros)} cuadros de {total}, {dur:.1f} s)")


# ---------------- final ----------------
def final(carpeta):
    aj = comun.ajustes(carpeta)
    fps, cierre = aj["fps"], aj["cierre"]["segundos"]
    total = comun.total_cuadros(carpeta)
    frames = carpeta / "out" / "frames"
    faltan = [f for f in range(total) if not ((frames / f"f{f:04d}.jpg").exists() and (frames / f"f{f:04d}.jpg").stat().st_size > 1000)]
    if faltan:
        raise SystemExit(f"Faltan {len(faltan)} de {total} cuadros (el primero: {faltan[0]}). Vuelve a lanzar render.mjs: sigue donde iba.")
    dur = total / fps
    out = carpeta / "out"

    if not (out / "mix_raw.wav").exists():
        print("  falta out/mix_raw.wav: corro audio.py")
        import audio
        audio.generar(carpeta)
    print("  normalizando el audio a -14 LUFS (dos pasadas)...")
    normalizar_audio(out / "mix_raw.wav", out / "mix.wav", dur + cierre)

    ass = subtitulos(carpeta, dur, cierre)
    fondo = comun.marca()["paleta"]["fondo"].replace("#", "0x")
    salida = carpeta / "final.mp4"
    print("  codificando final.mp4...")
    comun.ffmpeg("-y", "-framerate", fps, "-i", rel(frames / "f%04d.jpg"), "-i", rel(out / "mix.wav"),
                 "-vf", (f"tpad=stop_duration={cierre}:color={fondo}," if cierre > 0 else "") + f"ass={rel(ass)}:fontsdir=assets/fonts,format=yuv420p",
                 "-t", f"{dur + cierre:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-r", fps,
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", rel(salida), cwd=comun.RAIZ)

    # ---- control de calidad ----
    pr = probe(salida)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    d = float(pr["format"]["duration"])
    lufs, pico = medir(salida)
    txt = comun.ffmpeg("-t", f"{dur:.3f}", "-i", rel(salida), "-vf", "freezedetect=n=0.001:d=1.5,blackdetect=d=0.5:pix_th=0.05",
                       "-an", "-f", "null", "-", capturar=True, cwd=comun.RAIZ)
    congelados = re.findall(r"freeze_start: ([\d.]+)", txt)
    negros = re.findall(r"black_start:([\d.]+)", txt)
    n = 12
    comun.ffmpeg("-y", "-i", rel(salida), "-vf", f"fps={n / d:.4f},scale=270:-1,tile=6x2", "-frames:v", "1", "-q:v", "3",
                 rel(out / "qa_hoja.jpg"), cwd=comun.RAIZ)
    print("  ---- control de calidad ----")
    print(f"  {salida}")
    print(f"  {v['width']}x{v['height']} a {v['r_frame_rate']} | {d:.2f} s (historia {dur:.2f} + cierre {cierre:.1f})")
    print(f"  sonoridad {lufs} LUFS | pico {pico} dBFS")
    print(f"  congelados > 1,5 s: {', '.join(congelados) or 'ninguno'} | negros > 0,5 s: {', '.join(negros) or 'ninguno'}")
    print(f"  hoja de control: {out / 'qa_hoja.jpg'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    c = Path(sys.argv[1]).resolve()
    previa(c) if "--previa" in sys.argv else final(c)
