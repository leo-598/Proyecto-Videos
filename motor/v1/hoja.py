"""Hoja de contacto: 10 cuadros pequeños del video para aprobar las tomas antes de la previa.

Uso:  .venv\\Scripts\\python.exe motor\\v1\\hoja.py videos\\<carpeta> [--n 10] [--cuadros 0,120,300]

- Elige el cuadro del medio de cada toma (lee SHOTS de story.js: { id, a, b }); si hay más de n tomas,
  reparte; si hay menos, añade cuadros intermedios. Con --cuadros usas los tuyos.
- Los renderiza a 540x960 en out/hoja/ (registro en out/hoja/render.log, no toca out/render.log).
- Arma out/hoja.jpg (5 x 2) con el nombre de la toma y el número de cuadro.
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402


def tomas(carpeta):
    txt = (carpeta / "story.js").read_text(encoding="utf-8")
    m = re.search(r"SHOTS\s*=\s*\[(.*?)\];", txt, re.S)
    if not m:
        return []
    out = []
    for t in re.finditer(r"\{([^{}]*)\}", m.group(1)):
        c = t.group(1)
        a, b, i = re.search(r"\ba:\s*(\d+)", c), re.search(r"\bb:\s*(\d+)", c), re.search(r"\bid:\s*['\"]([^'\"]+)", c)
        if a and b:
            out.append((i.group(1) if i else f"toma{len(out) + 1}", int(a.group(1)), int(b.group(1))))
    return out


def elegir(carpeta, n):
    total = comun.total_cuadros(carpeta)
    ts = tomas(carpeta)
    if not ts:
        return [(f"f{f}", f) for f in (round(total * (k + 0.5) / n) for k in range(n))]
    if len(ts) >= n:
        idx = [round(k * (len(ts) - 1) / (n - 1)) for k in range(n)] if n > 1 else [0]
        return [(ts[i][0], (ts[i][1] + ts[i][2]) // 2) for i in idx]
    # menos tomas que n: reparto los n cuadros entre las tomas según su largo
    largos = [b - a + 1 for _, a, b in ts]
    cupos = [1] * len(ts)
    while sum(cupos) < n:
        k = max(range(len(ts)), key=lambda i: largos[i] / (cupos[i] + 1))
        cupos[k] += 1
    sel = []
    for (nom, a, b), c in zip(ts, cupos):
        for j in range(c):
            sel.append((nom if c == 1 else f"{nom} {j + 1}/{c}", a + round((b - a) * (j + 0.5) / c)))
    return sel


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    carpeta = Path(args[0]).resolve()
    n = int(args[args.index("--n") + 1]) if "--n" in args else 10
    if "--cuadros" in args:
        sel = [(f"f{x}", int(x)) for x in args[args.index("--cuadros") + 1].split(",")]
    else:
        sel = elegir(carpeta, n)
    destino = carpeta / "out" / "hoja"
    destino.mkdir(parents=True, exist_ok=True)
    lista = ",".join(str(f) for _, f in sel)
    r = subprocess.run(["node", str(comun.V1 / "render.mjs"), str(carpeta), "--cuadros", lista, "--escala", "0.5",
                        "--salida", str(destino), "--rehacer", "--bloque", "100"], cwd=comun.RAIZ)
    if r.returncode != 0:
        raise SystemExit(f"El render de la hoja falló: mira {destino / 'render.log'}")

    w, h, cols = 270, 480, 5
    filas = (len(sel) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * w, filas * (h + 34)), "#14161A")
    d = ImageDraw.Draw(hoja)
    try:
        fuente = ImageFont.truetype(str(comun.FONTS / "Inter-SemiBold.ttf"), 20)
    except OSError:
        fuente = ImageFont.load_default()
    for k, (nom, f) in enumerate(sel):
        im = Image.open(destino / f"f{f:04d}.jpg").convert("RGB").resize((w, h))
        x, y = (k % cols) * w, (k // cols) * (h + 34)
        hoja.paste(im, (x, y))
        d.text((x + 8, y + h + 5), f"{k + 1}. {nom} · f{f}", fill="#F7F4EE", font=fuente)
    salida = carpeta / "out" / "hoja.jpg"
    hoja.save(salida, quality=88)
    print(f"  hoja de contacto: {salida}")
    for k, (nom, f) in enumerate(sel):
        print(f"   {k + 1:2d}. {nom:<16} cuadro {f}")


if __name__ == "__main__":
    main()
