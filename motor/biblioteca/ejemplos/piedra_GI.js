// EJEMPLO de story.js: "La piedra que dice GI" (37,02 s, 1111 cuadros a 30 fps).
// Es el story.js con el que se hizo el avance en la nube, adaptado al motor v1:
// los escenarios, las luces y los ayudantes de personajes ahora vienen de la biblioteca.
import * as embalse from './biblioteca/escenarios/embalse.js';
import * as muelle from './biblioteca/escenarios/muelle.js';
import * as piedra from './biblioteca/escenarios/piedra.js';
import * as plaza from './biblioteca/escenarios/plaza_zocalos.js';
import * as pueblo from './biblioteca/escenarios/pueblo_iglesia.js';
import * as bosque from './biblioteca/escenarios/bosque.js';
import * as montanas from './biblioteca/escenarios/montanas.js';
import * as nubes from './biblioteca/escenarios/nubes.js';
import { LUCES } from './biblioteca/luces.js';
import { tarjeta, efecto, parpadeo, respira } from './biblioteca/personajes.js';
const { RH, Rof, surf, MPD, G_C, U_X, gPts, uPts } = piedra;

// escenarios en orden: [módulo, opciones]. Las opciones por defecto ya son las de la piedra.
export const ESCENARIOS = [[embalse], [muelle, { x: 20, z: 172 }], [piedra], [plaza, { centro: [-150, 0, 72] }], [pueblo, { centro: [160, 0, 60] }], [bosque], [montanas], [nubes]];
// "La piedra que dice GI" — timed to voice.wav (37.02 s, 1111 frames @30).
// phrases (frames): 4-110 hook | 120-264 mide/pueblos | 276-389 el que pega primero | 401-579 se colgaron... edificio |
// 590-694 G enorme / palito de la U | 706-812 los pillaron / bololó | 825-894 les tocó parar | 908-1032 hoy no dice | 1041-1058 Dice... | 1075-1093 G, I.
export const FPS = 30, TOTAL = 1111, DECK = 0;
export const SHOTS = [
  { id: 'hook', a: 0, b: 118, light: 'today', today: true },
  { id: 'alto', a: 119, b: 199, light: 'day' },
  { id: 'claim', a: 200, b: 272, light: 'day' },
  { id: 'plan', a: 273, b: 395, light: 'day' },
  { id: 'cuelgan', a: 396, b: 584, light: 'day' },
  { id: 'pintan', a: 585, b: 700, light: 'day' },
  { id: 'pillaron', a: 701, b: 818, light: 'day' },
  { id: 'paran', a: 819, b: 900, light: 'golden' },
  { id: 'hoy', a: 901, b: 1040, light: 'today', today: true },
  { id: 'gi', a: 1041, b: 1110, light: 'today', today: true },
];
export const shotAt = (f) => SHOTS.find((s) => f >= s.a && f <= s.b) || SHOTS[SHOTS.length - 1];

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const smooth = (t) => { t = clamp(t); return t * t * t * (t * (t * 6 - 15) + 10); };
const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
const ramp = (f, a, b) => clamp((f - a) / (b - a));
const add3 = (a, b) => a.map((v, i) => v + b[i]);
const q = (x, n = 2) => Math.round(x * 10 ** n) / 10 ** n;

const plen = (pts) => { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; };
const tip = (pts, k) => { const L = plen(pts) * clamp(k, 0.001, 1); let acc = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); if (acc + d >= L) { const t = (L - acc) / d; return [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t]; } acc += d; } return pts[pts.length - 1]; };
const gK = (f) => f < 596 ? 0 : smooth(ramp(f, 596, 650));
const uK = (f) => f < 664 ? 0 : smooth(ramp(f, 664, 694));

const NAR = [20, 0.5, 170];
const PLAZA = [-150, 0, 72];
const DIR = (() => { const d = [150, -72], l = Math.hypot(...d); return [d[0] / l, d[1] / l]; })(), PERP = [-DIR[1], DIR[0]];
const G0 = [PLAZA[0] + DIR[0] * 4, 0, PLAZA[2] + DIR[1] * 4];
const gp = (a, b) => [G0[0] + PERP[0] * a + DIR[0] * b, 0, G0[2] + PERP[1] * a + DIR[1] * b];

