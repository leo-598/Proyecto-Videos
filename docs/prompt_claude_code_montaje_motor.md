# Prompt para Claude Code: montaje del motor fijo de caricatura (Opción B)

> Úsalo en una sesión nueva de Claude Code, abierta en `C:\Users\EQUIPO\Desktop\Proyecto Videos`, con el modelo **Opus**.
> Antes de empezar, pon `proyecto_piedra_GI.zip` y `cartoon-short-kit.zip` en la carpeta `entrada/` del proyecto.

---

Hola. Vamos a montar el **motor fijo** para producir los videos de caricatura de ParchanCol (personajes 2D dentro de un mundo 3D). La meta es que cada video nuevo gaste los menos tokens posibles: en las sesiones de video solo vas a escribir la historia y los sonidos, nunca el motor.

## Reglas
- Lee `CLAUDE.md` primero y respeta todas sus reglas: todo en español, explicaciones simples y presupuesto USD 0.
- **Trabaja por etapas.** Al final de cada etapa te detienes, me cuentas el resultado en pocas líneas y esperas mi "OK" para seguir.
- **No toques el pipeline del MVP** que está en `src/`. Puedes reutilizar ideas o funciones de ahí, pero copiándolas a `motor/`.
- Todo lo que instales tiene que ser gratis y permitir uso comercial. Si algo no cumple, me consultas antes.
- Lleva un registro de lo que instales, con versión, ruta y licencia, en `docs/INSTALADO.md`.
- **No termines el render del video "La piedra que dice GI".** Ese video se termina en otro chat. Aquí solo se usa como material para la prueba de velocidad.

## Etapa 0: diagnóstico y plan (sin instalar nada)
1. Verifica estas versiones: Node.js (debe ser 22.6 o más), Python del `.venv`, FFmpeg, Git y Git Bash.
2. Descomprime los dos .zip en `entrada/_extraido/`.
3. Compara el motor del kit con el del proyecto. **El del proyecto es el más nuevo:** tiene `main.js`, `roman.js`, `toonbase.js` y `toon.js` modificados.
4. Dame un plan corto de las etapas 1 a 4 y espera mi OK.

## Etapa 1: instalación
Instala lo siguiente y anótalo en `docs/INSTALADO.md`:
- **Playwright con Chromium**, en `motor/` (`npm i playwright` y `npx playwright install chromium`).
- **numpy** en el `.venv`, si no está.
- **TTS Kokoro con sherpa-onnx.** Prefiere el paquete de pip `sherpa-onnx` dentro del `.venv`. Si falla, usa los binarios de Windows de los releases de GitHub de k2-fsa/sherpa-onnx.
- **El modelo `kokoro-multi-lang-v1_0`**, de los releases "tts-models" de k2-fsa/sherpa-onnx, guardado en `motor/modelos/`.
- **Prueba de voz:** hablante 29 (`em_alex`) con `lang=es` y la frase "Y ahora ya sabes, parce." El resultado va en `motor/pruebas/voz.wav`.
- **Licencias:** confirma la licencia de mromidev/claude-animated-shorts, de donde viene `toonbase.js`. Según Trendshift es MIT, pero hay que verlo en su archivo LICENSE. Copia esa licencia, la de three.js, la de sherpa-onnx y la de Kokoro a `motor/LICENCIAS.md`.

## Etapa 2: motor congelado `motor/v1/`
- **Motor web:** `index.html`, `main.js`, `toon.js`, `paint.js`, `motion.js`, `roman.js` y `lib/three.module.js`, tomados del proyecto de la piedra. No copies los archivos de depuración (`dbg.mjs`, `castshot.mjs`, `stills/test`).
- **`render.mjs` adaptado a Windows y a la tarjeta gráfica:**
  - Quita SwiftShader y prueba ANGLE con D3D11 (`--use-angle=d3d11`, `--ignore-gpu-blocklist`).
  - Compara el modo headless con una ventana visible y quédate con el más rápido.
  - Renderiza por bloques de unos 300 cuadros, reiniciando el navegador entre bloques (en la nube se cerró solo en el cuadro 493).
  - Activa por defecto la reanudación (`RESUME`).
  - Agrega un modo **previa**: 540×960 y un cuadro de cada tres.
  - Escribe el avance en `out/render.log`, con una línea final que diga: cuadros hechos, total y s/cuadro.
