# ParchanCol — Configuración del proyecto y brief del pipeline

Traspaso del chat de configuración, cerrado el 7 de noviembre de 2026. Es la base para todos los chats siguientes del PROYECTO JA_U.
Documento detallado (con fuentes y tablas): el doc de Claude "PROYECTO JA_U — Verificación de hechos y Fase -1 (a, b, f)".
Contexto técnico para Claude Code: `CLAUDE.md`, en la carpeta del proyecto.

---

## 1. Qué es el proyecto

- Videos cortos verticales (9:16) en español para YouTube Shorts, TikTok, Instagram Reels y Facebook Reels. Los videos largos de YouTube quedan para después.
- Mercado: Colombia, con temas que también interesen al resto del mundo hispano ("colombiano para el mundo hispano").
- Nombre: **ParchanCol** (temporal). Las cuentas ya están creadas por el dueño, que no comparte contraseñas.
- Prioridad 1: ingresos. Prioridad 2: marca reconocible. La identidad viene del **formato**, que es idéntico en todos los videos.

## 2. Reglas de trabajo del dueño (siempre)

1. No escribir código sin autorización explícita.
2. Entre fases, esperar aprobación explícita.
3. En decisiones importantes: 2–3 opciones con ventajas, desventajas, costo y recomendación. Decide el dueño.
4. Honestidad sobre riesgos y expectativas.
5. Soluciones simples y modulares, explicadas en lenguaje claro.
6. Todo en español.
7. Todo cambio que afecte la transparencia, las licencias o lo que se publica se consulta **antes** de aplicarlo.

## 3. Restricciones

- **Presupuesto: USD 0.**
- **Los videos se hacen solo con Claude y Claude Code**, más herramientas libres que corren en el PC. Nada de páginas ni servicios externos, a menos que sea imprescindible y gratuito.
  - Sin bancos de imágenes y sin claves.
  - Solo se permiten descargas únicas y gratuitas: paquetes de Python, FFmpeg, modelos abiertos, fuentes OFL.
- **Licencias:** todo debe permitir uso comercial. Descartados por ser no comerciales: XTTS v2, F5-TTS y el plan gratuito de ElevenLabs.
- **Equipo:** portátil Windows con i5-1035G1, gráficos Intel UHD integrados (sin GPU dedicada) y 12 GB de RAM.
  - Instalado: Python 3.10.4 global, FFmpeg 9.0.2 (build completo de gyan.dev con libass) y Git.
  - El proyecto usa `.venv` con Python 3.11.18, creado con uv.
- **Carpeta del proyecto:** `C:\Users\EQUIPO\Desktop\Proyecto Videos`.

## 4. Monetización (verificado en noviembre de 2026)

- **YouTube YPP:** hoy, 1.000 suscriptores + 4.000 h o 10M vistas de Shorts en 90 días. **Desde el 1 de febrero de 2027**, para nuevos solicitantes: 8.000 h o 20M vistas de Shorts en 90 días. Desde esa fecha, además, todos los socios necesitan 10M vistas en 90 días para cobrar del fondo de Shorts.
- **TikTok Creator Rewards:** no está disponible en Colombia. TikTok sirve para alcance y para validar ideas.
- **Instagram:** no paga por vistas. En Colombia hay Regalos y Suscripciones; los bonos son solo por invitación.
- **Facebook:** monetización de contenido por rendimiento de Reels, aparentemente disponible en Colombia. Hay que confirmarlo en el panel.
- **Pago real de los Shorts:** unos USD 0,02–0,07 por cada 1.000 vistas en contenido en español y LatAm.
- **Plan elegido: B + C.** Facebook y afiliados desde el inicio; YouTube largo como opción al día 60 si un pilar funciona. Marcas y patrocinios cuando haya audiencia.
- **Cobro:** AdSense con el formulario W-8BEN. Colombia no tiene convenio de doble tributación con EE. UU., así que hay retención sobre la parte que generan los espectadores estadounidenses. Hay que declarar ante la DIAN, con RUT y contador.
- **Políticas de IA:** se permite usar IA, pero no se monetiza el contenido repetitivo o hecho en masa ("no auténtico"). Lo realista y sintético se etiqueta. Meta castiga los reposts idénticos, así que cada plataforma recibe su propia versión.