// ---------- lights ----------
export const LIGHTS = LUCES;
export const lightFor = (S, f) => {
  const L = { ...LIGHTS[S.light] };
  L.shadowExt = { hook: f < 30 ? 6 : 160, alto: 160, claim: 8, plan: 14, cuelgan: f < 520 ? 22 : 160, pintan: f < 618 ? 22 : 60, pillaron: f < 736 ? 22 : 16, paran: 160, hoy: f < 978 ? 160 : 6, gi: f < 1062 ? 6 : 80 }[S.id];
  return L;
};

// ---------- cameras ----------
// helpers for cameras that look at the rock face along its normal
const faceCam = (ph, y, dist, dy = 0, dph = 0) => ({ pos: surf(ph + dph, y + dy, dist), look: surf(ph, y, 0) });
const A_PH = -12, B_PH = -4, C_PH = 4;
const yA = (f) => f < 401 ? 128 : lerp(128, 107, easeOut(ramp(f, 401, 445)));
const yB = (f) => f < 412 ? 131 : lerp(131, 112, easeOut(ramp(f, 412, 458)));
const yC = (f) => f < 424 ? 133 : lerp(133, 116, easeOut(ramp(f, 424, 470)));
const CAMS = {
  hook: [
    { f: 0, pos: [20.95, 2.25, 172.75], look: [20, 1.95, 170], fov: 36 },
    { f: 30, pos: [21.05, 2.27, 172.95], look: [20, 1.97, 170], fov: 36 },
    { f: 66, pos: [31, 6.5, 206], look: [2, 78, 70], fov: 44 },
    { f: 94, pos: [30, 7, 203], look: [1, 80, 68], fov: 43 },
    { f: 118, pos: [-4, 74, 175], look: [-6, 95, 86], fov: 31 },
  ],
  alto: [
    { f: 119, pos: [-4, 2.2, 150], look: [-3, 20, 80], fov: 44 },
    { f: 190, pos: [-3, 1.6, 162], look: [-1, 150, 20], fov: 50 },
    { f: 199, pos: [-3, 1.6, 163], look: [-1, 152, 20], fov: 50 },
  ],
  claim: [
    { f: 200, pos: [0.1, 1.55, 110.6], look: [0, 1.4, 104], fov: 36 },
    { f: 272, pos: [0.05, 1.52, 109.6], look: [0, 1.42, 104], fov: 35 },
  ],
  plan: [
    { f: 273, pos: add3(gp(0.3, -7.2), [0, 1.7, 0]), look: add3(gp(0, 0.6), [0, 1.35, 0]), fov: 40 },
    { f: 360, pos: add3(gp(-0.4, -6.0), [0, 1.6, 0]), look: add3(gp(0, 0.6), [0, 1.4, 0]), fov: 39 },
    { f: 395, pos: add3(gp(-0.6, -5.6), [0, 1.55, 0]), look: add3(gp(0, 0.6), [0, 1.45, 0]), fov: 38 },
  ],
  cuelgan: [],
  pintan: [],
  pillaron: [],
  paran: [
    { f: 819, pos: [14, 72, 196], look: [-4, 94, 80], fov: 34 },
    { f: 900, pos: [2, 88, 160], look: [-6, 95, 86], fov: 33 },
  ],
  hoy: [
    { f: 901, pos: [70, 16, 345], look: [0, 92, 0], fov: 36 },
    { f: 977, pos: [52, 12, 290], look: [0, 96, 10], fov: 34 },
    { f: 978, pos: [21.0, 2.25, 172.85], look: [20, 1.95, 170], fov: 36 },
    { f: 1040, pos: [20.9, 2.22, 172.55], look: [20, 1.97, 170], fov: 35 },
  ],
  gi: [
    { f: 1041, pos: [20.9, 2.22, 172.55], look: [20, 1.97, 170], fov: 35 },
    { f: 1061, pos: [20.7, 2.15, 171.95], look: [20, 2.0, 170], fov: 33 },
    { f: 1062, ...faceCam(-5.7, 95, 170, 2), fov: 31 },
    { f: 1093, ...faceCam(-5.7, 95, 132, 0.5), fov: 30, roll: -3 },
    { f: 1110, ...faceCam(-5.7, 95, 126, 0.3), fov: 29.5, roll: -3.6 },
  ],
};
// tracked cameras built from the painters' positions
const painterPos = (who, f) => {
  if (who === 'A') { if (f >= 590 && f < 819) { const t = tip(gPts, gK(f)); return surf(t[0] / MPD + 0.4, t[1] - 1.85, 1.3); } return surf(A_PH, f >= 819 ? slideY(yA(700), f, 830) : yA(f), 1.3); }
  if (who === 'B') { if (f >= 650 && f < 819) { const t = tip(uPts, uK(f)); return surf(t[0] / MPD + 0.4, t[1] - 1.85, 1.3); } return surf(f >= 590 ? lerp(B_PH, U_X / MPD + 0.4, smooth(ramp(f, 600, 660))) : B_PH, f >= 590 ? lerp(yB(f), 109.5 - 1.85, smooth(ramp(f, 600, 660))) : f >= 819 ? slideY(112, f, 836) : yB(f), 1.3); }
  return surf(C_PH, f >= 819 ? slideY(116, f, 842) : yC(f), 1.3);
};
const slideY = (y0, f, f0) => f < f0 ? y0 : Math.max(-20, y0 - 0.5 * 0.35 * (f - f0) ** 2);
CAMS.cuelgan = [
  { f: 396, ...faceCam(A_PH, 122, 9, 1.5, 3), fov: 38 },
  { f: 440, ...faceCam(A_PH, 108, 8.5, 1.0, 3.5), fov: 38 },
  { f: 470, ...faceCam(A_PH + 0.5, 107.6, 5.5, 0.2, 2.5), fov: 36 },
  { f: 484, ...faceCam(-1, 104, 26, 0, 4), fov: 42 },
  { f: 518, ...faceCam(2, 102, 34, 0, 9), fov: 42 },
  { f: 575, pos: [40, 60, 300], look: [6, 98, 60], fov: 33 },
  { f: 584, pos: [39, 60, 298], look: [6, 98, 60], fov: 33 },
];
CAMS.pintan = [
  { f: 585, ...faceCam(-10.5, 106.5, 9, 0.4, 2.5), fov: 38 },
  { f: 612, ...faceCam(-10.8, 106, 8.6, 0.3, 2.5), fov: 38 },
  { f: 652, ...faceCam(-5.7, 95, 120, 0, 3), fov: 32 },
  { f: 700, ...faceCam(-5.7, 95, 112, 0, 2), fov: 32 },
];
CAMS.pillaron = [
  { f: 701, ...faceCam(-3, 104, 11, 0.3, 1), fov: 40 },
  { f: 735, ...faceCam(-3, 103.6, 10, 0.2, 1), fov: 40 },
  { f: 736, pos: surf(-4.6, 3.6, 11.5), look: [-6.4, 1.25, 109.5], fov: 42 },
  { f: 780, pos: surf(-4.7, 3.4, 12.2), look: [-6.4, 1.3, 109.5], fov: 41 },
  { f: 818, pos: surf(-4.8, 3.2, 12.8), look: [-6.4, 1.35, 109.5], fov: 40, roll: 3 },
];
const KICKS = [{ f: 379, a: 0.03 }, { f: 631, a: 0.02 }, { f: 736, a: 0.03 }, { f: 787, a: 0.05 }, { f: 799, a: 0.06 }, { f: 1075, a: 0.04 }, { f: 1084, a: 0.06 }];
export const camAt = (f) => {
  const S = shotAt(f), K = CAMS[S.id];
  let c;
  if (f <= K[0].f) c = { ...K[0] };
  else if (f >= K[K.length - 1].f) c = { ...K[K.length - 1] };
  else for (let i = 0; i < K.length - 1; i++) if (f >= K[i].f && f <= K[i + 1].f) {
    const t = smooth((f - K[i].f) / (K[i + 1].f - K[i].f)), a = K[i], b = K[i + 1];
    c = { pos: lerp3(a.pos, b.pos, t), look: lerp3(a.look, b.look, t), fov: lerp(a.fov, b.fov, t), roll: lerp(a.roll || 0, b.roll || 0, t) };
    break;
  }
  // painters shots: close cameras glued to the painter, blended into the keyed moves
  const closeOn = (who, ff, dist_, dph, dy) => { const p = painterPos(who, ff), ph = Math.atan2(p[0], p[2]) * 180 / Math.PI; return { pos: surf(ph + dph, p[1] + dy, dist_), look: add3(p, [0, 1.15, 0]) }; };
  const blendTo = (cc, k) => { c.pos = lerp3(cc.pos, c.pos, k); c.look = lerp3(cc.look, c.look, k); };
  if (S.id === 'cuelgan' && f < 484) { const k = smooth(ramp(f, 466, 484)); const cc = closeOn('A', Math.min(f, 466), lerp(7.5, 6.2, ramp(f, 440, 466)), 2.6, lerp(2.0, 1.4, ramp(f, 440, 466))); c.fov = lerp(38, c.fov, k); blendTo(cc, k); }
  if (S.id === 'pintan' && f < 652) { const k = smooth(ramp(f, 618, 652)); const cc = closeOn('A', f, 7.5, 2.4, 1.6); c.fov = lerp(38, c.fov, k); blendTo(cc, k); }
  if (S.id === 'pillaron' && f < 736) { const cc = closeOn('A', 700, lerp(7.2, 6.4, ramp(f, 701, 735)), 2.0, 1.5); c.pos = cc.pos; c.look = cc.look; c.fov = 40; }
  for (const k of KICKS) { const d = f - k.f; if (d >= 0 && d < 7) { const s = (d % 2 ? -1 : 1) * k.a * (1 - d / 7); c.look = [c.look[0] + s * 2, c.look[1] + s * 3, c.look[2]]; c.roll = (c.roll || 0) + s * 20; } }
  c.flash = (f >= 119 && f < 125) ? (1 - (f - 119) / 6) * 0.85 : (f >= 901 && f < 907) ? (1 - (f - 901) / 6) * 0.85 : (f >= 1062 && f < 1065) ? 0.3 * (1 - (f - 1062) / 3) : 0;
  const sa = { hook: f < 30 ? NAR : [0, 60, 60], alto: [0, 40, 60], claim: [0, 0, 104], plan: G0, cuelgan: f < 520 ? surf(-5, 108, 0) : [0, 90, 60], pintan: f < 618 ? surf(-10, 104, 0) : surf(-5, 95, 0), pillaron: f < 736 ? surf(-3, 104, 0) : [-6, 0, 107], paran: [0, 90, 60], hoy: f < 978 ? [0, 80, 40] : NAR, gi: f < 1062 ? NAR : surf(-5, 95, 0) };
  c.shadowAt = sa[S.id];
  c.ink = (S.id === 'hoy' && f < 978) || S.id === 'alto' ? 2.2 : 2.5;
  return c;
};

