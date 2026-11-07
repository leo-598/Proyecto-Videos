"""Audio del video: música sintetizada + efectos + mezcla con la voz. Todo sale de sonidos.json.

Uso:  .venv\\Scripts\\python.exe motor\\v1\\audio.py videos\\<carpeta>
Salida: work/musica.wav, work/efectos.wav y out/mix_raw.wav (48 kHz, mono). La normalización a -14 LUFS la hace finish.py.

Mezcla (de mix.py de la piedra): la música queda exactamente a -6 dB (50 %) del RMS de la voz;
los efectos a <= -6 dB, con picos de como mucho 0,7 veces el pico de la voz. Una sola ganancia lineal, sin compresor.

Tiempos en sonidos.json: número = segundos · "f123" = cuadro 123 · "fin" = final de la historia · "@palabra" = cuando empieza esa palabra
(primera vez; "@palabra#2" = segunda vez; "@palabra>" = cuando termina). Formato completo en GUIA_MOTOR.md.
"""
import inspect
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

SR = 48000
rng = np.random.default_rng(7)
midi = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731


# ---------------- utilidades DSP ----------------
def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)


def lp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)


def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)


def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf) and j > i:
        buf[i:j] += sig[: j - i] * gain


def noise(d):
    return rng.standard_normal(int(d * SR)).astype(np.float32)


# ---------------- instrumentos ----------------
def pluck(f, dur=0.35, bright=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t) / (k + 1) for k in range(6))
    return (s * env(n, 0.003, dur * 0.35)).astype(np.float32)


def accordion(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for det in (1.0, 1.006):
        ph = 2 * np.pi * f * det * t + 0.004 * np.sin(2 * np.pi * 5.5 * t)
        s += sum(np.sin((k + 1) * ph) * (0.75 ** k) for k in range(7))
    a = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.05).clip(0)
    return lp_fast((s * a * 0.25).astype(np.float32), 3200)


def brass(fs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in fs:
        ph = 2 * np.pi * f * t + 0.003 * np.sin(2 * np.pi * 5 * t)
        s += sum(np.sin((k + 1) * ph) / (k + 1) ** 1.3 for k in range(8))
    a = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.15).clip(0)
    return lp_fast((s * a).astype(np.float32), 1800) / len(fs)


def guacharaca(d=0.09, acc=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 180 * t))) * np.exp(-t * 35) * acc
    return hp_fast(s.astype(np.float32), 2500)


def tambora(f=95, d=0.3):
    n = int(d * SR); t = np.arange(n) / SR; fr = f * (1 + 0.5 * np.exp(-t * 40))
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 11)).astype(np.float32)


def kick():
    n = int(0.3 * SR); t = np.arange(n) / SR; f = 48 + 80 * np.exp(-t * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)).astype(np.float32)