## 5. Estrategia de contenido

- **Carril base (~70 %), producido en lotes. Pilares:**
  - P1 Colombia explicada
  - P2 Plata clara (economía cotidiana; sin recomendar inversiones; riesgo medio)
  - P3 Así funciona
  - P4 Parece mentira
- **Carril express (~30 %):** tendencias publicadas en 24–48 h, con filtro de seguridad y revisión humana obligatoria. Fuentes para detectarlas: Google Trends CO, tendencias de YouTube y TikTok, X Colombia, portadas de El Tiempo, El Espectador y Semana, r/Colombia.
  - Un tema entra si cumple todo: encaja en un pilar, aporta contexto, se verifica con al menos 2 fuentes, durará 48 h o más, es apto para anunciantes y no requiere imágenes de IA de personas reales.
- **Series:**
  - "¿Por qué…?" (30–45 s): gancho-pregunta, 3 golpes, giro, cierre.
  - "Mito o dato" (20–35 s): MITO en coral, DATO en azul, fuente visible.
  - "En 60 segundos" (50–90 s): contexto, lo que nadie te cuenta, qué significa para ti.
- **Banco de ideas:** `ideas/banco_ideas.csv` tiene 40 ideas, 10 por pilar. **Son solo propuestas**: no se usan todas ni siempre, y el dueño las modifica al escribir cada guion.
- **Metas:** el reloj empieza con el primer video publicado.
  - Día 30: 10–15 videos de validación.
  - Día 60: pipeline semiautomático y 1–2 pilares ganadores.
  - Día 90: 5.000–10.000 seguidores en la mejor plataforma.
  - Criterios para pivotar o parar: los define el documento detallado.
- **Validación (pendiente):** 12 videos del carril base, 3 por pilar, y 3 del carril express, a uno por día. Se mide retención, compartidos, guardados, seguidores y minutos de producción.

## 6. Filtro de seguridad (semáforo; ante la duda, el color más restrictivo)

- **Siempre rojo:**
  - Tragedias recientes con víctimas.
  - Conflicto armado con imágenes gráficas.
  - Política partidista.
  - Rumores o vida privada de personas reales.
  - Menores.
  - Afirmaciones médicas.
  - Recomendaciones de inversión.
  - Drogas y apuestas.
  - Deepfakes o voces de terceros.
  - Material sin derechos.
  - Contenido que estigmatice regiones o grupos.
- **Hechos:** cada afirmación tiene su fuente en `fuentes.md`. En temas de actualidad, al menos 2 fuentes independientes.
- **Personas reales:** nunca generadas ni alteradas con IA. En Colombia, la injuria y la calumnia son delitos.
- **Dos controles humanos:**
  - CONTROL 1: guion y fuentes.
  - CONTROL 2: video final.
- **Correcciones:** error menor, comentario fijado; error grave, se borra el video. Todo queda en `logs/correcciones.md`.
- **Transparencia:** la voz es sintética y se declara cuando la plataforma lo pregunte. Los afiliados se declaran siempre como publicidad.

## 7. Marca (brand kit vigente)

- **Tono:** un parcero que sabe mucho y te lo cuenta rápido. Cercano, con humor ligero, nunca alarmista ni condescendiente. "Parce" con medida.
- **Frase de cierre:** "Y ahora ya sabes, parce."
- **Paleta:**
  - Fondo #14161A
  - Acento y palabra clave #FFC832
  - MITO #E8505B
  - DATO #2F6BFF
  - Texto #F7F4EE
- **Fuentes:** Archivo Black (títulos y sellos) e Inter SemiBold (subtítulos). Licencia OFL.
- **Formato:** 1080×1920, 30 fps.
  - Subtítulos palabra por palabra.
  - Sello de serie arriba.
  - Fuentes en letra pequeña.
  - Cierre de 2 s con "ParchanCol" en texto, "Col" en amarillo (logo provisional).
  - Zonas seguras: nada importante en el 20 % inferior ni en el 15 % derecho.
