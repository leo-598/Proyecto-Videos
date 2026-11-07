# Instalado — motor de caricatura

Registro de todo lo instalado para el motor. Licencias completas en `motor/LICENCIAS.md`.

| Qué | Versión | Ruta | Licencia | Fecha |
|---|---|---|---|---|
| Playwright (npm) | 1.65.0 | `motor/node_modules/playwright` (`motor/package.json`) | Apache-2.0 | 2026-11-07 |
| Chromium para Playwright | build 1254 (158.0.8127.18) + headless shell 1254 | `%LOCALAPPDATA%\ms-playwright\` | BSD-3-Clause | 2026-11-07 |
| numpy | 1.26.4 (ya estaba) | `.venv` | BSD-3-Clause | — |
| faster-whisper | 1.2.1 (ya estaba, lo usa el MVP) | `.venv`; modelo `small` en `modelos/whisper/` | MIT | — |
| sherpa-onnx + sherpa-onnx-core (pip) | **1.13.8** (versión fija) | `.venv` | Apache-2.0 | 2026-11-07 |
| Modelo Kokoro `kokoro-multi-lang-v1_0` | v1.0 (release `tts-models` de k2-fsa) | `motor/modelos/kokoro-multi-lang-v1_0/` (~350 MB) | Apache-2.0 (+ espeak-ng-data GPL-3.0) | 2026-11-07 |

## Notas

- **sherpa-onnx tiene que quedarse en la 1.13.8.** La 2.0.1 (la última) quitó espeak de Kokoro y solo
  pronuncia con léxicos (inglés y chino). En español se saltaba casi todas las palabras. La 1.13.8 es
  la misma que se usó en la nube. Instalar con: `uv pip install --python .venv\Scripts\python.exe "sherpa-onnx==1.13.8"`
  (el `.venv` lo maneja uv y no tiene pip).
- **Voz:** hablante 29 = `em_alex` (comprobado en los metadatos del modelo). También hay `ef_dora` (28) y `em_santa` (53) en español.
  Para español **no** se pasa léxico: solo `model`, `voices`, `tokens`, `data_dir` y `lang="es"`.
- **Prueba de voz (2026-11-07):** "Y ahora ya sabes, parce." → `motor/pruebas/voz.wav`, 1,95 s, 24 kHz,
  generada en 1,1 s en CPU. Whisper la transcribe completa (5/5 palabras). Volumen sin normalizar: −25,4 LUFS.
- Carpetas fuera de git (`.gitignore`): `entrada/`, `node_modules/`, `motor/modelos/`, `motor/pruebas/`, `out/`, `frames/`.