# ---------------- estilos de música ----------------
def cumbia(music, desde, hasta, bpm=96, melodia=True, tono=0):
    """Cumbia en Sol mayor: bombo, tambora a contratiempo, guacharaca, bajo y acordeón."""
    beat = 60 / bpm
    CH = {'G': (43, [67, 71, 74]), 'D': (38, [66, 69, 74]), 'C': (36, [64, 67, 72])}
    PROG = ['G', 'D', 'D', 'G', 'C', 'G', 'D', 'G']
    MEL = [74, 76, 74, 71, 72, 74, 71, 67, 69, 71, 72, 69, 66, 69, 74, 72, 71, 72, 74, 76, 74, 72, 71, 69, 67, 71, 69, 66, 67, 69, 71, 67]
    tt, bar = desde, 0
    while tt < hasta:
        root, tri = CH[PROG[bar % 8]]; root += tono; tri = [m + tono for m in tri]
        for b in range(4):
            tb = tt + b * beat
            if tb >= hasta:
                break
            place(music, kick(), tb, 0.45 if b in (0, 2) else 0.0)
            place(music, tambora(110 if b % 2 else 92), tb + beat * 0.5, 0.35)
            for e in range(4):
                place(music, guacharaca(0.08 if e % 2 else 0.12, 1.0 if e % 2 == 0 else 0.6), tb + e * beat / 4, 0.18)
            if b == 0: place(music, pluck(midi(root), 0.45, 0.35), tb, 0.55)
            if b == 2: place(music, pluck(midi(root + 7), 0.45, 0.35), tb, 0.5)
            if b == 3: place(music, pluck(midi(root + 5), 0.2, 0.35), tb + beat / 2, 0.4)
            for m in tri: place(music, accordion(midi(m - 12), beat * 0.35), tb + beat / 2, 0.05)
        if melodia and (bar // 8) % 2 == 0:
            for k in range(4):
                idx = (bar % 8) * 4 + k
                m = (MEL[idx] if idx < len(MEL) else 74) + tono
                if tt + k * beat < hasta: place(music, accordion(midi(m), beat * 0.8), tt + k * beat, 0.09)
        bar += 1; tt += beat * 4
    i0 = int((hasta - 0.06) * SR)
    if 0 <= i0 < len(music):
        music[i0:] *= np.linspace(1, 0, len(music) - i0) ** 10


ESTILOS = {"cumbia": cumbia}


def dron(music, desde, hasta, vol=0.12):
    """Dron de suspenso grave (sol, re, sol)."""
    dn = int((hasta - desde) * SR)
    if dn <= 0:
        return
    td = np.arange(dn) / SR
    d = (np.sin(2 * np.pi * 49 * td) + 0.5 * np.sin(2 * np.pi * 73.4 * td) + 0.25 * np.sin(2 * np.pi * 98 * td)) * np.minimum(1, td / 0.6)
    place(music, lp_fast(d.astype(np.float32), 500), desde, vol)


def remate(music, t, vol=0.12):
    """El "chan-chan" final: botón de acordeón + bombo y tambora."""
    for k, (m, d) in enumerate([(74, 0.12), (79, 0.3)]):
        for mm in (m, m - 5, m - 12): place(music, accordion(midi(mm), d), t + k * 0.17, vol)
    place(music, kick(), t + 0.17, 0.6); place(music, tambora(92), t + 0.17, 0.5)


# ---------------- efectos ----------------
def thunk(f0=90, d=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * t * (1 + 0.6 * np.exp(-t * 40))) * np.exp(-t * 14) + lp_fast(noise(d), 1200) * np.exp(-t * 30) * 0.5).astype(np.float32)
def rumble(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 160) * 3 * np.minimum(1, t / 0.15) * np.exp(-t / (d * 0.45))).astype(np.float32)
def crash(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n, np.float32)
    for k in range(14):
        tk = rng.uniform(0, d * 0.6); i = int(tk * SR); g = thunk(rng.uniform(60, 160), 0.35) * rng.uniform(0.3, 0.9)
        s[i:i + len(g)] += g[: n - i]
    return s + lp_fast(noise(d), 2500) * np.exp(-t * 3) * 0.25
def cuckoo():
    out = []
    for f, d in [(740, 0.16), (587, 0.24)]:
        n = int(d * SR); t = np.arange(n) / SR
        out.append(np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.01) * np.exp(-t * 6)); out.append(np.zeros(int(0.06 * SR)))
    return np.concatenate(out).astype(np.float32)
def scrape(d=0.8):
    n = int(d * SR); t = np.arange(n) / SR
    s = hp_fast(lp_fast(noise(d) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) * np.sin(np.pi * t / d), 5000), 1500)
    return (s * 0.6 + np.sin(2 * np.pi * 1870 * t) * np.exp(-t * 3) * 0.2).astype(np.float32)
def ting():
    n = int(1.2 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(2093, 4), (3136, 6), (4186, 8)]) * 0.3).astype(np.float32)
def sting():
    n = int(2.0 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 41 * t) * np.exp(-t * 1.5) * 1.2 + lp_fast(noise(2.0), 900) * np.exp(-t * 6) * 0.8
    stab = brass([midi(45), midi(48), midi(51)], 1.4); s[: len(stab)] += stab * 2.2 * np.exp(-np.arange(len(stab)) / SR * 2)
    return s.astype(np.float32)
def creak(d=0.6, f0=140):
    n = int(d * SR); t = np.arange(n) / SR
    ph = np.cumsum(f0 * (1 + 0.35 * np.sin(2 * np.pi * 1.3 * t / d))) / SR; pulses = (np.mod(ph, 1) < 0.08).astype(np.float32)
    return hp_fast(lp_fast(pulses * (0.6 + 0.4 * rng.random(n).astype(np.float32)), 2200) * np.sin(np.pi * t / d), 200) * 2.5
def snap():
    d = 0.5; n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(noise(d), 800) * np.exp(-t * 18) * 1.4 + np.pad(thunk(120, 0.4), (0, n - int(0.4 * SR))) * 0.6).astype(np.float32)
def splash(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 4000) * (np.exp(-t * 4) * np.minimum(1, t / 0.01)) + lp_fast(noise(d), 400) * np.exp(-t * 7) * 1.5).astype(np.float32)
def whoosh(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1500) * np.sin(np.pi * t / d) ** 2 * 0.6).astype(np.float32)
def snore(d=1.1):
    n = int(d * SR); t = np.arange(n) / SR
    buzz = (np.mod(np.cumsum(60 + 25 * np.sin(np.pi * t / d)) / SR, 1) < 0.3).astype(np.float32)
    return (lp_fast(buzz * 0.5 + noise(d) * 0.15, 700) * np.sin(np.pi * t / d) ** 2).astype(np.float32)
