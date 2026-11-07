"""Tiempos de cada palabra con faster-whisper (MIT): words.json y phrases.json.

Uso:  .venv\\Scripts\\python.exe motor\\v1\\tiempos.py videos\\<carpeta>

- Whisper escucha voz.wav y da el momento real de cada palabra (lógica copiada de src/tiempos.py).
- El texto oficial es el del guion: Whisper solo dice CUÁNDO suena cada palabra.
- Se alinea frase por frase con los tramos exactos de voz_frases.json (ninguna palabra salta una pausa).
- Palabras que Whisper no reconoce (ej. "parce") se reparten entre sus vecinas medidas, según su largo.
- RESPALDO: si Whisper falla, se reparte cada frase por sílabas (como en la nube) y se avisa.
Salida:
  words.json   [{w, s, e, f0, f1, i (frase), bloque, enfasis, ancla}]  (s, e en segundos; f0, f1 en cuadros)
  phrases.json {duration, fps, frames, anclas, phrases: [{i, text, bloque, s, e, f0, f1}]}
"""
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def transcribir(ruta_wav, aj):
    from faster_whisper import WhisperModel
    modelo = WhisperModel(aj["whisper"]["modelo"], device="cpu", compute_type="int8", download_root=aj["whisper"]["carpeta"])
    segs, _ = modelo.transcribe(str(ruta_wav), language="es", word_timestamps=True, beam_size=5, vad_filter=False)
    out = []
    for s in segs:
        for w in s.words:
            n = comun.normalizar(w.word)
            if n:
                out.append({"norm": n, "inicio": w.start, "fin": w.end})
    return out


def repartir(palabras, desde, hasta):
    """Reparte [desde, hasta] entre palabras sin tiempo, según su largo."""
    if not palabras:
        return
    pesos = [len(p["norm"]) + 1 for p in palabras]
    total, t = sum(pesos), desde
    for p, peso in zip(palabras, pesos):
        d = (hasta - desde) * peso / total
        p["inicio"], p["fin"] = t, t + d
        t += d


def alinear(palabras, transcritas, ini, fin):
    a = [p["norm"] for p in palabras]
    b = [t["norm"] for t in transcritas]
    # una palabra con cambio {G|ge} vale con cualquiera de sus dos formas
    for i, p in enumerate(palabras):
        if p.get("alt") and p["alt"] in b and p["norm"] not in b:
            a[i] = p["alt"]
    for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(m.size):
            g, t = palabras[m.a + k], transcritas[m.b + k]
            g["inicio"], g["fin"], g["ancla"] = t["inicio"], t["fin"], True
    i, n = 0, len(palabras)
    while i < n:
        if palabras[i].get("ancla"):
            i += 1
            continue
        j = i
        while j < n and not palabras[j].get("ancla"):
            j += 1
        desde = palabras[i - 1]["fin"] if i > 0 else ini
        hasta = palabras[j]["inicio"] if j < n else fin
        repartir(palabras[i:j], desde, max(desde + 0.05 * (j - i), hasta))
        i = j
    previo = ini
    for p in palabras:
        p["inicio"] = min(max(p["inicio"], previo, ini), fin)
        p["fin"] = min(max(p["fin"], p["inicio"] + 0.05), fin)
        previo = p["inicio"]


def por_silabas(palabras, ini, fin):
    """Respaldo: reparte la frase según los grupos de vocales de cada palabra."""
    pesos = [max(1, len(re.findall(r"[aeiouáéíóúü]+", p["texto"].lower()))) for p in palabras]
    tot, c = sum(pesos), ini
    for p, k in zip(palabras, pesos):
        d = (fin - ini) * k / tot
        p["inicio"], p["fin"] = c, c + d
        c += d


def generar(carpeta):
    carpeta = Path(carpeta)
    aj = comun.ajustes(carpeta)
    fps = aj["fps"]
    voz = json.loads((carpeta / "voz_frases.json").read_text(encoding="utf-8"))
    frases = comun.leer_guion(carpeta, aj)
    if len(frases) != len(voz["frases"]):
        raise SystemExit("guion.md cambió después de generar la voz: vuelve a correr voz.py")
    try:
        print(f"  Whisper {aj['whisper']['modelo']} escuchando voz.wav...")
        transcritas, metodo = transcribir(carpeta / "voz.wav", aj), "whisper"
    except Exception as e:  # respaldo
        print(f"  AVISO: Whisper falló ({e}); uso el reparto por sílabas (menos preciso)")
        transcritas, metodo = None, "silabas"

    words, phrases, anclas, total = [], [], 0, 0
    for fr, tr in zip(frases, voz["frases"]):
        ini, fin = tr["inicio"], tr["fin"]
        pals = [{"texto": p["texto"], "norm": comun.normalizar(p["texto"]), "alt": comun.normalizar(p["voz"]) if p["cambio"] else None,
                 "enfasis": p["enfasis"]} for p in fr["palabras"]]
        if transcritas is None:
            por_silabas(pals, ini, fin)
        else:
            del_tramo = [t for t in transcritas if ini - 0.1 <= (t["inicio"] + t["fin"]) / 2 <= fin + 0.1]
            alinear(pals, del_tramo, ini, fin)
            pals[0]["inicio"] = ini
        total += len(pals); anclas += sum(1 for p in pals if p.get("ancla"))
        for p in pals:
            words.append({"w": p["texto"], "s": round(p["inicio"], 3), "e": round(p["fin"], 3),
                          "f0": round(p["inicio"] * fps), "f1": round(p["fin"] * fps), "i": tr["i"], "bloque": fr["bloque"],
                          "enfasis": p["enfasis"], "ancla": bool(p.get("ancla"))})
        phrases.append({"i": tr["i"], "text": fr["texto"], "bloque": fr["bloque"], "s": ini, "e": fin,
                        "f0": round(ini * fps), "f1": round(fin * fps)})
    dur = voz["duracion"]
    salida = {"duration": dur, "fps": fps, "frames": round(dur * fps), "metodo": metodo, "anclas": f"{anclas}/{total}", "phrases": phrases}
    (carpeta / "phrases.json").write_text(json.dumps(salida, indent=1, ensure_ascii=False), encoding="utf-8")
    (carpeta / "words.json").write_text("[\n" + ",\n".join(json.dumps(w, ensure_ascii=False) for w in words) + "\n]\n", encoding="utf-8")
    for p in phrases:
        print(f"  {p['s']:6.2f}-{p['e']:6.2f}  f{p['f0']:4d}-{p['f1']:4d}  {p['text']}")
    print(f"  duración {dur:.2f} s = {salida['frames']} cuadros | método {metodo} | palabras medidas {anclas}/{total}")
    return salida


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    generar(sys.argv[1])
