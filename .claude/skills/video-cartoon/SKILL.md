---
name: video-cartoon
description: Produce un video de caricatura ParchanCol (personajes 2D en mundo 3D) con el motor congelado motor/v1. Uso /video-cartoon videos/<carpeta>. Escribe solo story.js y sonidos.json (y escenarios nuevos en la biblioteca), con hoja de contacto, previa y render final en ventana aparte.
---

# /video-cartoon videos/<carpeta>

Todo en español. `PY` = `.venv\Scripts\python.exe`; comandos desde la raíz del proyecto. `<v>` = la carpeta del video.

## Reglas fijas
- **Leer solo**: `<v>/guion.md`, `<v>/tomas.md` y `motor/GUIA_MOTOR.md` (más los JSON que generan los scripts: `words.json`, `phrases.json`,
  `voz_frases.json`). Para un escenario nuevo, además `motor/biblioteca/escenarios/_plantilla.js`.
- **Prohibido leer o editar cualquier cosa dentro de `motor/v1/`** (núcleo congelado). Se puede leer y escribir en `motor/biblioteca/`
  (escenarios nuevos desde la plantilla, que quedan para reutilizar). No abrir `motor/ANEXO_MOTOR.md`.
- Si una toma pide algo que el motor no tiene: **parar** y proponer una sesión de motor aparte (v1.1). No improvisar parches.
- El guion debe venir aprobado en el CONTROL 1 (`checklist.md`). Si no lo está, parar y avisar.
- Final sin sello de serie y sin tarjeta ParchanCol al final.

## Pasos
1. **Voz y tiempos**: `PY motor/v1/voz.py <v>` y `PY motor/v1/tiempos.py <v>`. Si `voz.py` deja AVISOS (frases que no quedaron iguales al
   guion), mostrarlos al dueño antes de seguir. Anotar `frames` de `phrases.json` = TOTAL.
2. **Escribir** `<v>/story.js` y `<v>/sonidos.json` según `tomas.md` y la guía (TOTAL, SHOTS por frases, gestos en los `f0` de `words.json`).
3. **Hoja de contacto**: `PY motor/v1/hoja.py <v>` → mostrar `<v>/out/hoja.jpg` (10 cuadros) y **esperar aprobación**.
   **Una hoja por ronda, máximo 2 rondas de corrección.** Si tras la 2.ª ronda sigue sin aprobarse, parar y hablar con el dueño
   (¿simplificar tomas o sesión de motor?).
4. **Previa**: `node motor/v1/render.mjs <v> --previa`, `PY motor/v1/audio.py <v>`, `PY motor/v1/finish.py <v> --previa` →
   entregar `<v>/out/previa.mp4` y **esperar el OK** del dueño.
5. **Render final en una ventana aparte** y terminar el turno sin mirarlo:
   `start "render <carpeta>" cmd /c node motor/v1/render.mjs <v>` (PowerShell: `Start-Process cmd -ArgumentList '/c','node','motor/v1/render.mjs','<v>'`).
   Decir al dueño cuánto tardará aprox. (cuadros × s/cuadro de la previa × 3) y que avise al terminar. No hacer polling.
6. **Al volver** (cuando el dueño lo diga): leer **solo la última línea** de `<v>/out/render.log` (debe empezar con `FIN` y decir `hechos N/N`).
   Si faltan cuadros, relanzar el paso 5 (retoma donde iba). Si está completo: `PY motor/v1/finish.py <v>`.
7. **Entregar** `<v>/final.mp4` con el resumen del control de calidad (duración, LUFS, congelados/negros, `out/qa_hoja.jpg`) para el
   **CONTROL 2**, y poner `estado: render` en `metadata.yaml`. Publicar nunca: eso es del dueño tras el CONTROL 2.
