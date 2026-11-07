"""Etapa 4 — Voz con Chatterbox Multilingual (MIT), en CPU, en español.

- Si hay un audio en assets/voz_referencia/, clona esa voz. Si no, usa la voz por defecto.
- Cada frase pasa un control con Whisper: se recortan palabras inventadas al final y
  se regenera (otra semilla) si no coincide con el guion.
- Genera cada frase por separado, pone silencios en cada [pausa] y entre bloques, y une todo.
- Guarda voz.wav (pico normalizado; el volumen final -14 LUFS se ajusta en el render)
  y voz_bloques.json (dónde empieza y termina cada bloque y cada frase, en segundos).
"""
import json
import os
from pathlib import Path

from src import config, guion

EXTENSIONES_AUDIO = (".wav", ".mp3", ".flac", ".m4a", ".ogg")


def buscar_referencia():
    carpeta = config.RAIZ / "assets" / "voz_referencia"
    if not carpeta.exists():
        return None
    audios = sorted(p for p in carpeta.iterdir() if p.suffix.lower() in EXTENSIONES_AUDIO)
    return audios[0] if audios else None


def revisar(wav, sr, frase, oidor):
    """Control de calidad de una frase: Whisper escucha el audio y se compara con el guion.

    - Si el modelo siguió hablando después de la frase (palabras inventadas al final),
      se corta el audio justo después de la última palabra del guion.
    - Devuelve (audio, parecido 0..1, lo que se oyó). Parecido = qué tanto coinciden
      las palabras oídas con las del guion (1 = idénticas).
    """
    import difflib

    import librosa
    import numpy as np

    audio16 = librosa.resample(wav, orig_sr=sr, target_sr=16000)
    segmentos, _ = oidor.transcribe(audio16, language="es", word_timestamps=True, beam_size=5)
    oidas = [w for s in segmentos for w in s.words if guion.normalizar(w.word)]
    esperadas = [guion.normalizar(p) for p in frase.split() if guion.normalizar(p)]
    normas = [guion.normalizar(w.word) for w in oidas]

    # Última palabra oída que corresponde a una palabra del guion (en_guion = su posición en el guion)
    ultima, en_guion = -1, -1
    for m in difflib.SequenceMatcher(None, esperadas, normas, autojunk=False).get_matching_blocks():
        if m.size:
            ultima, en_guion = m.b + m.size - 1, m.a + m.size - 1
    # Las palabras del guion que faltan después de esa (ej. "parce", que Whisper no conoce)
    # se respetan: solo se corta lo que sobra DESPUÉS de cubrirlas.
    ultima += len(esperadas) - 1 - en_guion
    if 0 <= ultima < len(oidas) - 1:
        # Sobran palabras al final: cortar antes de que empiecen
        corte = min(oidas[ultima].end + 0.15, oidas[ultima + 1].start)
        wav = wav[: int(corte * sr)]
        normas = normas[: ultima + 1]

    parecido = difflib.SequenceMatcher(None, esperadas, normas, autojunk=False).ratio()
    oido = " ".join(w.word.strip() for w in oidas[: len(normas)])
    return wav.astype(np.float32), parecido, oido


def generar(carpeta):
    carpeta = Path(carpeta)
    ajustes = config.marca()["voz"]

    # Los pesos del modelo se guardan en modelos/ (fuera de git). Debe ir antes del import.
    os.environ.setdefault("HF_HOME", str(config.MODELOS / "huggingface"))
    os.environ.setdefault("PKUSEG_HOME", str(config.MODELOS / "pkuseg"))   # lo usa Chatterbox internamente
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    import librosa
    import numpy as np
    import soundfile as sf
    import perth
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    # Decisión del dueño (2026-11-07): sin marca de agua. La marca de Perth necesita
    # pkg_resources (setuptools), que no está en .venv. DummyWatermarker deja el audio igual.
    perth.PerthImplicitWatermarker = perth.DummyWatermarker

    torch.manual_seed(ajustes["semilla"])
    print("  Cargando Chatterbox Multilingual (la primera vez descarga ~3 GB)...")
    modelo = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    sr = modelo.sr

    referencia = buscar_referencia()
    if referencia:
        print(f"  Clonando la voz de: {referencia.name}")
        modelo.prepare_conditionals(str(referencia), exaggeration=ajustes["exageracion"])
    else:
        print("  Sin audio en assets/voz_referencia/: uso la voz por defecto de Chatterbox.")

    def silencio(segundos):
        return np.zeros(int(sr * segundos), dtype=np.float32)

    from faster_whisper import WhisperModel
    oidor = WhisperModel("small", device="cpu", compute_type="int8",
                         download_root=str(config.MODELOS / "whisper"))

    partes, bloques_tiempo, frases_tiempo, cursor, avisos = [], [], [], 0, []
    bloques = guion.leer(carpeta)
    for i, bloque in enumerate(bloques):
        inicio = cursor
        for j, frase in enumerate(bloque["frases"]):
            print(f"  {bloque['id']}: {frase}")
            mejor = None
            for intento in range(ajustes["intentos"]):
                torch.manual_seed(ajustes["semilla"] + 1000 * intento + 17 * len(partes))
                crudo = modelo.generate(
                    frase,
                    language_id=ajustes["idioma"],
                    exaggeration=ajustes["exageracion"],
                    cfg_weight=ajustes["cfg"],
                    temperature=ajustes["temperatura"],
                ).squeeze(0).numpy().astype(np.float32)
                revisado, puntaje, oido = revisar(crudo, sr, frase, oidor)
                print(f"    intento {intento + 1}: parecido {puntaje:.2f} -> \"{oido}\"")
                if mejor is None or puntaje > mejor[1]:
                    mejor = (revisado, puntaje)
                if puntaje >= ajustes["parecido_minimo"]:
                    break
            wav, puntaje = mejor
            if puntaje < ajustes["parecido_minimo"]:
                avisos.append(f"{bloque['id']}: \"{frase}\" (parecido {puntaje:.2f})")
            # Quita el silencio que el modelo deja al principio y al final
            wav, _ = librosa.effects.trim(wav, top_db=35)
            wav = np.concatenate([silencio(0.06), wav, silencio(0.06)])
            if j > 0:
                partes.append(silencio(ajustes["pausa_corta"]))
                cursor += len(partes[-1])
            frases_tiempo.append({"bloque": bloque["id"], "frase": j,
                                  "inicio": (cursor + int(sr * 0.06)) / sr,      # sin el relleno de 0,06 s
                                  "fin": (cursor + len(wav) - int(sr * 0.06)) / sr})
            partes.append(wav)
            cursor += len(wav)
        bloques_tiempo.append({"id": bloque["id"], "inicio": inicio / sr, "fin": cursor / sr})
        if i < len(bloques) - 1:
            partes.append(silencio(ajustes["pausa_bloque"]))
            cursor += len(partes[-1])

    audio = np.concatenate(partes)
    audio = audio / max(1e-6, float(np.abs(audio).max())) * 0.89  # pico a -1 dB
    sf.write(carpeta / "voz.wav", audio, sr, subtype="PCM_16")
    datos = {"duracion": len(audio) / sr, "bloques": bloques_tiempo, "frases": frases_tiempo}
    (carpeta / "voz_bloques.json").write_text(json.dumps(datos, indent=2), encoding="utf-8")
    print(f"  voz.wav listo: {datos['duracion']:.2f} s")
    if avisos:
        print("  AVISO: estas frases no quedaron iguales al guion; escúchalas en el CONTROL 2:")
        for a in avisos:
            print(f"    - {a}")
