"""Voz del video con Kokoro (sherpa-onnx 1.13.8, Apache-2.0), hablante 29 = em_alex, en español.

Uso:  .venv\\Scripts\\python.exe motor\\v1\\voz.py videos\\<carpeta>

- Lee guion.md (ver comun.py) y genera cada frase por separado.
- Control de calidad de cada frase (adaptado de src/voz.py): Whisper la escucha y se compara con el guion.
  Si sobran palabras al final (cola inventada) se recortan; si faltan o cambian palabras
  (parecido < parecido_minimo) se regenera con otra velocidad. Si ninguna pasa, queda un AVISO.
- Guarda voz.wav (24 kHz, pico a -1 dB) y voz_frases.json (inicio y fin exactos de cada frase).
"""
import difflib
import json
import sys
import time
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def cargar_tts(aj):
    import sherpa_onnx
    K = comun.MODELOS / aj["voz"]["modelo"]
    if not (K / "model.onnx").exists():
        raise SystemExit(f"Falta el modelo Kokoro en {K} (ver docs/INSTALADO.md)")
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=str(K / "model.onnx"), voices=str(K / "voices.bin"), tokens=str(K / "tokens.txt"),
            data_dir=str(K / "espeak-ng-data"), lang=aj["voz"]["lang"], length_scale=1.0),
        num_threads=aj["voz"]["hilos"]))
    return sherpa_onnx.OfflineTts(cfg)


def recortar_silencio(a, sr):
    idx = np.where(np.abs(a) > 0.01)[0]
    if not len(idx):
        return a
    return a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.04 * sr)]


def guardar_wav(ruta, a, sr):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


def revisar(ruta_wav, a, sr, frase, oidor):
    """Whisper escucha la frase. Recorta palabras inventadas al final. Devuelve (audio, parecido, oído).
    Las palabras con cambio {mostrado|dicho} valen si Whisper oye cualquiera de las dos formas."""
    segs, _ = oidor.transcribe(str(ruta_wav), language="es", word_timestamps=True, beam_size=5)
    oidas = [w for s in segs for w in s.words if comun.normalizar(w.word)]
    opciones = [{comun.normalizar(p["texto"]), comun.normalizar(p["voz"])} - {""} for p in frase["palabras"]]
    opciones = [o for o in opciones if o]
    normas = [comun.normalizar(w.word) for w in oidas]
    # cada palabra oída se compara con la forma esperada que mejor le calza
    esperadas = [next(iter(o)) for o in opciones]
    for i, o in enumerate(opciones):
        for n in normas:
            if n in o:
                esperadas[i] = n
                break
    ultima, en_guion = -1, -1
    for m in difflib.SequenceMatcher(None, esperadas, normas, autojunk=False).get_matching_blocks():
        if m.size:
            ultima, en_guion = m.b + m.size - 1, m.a + m.size - 1
    ultima += len(esperadas) - 1 - en_guion
    if 0 <= ultima < len(oidas) - 1:
        corte = min(oidas[ultima].end + 0.15, oidas[ultima + 1].start)
        a = a[: int(corte * sr)]
        normas = normas[: ultima + 1]
    parecido = difflib.SequenceMatcher(None, esperadas, normas, autojunk=False).ratio()
    return a, parecido, " ".join(w.word.strip() for w in oidas[: len(normas)])


def generar(carpeta):
    carpeta = Path(carpeta)
    aj = comun.ajustes(carpeta)
    frases = comun.leer_guion(carpeta, aj)
    if not frases:
        raise SystemExit("guion.md no tiene frases para la voz")
    trabajo = carpeta / "work" / "tts"
    trabajo.mkdir(parents=True, exist_ok=True)
    print(f"  Kokoro: hablante {aj['voz']['sid']}, {len(frases)} frases")
    tts = cargar_tts(aj)
    from faster_whisper import WhisperModel
    oidor = WhisperModel(aj["whisper"]["modelo"], device="cpu", compute_type="int8", download_root=aj["whisper"]["carpeta"])

    sr, partes, tramos, avisos, t = None, [], [], [], 0.0
    t0 = time.time()
    for i, fr in enumerate(frases):
        escalas = [aj["voz"]["escala_tiempo"]] + list(aj["voz"]["reintentos_escala"])
        mejor = None
        for k, esc in enumerate(escalas):
            audio = tts.generate(fr["voz"], sid=aj["voz"]["sid"], speed=1.0 / esc)
            sr = audio.sample_rate
            a = recortar_silencio(np.array(audio.samples, dtype=np.float32), sr)
            ruta = trabajo / f"p{i:02d}.wav"
            guardar_wav(ruta, a, sr)
            a, parecido, oido = revisar(ruta, a, sr, fr, oidor)
            print(f"  {fr['bloque']} p{i:02d} intento {k + 1}: parecido {parecido:.2f} -> \"{oido}\"")
            if mejor is None or parecido > mejor[1]:
                mejor = (a, parecido, oido)
            if parecido >= aj["voz"]["parecido_minimo"]:
                break
        a, parecido, oido = mejor
        guardar_wav(trabajo / f"p{i:02d}.wav", a, sr)
        if parecido < aj["voz"]["parecido_minimo"]:
            avisos.append(f"p{i:02d} \"{fr['texto']}\" (parecido {parecido:.2f}, se oyó: \"{oido}\")")
        if i == 0:
            partes.append(np.zeros(int(aj["voz"]["inicio"] * sr), np.float32)); t = aj["voz"]["inicio"]
        tramos.append({"i": i, "bloque": fr["bloque"], "texto": fr["texto"], "inicio": round(t, 3),
                       "fin": round(t + len(a) / sr, 3), "parecido": round(parecido, 2)})
        partes.append(a); t += len(a) / sr
        partes.append(np.zeros(int(fr["pausa"] * sr), np.float32)); t += fr["pausa"]

    y = np.concatenate(partes)
    y = y / max(1e-6, float(np.abs(y).max())) * 0.89
    guardar_wav(carpeta / "voz.wav", y, sr)
    datos = {"duracion": round(len(y) / sr, 3), "sr": sr, "frases": tramos, "avisos": avisos}
    (carpeta / "voz_frases.json").write_text(json.dumps(datos, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  voz.wav listo: {datos['duracion']:.2f} s ({time.time() - t0:.0f} s de trabajo)")
    if avisos:
        print("  AVISO: estas frases no quedaron iguales al guion; escúchalas:")
        for x in avisos:
            print("    - " + x)
    return datos


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    generar(sys.argv[1])