// ---------- lens ----------
const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
export const dofAt = (f) => {
  const S = shotAt(f), C = camAt(f), narEye = [NAR[0], NAR[1] + 1.5, NAR[2]];
  switch (S.id) {
    case 'hook': return { focus: dist(C.pos, narEye), cinf: lerp(10, 0, smooth(ramp(f, 30, 58))) };
    case 'claim': return { focus: dist(C.pos, [0, 1.5, 104]), cinf: 10 };
    case 'plan': return { focus: dist(C.pos, add3(G0, [0, 1.5, 0])), cinf: 8 };
    case 'cuelgan': { const p = painterPos('A', f); return f < 484 ? { focus: dist(C.pos, add3(p, [0, 1.5, 0])), cinf: 8 } : { focus: 40, cinf: 0 }; }
    case 'pintan': { const p = painterPos('A', f); return f < 630 ? { focus: dist(C.pos, add3(p, [0, 1.5, 0])), cinf: lerp(8, 0, smooth(ramp(f, 612, 630))) } : { focus: 80, cinf: 0 }; }
    case 'pillaron': return f < 736 ? { focus: dist(C.pos, add3(painterPos('A', 700), [0, 1.5, 0])), cinf: 7 } : { focus: dist(C.pos, [-6, 1.5, 108]), cinf: 6 };
    case 'hoy': return f < 978 ? { focus: 300, cinf: 0 } : { focus: dist(C.pos, narEye), cinf: 9 };
    case 'gi': return f < 1062 ? { focus: dist(C.pos, narEye), cinf: 10 } : { focus: 100, cinf: 0 };
  }
  return { focus: 10, cinf: 0 };
};

