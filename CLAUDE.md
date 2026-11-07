# CLAUDE.md — ParchanCol (Proyecto Videos)

Contexto permanente para Claude. Léelo completo antes de trabajar en este proyecto.
Estrategia completa: documento "PROYECTO JA_U — Verificación de hechos y Fase -1 (a, b, f)" (Claude Docs).

## Qué es

Marca de videos cortos verticales (9:16) en español, con sello colombiano, para
YouTube Shorts, TikTok, Instagram Reels y Facebook Reels. Nombre temporal: **ParchanCol**.
Público: Colombia y el mundo hispano ("colombiano para el mundo hispano").

- Prioridad 1: ingresos (Facebook pago por rendimiento, afiliados, marcas; YouTube cuando se cumpla el YPP).
- Prioridad 2: marca reconocible. La identidad viene del FORMATO, idéntico en todos los videos.

## Reglas de trabajo (del dueño del proyecto — obligatorias)

1. No escribir código sin autorización explícita.
2. Entre fases, esperar aprobación explícita.
3. En decisiones importantes: 2–3 opciones con ventajas, desventajas, costo y recomendación. Decide el dueño.
4. Honestidad sobre riesgos y expectativas. Nada de humo.
5. Soluciones simples y modulares. Explicar lo técnico en lenguaje claro.
6. Todo en español.

## Restricciones

- **Presupuesto: USD 0.** Solo herramientas gratuitas o de código abierto con licencia que permita USO COMERCIAL. Verificar la licencia antes de adoptar cualquier herramienta, modelo, imagen, fuente o música.
- **Equipo:** portátil Windows, i5-1035G1, gráficos Intel UHD integrados (sin GPU dedicada), 12 GB RAM.
  Nada de generar video ni modelos grandes en local. Voz, edición y render sí.
- **Descartados por licencia no comercial:** XTTS v2, F5-TTS, plan gratuito de ElevenLabs.
- **Publicación:** manual con los programadores nativos (YouTube Studio, Meta Business Suite, TikTok).
  Las APIs de publicación de YouTube y TikTok dejan los videos en privado hasta pasar una auditoría.

## Pipeline (modelo híbrido B)

Claude: ideas, guion, verificación de hechos, metadatos. Scripts locales: voz, visuales, edición, render.

1 Idea → 2 Guion → 3 Verificación → **CONTROL 1 (humano aprueba guion + fuentes)** →
4 Voz → 5 Visuales → 6 Edición y subtítulos → 7 Render → **CONTROL 2 (humano revisa el video)** →
8 Metadatos por plataforma → 9 Publicación manual → 10 Métricas.

- Carril de lotes (~70 %): ciclo semanal de ~7 videos.
- Carril express (~30 %): tendencias, publicado en 24–48 h, con un nuevo chequeo de hechos justo antes de publicar.
- Mismas plantillas en los dos carriles.

## Contenido

Pilares: P1 Colombia explicada · P2 Plata clara · P3 Así funciona · P4 Parece mentira.
Series:
- "¿Por qué…?" (30–45 s): gancho-pregunta, 3 golpes, giro, cierre.
- "Mito o dato" (20–35 s): creencia, veredicto, evidencia, fuente visible.
- "En 60 segundos" (50–90 s): contexto, lo que nadie te cuenta, qué significa para ti.

Frase de cierre de marca: "Y ahora ya sabes, parce."

## Marca

- Tono: un parcero que sabe mucho y te lo cuenta rápido. Cercano, humor ligero, nunca alarmista ni condescendiente. "Parce" con medida.
- Voz: Chatterbox Multilingual (MIT) clonando la voz del dueño desde `assets/voz_referencia/`. Plan B: Kokoro (Apache 2.0).
  Solo voces propias o con permiso escrito. Nunca imitar a personas reales.
- Paleta: fondo #14161A · acento/palabra clave #FFC832 · "MITO" #E8505B · "DATO" #2F6BFF · texto #F7F4EE.
- Fuentes: Archivo Black (títulos y sellos) e Inter Semibold (subtítulos). Licencia OFL.
- Formato: 1080×1920, subtítulos grandes palabra por palabra, sello de serie arriba, fuentes en letra pequeña, cierre de 2 s con logo.

## Filtro de seguridad (resumen; la versión completa está en el documento de estrategia)

Semáforo verde, amarillo o rojo; ante la duda, el más restrictivo.

- **Siempre ROJO:** tragedias recientes con víctimas; conflicto armado con imágenes gráficas; política partidista; rumores o vida privada de personas reales; menores; afirmaciones médicas; recomendaciones de inversión; drogas y apuestas; deepfakes o voces clonadas de terceros; material sin derechos; estigmatizar regiones o grupos.
- **Hechos:** cada afirmación lleva su fuente en `fuentes.md`. En temas de actualidad, al menos 2 fuentes independientes. Si un dato no se puede verificar, se quita.
- **Personas reales:** nunca generadas ni alteradas con IA. Sobre figuras públicas, solo actos públicos verificados.
- **IA:** si un visual parece real y es sintético, se activa la etiqueta de IA en cada plataforma.
- **Afiliados y patrocinios:** siempre declarados como publicidad.
- **Errores:** comentario fijado con la corrección, o borrar el video si el error es grave. Todo queda en `logs/correcciones.md`.

## Videos de caricatura

- Videos de caricatura → usar `/video-cartoon videos/<carpeta>`; `motor/v1/` está congelado (no se lee ni se edita en sesiones de video).
  Solo se escriben `story.js`, `sonidos.json` y, si hace falta, escenarios nuevos en `motor/biblioteca/`. Guía: `motor/GUIA_MOTOR.md`.
- Excepción de formato: los videos de caricatura **no llevan sello de serie ni tarjeta de cierre con el logo** (decisión del dueño,
  2026-11-07); solo subtítulos. Voz: Kokoro `em_alex` (Apache 2.0) vía sherpa-onnx 1.13.8.
- Cambios al motor: sesión aparte, en una copia `motor/v1.1/`, con aprobación del dueño.

## Estructura de carpetas

```
CLAUDE.md          este archivo
README.md          guía rápida para humanos
.env.example       nombres de las claves (las reales van en .env, NUNCA en git ni en el chat)
docs/              estrategia, brand kit, plantillas de guion por serie
config/            marca, series y plataformas (los scripts leen de aquí)
assets/            fonts/, logo/, sonidos/ (con licencia anotada), voz_referencia/
ideas/             banco de ideas por pilar + tendencias/ (carril express)
videos/            una carpeta por video (ver abajo)
src/               código (cuando se autorice)
metricas/          registro de resultados
reference/         videos y ejemplos de referencia (Fase 0)
logs/              errores, correcciones, decisiones
```

### Carpeta de cada video: `videos/AAAA-MM-DD_serie_slug/`

- `guion.md`: texto final con marcas de locución.
- `fuentes.md`: tabla afirmación → fuente → fecha.
- `checklist.md`: filtro de seguridad marcado (control 1 y control 2).
- `voz.wav`, `visuales/`, `subtitulos.ass`, `final.mp4`.
- `metadata.yaml`: pilar, serie, carril, estado, título y texto por plataforma, etiqueta de IA (sí/no), enlaces de afiliado.

Estados posibles en `metadata.yaml`: idea → guion_aprobado → voz → render → revisado → programado → publicado (o descartado).

## Nunca

- Publicar sin pasar por los dos controles humanos.
- Guardar contraseñas o claves fuera de `.env`.
- Usar recursos sin licencia comercial verificada.
- Producir en serie videos casi idénticos: cada video necesita idea, guion y verificación propios.
