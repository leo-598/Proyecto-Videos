"""Crea la carpeta de un video de caricatura con sus plantillas (port de setup.sh).

Uso:  .venv\\Scripts\\python.exe motor\\v1\\nuevo_video.py <slug> [--fecha AAAA-MM-DD] [--pilar P1] [--serie porque] [--en <carpeta>]

Crea videos/AAAA-MM-DD_cartoon_<slug>/ con:
  guion.md  tomas.md  story.js  sonidos.json  fuentes.md  checklist.md  metadata.yaml
No pisa nada: si la carpeta ya existe, se detiene.
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

GUION = """# Guion — {titulo}

Serie: {serie} · Pilar: {pilar} · Caricatura
Marcas: [B1 – NOMBRE] bloque · [pausa] o [pausa:0.6] silencio · *palabra* énfasis (amarillo) ·
{{G|ge}} se ve "G" en el subtítulo pero la voz dice "ge". Cada línea es una frase.

[B1 – GANCHO]
¿Sabías que esto es un guion de *prueba*?

[B2 – CIERRE]
Y ahora ya sabes, parce.
"""

TOMAS = """# Tomas — {titulo}

Una fila por toma. Los cuadros (a–b) salen de phrases.json (30 cuadros = 1 s).

| # | id | Frase(s) | Escenario | Cámara | Quién y qué hace | Efectos y sonidos |
|---|----|----------|-----------|--------|------------------|-------------------|
| 1 | gancho | B1 | embalse + muelle | plano medio del narrador, acerca lento | costeño con tinto, sonríe, pulgar arriba en *prueba* | zas al empezar |
| 2 | cierre | B2 | igual | se aleja al paisaje | narrador saluda | remate de la música |
"""

STORY = """// story.js — {titulo}
// Lo único que cambia en cada video (junto con sonidos.json). Guía: motor/GUIA_MOTOR.md
// Escenarios, luces y personajes vienen de motor/biblioteca/ (se sirven en ./biblioteca/).
import * as embalse from './biblioteca/escenarios/embalse.js';
import * as muelle from './biblioteca/escenarios/muelle.js';
import * as montanas from './biblioteca/escenarios/montanas.js';
import * as nubes from './biblioteca/escenarios/nubes.js';
import {{ LUCES }} from './biblioteca/luces.js';
import {{ tarjeta, parpadeo, respira }} from './biblioteca/personajes.js';

export const ESCENARIOS = [[embalse], [muelle, {{ epoca: 'siempre' }}], [montanas], [nubes]];

// TOTAL = "frames" de phrases.json. Cada toma: id, a (primer cuadro), b (último), luz y época.
export const FPS = 30, TOTAL = 150;
export const SHOTS = [
  {{ id: 'gancho', a: 0, b: 89, light: 'hoy', today: true }},
  {{ id: 'cierre', a: 90, b: 149, light: 'hoy', today: true }},
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const smooth = (t) => {{ t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); }};
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));

export const lightFor = (S, f) => ({{ ...LUCES[S.light], shadowExt: 8 }});

// cámaras: puntos clave por toma {{ f, pos, look, fov }}; entre puntos se interpola suave
const NAR = [20, 0.5, 170];          // el narrador, de pie en el muelle
const CAMS = {{
  gancho: [{{ f: 0, pos: [21.0, 2.2, 173.4], look: [20, 1.9, 170], fov: 36 }}, {{ f: 89, pos: [20.9, 2.1, 172.6], look: [20, 1.95, 170], fov: 34 }}],
  cierre: [{{ f: 90, pos: [21.5, 2.6, 175], look: [20, 2.2, 170], fov: 40 }}, {{ f: 149, pos: [25, 3.5, 186], look: [19, 3.2, 168], fov: 42 }}],
}};
export const camAt = (f) => {{
  const K = CAMS[shotAt(f).id];
  if (f <= K[0].f) return {{ ...K[0] }};
  for (let i = 0; i < K.length - 1; i++) if (f <= K[i + 1].f) {{
    const t = smooth((f - K[i].f) / (K[i + 1].f - K[i].f));
    return {{ pos: lerp3(K[i].pos, K[i + 1].pos, t), look: lerp3(K[i].look, K[i + 1].look, t), fov: lerp(K[i].fov, K[i + 1].fov, t), shadowAt: NAR }};
  }}
  return {{ ...K[K.length - 1], shadowAt: NAR }};
}};

export const worldAt = (f) => ({{ today: !!shotAt(f).today }});