// ---------- world state ----------
export const worldAt = (f) => {
  const S = shotAt(f);
  const W = { today: !!S.today, g: 0, u: 0, guide: 0, ropes: [] };
  if (S.today) { W.g = 1; W.u = 1; return W; }
  W.g = f >= 819 ? 1 : gK(f); W.u = f >= 819 ? 1 : uK(f);
  W.guide = f >= 470 && f < 819 ? smooth(ramp(f, 478, 500)) : 0;
  if (S.id === 'cuelgan' || S.id === 'pintan' || S.id === 'pillaron' || S.id === 'paran') {
    const ropeFor = (who, ph0) => { const p = painterPos(who, f); const ph = Math.atan2(p[0], p[2]) * 180 / Math.PI; return [q(ph, 2), q(p[1] + 1.9, 2), RH - 30]; };
    if (S.id !== 'paran' || f < 868) { W.ropes = [ropeFor('A'), ropeFor('B'), ropeFor('C')]; }
    if (S.id === 'paran') { const pull = f < 866 ? 0 : (f - 866) * 2.2; W.ropes = [[A_PH, q(Math.min(RH - 31, 8 + pull), 1), RH - 30], [B_PH, q(Math.min(RH - 31, 10 + pull), 1), RH - 30], [C_PH, q(Math.min(RH - 31, 12 + pull), 1), RH - 30]].filter((r) => r[1] < RH - 32); }
  }
  return W;
};

