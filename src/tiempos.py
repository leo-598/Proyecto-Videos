"""Etapa — Tiempos de cada palabra con faster-whisper (MIT), modelo "small", int8, CPU.

Whisper escucha voz.wav y da el momento de cada palabra. El texto oficial es el del guion:
la transcripción solo se usa para saber CUÁNDO suena cada palabra del guion.
- Los bloques B1..B6 y cada frase vienen exactos de voz_bloques.json (los marcó la etapa de voz).
- Dentro de cada frase se emparejan las palabras del guion con las de Whisper.
- Las palabras que no coinciden (ej. "cuarenta y dos" escrito como "42") se reparten
  entre las palabras vecinas que sí coincidieron, según su largo.
Guarda tiempos.json.
"""
import difflib
import json
from pathlib import Path

from src import config, guion


def transcribir(ruta_wav):
    from faster_whisper import WhisperModel

    modelo = WhisperModel("small", device="cpu", compute_type="int8",
                          download_root=str(config.MODELOS / "whisper"))
    segmentos, _ = modelo.transcribe(str(ruta_wav), language="es", word_timestamps=True,
                                     beam_size=5, vad_filter=False)
    palabras = []
    for seg in segmentos:
        for w in seg.words:
            norm = guion.normalizar(w.word)
            if norm:
                palabras.append({"norm": norm, "inicio": w.start, "fin": w.end})
    return palabras


def repartir(palabras, desde, hasta):
    """Reparte el intervalo [desde, hasta] entre palabras sin tiempo, según su largo."""
    if not palabras:
        return
    pesos = [len(p["norm"]) + 1 for p in palabras]
    total, t = sum(pesos), desde
    for p, peso in zip(palabras, pesos):
        dur = (hasta - desde) * peso / total
        p["inicio"], p["fin"] = t, t + dur
        t += dur


def alinear_bloque(palabras_guion, transcritas, inicio_bloque, fin_bloque):
    a = [p["norm"] for p in palabras_guion]
    b = [p["norm"] for p in transcritas]
    for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(m.size):
            g, t = palabras_guion[m.a + k], transcritas[m.b + k]
            g["inicio"], g["fin"], g["ancla"] = t["inicio"], t["fin"], True

    # Rellena los huecos entre palabras ancladas
    i, n = 0, len(palabras_guion)
    while i < n:
        if palabras_guion[i].get("ancla"):
            i += 1
            continue
        j = i
        while j < n and not palabras_guion[j].get("ancla"):
            j += 1
        desde = palabras_guion[i - 1]["fin"] if i > 0 else inicio_bloque
        hasta = palabras_guion[j]["inicio"] if j < n else fin_bloque
        repartir(palabras_guion[i:j], desde, max(desde + 0.05 * (j - i), hasta))
        i = j

    # Que ninguna palabra se salga de su bloque ni se monte sobre la anterior
    previo = inicio_bloque
    for p in palabras_guion:
        p["inicio"] = min(max(p["inicio"], previo, inicio_bloque), fin_bloque)
        p["fin"] = min(max(p["fin"], p["inicio"] + 0.05), fin_bloque)
        previo = p["inicio"]


def generar(carpeta):
    carpeta = Path(carpeta)
    voz = json.loads((carpeta / "voz_bloques.json").read_text(encoding="utf-8"))
    print("  Transcribiendo con faster-whisper small (la primera vez descarga ~500 MB)...")
    transcritas = transcribir(carpeta / "voz.wav")

    salida = {"duracion_voz": voz["duracion"], "bloques": voz["bloques"], "palabras": []}
    total = anclas = 0
    bloques = {b["id"]: b for b in guion.leer(carpeta)}
    # Se alinea frase por frase: la etapa de voz sabe exactamente dónde empieza y termina cada una,
    # así ninguna palabra puede "saltar" por encima de una [pausa].
    for tramo in voz["frases"]:
        ini, fin = tramo["inicio"], tramo["fin"]
        del_tramo = [t for t in transcritas if ini - 0.1 <= (t["inicio"] + t["fin"]) / 2 <= fin + 0.1]
        palabras = [dict(p, norm=guion.normalizar(p["texto"]), bloque=tramo["bloque"])
                    for p in bloques[tramo["bloque"]]["palabras"] if p["frase"] == tramo["frase"]]
        alinear_bloque(palabras, del_tramo, ini, fin)
        palabras[0]["inicio"] = ini  # la primera palabra arranca justo con la frase (dato exacto)
        total += len(palabras)
        anclas += sum(1 for p in palabras if p.get("ancla"))
        for p in palabras:
            salida["palabras"].append({
                "texto": p["texto"], "norm": p["norm"], "bloque": p["bloque"], "enfasis": p["enfasis"],
                "inicio": round(p["inicio"], 3), "fin": round(p["fin"], 3), "ancla": bool(p.get("ancla")),
            })

    salida["anclas"] = f"{anclas}/{total}"
    (carpeta / "tiempos.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  tiempos.json listo. Palabras con tiempo medido por Whisper: {anclas} de {total}")