- **Pasa los scripts de bash a Python** (`finish.sh` y `setup.sh` → `finish.py` y `nuevo_video.py`) para que funcionen en Windows sin Git Bash.
- **Audio por datos:** separa de `audio.py` lo que es motor (sintetizador de cumbia, efectos, dron, mezcla con la música a −6 dB de la voz) de lo que cambia en cada video (`sonidos.json`, con la tabla de efectos). Haz lo mismo con `tts_build.py` y `timing.py`, que leen `guion.md` y sacan `words.json` y `phrases.json`.
- **Acabado (`finish.py`):**
  - Une los cuadros, el audio y la normalización a −14 LUFS.
  - Agrega **solo subtítulos y cierre.** No lleva sello de serie.
  - Los subtítulos van palabra por palabra en formato ASS, con Inter SemiBold de `assets/fonts/`, la palabra clave en #FFC832 y texto #F7F4EE.
  - Respeta las zonas seguras: nada importante en el 20 % inferior ni en el 15 % derecho.
  - El cierre dura 2 s y dice "ParchanCol", con "Col" en amarillo, en Archivo Black.
  - Si sirve, reutiliza la lógica de subtítulos del MVP (`src/`).
- **`biblioteca/`:** saca del `story.js` de la piedra los personajes y escenarios reutilizables (narrador costeño, aldeanos, piedra, muelle, plaza de zócalos, embalse, atardecer) y ponlos en módulos que se puedan importar. Guarda ese `story.js` como ejemplo en `biblioteca/ejemplos/piedra_GI.js`.

## Etapa 3: guía y skill
- **`motor/GUIA_MOTOR.md`, de una página como máximo:**
  - Estructura de `story.js`.
  - Personajes y escenarios de la biblioteca, con sus parámetros.
  - Gestos y expresiones.
  - Movimientos de cámara.
  - Cómo se sincroniza con `words.json`.
  - Formato de `sonidos.json`.
  - Una toma de ejemplo.
- **`.claude/skills/video-cartoon/SKILL.md`**, con el flujo de cada video (se usa como `/video-cartoon videos/<carpeta>`):
  1. Leer solo `guion.md`, `tomas.md` y `GUIA_MOTOR.md`. **Prohibido leer `motor/v1/` y `biblioteca/` por dentro.**
  2. Voz Kokoro y tiempos.
  3. Escribir `story.js` y `sonidos.json`.
  4. Hoja de contacto: 10 cuadros pequeños en una sola imagen. Se muestra y se espera aprobación, con un máximo de 2 rondas de corrección.
  5. Previa → mi OK → render final lanzado **en una ventana aparte** (`start`), y terminar el turno sin vigilarlo.
  6. Cuando yo avise, leer solo la última línea de `render.log` y correr `finish.py`.
  7. Entregar `final.mp4` para el CONTROL 2.
- **Si una toma necesita algo que el motor no tiene:** detenerse y proponer una "sesión de motor" aparte (v1.1). No improvisar dentro del motor.
- **Actualiza `CLAUDE.md`** con una sección corta: "Videos de caricatura → usar /video-cartoon; motor/ está congelado".

## Etapa 4: prueba de velocidad
- Renderiza los cuadros 0–59 del `story.js` de la piedra a resolución completa con el motor nuevo, en `motor/pruebas/bench/`. Mide s/cuadro, RAM máxima y si hubo errores.
- Calcula cuánto tardaría un video de 37 s (1.111 cuadros).
- Arma una hoja de contacto con 6 de esos cuadros para que compruebe que se ven igual que en la nube.
- **Solo es una medición.** No completes el video.

Al terminar, dame un resumen de 10 líneas como máximo: qué quedó instalado, la velocidad medida, problemas encontrados y qué falta.