// ---------- actors (2D cards) ----------
const blinkAt = parpadeo, idleBob = respira;
const R = (T, who, o, pos, extra = {}) => tarjeta(T, who, o, pos, extra);
export const actorsAt = (f, T) => {
  const S = shotAt(f), out = [];
  const tint = S.light === 'golden' ? '#ffe2c8' : '#ffffff';
  const narr = (o, extra = {}) => out.push(R(T, 'costeno', { seed: 5, expr: 'grin', blink: blinkAt(f, 5), bob: idleBob(f, 5), steam: q((f * 0.25) % 6.28, 1), ...o }, NAR, { ground: NAR[1], tint, ...extra }));
  switch (S.id) {
    case 'hook': {
      const toast = f < 30;
      narr({ L: toast ? 'lift' : 'hang', holdL: 'tinto', R: f > 26 && f < 70 ? 'thumb' : 'hang', expr: f < 26 ? 'grin' : 'smile', look: f > 26 && f < 70 ? 0.4 : 0, headTilt: q(4 * Math.sin(f * 0.12), 1) });
      break;
    }
    case 'alto': case 'claim': {
      const isClaim = S.id === 'claim';
      const gA = { seed: 21, look: 0.5, facing: 1, blink: blinkAt(f, 21), bob: idleBob(f, 21) }, pA = { seed: 22, look: -0.5, facing: -1, blink: blinkAt(f, 22), bob: idleBob(f, 22, 0.006) };
      if (!isClaim) { gA.L = 'up'; gA.expr = 'grin'; pA.R = 'up'; pA.expr = 'stern'; out.push(R(T, 'guaA', gA, [-9, 0, 104])); out.push(R(T, 'penA', pA, [4, 0, 104])); break; }
      if (f < 229) { gA.L = 'up'; pA.R = 'up'; gA.expr = 'stern'; pA.expr = 'stubborn'; if (f > 209) { gA.L = 'belly'; pA.R = 'belly'; } }
      else if (f < 247) { gA.expr = 'grin'; gA.R = 'thumb'; gA.headTilt = q(6 * Math.sin((f - 229) * 0.6), 1); gA.bob = q(Math.abs(Math.sin((f - 229) * 0.35)) * 0.03, 3); pA.expr = 'squint'; pA.R = 'cross'; pA.L = 'cross'; }
      else { pA.expr = 'stubborn'; pA.L = 'thumb'; pA.headTilt = q(-6 * Math.sin((f - 247) * 0.6), 1); pA.bob = q(Math.abs(Math.sin((f - 247) * 0.35)) * 0.03, 3); gA.expr = 'squint'; gA.L = 'cross'; gA.R = 'cross'; }
      out.push(R(T, 'guaA', gA, [-0.62, 0, 104.4])); out.push(R(T, 'penA', pA, [0.62, 0, 103.7]));
      break;
    }
    case 'plan': {
      const idea = f >= 327, thumbs = f >= 363;
      const lean = (s) => f < 327 ? q(s * 6 * smooth(ramp(f, 276, 300)), 1) : 0;
      const laugh = (s) => thumbs ? q(Math.abs(Math.sin((f + s) * 0.5)) * 0.03, 3) : idleBob(f, s);
      out.push(R(T, 'guaB', { seed: 31, expr: idea ? (thumbs ? 'laugh' : 'grin') : 'whistle', L: idea ? 'up' : 'hang', R: thumbs ? 'thumb' : 'hip', blink: blinkAt(f, 31), bob: laugh(0), headTilt: idea && !thumbs ? q(5 * Math.sin(f * 0.3), 1) : 0 }, gp(0, 0.6)));
      out.push(R(T, 'guaC', { seed: 32, expr: thumbs ? 'laugh' : idea ? 'smile' : 'nervous', R: thumbs ? 'thumb' : 'hang', holdL: 'bucket', tilt: lean(1), look: -0.5, blink: blinkAt(f, 32), bob: laugh(3) }, gp(-1.15, 1.2)));
      out.push(R(T, 'guaD', { seed: 33, expr: thumbs ? 'laugh' : idea ? 'grin' : 'whistle', L: thumbs ? 'thumb' : 'hang', tilt: lean(-1), look: 0.5, blink: blinkAt(f, 33), bob: laugh(6) }, gp(1.15, 1.1)));
      out.push(R(T, 'pintA', { seed: 34, expr: thumbs ? 'laugh' : 'smile', holdR: 'brush', R: 'up', tilt: lean(0.6), look: -0.3, blink: blinkAt(f, 34), bob: laugh(9) }, gp(-0.55, 2.3)));
      out.push(R(T, 'pintB', { seed: 35, expr: thumbs ? 'grin' : 'nervous', holdL: 'bucket', tilt: lean(-0.6), look: 0.3, blink: blinkAt(f, 35), bob: laugh(12) }, gp(0.6, 2.4)));
      break;
    }
    case 'cuelgan': case 'pintan': case 'pillaron': case 'paran': {
      const caught = f >= 701 && f < 819, sliding = S.id === 'paran';
      const kick = (s) => q((f * 0.05 + s) % 1, 2);
      const pain = (who, key, seed, o) => { const p = painterPos(who, f); if (p[1] < -1) return; out.push(R(T, key, { seed, blink: blinkAt(f, seed), step: sliding ? kick(seed) : f < 470 ? kick(seed * 0.3) : 0, ...o }, p, { blob: false, tint })); };
      const busy = (S.id === 'pintan');
      pain('A', 'pintA', 41, caught ? { expr: 'shock', L: 'lift', R: 'cheek', look: 0 } : sliding ? { expr: 'nervous', L: 'lift', R: 'lift' } : { expr: busy ? (f > 640 ? 'grin' : 'whistle') : 'grin', L: 'lift', R: busy ? 'up' : 'hang', holdR: busy ? 'brush' : 'bucket', headTilt: busy ? q(4 * Math.sin(f * 0.4), 1) : 0 });
      pain('B', 'pintB', 42, caught ? { expr: 'shock', L: 'lift', R: 'cheek' } : sliding ? { expr: 'nervous', L: 'lift', R: 'lift' } : { expr: f > 664 && busy ? 'grin' : 'smile', L: 'lift', R: busy && f > 650 ? 'up' : 'hang', holdR: busy && f > 650 ? 'brush' : 'bucket' });
      pain('C', 'pintC', 43, caught ? { expr: 'nervous', L: 'lift', R: 'cheek' } : sliding ? { expr: 'shock', L: 'lift', R: 'lift' } : { expr: 'smile', L: 'lift', R: 'hang', holdR: 'bucket', look: -0.4 });
      if (S.id === 'pillaron' && f >= 736) { // El Peñol crowd below, looking up at the camera
        const mob = f >= 783, pts = [[-7.0, 107.2], [-5.4, 108.2], [-8.4, 109.2], [-4.2, 110.0], [-6.5, 110.8], [-9.6, 111.6], [-3.0, 112.0]], keys = ['penA', 'penB', 'penC', 'penD', 'penE', 'penB', 'penD'];
        keys.forEach((k, i) => {
          const s = 51 + i, jump = mob ? q(Math.abs(Math.sin((f + i * 5) * 0.55)) * 0.06, 3) : idleBob(f, s);
          const o = { seed: s, blink: blinkAt(f, s), bob: jump, expr: mob ? (i % 2 ? 'stubborn' : 'stern') : (i === 2 ? 'shock' : 'stern'), L: mob ? (i % 2 ? 'up' : 'point') : (i < 2 ? 'point' : 'hang'), R: mob ? 'up' : (i === 3 ? 'up' : 'hang'), look: q((i - 2) * -0.15, 2), headTilt: mob ? q(6 * Math.sin((f + i * 3) * 0.7), 1) : 0, tilt: mob ? q(3 * Math.sin((f + i * 7) * 0.45), 1) : 0 };
          out.push(R(T, k, o, [pts[i][0], 0, pts[i][1]]));
        });
      }
      break;
    }
    case 'hoy': {
      if (f >= 978) {
        const shake = f >= 984 && f < 1006 ? q(9 * Math.sin((f - 984) * 0.55), 1) : 0, wag = f >= 1010;
        narr({ L: f < 1006 ? 'point' : 'hang', R: wag ? 'up' : 'hang', holdL: f >= 1006 ? 'tinto' : undefined, expr: wag ? 'smile' : 'grin', headTilt: shake, look: f < 1006 ? -0.3 : 0 });
      }
      break;
    }
    case 'gi': {
      if (f < 1062) narr({ expr: f < 1050 ? 'squint' : 'grin', L: 'hang', holdL: 'tinto', R: 'cheek', look: 0.2, headTilt: q(-5 * smooth(ramp(f, 1041, 1055)), 1) });
      break;
    }
  }
  return out;
};