// personajes: tarjetas 2D. Sincronía: usa los f0 de words.json (ej. "prueba" empieza en el cuadro F_PRUEBA)
const F_PRUEBA = 40;
export const actorsAt = (f, T) => {{
  const S = shotAt(f), out = [];
  const narr = (o) => out.push(tarjeta(T, 'costeno', {{ seed: 5, expr: 'grin', blink: parpadeo(f, 5), bob: respira(f, 5), L: 'hang', holdL: 'tinto', R: 'hang', ...o }}, NAR, {{ ground: NAR[1] }}));
  if (S.id === 'gancho') narr({{ R: f >= F_PRUEBA ? 'thumb' : 'hang', expr: f >= F_PRUEBA ? 'grin' : 'smile' }});
  if (S.id === 'cierre') narr({{ R: 'wave', expr: 'smile' }});
  return out;
}};

// opcionales: desenfoque (dofAt) y efectos 2D (fxAt)
export const dofAt = (f) => shotAt(f).id === 'gancho' ? {{ focus: 3.5, cinf: 8 }} : {{ focus: 10, cinf: 0 }};
export const fxAt = () => [];
"""

SONIDOS = """{{
  "_ayuda": "Tiempos: segundos (2.5), cuadro ('f75') 'fin' (final de la historia) o palabra ('@prueba', '@parce#2', '@parce>' = cuando termina). Lista de sonidos en motor/GUIA_MOTOR.md",
  "musica": {{ "estilo": "cumbia", "bpm": 96, "desde": 0, "hasta": "@ahora", "melodia": true, "dron": false, "remate": "@parce>" }},
  "musica_db": -6,
  "ambientes": [
    {{ "sonido": "agua", "desde": 0, "hasta": "fin", "vol": 0.25 }}
  ],
  "efectos": [
    {{ "sonido": "zas", "t": 0.05, "vol": 0.5 }},
    {{ "sonido": "ding", "t": "@prueba", "vol": 0.5 }}
  ]
}}
"""

FUENTES = """# Fuentes — {titulo}

Estado: PENDIENTE de verificación.

| # | Afirmación | Fuente | Cita textual (resumen) | Fecha consulta | Verificado |
|---|---|---|---|---|---|
| 1 |  |  |  |  | [ ] |
"""

CHECKLIST = """# Checklist — filtro de seguridad

## Control 1 (guion + fuentes) — lo marca el humano
- [ ] Tema fuera de la lista roja
- [ ] Cada afirmación tiene fuente verificada en fuentes.md
- [ ] Sin personas reales, menores, salud ni consejos de inversión
- [ ] Ningún personaje imita a una persona real ni estigmatiza una región o grupo
- [ ] Tono de marca y cierre correctos

## Control 2 (video final) — lo marca el humano
- [ ] Visto completo con sonido
- [ ] Subtítulos sin errores y sincronizados
- [ ] Nada importante en las zonas de botones de las apps (20 % de abajo, 15 % derecho)
- [ ] Fuentes en la descripción
- [ ] Decisión sobre la etiqueta de IA tomada por plataforma
- [ ] Semáforo final: verde / amarillo / rojo
"""

METADATA = """id: {id}
pilar: {pilar}
serie: {serie}
formato: caricatura   # sin sello de serie: solo subtítulos y cierre
carril: base
estado: idea  # idea → guion_aprobado → voz → render → revisado → programado → publicado
etiqueta_ia: voz_sintetica  # caricatura 2D/3D (no realista); voz sintética Kokoro -> declararla cuando la plataforma lo pregunte
afiliados: []
textos_aprobados: no
plataformas:
  youtube:
    titulo: ""
    descripcion: |
      Fuentes:
  tiktok:
    texto: ""
  instagram:
    texto: ""
  facebook:
    texto: ""
"""


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        raise SystemExit(__doc__)
    op = lambda k, d: a[a.index(k) + 1] if k in a else d  # noqa: E731
    slug = a[0].strip().lower().replace(" ", "-")
    fecha = op("--fecha", dt.date.today().isoformat())
    pilar, serie = op("--pilar", "P1"), op("--serie", "porque")
    base = Path(op("--en", comun.RAIZ / "videos"))
    vid = f"{fecha}_cartoon_{slug}"
    c = base / vid
    if c.exists():
        raise SystemExit(f"Ya existe {c}: no piso nada")
    c.mkdir(parents=True)
    titulo = slug.replace("-", " ").capitalize()
    d = dict(titulo=titulo, serie=serie, pilar=pilar, id=vid)
    for nombre, plantilla in [("guion.md", GUION), ("tomas.md", TOMAS), ("story.js", STORY), ("sonidos.json", SONIDOS),
                              ("fuentes.md", FUENTES), ("checklist.md", CHECKLIST), ("metadata.yaml", METADATA)]:
        (c / nombre).write_text(plantilla.format(**d), encoding="utf-8")
    print(f"  carpeta lista: {c}")


if __name__ == "__main__":
    main()
