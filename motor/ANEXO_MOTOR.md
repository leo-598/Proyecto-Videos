# ANEXO_MOTOR — solo para sesiones de motor (no se abre en sesiones de video)

## Mapa de motor/
- `v1/` núcleo CONGELADO. Un cambio = sesión de motor aparte → copiar a `v1.1/`, probar, y que el dueño apruebe. Nunca editar `v1/` en sitio.
  - `web/index.html` carga `nucleo.js` (renderer three.js r160, tinta por normales+profundidad, desenfoque, tarjetas 2D, cielo y luces).
    `toon.js` = `toonbase.js` + `roman.js` (dibujo 2D de personajes y efectos), `paint.js` (texturas pintadas, `P.rng`), `motion.js`, `lib/three.module.js`.
  - `render.mjs` servidor local: `/story.js` → story del video, `/biblioteca/*` → `motor/biblioteca`, el resto → `v1/web`.
    Chromium headless shell + ANGLE D3D11 (`--use-angle=d3d11 --ignore-gpu-blocklist`); bloques de 300 con reinicio; reanuda; `?escala=` para previa.
  - `comun.py` (rutas, `AJUSTES`, lector de guion), `voz.py` (Kokoro sherpa-onnx 1.13.8, sid 29 em_alex, control con Whisper),
    `tiempos.py` (alineación Whisper copiada del MVP; respaldo por sílabas), `audio.py` (DSP, cumbia, efectos, mezcla -6 dB),
    `finish.py` (-14 LUFS, ASS, cierre opcional, QA), `hoja.py`, `nuevo_video.py`.
- `biblioteca/` crece en sesiones de video (escenarios nuevos desde `_plantilla.js`); `ejemplos/piedra_GI.js` es la referencia.
- `modelos/` (Kokoro), `pruebas/` (bench y videos de prueba) están en .gitignore. Licencias: `motor/LICENCIAS.md`; instalaciones: `docs/INSTALADO.md`.

## Contrato núcleo ↔ escenario
`crear(ctx, opts)` → `{ estado(W, f, cam), luz(L, f) }`. `ctx`: ver cabecera de `_plantilla.js`. Grupos `hoy`/`antes` los conmuta el núcleo con `W.today`.
`billboards` miran a la cámara cada cuadro. Orden de creación = orden de `ESCENARIOS` (afecta la secuencia de `P.rng` solo dentro de cada módulo).

## Pruebas de regresión al cambiar el núcleo
1. Render de `ejemplos/piedra_GI.js` en cuadros 0, 200, 500, 800, 1100 con el motor viejo (`--web`, `--story`) y el nuevo; diferencia máx. ≈ 0 (JPEG).
2. Video de prueba de `nuevo_video.py` de punta a punta (voz → final.mp4) con QA en verde.

## Decisiones guardadas
- Sin sello de serie en caricatura; sin tarjeta ParchanCol al final desde 2026-11-07 (`cierre.segundos = 0`).
- Audio a -14 LUFS con ganancia fija + limitador iterado (loudnorm lineal quedaba por debajo); pico ≤ -1,5 dBTP tras AAC.
- sherpa-onnx fijo en 1.13.8 (la 2.x quitó espeak para Kokoro).
