# GUIA_MOTOR — caricatura v1 (una página; lo único que se lee en cada video)

`motor/v1/` está **congelado**: no se lee ni se edita en una sesión de video. Cada video escribe solo
`story.js` y `sonidos.json` (y, si hace falta, un escenario nuevo en `biblioteca/escenarios/`). Si una toma pide algo que el
motor no tiene, se para y se propone una sesión de motor (v1.1). Detalles internos: `motor/ANEXO_MOTOR.md` (solo para sesiones de motor).

**Comandos** (`PY=.venv\Scripts\python.exe`, desde la raíz): `PY motor/v1/nuevo_video.py <slug>` → `PY motor/v1/voz.py <v>` →
`PY motor/v1/tiempos.py <v>` → `PY motor/v1/hoja.py <v>` → `node motor/v1/render.mjs <v> --previa` + `PY motor/v1/finish.py <v> --previa`
→ `node motor/v1/render.mjs <v>` (final; retoma solo) → `PY motor/v1/finish.py <v>` → `<v>/final.mp4`. Final sin sello de serie ni tarjeta de cierre
(para ponerla en un video: `ajustes.json` `{"cierre": {"segundos": 2}}`).

**story.js exporta**: `ESCENARIOS` `[[modulo, {opciones}], ...]` · `FPS=30, TOTAL` (= `frames` de `phrases.json`) ·
`SHOTS [{id, a, b, light:'dia'|'hoy'|'atardecer', today}]` + `shotAt(f)` · `lightFor(S,f)` → `{...LUCES[S.light], shadowExt: 8}` (tamaño de sombra, m) ·
`camAt(f)` → `{pos, look, fov, roll?, shadowAt?, flash? 0..1, ink? 2.5}` · `worldAt(f)` → `{today, ...estado de escenarios}` ·
`actorsAt(f,T)` → lista de tarjetas · opcionales `dofAt(f)` → `{focus (m), cinf (0 = nítido, 8–10 = fondo borroso)}` y `fxAt(f,T)`.
Todo determinista (nada de `Math.random`; usa `P.rng(semilla)`). Importa de `./biblioteca/...`. Plantilla funcionando: la que crea `nuevo_video.py`.

**Escenarios** (`./biblioteca/escenarios/`): `embalse` {isla{x,z,radio}, colinas{n,semilla,dmin,dmax}, agua{y}} agua animada, isla y colinas en "hoy", valle en "antes" ·
`muelle` {x 20, z 172, rotY, epoca 'hoy'|'antes'|'siempre'} · `piedra` {letras, guia 'ATAPÉ', cuerdas 4}; worldAt: g, u, guide, ropes; exporta `surf(phi°, y, sep)`, `RH` ·
`plaza_zocalos` {centro [-150,0,72], semilla, casasAnillo 15, casasAtras 14, abiertaHacia°} · `pueblo_iglesia` {centro [160,0,60], semilla, casas 16, rotIglesia} ·
`bosque` {n 160, dmin, dmax, semilla, evitar [[x,z,r]], evitarCaja, arbustos} · `montanas` {montanas 18, colinas 14, distancia 560} · `nubes` {n 14, altura 220}.
Puntos útiles de la piedra: narrador en el muelle `[20, 0.5, 170]` (ground 0.5), plaza `[-150,0,72]`.
**Escenario nuevo**: copia `biblioteca/escenarios/_plantilla.js` (terreno, objetos con `P.rng`, épocas `grupo('hoy'|'antes')`, `info` con luz y cámaras
sugeridas, ganchos `estado(W,f,cam)` y `luz(L,f)`). Solo se leen la plantilla y esta guía. Queda en la biblioteca para reutilizarlo.

