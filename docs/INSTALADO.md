# Instalado — guía de instalación de ParchanCol

Qué hay que tener instalado para que funcionen las dos líneas de producción:

- **MVP** (videos con voz clonada del dueño): `src/` → `.venv\Scripts\python -m src.producir videos/<carpeta>`
- **Motor de caricatura** (Kokoro + personajes 2D en 3D): `motor/v1/` → ver `motor/GUIA_MOTOR.md`

Todo es gratuito y con licencia que permite uso comercial (detalle en `motor/LICENCIAS.md` y `assets/fonts/LICENCIAS.md`).
Equipo de referencia: Windows 11, i5-1035G1, sin GPU dedicada, 12 GB RAM. Todo corre en CPU.

## 1. Programas del sistema

| Programa | Versión probada | Para qué | Licencia | Cómo instalar |
|---|---|---|---|---|
| Git | 2.52.0 | control de versiones | GPL-2.0 (herramienta) | `winget install Git.Git` |
| uv | 0.13.7 | crea y maneja el `.venv` (el `.venv` **no tiene pip**) | MIT / Apache-2.0 | `winget install astral-sh.uv` |
| Python | 3.11 (dentro del `.venv`) | voz, tiempos, subtítulos, escenas | PSF | lo descarga uv (paso 2) |
| FFmpeg | 9.0.2 (build de gyan.dev) | escenas y render final; tiene que estar en el PATH | GPL (herramienta externa, no se distribuye) | `winget install Gyan.FFmpeg` |
| Node.js | 24.18.0 | render del motor con Playwright | MIT | `winget install OpenJS.NodeJS` |

Después de instalar, cerrar y abrir la terminal, y comprobar: `git --version`, `uv --version`, `ffmpeg -version`, `node -v`.

> Ojo: el Python del sistema (3.10) **no** se usa. Siempre `.venv\Scripts\python.exe`.

## 2. Entorno de Python (`.venv`)

Desde la raíz del proyecto:

```
uv venv --python 3.11 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

| Paquete | Versión | Para qué | Licencia |
|---|---|---|---|
| chatterbox-tts | 0.1.7 | voz clonada del dueño (MVP) | MIT |
| torch / torchaudio | 2.6.0+cpu (llegan como dependencia de Chatterbox) | motor de Chatterbox | BSD-3-Clause |
| faster-whisper | 1.2.1 | tiempos por palabra y control de calidad de la voz | MIT |
| numpy | 1.26.4 | audio | BSD-3-Clause |
| sherpa-onnx + sherpa-onnx-core | **1.13.8 (fija)** | Kokoro TTS del motor | Apache-2.0 |

- Si torch se instala en versión con CUDA (pesada e inútil aquí), forzar la de CPU:
  `uv pip install --python .venv\Scripts\python.exe torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu`
  (recomendado, no verificado: el .venv actual tiene torch 2.6.0 CPU)
- **sherpa-onnx tiene que quedarse en la 1.13.8.** La 2.0.1 quitó espeak de Kokoro y solo pronuncia con léxicos
  (inglés y chino); en español se saltaba casi todas las palabras.

## 3. Motor de caricatura (Node + Chromium)

```
cd motor
npm install
npx playwright install chromium
```

| Qué | Versión | Ruta | Licencia |
|---|---|---|---|
| Playwright (npm) | 1.65.0 | `motor/node_modules/playwright` | Apache-2.0 |
| Chromium para Playwright | build 1254 (158.0.8127.18) + headless shell 1254 | `%LOCALAPPDATA%\ms-playwright\` | BSD-3-Clause |
| three.js | incluido en el repo | `motor/v1/web/lib/three.module.js` | MIT |

## 4. Modelos (no van en git)

| Modelo | Ruta | Tamaño aprox. | Cómo se obtiene | Licencia |
|---|---|---|---|---|
| Chatterbox Multilingual | `modelos/huggingface/` | varios GB | se descarga solo la primera vez que corre la etapa de voz del MVP | MIT |
| pkuseg (lo usa Chatterbox) | `modelos/pkuseg/` | pequeño | automático | MIT |
| Whisper `small` | `modelos/whisper/` | ~480 MB | automático (faster-whisper) | MIT |
| Kokoro `kokoro-multi-lang-v1_0` | `motor/modelos/kokoro-multi-lang-v1_0/` | ~350 MB | **manual**: descargar `kokoro-multi-lang-v1_0.tar.bz2` del release `tts-models` de k2-fsa/sherpa-onnx en GitHub y descomprimir ahí | Apache-2.0 (+ espeak-ng-data GPL-3.0) |

La primera corrida necesita internet y tarda más por las descargas. Después todo funciona sin conexión.

## 5. Archivos propios que no están en git

- `assets/voz_referencia/`: grabación de la voz del dueño para clonar con Chatterbox (MVP).
- `.env`: solo si algún día hace falta una clave. Copiar de `.env.example`. Nunca se sube ni se pega en el chat.

Las fuentes (Archivo Black, Inter SemiBold, licencia OFL) **sí** están en el repo, en `assets/fonts/`.

## 6. Comprobación rápida

```
.venv\Scripts\python.exe -c "import chatterbox, faster_whisper, sherpa_onnx; print(sherpa_onnx.__version__)"
```
Debe imprimir `1.13.8`. Luego, una prueba del motor con `motor/v1/voz.py` (ver `motor/GUIA_MOTOR.md`).

## Notas del motor

- **Voz:** hablante 29 = `em_alex` (comprobado en los metadatos del modelo). También hay `ef_dora` (28) y `em_santa` (53) en español.
  Para español **no** se pasa léxico: solo `model`, `voices`, `tokens`, `data_dir` y `lang="es"`.
- **Prueba de voz (2026-11-07):** "Y ahora ya sabes, parce." → `motor/pruebas/voz.wav`, 1,95 s, 24 kHz,
  generada en 1,1 s en CPU. Whisper la transcribe completa (5/5 palabras). Volumen sin normalizar: −25,4 LUFS.
- Carpetas fuera de git (`.gitignore`): `.venv/`, `modelos/`, `entrada/`, `node_modules/`, `motor/modelos/`, `motor/pruebas/`,
  `out/`, `frames/`, `work/` y los `.wav`/`.mp4` intermedios de `videos/` (el `final.mp4` sí se sube).

_Última actualización: 2026-11-08._