def leaves(d=2.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 6000), 2500) * (0.3 + 0.3 * np.sin(2 * np.pi * 0.7 * t) ** 2) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)).astype(np.float32)
def water(d=2.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 900) * 0.5 + hp_fast(lp_fast(noise(d), 3000), 1200) * 0.15 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))).astype(np.float32)
def ding():
    n = int(0.9 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(1568, 5), (2349, 7), (3136, 9)]) * 0.35).astype(np.float32)
def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 900 * np.exp(-t * 30) + 300
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)).astype(np.float32)
def splat():
    d = 0.25; n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1800) * np.exp(-t * 22) * 1.2 + np.sin(2 * np.pi * 140 * t) * np.exp(-t * 30) * 0.5).astype(np.float32)
def clank():
    n = int(0.5 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(620, 9), (1340, 12), (2210, 16)]) * 0.35 + hp_fast(noise(0.5), 2000) * np.exp(-t * 40) * 0.4).astype(np.float32)
def zip_(d=0.9):
    n = int(d * SR); t = np.arange(n) / SR; ph = np.cumsum(30 + 160 * (t / d)) / SR
    return (hp_fast(noise(d), 1500) * (0.5 + 0.5 * (np.mod(ph, 1) < 0.5)) * np.sin(np.pi * t / d)).astype(np.float32) * 0.7
def chalk(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 7000), 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t)) * np.sin(np.pi * t / d) * 0.6).astype(np.float32)
def crowd(d=2.0, angry=1.0):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n, np.float32)
    for k in range(10):
        f0 = rng.uniform(140, 320); ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.08 * np.sin(2 * np.pi * rng.uniform(2, 5) * t))) / SR
        v = sum(np.sin((h + 1) * ph) / (h + 1) for h in range(5)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(1.5, 4) * t + k)) ** 2
        s += v.astype(np.float32) * 0.12
    return lp_fast(s + lp_fast(noise(d), 1200) * 0.3, 2400) * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3) * angry
def birds(d=2.0):
    n = int(d * SR); s = np.zeros(n, np.float32)
    for k in range(int(d * 1.5)):
        t0 = rng.uniform(0, max(0.01, d - 0.4)); m = int(0.25 * SR); t = np.arange(m) / SR; f = rng.uniform(2800, 4200) * (1 + 0.15 * np.sin(2 * np.pi * 18 * t))
        c = (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.25) ** 2 * 0.25).astype(np.float32); i = int(t0 * SR); s[i:i + m] += c[: n - i]
    return s
def wahwah():
    out = []
    for m, d in [(55, 0.32), (54, 0.32), (53, 0.32), (52, 0.9)]:
        n = int(d * SR); t = np.arange(n) / SR; f = midi(m) * (1 - 0.03 * (t / d) * (d > 0.5))
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))) / SR
        s = sum(np.sin((k + 1) * ph) / (k + 1) ** 1.1 for k in range(8)) * (0.6 + 0.4 * np.sin(np.pi * t / d)) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.05)
        out.append(lp_fast(s.astype(np.float32), 1500))
    return np.concatenate(out) * 0.4


# nombre en sonidos.json -> (función, {nombre del parámetro en json: nombre en la función})
EFECTOS = {
    "zas": (whoosh, {"dur": "d"}), "golpe": (thunk, {"tono": "f0", "dur": "d"}), "retumbo": (rumble, {"dur": "d"}),
    "derrumbe": (crash, {"dur": "d"}), "cucu": (cuckoo, {}), "raspado": (scrape, {"dur": "d"}), "tin": (ting, {}),
    "ding": (ding, {}), "pop": (pop, {}), "golpe_dramatico": (sting, {}), "crujido": (creak, {"dur": "d", "tono": "f0"}),
    "chasquido": (snap, {}), "chapuzon": (splash, {"dur": "d"}), "ronquido": (snore, {"dur": "d"}), "salpicon": (splat, {}),
    "clanc": (clank, {}), "cremallera": (zip_, {"dur": "d"}), "tiza": (chalk, {"dur": "d"}), "wawa": (wahwah, {}),
    "agua": (water, {"dur": "d"}), "pajaros": (birds, {"dur": "d"}), "hojas": (leaves, {"dur": "d"}),
    "multitud": (crowd, {"dur": "d", "enojo": "angry"}),
}