**Personajes** (`./biblioteca/personajes.js`): `tarjeta(T, quien, o, [x,y,z], extra)`. `quien`: `costeno` (narrador, vueltiao + mochila), `guaA–D`, `pintA–C`
(pintores), `penA–E` (ruanas), `turA/B`, o un vestuario nuevo `{tunic:'#c33', pants, skin, hair, cap, moustache, ruana, vueltiao, mochila, stout, dress...}`.
`o`: `expr` neutral smile grin laugh whistle nervous shock relief dazed pained lick snore stern stubborn squint · brazos `L`/`R` hang up point wave thumb
hip cross belly cheek temple lift reach · `holdL/holdR` tinto bucket brush rope · `look` -1..1 · `facing` ±1 · `headTilt`° · `tilt`° · `bob` · `step` 0..1 (caminar) ·
`blink: parpadeo(f, seed)` · `bob: respira(f, seed)` · `seed`. `extra`: `s` escala, `flip`, `tint` (`tinteDe(luz)`), `alpha`, `ground`, `order`.
**Efectos 2D**: `efecto(key, p => T.fxBurst(p, t), pos, s)` con `T.fxPuff/fxBurst/fxStars/fxSplash/fxRing/fxCreak/fxAnger/fxBololo/fxDust/fxZ/fxNote/fxLeaf` (t 0..1;
la `key` debe cambiar con t, p. ej. `'idea' + t` redondeado a 2 decimales).

**Cámara**: puntos clave por toma `{f, pos, look, fov}` interpolados con `smooth` (ver plantilla). Plano medio del narrador: pos `[21, 2.2, 173.4]` → look `[20, 1.9, 170]`, fov 36.
Golpe de cámara: sumar ±0,03 a `look` durante 6 cuadros. Corte = cambio de toma. Flash: `flash` 0.85 → 0 en 6 cuadros. Nada importante en el 20 % de abajo ni en el 15 % derecho.

**Sincronía**: `words.json` `[{w, s, e, f0, f1, bloque, enfasis}]` (f0 = cuadro donde empieza la palabra, medido por Whisper). Copia los `f0` a constantes en story.js
(`const F_PRUEBA = 53;`) y cambia gesto o cámara en ese cuadro. Toma = frase(s) de `phrases.json` (`f0`–`f1`).

**sonidos.json** (tiempos: `2.5` segundos · `"f75"` cuadro · `"fin"` final de la historia · `"@palabra"` inicio, `"@palabra#2"` 2.ª vez, `"@palabra>"` cuando termina):
```json
{ "musica": { "estilo": "cumbia", "bpm": 96, "desde": 0, "hasta": "@ahora", "melodia": true, "tono": 0, "dron": false, "remate": "@parce>" },
  "musica_db": -6,
  "ambientes": [ { "sonido": "agua", "desde": 0, "hasta": "fin", "vol": 0.25 } ],
  "efectos": [ { "sonido": "zas", "t": 0.05, "vol": 0.5 }, { "sonido": "golpe", "t": "f75", "tono": 90, "repetir": 3, "cada": 0.2, "tono_paso": 15 },
               { "sonido": "ding", "t": "@prueba", "vol": 0.5 } ] }
```
Sonidos: zas golpe{tono,dur} retumbo derrumbe cucu raspado tin ding pop golpe_dramatico crujido chasquido chapuzon ronquido salpicon clanc cremallera tiza wawa ·
ambientes con `desde/hasta`: agua pajaros hojas multitud{enojo}. Música `"estilo": "ninguna"` = sin música; `dron` = suspenso grave después de `hasta`.

**Ejemplo de toma** (narrador levanta el pulgar cuando dice "prueba", f0 = 53):
```js
if (S.id === 'gancho') out.push(tarjeta(T, 'costeno', { seed: 5, expr: f >= 53 ? 'grin' : 'smile', L: 'hang', holdL: 'tinto',
  R: f >= 53 ? 'thumb' : 'hang', blink: parpadeo(f, 5), bob: respira(f, 5) }, [20, 0.5, 170], { ground: 0.5 }));
```
Ejemplo completo y largo: `biblioteca/ejemplos/piedra_GI.js`.
