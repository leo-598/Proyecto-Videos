# Prompt para Claude Code — Fase 4, Sprint 1: del MVP a la producción en lotes

Pega esto en Claude Code, abierto dentro de `Proyecto Videos`, o dile:
"Lee docs/prompt_claude_code_fase4_sprint1.md y ejecútalo".

---

Vuelve a leer `CLAUDE.md` y `logs/decisiones.md`. Siguen todas las reglas: español, costo 0, sin servicios externos, nada de publicar, y consultarme antes de cualquier cambio que afecte la transparencia, las licencias o lo que se publica.

## Contexto

La Fase 3 (MVP) quedó cerrada: el pipeline produce un video de punta a punta en unos 10 minutos.
Ahora el objetivo es producir los **12 videos de validación** del carril base: las filas con `validacion = si` en `ideas/banco_ideas.csv`.
El de P3-01 (arcoíris) ya existe.

## Pendiente conocido (NO lo resuelvas en este sprint)

- **Audio:** la voz se corta muchas veces y tiene interrupciones.
  - Anótalo en `logs/pendientes.md` con prioridad ALTA y la etiqueta "bloquea la publicación".
  - Lo atacaremos en el Sprint 2, junto con la clonación de mi voz.
  - No se publica ningún video hasta resolverlo.

## Tareas del sprint

1. **Visuales más grandes** (lo detectó la revisión del MVP):
   - Agranda los diagramas 1,5–2 veces y céntralos entre el sello y los subtítulos, respetando las zonas seguras.
   - Ningún texto dentro de los diagramas puede medir menos de 40 px de alto.
   - En B2 del arcoíris, el abanico de colores debe ser grande y estar en el centro.
   - Vuelve a renderizar el MVP sin regenerar la voz y muéstrame los fotogramas antes y después.
2. **Plantillas de guion por serie** en `docs/plantillas/`: `porque.md`, `mito_o_dato.md` y `en_60s.md`.
   - Cada una con su estructura de bloques, duración, número de palabras, reglas de tono y un ejemplo.
   - Para "Mito o dato", define cómo se ve el veredicto: MITO en coral #E8505B y DATO en azul #2F6BFF.
3. **Escenas reutilizables:** convierte los dibujos del MVP en una pequeña biblioteca de componentes en `src/componentes/`.
   - Ejemplos: título grande, tarjeta de dato con número, comparación A vs. B, línea de tiempo, gráfico de barras simple, icono con etiqueta, sello de veredicto MITO/DATO y muñeco.
   - Así, `escenas.yaml` describe cada escena combinando componentes, en lugar de programar cada video desde cero.
   - Mantenlo simple.
4. **Regenerar una sola frase:** `python -m src.producir videos/<carpeta> --solo-frase B3` rehace solo la voz de ese bloque, la empalma y vuelve a renderizar.
5. **Verificación automática:** `python -m src.verificar videos/<carpeta>` revisa los criterios de aceptación de la Fase 3 y genera `verificacion.md` dentro de la carpeta del video.
   - Formato, duración, LUFS, subtítulos sincronizados contra el audio, frases inventadas o recortadas, zonas seguras, sello, fuentes y cierre.
6. **Modo lote:** `python -m src.lote --validacion` crea la carpeta de cada video pendiente a partir del banco de ideas, con `metadata.yaml` en estado `idea`.
   - **Los guiones NO los genera un script.** Los escribes tú (Claude) siguiendo las plantillas, con verificación de hechos y `fuentes.md`, igual que en el Paso 0 del MVP.
   - Hazlo en tandas de 3 guiones. Después de cada tanda, detente para que yo haga el CONTROL 1.
   - Después del CONTROL 1, produce la voz y el render de la tanda, preferiblemente de noche, y deja `verificacion.md` en cada carpeta.
7. **Métricas:** crea `metricas/registro.csv` vacío, con estas columnas:
   - id, plataforma, fecha_publicacion, vistas_48h, vistas_7d, retencion_pct, compartidos, guardados, comentarios, seguidores_ganados, minutos_produccion.

## Criterios de cierre del sprint

- MVP re-renderizado con los visuales grandes y aprobado por mí.
- Las 3 plantillas y la biblioteca de componentes, cada una con un ejemplo funcionando.
- `--solo-frase` y `src.verificar` funcionando sobre el MVP.
- Primera tanda de 3 guiones lista para mi CONTROL 1.
- Reporte final: qué hiciste, tiempos de cada etapa, problemas y propuestas para el Sprint 2 (audio y mi voz).

Commits pequeños y claros. Si algo nuevo hay que instalar, pregúntame primero, con su licencia y su costo (debe ser 0).
