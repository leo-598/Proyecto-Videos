"""Etapa 4 — Voz con Chatterbox Multilingual (MIT), en CPU, en español.

- Si hay un audio en assets/voz_referencia/, clona esa voz. Si no, usa la voz por defecto.
- Genera cada frase por separado, pone silencios en cada [pausa] y entre bloques, y une todo.
- Guarda voz.wav (pico normalizado; el volumen final -14 LUFS se ajusta en el render)
  y voz_bloques.json (dónde empieza y termina cada bloque, en segundos).
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


def generar(carpeta):
    carpeta = Path(carpeta)
    ajustes = config.marca()["voz"]

    # Los pesos del modelo se guardan en modelos/ (fuera de git). Debe ir antes del import.
    os.environ.setdefault("HF_HOME", str(config.MODELOS / "huggingface"))
    import librosa
    import numpy as np
    import soundfile as sf
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

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

    partes, bloques_tiempo, cursor = [], [], 0
    bloques = guion.leer(carpeta)
    for i, bloque in enumerate(bloques):
        inicio = cursor
        for j, frase in enumerate(bloque["frases"]):
            print(f"  {bloque['id']}: {frase}")
            wav = modelo.generate(
                frase,
                language_id=ajustes["idioma"],
                exaggeration=ajustes["exageracion"],
                cfg_weight=ajustes["cfg"],
                temperature=ajustes["temperatura"],
            ).squeeze(0).numpy().astype(np.float32)
            # Quita el silencio que el modelo deja al principio y al final
            wav, _ = librosa.effects.trim(wav, top_db=35)
            wav = np.concatenate([silencio(0.06), wav, silencio(0.06)])
            if j > 0:
                partes.append(silencio(ajustes["pausa_corta"]))
                cursor += len(partes[-1])
            partes.append(wav)
            cursor += len(wav)
        bloques_tiempo.append({"id": bloque["id"], "inicio": inicio / sr, "fin": cursor / sr})
        if i < len(bloques) - 1:
            partes.append(silencio(ajustes["pausa_bloque"]))
            cursor += len(partes[-1])

    audio = np.concatenate(partes)
    audio = audio / max(1e-6, float(np.abs(audio).max())) * 0.89  # pico a -1 dB
    sf.write(carpeta / "voz.wav", audio, sr, subtype="PCM_16")
    datos = {"duracion": len(audio) / sr, "bloques": bloques_tiempo}
    (carpeta / "voz_bloques.json").write_text(json.dumps(datos, indent=2), encoding="utf-8")
    print(f"  voz.wav listo: {datos['duracion']:.2f} s")