- **Estilo visual actual:** explicador gráfico 100 % generado por código. **El estilo de animación y visual definitivo está POR DEFINIR** a partir de la carpeta `reference/` (ver sección 10).

## 8. Pipeline (modelo híbrido B)

1. Idea
2. Guion (Claude)
3. Verificación (Claude)
4. **CONTROL 1**
5. Voz (Chatterbox, local)
6. Visuales generados por código
7. Subtítulos ASS
8. Render con FFmpeg
9. **CONTROL 2**
10. Metadatos por plataforma (Claude; textos distintos en cada una)
11. Publicación **manual** con los programadores nativos (YouTube Studio, Meta Business Suite, TikTok)
12. Métricas en `metricas/registro.csv`

- **Publicación por API:** queda para después. YouTube y TikTok dejan en privado lo que publica un cliente no auditado.
- **Voz:** Chatterbox Multilingual (MIT, local, clona voces con un clip de referencia).
  - Por ahora usa la voz por defecto.
  - Plan: clonar la voz del dueño con un audio de 10–30 s en `assets/voz_referencia/`, que todavía no llega.
  - Respaldo: Kokoro (Apache 2.0).
  - La marca de agua de Chatterbox está desactivada porque falla en Windows; se aprobó con la condición de declarar la voz sintética.
- **Carril de lotes:** ciclo semanal de unos 7 videos. **Carril express:** menos de 2 h del tiempo del dueño por video.

## 9. Estado actual

- **Fases −1, 1 y 2:** completas.
- **Fase 0** (análisis de `reference/`): pendiente.
- **Fase 3 (MVP): cerrada.** El video "¿Por qué el arcoíris es curvo?" (P3, serie ¿Por qué…?) se produce de punta a punta en unos 10,5 min: voz 8,6 min, escenas 80 s, render 10 s.
  - Salida: 1080×1920, 30 fps, −14,5 LUFS.
  - Ubicación: `videos/2026-11-07_porque_arcoiris-curvo/`.
  - Hecho por Claude Code: `src/` (config, guion, voz, tiempos, subtitulos, escenas, render, producir), `config/marca.yaml` y `config/series.yaml`, más un control con Whisper contra frases inventadas por la voz.
  - Opinión del dueño: "relativamente bien, sencillo y corto; es una prueba".
- **Problemas conocidos:**
  - **La voz se corta y tiene interrupciones.** Bloquea la publicación; está aplazado.
  - Los diagramas son pequeños y algunas etiquetas no se leen en el celular.
  - La voz por defecto no tiene acento colombiano.
- **Fase 4, Sprint 1:** el prompt está listo en `docs/prompt_claude_code_fase4_sprint1.md`, pero **está en PAUSA** por decisión del dueño, hasta definir el estilo visual.
- **Ningún video se ha publicado.**

## 10. Próximos pasos (en un chat nuevo)

1. **Definir el estilo de animación y visual** con la carpeta `reference/`. El dueño pondrá ahí sus referencias, y es la Fase 0: qué funcionó, qué no y un máximo de 5 preguntas.
2. **Probar una skill para generar los videos.** Hay que comparar su resultado con el pipeline actual en calidad, costo (debe ser 0), licencias y peso para el equipo.
3. Después: resolver el audio, clonar la voz del dueño y retomar el Sprint 1 con el estilo ya definido.

## 11. Mapa de la carpeta del proyecto

```
CLAUDE.md · README.md · .env.example · .gitignore
docs/      este traspaso, los prompts para Claude Code y, más adelante, las plantillas
config/    marca.yaml, series.yaml
assets/    fonts/ (con LICENCIAS.md), logo/, sonidos/, voz_referencia/
ideas/     banco_ideas.csv (propuestas)
videos/    una carpeta por video: guion.md, fuentes.md, escenas.yaml, metadata.yaml, checklist.md, voz.wav, final.mp4
src/       código del pipeline (Claude Code)
metricas/  registro.csv
reference/ referencias de estilo (Fase 0)
logs/      decisiones.md, pendientes.md, correcciones.md
```
