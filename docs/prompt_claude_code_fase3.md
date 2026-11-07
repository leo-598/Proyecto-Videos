# Prompt para Claude Code — Fase 3 (MVP: un video de punta a punta)

Pega esto en Claude Code, abierto dentro de la carpeta `Proyecto Videos`.
También puedes decirle: "Lee docs/prompt_claude_code_fase3.md y ejecútalo".

---

Eres el ingeniero del proyecto ParchanCol. Antes de nada, lee `CLAUDE.md` completo y respeta todas sus reglas. Trabaja y respóndeme siempre en español.

## Objetivo

Construir el MVP: producir UN video de punta a punta, en local, a partir de los archivos de
`videos/2026-11-07_porque_arcoiris-curvo/` (guion.md, fuentes.md, escenas.yaml, metadata.yaml, checklist.md).
No publiques nada. No uses servicios en la nube, claves ni bancos de imágenes.

## Mi equipo

- Windows, i5-1035G1, gráficos Intel UHD integrados (sin GPU dedicada), 12 GB de RAM.
- Ya instalado: Python 3.10.4 (global; no lo modifiques), FFmpeg 9.0.2 (build completo de gyan.dev, con libass y freetype) y Git.

## Instalaciones permitidas (gratuitas, licencia comercial; pídeme confirmación antes de cada una)

1. `uv` (Astral), para crear un entorno con **Python 3.11** en `.venv` dentro del proyecto, sin tocar el Python global.
2. Paquetes de Python: `chatterbox-tts` (Resemble AI, MIT) con PyTorch **solo CPU**, `faster-whisper` (MIT), `pillow`, `numpy`, `pyyaml`.
3. Fuentes Archivo Black e Inter (licencia OFL), desde el repositorio oficial de Google Fonts, en `assets/fonts/` junto con su archivo de licencia.
4. La primera ejecución descargará los pesos de Chatterbox Multilingual y el modelo "small" de faster-whisper. Guárdalos en `modelos/`, que está en .gitignore.

Si algo más resulta imprescindible, detente y pregúntame, con su licencia y su costo (debe ser 0).

## Paso 0: verificación de hechos (antes de escribir código)

Abre cada fuente sugerida en `fuentes.md`, confirma o corrige cada afirmación y marca la columna "Verificado".
Si alguna afirmación no se puede verificar, propón un cambio al guion y espera mi aprobación.
Después, pídeme el CONTROL 1: yo apruebo guion y fuentes, y tú cambias el estado en metadata.yaml a `guion_aprobado`.

## Arquitectura (simple y modular; un archivo por etapa en `src/`)

- `src/config.py`: carga `config/marca.yaml` (paleta, fuentes, zonas seguras) y `config/series.yaml`. Crea esos YAML a partir de CLAUDE.md.
- `src/voz.py`: Chatterbox Multilingual en CPU, idioma español.
  - Si existe un audio en `assets/voz_referencia/`, úsalo para clonar la voz; si no, usa la voz por defecto.
  - Lee `guion.md` sin las marcas de bloque ni de locución, convierte "[pausa]" en silencios cortos y genera por bloque, uniendo después.
  - Normaliza el volumen y guarda `voz.wav`.
- `src/tiempos.py`: faster-whisper "small", int8, CPU, idioma "es", con marcas de tiempo por palabra.
  - Alinea con el texto del guion (el texto oficial es el del guion, no la transcripción) y guarda `tiempos.json` con los tiempos de cada palabra y de cada bloque B1–B6.
- `src/escenas.py`: dibuja con Pillow cada escena de `escenas.yaml` (formas, líneas, arcos, gota, muñeco, sol, avión, tarjeta de cierre), con animaciones simples (aparecer, deslizar, escalar, trazo que crece).
  - Cada escena dura lo que dura su bloque según `tiempos.json`, y hay un cambio visual cada 1,5–2 s.
  - Genera los fotogramas a 30 fps y envíalos por tubería a FFmpeg; no guardes miles de PNG.
  - Siempre visibles: sello de serie arriba y texto de fuentes pequeño en B2–B5.
- `src/subtitulos.py`: archivo ASS palabra por palabra.
  - Inter Semibold, grande, blanco #F7F4EE con borde oscuro y la palabra actual en amarillo #FFC832.
  - Ubicado hacia el 60–65 % de la altura, fuera de las zonas de botones.
- `src/render.py`: FFmpeg une el video de escenas, la voz y los subtítulos ASS quemados.
  - Salida 1080×1920, 30 fps, H.264 yuv420p, `-preset veryfast`, AAC 192k y loudnorm a unos -14 LUFS.
  - Guarda `final.mp4`.
- `src/producir.py`: orquestador que se ejecuta como `python -m src.producir videos/<carpeta>`.
  - Corre cada etapa, salta las que ya tienen salida (si no se usa `--forzar`) y actualiza `estado` en metadata.yaml.
  - Registra el tiempo de cada etapa en `metricas/tiempos_produccion.csv`.
- Al terminar, propón en metadata.yaml el título y el texto para cada plataforma: YouTube (título de 60 caracteres o menos y descripción con las fuentes), TikTok, Instagram y Facebook. Los cuatro deben ser distintos entre sí, no copias.

## Reglas de código

- Simple, comentado en español, sin sobreingeniería. Nada de servicios externos.
- `git init` y commits pequeños con mensajes claros. Nunca subas `.env`, `.venv`, `modelos/` ni los audios y videos generados.
- Si un paso falla, explícame el error en lenguaje claro y propón la solución antes de instalar nada nuevo.

## Criterios de aceptación (verifícalos tú y dame el reporte)

1. `final.mp4` de 1080×1920 y 30 fps, cuya duración coincide con la voz más 2 s de cierre. Verifícalo con ffprobe.
2. Subtítulos sincronizados (desfase de 0,1 s o menos) y sin faltas de ortografía.
3. Nada importante en el 20 % inferior ni en el 15 % derecho de la pantalla.
4. Sello de serie, texto de fuentes y tarjeta de cierre presentes.
5. Reporte de tiempos por etapa. Si la voz con Chatterbox tarda más de 10 minutos para unos 40 s de audio, avísame y propón Kokoro (Apache 2.0) como alternativa.
6. Pásame el CONTROL 2: reviso el video, marco checklist.md y paso el estado a `revisado`.

Al final, resúmeme qué hiciste, qué falló, cuánto tardó cada etapa y qué mejorarías para la Fase 4.