# ---------------- tiempos ----------------
class Tiempo:
    def __init__(self, fps, words, dur):
        self.fps, self.words, self.dur = fps, words, dur

    def __call__(self, v):
        if isinstance(v, (int, float)):
            return float(v)
        v = str(v).strip()
        if v == "fin":
            return self.dur
        if v.startswith("f") and v[1:].isdigit():
            return int(v[1:]) / self.fps
        if v.startswith("@"):
            fin = v.endswith(">")
            nombre, _, n = v[1:].rstrip(">").partition("#")
            n = int(n or 1); buscada = comun.normalizar(nombre)
            hits = [w for w in self.words if comun.normalizar(w["w"]) == buscada]
            if len(hits) < n:
                raise SystemExit(f"sonidos.json: no encuentro la palabra '{nombre}' (vez {n}) en words.json")
            return hits[n - 1]["e" if fin else "s"]
        return float(v)


def cargar(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def gated_rms(x, gate_db=-40):
    w = int(0.4 * SR); n = len(x) // w
    if n == 0:
        return 1e-9
    r = np.sqrt((x[: n * w].reshape(n, w) ** 2).mean(1) + 1e-12)
    keep = r[r > r.max() * 10 ** (gate_db / 20)]
    return float(np.sqrt((keep ** 2).mean())) if len(keep) else 1e-9


def guardar(ruta, x):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def generar(carpeta):
    carpeta = Path(carpeta)
    aj = comun.ajustes(carpeta)
    fps = aj["fps"]
    cfg = json.loads((carpeta / "sonidos.json").read_text(encoding="utf-8"))
    words = json.loads((carpeta / "words.json").read_text(encoding="utf-8")) if (carpeta / "words.json").exists() else []
    DUR = comun.total_cuadros(carpeta) / fps
    T = Tiempo(fps, words, DUR)
    N = int(DUR * SR)

    music = np.zeros(N, np.float32)
    mu = cfg.get("musica") or {}
    if mu.get("estilo", "ninguna") != "ninguna":
        desde, hasta = T(mu.get("desde", 0)), T(mu.get("hasta", DUR))
        ESTILOS[mu["estilo"]](music, desde, hasta, bpm=mu.get("bpm", 96), melodia=mu.get("melodia", True), tono=mu.get("tono", 0))
        if mu.get("dron"):
            dron(music, hasta, DUR, mu.get("vol_dron", 0.12))
        if mu.get("remate") is not None:
            remate(music, T(mu["remate"]))

    sfx = np.zeros(N, np.float32)
    for e in cfg.get("ambientes", []) + cfg.get("efectos", []):
        fn, mapa = EFECTOS[e["sonido"]]
        params = {mapa[k]: v for k, v in e.items() if k in mapa}
        t0 = T(e.get("t", e.get("desde", 0)))
        if "hasta" in e and "d" in inspect.signature(fn).parameters:
            params["d"] = max(0.05, T(e["hasta"]) - t0)
        cada = T(e.get("cada", 0)) if e.get("cada") is not None else 0
        for k in range(int(e.get("repetir", 1))):
            p = dict(params)
            if "tono_paso" in e and "f0" in inspect.signature(fn).parameters:
                p["f0"] = p.get("f0", inspect.signature(fn).parameters["f0"].default) + e["tono_paso"] * k
            place(sfx, fn(**p), t0 + k * cada, e.get("vol", 0.5))

    (carpeta / "work").mkdir(exist_ok=True); (carpeta / "out").mkdir(exist_ok=True)
    pk = max(np.abs(music).max(), 1e-6)
    guardar(carpeta / "work" / "musica.wav", music / pk * 0.9)
    guardar(carpeta / "work" / "efectos.wav", sfx / max(np.abs(sfx).max(), 1e-6) * 0.9)

    # mezcla: música a -6 dB de la voz, efectos <= -6 dB y picos <= 0,7 x pico de la voz
    v = cargar(carpeta / "voz.wav"); v = np.pad(v, (0, max(0, N - len(v))))[:N]
    m = music.copy(); s = sfx.copy()
    rv = gated_rms(v); objetivo = rv * 10 ** (cfg.get("musica_db", -6) / 20)
    if np.abs(m).max() > 0: m *= objetivo / gated_rms(m)
    if np.abs(s).max() > 0:
        gs = (rv * 0.5) / gated_rms(s); gs = min(gs, 0.7 * np.abs(v).max() / max(np.abs(s).max(), 1e-9)); s *= gs
    db = lambda x: 20 * np.log10(max(x, 1e-12))  # noqa: E731
    mix = v + m + s
    mix *= min(0.89 / max(np.abs(mix).max(), 1e-9), 1.0)
    guardar(carpeta / "out" / "mix_raw.wav", mix)
    print(f"  mezcla: voz {db(rv):.1f} dBFS | música {db(gated_rms(m)) - db(rv):+.1f} dB vs voz | efectos {db(gated_rms(s)) - db(rv):+.1f} dB vs voz | {DUR:.2f} s")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    generar(sys.argv[1])