// ---------- 2D effects ----------
const FX = efecto;
export const fxAt = (f, T) => {
  const S = shotAt(f), out = [];
  // paint splats while painting
  if (S.id === 'pintan' && f > 596 && f < 652) { const t = tip(gPts, gK(f)); const k = q((f % 6) / 6, 2); out.push(FX('puffP' + k, (p) => { p.g.translate(150, 700); T.fxPuff(p, k); }, surf(t[0] / MPD, t[1] - 0.6, 1.6), 0.9)); }
  if (S.id === 'pintan' && f > 664 && f < 696) { const t = tip(uPts, uK(f)); const k = q((f % 6) / 6, 2); out.push(FX('puffU' + k, (p) => { p.g.translate(150, 700); T.fxPuff(p, k); }, surf(t[0] / MPD, t[1] - 0.6, 1.6), 0.9)); }
  if (S.id === 'pillaron' && f >= 701 && f < 736) { const t = q(((f - 701) / 34), 2); out.push(FX('shockS' + t, (p) => { p.g.translate(150, 400); T.fxCreak(p, t); }, add3(painterPos('A', 700), [0.6, 2.0, 0.4]), 0.6)); }
  if (S.id === 'pillaron' && f >= 783) {
    const t = q((f - 783) / 36, 2);
    out.push(FX('bololo' + t, (p) => T.fxBololo(p, t), [-5.6, 0.0, 114.0], 2.6, { order: 1 }));
    for (const [i, x, z] of [[0, -7.2, 107.2], [1, -3.8, 110.2]]) if ((f + i * 4) % 10 < 7) out.push(FX('anger' + i, (p) => T.fxAnger(p), [x + 0.35, 2.25, z + 0.1], 0.35));
  }
  if (S.id === 'plan' && f >= 327 && f < 362) { const t = q((f - 327) / 35, 2); out.push(FX('idea' + t, (p) => T.fxBurst(p, t, '#fff3b0', 10, 40, 200), add3(gp(0, 0.6), [0.25, 2.25, 0]), 0.8)); }
  return out;
};
