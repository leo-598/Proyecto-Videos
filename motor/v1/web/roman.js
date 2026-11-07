FACE.snore = { eye: ["dash", "dash"], brow: [0, -1], mouth: "o" };
FACE.stubborn = { eye: ["lid", "lid"], brow: [4, -3], mouth: "frown" };
FACE.squint = { eye: ["slit", "slit"], brow: [3, -2], mouth: "dash" };

// ---------------- Roman-era cast (our own designs), built on the Pen / blob / face helpers above ----------------
const STEEL = "#aeb6bf", BRASS = "#d9a845", LEATHER = "#7a4a2a";
export const OUTFITS = {
  legion: { tunic: "#b8322f", cape: "#8f2228", skin: SKIN, helmet: true, armor: true, spear: true, shield: true },
  old: { tunic: "#9c4a3c", cape: "#6e3330", skin: "#f3d6bb", helmet: "old", armor: true, spear: true, shield: false, beard: "#f4f1ea", brows: "#f4f1ea" },
  toga: { tunic: "#f1ead8", skin: "#f5c9a0", toga: "#6b3c8f", hair: "#3b2a20", stout: true },
  civA: { tunic: "#4f7fb8", skin: "#f5c9a0", hair: "#5a3b2a" },
  civB: { tunic: "#d9a441", skin: SKIN, hair: "#2b211c", dress: "#c25a7a" },
  civC: { tunic: "#5d8a3a", skin: "#c99067", hair: "#1e1714", stout: true },
  workA: { tunic: "#8a5d3b", skin: "#f5c9a0", cap: "#c2733a", apron: "#d8c9a6" },
  workB: { tunic: "#3f6a6f", skin: "#ecd0b6", cap: "#5b4a8a", moustache: "#4a3020" },
};

/** galea: iron bowl, brass brow band, cheek guards, transverse red crest */
const galea = (p, H, cx, hc, light, thick, ow, old, u) => {
  const crest = old ? "#8d4b3f" : "#d2372f", bowl = old ? "#8f8a7e" : STEEL;
  // crest (behind the bowl top)
  const cy0 = hc - H.b * 0.98;
  const cr = ellPts(cx, cy0, 0.66 * 2 * H.a, 0.42 * 2 * H.b, 180, 360, 0, 40);
  cr.push([cx + 0.66 * 2 * H.a * 0.98, cy0 + 4 * u], [cx - 0.66 * 2 * H.a * 0.98, cy0 + 4 * u]);
  const crP = [...ellPts(cx, cy0 + 2 * u, 0.62 * 2 * H.a, 0.36 * 2 * H.b, 180, 360, 0, 40)];
  p.shadedFill(crP, crest, mul(crest, [0.7, 0.62, 0.7]), light, 0.62 * 2 * H.a, 0.3);
  p.clip(crP, () => { for (let i = -9; i <= 9; i++) p.stroke([[cx + i * 7.4 * u, cy0], [cx + i * 9.4 * u, cy0 - 0.62 * H.b * Math.cos(i / 11)]], 1.4 * u, mul(crest, [0.62, 0.55, 0.62])); });
  if (old) p.clip(crP, () => { for (let i = 0; i < 6; i++) p.ell(cx + (i - 3) * 22 * u, cy0 - 18 * u - (i % 2) * 10 * u, 9 * u, 5 * u, "#6f6a5e", 0); });
  p.inkRing(crP, ow * 0.85, thick);
  p.poly(rrect(cx - 10 * u, cy0 - 6 * u, cx + 10 * u, cy0 + 6 * u, 3 * u), BRASS, 2 * u);
  // bowl: upper head cap
  const bandY = hc - H.b * 0.42;
  const bp = ellPts(cx, bandY, H.a * 1.05, H.b * 0.66, 180, 360, 0, 48);
  p.shadedFill(bp, bowl, mul(bowl, [0.62, 0.64, 0.72]), light, H.a, 0.4);
  p.clip(bp, () => {
    p.stroke(ellPts(cx - 20 * u, bandY - 0.3 * H.b, 0.25 * H.a, 0.18 * H.b, 200, 300, 0, 16), 4 * u, "#ffffff55");
    if (old) for (let i = 0; i < 9; i++) p.ell(cx + Math.sin(i * 2.3) * 0.8 * H.a, bandY - (0.08 + 0.5 * ((i * 0.37) % 1)) * H.b, (3 + (i % 3) * 2) * u, (2 + (i % 2)) * u, "#8a4b22", 0);
  });
  p.inkRing(bp, ow * 0.9, thick);
  p.band([[cx - H.a * 1.04, bandY], [cx + H.a * 1.04, bandY]], old ? "#a88a4a" : BRASS, 7 * u, 1.8 * u, "round");
  for (const s of [-1, 1]) p.dot(cx + s * 0.55 * H.a, bandY, 2.2 * u, "#fff3c4");
};
const cheeks = (p, H, cx, hc, light, ow, old, u) => {
  const bowl = old ? "#8f8a7e" : STEEL;
  for (const s of [-1, 1]) {
    const x0 = cx + s * 0.78 * H.a, x1 = cx + s * 1.07 * H.a, y0 = hc - H.b * 0.42, y1 = hc + H.b * 0.48;
    const pts = [[x0, y0], [x1, y0], [x1 - s * 0.04 * H.a, y1 - 0.1 * H.b], [x0 + s * 0.06 * H.a, y1], [x0 - s * 0.05 * H.a, (y0 + y1) / 2]];
    p.shadedFill(pts, bowl, mul(bowl, [0.62, 0.64, 0.72]), light, 0.2 * H.a, 0.3);
    p.poly(pts, null, ow * 0.8);
    p.dot((x0 + x1) / 2, (y0 + y1) / 2 - 0.05 * H.b, 2.2 * u, BRASS);
  }
};
const cobweb = (p, cx, cy, r, u) => {
  const g = p.g; g.save(); g.globalAlpha = 0.8;
  for (let i = 0; i < 7; i++) { const a = -Math.PI * (0.05 + 0.9 * i / 6); p.stroke([[cx, cy], [cx + Math.cos(a) * r, cy + Math.sin(a) * r]], 1.1 * u, "#f2f2f2"); }
  for (let k = 1; k <= 4; k++) { const rr = r * k / 4.3, pts = []; for (let i = 0; i < 7; i++) { const a = -Math.PI * (0.05 + 0.9 * i / 6); pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); } p.stroke(pts, 1 * u, "#f2f2f2"); }
  g.restore();
};

/** front-facing Roman-era character. opts: expr, blink, look, facing, seed, L/R arm poses, tilt, headTilt, bob, nohelmet, light */
export const romanFront = (p, key, opts = {}) => {
  const O = typeof key === "string" ? OUTFITS[key] : key;
  const { expr = "neutral", blink = 0, look = 0, facing = 0, seed = 3, L = "hang", R = O.spear ? "spear" : "hang", tilt = 0, headTilt = 0,
    bob = 0, nohelmet = false, light = rad(-120), web = false, step = 0 } = opts;
  const lid = lidOf(blink), skin = O.skin ?? SKIN;
  const H = headBlob(seed, 118, facing), W = 2 * H.a, HH = 2 * H.b, u = W / 100;
  const torsoL = O.stout ? 1.12 : 1.08, legsL = 1.38, sole = 975;
  const torsoBot = sole - legsL * HH - bob * HH, chin = torsoBot - torsoL * HH, hc = chin - H.b, hipY = torsoBot - 0.12 * HH;
  const thick = thickAngle(light), ow = 5 * u, cx = 300;
  const legCol = O.pants || mix(O.tunic, INK, 0.62), armCol = mix(O.tunic, INK, 0.5);
  const helmet = !!O.helmet && !nohelmet, old = O.helmet === "old";
  p.rot = null;
  // ---- cape behind everything ----
  if (O.cape) {
    const cp = [[cx - 0.48 * W, chin + 0.08 * HH], [cx + 0.48 * W, chin + 0.08 * HH], [cx + 0.62 * W, sole - 0.55 * HH], [cx + 0.2 * W, sole - 0.45 * HH], [cx - 0.2 * W, sole - 0.5 * HH], [cx - 0.62 * W, sole - 0.55 * HH]];
    p.gradFill(cp, O.cape, mul(O.cape, [0.6, 0.6, 0.7]), light); p.inkRing(cp, ow * 0.8, thick);
  }
  // ---- legs ----
  const dress = !!O.dress;
  for (const side of [-1, 1]) {
    const up = Math.max(0, Math.sin(Math.PI * 2 * (step + (side > 0 ? 0.5 : 0)))) * 30 * (step ? 1 : 0);
    const hx = cx + side * 16 * u, fx = cx + side * 22 * u, fy = sole - 4 * u - up;
    p.stroke(curve([hx, hipY], [(hx + fx) / 2 + side * 2 * u, (hipY + fy) / 2], [fx, fy]), 5.8 * u, legCol);
    const sandal = O.helmet ? LEATHER : "#5a3b2a";
    p.stroke([[fx - side * 3 * u, fy], [fx + side * 13 * u, fy + 0.5 * u]], 7.5 * u + 3, INK);
    p.stroke([[fx - side * 3 * u, fy], [fx + side * 13 * u, fy + 0.5 * u]], 7.5 * u, sandal);
    if (O.helmet) for (let k = 1; k <= 3; k++) p.stroke([[fx - 4 * u, fy - k * 0.07 * HH], [fx + 4 * u, fy - k * 0.07 * HH - 2 * u]], 2 * u, LEATHER);
  }
  // ---- upper body ----
  p.rot = tilt ? [rad(tilt), cx, hipY] : null;
  const T = { a: (0.4 * W) / 1.06 * (O.stout ? 1.12 : 1), b: 0.5 * (torsoBot - (chin - 0.25 * HH)), nTop: 2.2, nBot: 2.6, egg: O.stout ? 0.17 : 0.12, asym: 0.04 * facing, rot: 0, noise: 0.006, seed: seed + 7 };
  const tcx = cx + 3 * u * facing, tcy = torsoBot - T.b, tp = blobPts(tcx, tcy, T);
  const S = (side) => [tcx + side * 0.85 * T.a, chin + 0.12 * HH];
  const arm = (side, pose) => {
    const s = S(side), X = (k) => tcx + side * (T.a * 1.1 + k * u);
    switch (pose) {
      case "spear": return { pts: [s, [X(6), s[1] + 0.42 * HH], [X(10), s[1] + 0.2 * HH]], front: false };
      case "point": return { pts: [s, [X(28), s[1] - 0.02 * HH], [X(62), s[1] - 0.1 * HH]], front: false, finger: true };
      case "up": return { pts: [s, [X(14), s[1] - 0.3 * HH], [X(22), s[1] - 0.75 * HH]], front: false };
      case "wave": return { pts: [s, [X(16), s[1] - 0.2 * HH], [X(30 + 10 * Math.sin(opts.wv || 0)), s[1] - 0.62 * HH]], front: false };
      case "hip": return { pts: [s, [X(22), s[1] + 0.3 * HH], [tcx + side * T.a * 0.95, torsoBot - 0.3 * HH]], front: false };
      case "belly": return { pts: [s, [X(8), s[1] + 0.45 * HH], [tcx + side * 0.25 * T.a, torsoBot - 0.35 * HH]], front: true };
      case "temple": return { pts: [s, [X(26), s[1] + 0.05 * HH], [cx + side * (H.a + 16 * u), hc - 0.1 * HH]], front: false, swirl: true };
      case "lift": return { pts: [s, [X(20), s[1] - 0.25 * HH], [X(4), s[1] - 0.82 * HH]], front: false };
      case "shield": return { pts: [s, [X(4), s[1] + 0.4 * HH], [tcx + side * 0.6 * T.a, torsoBot - 0.1 * HH]], front: true };
      case "cross": return { pts: [s, [X(2), s[1] + 0.38 * HH], [tcx - side * 0.45 * T.a, s[1] + 0.32 * HH]], front: true };
      case "reach": { const lf = (opts.lift || 0) * 0.62 * HH; return { pts: [s, [X(42), s[1] - 0.12 * HH - lf * 0.6], [X(82), s[1] - 0.5 * HH - lf]], front: false }; }
      case "cheek": return { pts: [s, [X(16), s[1] + 0.05 * HH], [cx + side * (H.a + 2 * u), hc + 0.25 * H.b]], front: false };
      case "thumb": return { pts: [s, [X(20), s[1] + 0.12 * HH], [X(44), s[1] - 0.12 * HH]], front: false, thumb: true };
      default: return { pts: [s, [X(4), s[1] + 0.48 * HH], [X(3), chin + 1.04 * HH]], front: false };
    }
  };
  const arms = [arm(-1, L), arm(1, R)]; arms[0].item = opts.holdL; arms[1].item = opts.holdR; arms[0].side = -1; arms[1].side = 1;
  const drawArm = (a) => {
    p.stroke(curve(a.pts[0], a.pts[1], a.pts[2]), 5.2 * u, armCol);
    const [hx, hy] = a.pts[2];
    p.dot(hx, hy, 5.5 * u);
    if (a.finger) { const dx = a.pts[2][0] - a.pts[1][0], dy = a.pts[2][1] - a.pts[1][1], l = Math.hypot(dx, dy); p.stroke([[hx, hy], [hx + dx / l * 14 * u, hy + dy / l * 14 * u]], 2.6 * u); }
    if (a.thumb) p.stroke([[hx, hy], [hx + Math.sign(hx - cx) * 6 * u, hy - 12 * u]], 2.6 * u);
    if (a.item) holdItem(p, a.item, hx, hy, a.side, u, opts);
  };
  // spear behind
  if (O.spear && R === "spear") {
    const [hx, hy] = arms[1].pts[2], s0 = [hx + 2 * u, sole - 2 * u], s1 = [hx - 3 * u, 70];
    p.band([s0, s1], old ? "#6d5236" : "#8a5a34", 4.2 * u, 1.4 * u, "round");
    const tip = [[s1[0] - 7 * u, s1[1] + 6 * u], [s1[0], s1[1] - 34 * u], [s1[0] + 7 * u, s1[1] + 6 * u], [s1[0], s1[1] + 14 * u]];
    p.poly(tip, old ? "#8b7c6a" : "#c9cfd6", 2 * u);
    if (web) cobweb(p, s1[0] - 2 * u, s1[1] + 60 * u, 70 * u, u);
  }
  for (const a of arms) if (!a.front) drawArm(a);
  // torso
  if (dress) {
    const D = { a: 0.5 * W * 0.98, b: 0.5 * ((sole - 0.35 * HH) - (chin - 0.2 * HH)), nTop: 2.0, nBot: 3.0, egg: 0.35, asym: 0, rot: 0, noise: 0.006, seed: seed + 9 };
    const dp = blobPts(cx, sole - 0.35 * HH - D.b, D);
    p.gradFill(dp, O.dress, mul(O.dress, SH_CLOTH), light); p.inkRing(dp, ow, thick);
  }
  // skirt / pteruges below the torso
  if (!dress) {
    const sk = [[tcx - 0.92 * T.a, torsoBot - 0.2 * HH], [tcx + 0.92 * T.a, torsoBot - 0.2 * HH], [tcx + 1.0 * T.a, torsoBot + 0.3 * HH], [tcx - 1.0 * T.a, torsoBot + 0.3 * HH]];
    p.gradFill(sk, O.tunic, mul(O.tunic, SH_CLOTH), light); p.poly(sk, null, ow * 0.8);
    if (O.armor) for (let i = -3; i <= 3; i++) { const x = tcx + i * 0.27 * T.a, st = [[x - 9 * u, torsoBot - 0.05 * HH], [x + 9 * u, torsoBot - 0.05 * HH], [x + 9 * u, torsoBot + 0.22 * HH], [x - 9 * u, torsoBot + 0.22 * HH]]; p.poly(st, old ? "#5e4632" : LEATHER, 1.6 * u); }
  }
  p.gradFill(tp, O.tunic, mul(O.tunic, SH_CLOTH), light);
  p.clip(tp, () => {
    if (O.armor) {
      const top = chin - 0.1 * HH, bot = torsoBot - 0.25 * HH, n = 5;
      for (let i = 0; i < n; i++) {
        const y0 = top + (bot - top) * i / n, y1 = top + (bot - top) * (i + 1) / n;
        const c = old ? (i % 2 ? "#8d8679" : "#9a9384") : (i % 2 ? "#a7b0ba" : "#bcc4cc");
        p.poly([[tcx - 1.5 * T.a, y0], [tcx + 1.5 * T.a, y0 + 3 * u], [tcx + 1.5 * T.a, y1 + 3 * u], [tcx - 1.5 * T.a, y1]], c, 1.8 * u);
      }
      p.band([[tcx - 1.4 * T.a, torsoBot - 0.2 * HH], [tcx + 1.4 * T.a, torsoBot - 0.2 * HH]], LEATHER, 0.08 * HH, 1.5 * u);
      for (let i = -2; i <= 2; i++) p.dot(tcx + i * 0.3 * T.a, torsoBot - 0.2 * HH, 2.4 * u, BRASS);
      if (old) for (let i = 0; i < 5; i++) p.ell(tcx + Math.sin(i * 1.7) * 0.7 * T.a, top + (bot - top) * ((i * 0.31) % 1), 6 * u, 3 * u, "#8a4b22", 0);
    } else {
      p.band([[tcx - 1.4 * T.a, torsoBot - 0.24 * HH], [tcx + 1.4 * T.a, torsoBot - 0.24 * HH]], O.apron ? "#5a3b2a" : "#e2c27a", 0.05 * HH, 1.2 * u);
      if (O.toga) p.band([[tcx - 1.0 * T.a, chin - 0.1 * HH], [tcx + 1.1 * T.a, torsoBot - 0.1 * HH]], O.toga, 0.16 * HH, 1.6 * u);
      if (O.apron) p.poly([[tcx - 0.55 * T.a, torsoBot - 0.2 * HH], [tcx + 0.55 * T.a, torsoBot - 0.2 * HH], [tcx + 0.6 * T.a, torsoBot + 0.2 * HH], [tcx - 0.6 * T.a, torsoBot + 0.2 * HH]], O.apron, 1.6 * u);
      p.stroke([[tcx - 0.2 * T.a, chin + 0.02 * HH], [tcx, chin + 0.16 * HH], [tcx + 0.2 * T.a, chin + 0.02 * HH]], 2 * u);
    }
  });
  p.inkRing(tp, ow, thick);
  if (O.splat) p.clip(tp, () => { const r = (k) => ((Math.sin(k * 91.7 + seed) * 43758.5) % 1 + 1) % 1; for (let i = 0; i < 9; i++) { const col = ['#ffffff', '#ffffff', '#f2c230', '#e8574a'][i % 4]; p.ell(tcx + (r(i) - 0.5) * 1.6 * T.a, chin + 0.1 * HH + r(i + 20) * (torsoBot - chin), (5 + r(i + 40) * 7) * u, (4 + r(i + 60) * 5) * u, col, 0); } });
  if (O.ruana) ruanaOn(p, O, tcx, T, chin, torsoBot, HH, u, ow, thick, light);
  if (O.mochila) mochilaOn(p, tcx, T, chin, torsoBot, HH, u, ow);
  if (O.armor) for (const s of [-1, 1]) { // shoulder plates
    const sp = ellPts(tcx + s * 0.72 * T.a, chin + 0.1 * HH, 0.42 * T.a, 0.13 * HH, 180, 360, s * 8, 20);
    p.poly(sp, old ? "#9a9384" : "#c5ccd3", 1.8 * u);
  }
  if (O.moss) {/* reserved */}
  for (const a of arms) if (a.front) drawArm(a);
  // shield in front, held by the left hand
  if (O.shield && L === "shield") {
    const sx = tcx - 0.55 * T.a, sy = torsoBot + 0.05 * HH, sw = 0.36 * W, sh = 0.78 * HH;
    const sp = rrect(sx - sw, sy - sh, sx + sw, sy + sh, 8 * u);
    p.gradFill(sp, "#c0302c", "#7d1d22", light);
    p.clip(sp, () => {
      p.band([[sx - sw, sy], [sx + sw, sy]], BRASS, 6 * u, 1.2 * u);
      p.band([[sx, sy - sh], [sx, sy + sh]], BRASS, 6 * u, 1.2 * u);
      for (const s of [-1, 1]) { p.stroke([[sx + s * 12 * u, sy - 14 * u], [sx + s * 34 * u, sy - 46 * u], [sx + s * 22 * u, sy - 44 * u], [sx + s * 46 * u, sy - 74 * u]], 3.5 * u, BRASS); p.stroke([[sx + s * 12 * u, sy + 14 * u], [sx + s * 34 * u, sy + 46 * u], [sx + s * 22 * u, sy + 44 * u], [sx + s * 46 * u, sy + 74 * u]], 3.5 * u, BRASS); }
      p.stroke(ellPts(sx - sw * 0.5, sy - sh * 0.7, sw * 0.3, sh * 0.1, 200, 320, 0, 10), 3 * u, "#ffffff44");
    });
    p.ell(sx, sy, 13 * u, 13 * u, "#e6c068", 2.2 * u);
    p.inkRing(sp, ow, thick);
  }
  // ---- head ----
  const [cpx, cpy] = rotAbout([cx, chin], rad(tilt), [cx, hipY]);
  const Ah = tilt + headTilt;
  p.rot = Ah ? [rad(Ah), cx, chin, cpx - cx, cpy - chin] : null;
  if (helmet) galea(p, H, cx, hc, light, thick, ow, old, u);
  const hp = blobPts(cx, hc, H);
  if (O.hair && !helmet) { const hb = blobPts(cx, hc - 0.03 * HH, { ...H, a: H.a * 1.04, b: H.b * 1.05 }); p.poly(hb, O.hair, 0); }
  p.shadedFill(hp, skin, mul(skin, SH_SKIN), light, H.a);
  p.inkRing(hp, ow, thick);
  if (helmet) {
    const bandY = hc - H.b * 0.42, bp = ellPts(cx, bandY, H.a * 1.05, H.b * 0.66, 180, 360, 0, 48);
    p.shadedFill(bp, old ? "#8f8a7e" : STEEL, mul(old ? "#8f8a7e" : STEEL, [0.62, 0.64, 0.72]), light, H.a, 0.4);
    p.clip(bp, () => { p.stroke(ellPts(cx - 20 * u, bandY - 0.3 * H.b, 0.25 * H.a, 0.18 * H.b, 200, 300, 0, 16), 5 * u, "#ffffff66");
      if (old) for (let i = 0; i < 9; i++) p.ell(cx + Math.sin(i * 2.3) * 0.8 * H.a, bandY - (0.08 + 0.5 * ((i * 0.37) % 1)) * H.b, (4 + (i % 3) * 2) * u, (2.5 + (i % 2)) * u, "#8a4b22", 0); });
    p.poly(bp, null, ow * 0.9);
    p.band([[cx - H.a * 1.05, bandY], [cx + H.a * 1.05, bandY]], old ? "#a88a4a" : BRASS, 7 * u, 1.8 * u, "round");
    p.poly(rrect(cx - 4 * u, bandY - 0.55 * H.b, cx + 4 * u, bandY - 3 * u, 2 * u), old ? "#a88a4a" : BRASS, 1.5 * u);
    cheeks(p, H, cx, hc, light, ow, old, u);
  } else if (O.cap) hatOn(p, { hat: "cap", cap: O.cap, jacket: O.tunic }, hp, H, cx, hc, light, seed, facing, false);
  else if (O.hair) hatOn(p, { hat: "hair", hair: O.hair, jacket: O.tunic }, hp, H, cx, hc, light, seed, facing, false);
  else if (O.helmet && nohelmet) { // bald old head with white side tufts
    for (const s of [-1, 1]) p.ell(cx + s * 0.9 * H.a, hc - 0.1 * H.b, 0.22 * H.a, 0.3 * H.b, "#f4f1ea", 3 * u);
  }
  if (O.beard) {
    const bd = blobPts(cx + 6 * u * facing, hc + 0.85 * H.b, { a: 0.62 * H.a, b: 0.75 * H.b, nTop: 2.4, nBot: 1.6, egg: -0.35, asym: 0, rot: 0, noise: 0.02, seed: seed + 4 });
    p.shadedFill(bd, O.beard, mul(O.beard, [0.86, 0.86, 0.92]), light, 0.6 * H.a, 0.3);
    p.clip(bd, () => { for (let i = -3; i <= 3; i++) p.stroke([[cx + i * 9 * u, hc + 0.45 * H.b], [cx + i * 7 * u, hc + 1.35 * H.b]], 1.2 * u, "#c9c4bb"); });
    p.inkRing(bd, ow * 0.8, thick);
  }
  faceFront(p, cx, hc, W, expr, facing, look, lid, helmet, skin, O.beard ? O.beard : O.moustache, !!O.stout);
  if (O.brows) for (const s of [-1, 1]) p.ell(cx + 7 * u * facing + s * 14 * u, hc - 20 * u, 11 * u, 5 * u, O.brows, 2 * u);
  if (O.vueltiao && !opts.nohat) vueltiao(p, H, cx, hc, u, ow, thick, light, opts.hatTip || 0);
  if (O.beard) { // re-draw the mouth over the beard for open mouths
    if (expr === "shock" || expr === "snore") p.ell(cx + 8 * u * facing, hc + 22 * u, 6 * u, 7 * u, "#5a1e28", 2 * u);
  }
  p.rot = null;
  if (arms.some((a) => a.swirl)) { // cuckoo swirl next to the temple
    const a = arms.find((x) => x.swirl), [hx, hy] = a.pts[2], ph = opts.swirl || 0, pts = [];
    for (let i = 0; i < 40; i++) { const t = i / 40 * Math.PI * 4 + ph, r = (4 + i * 0.7) * u; pts.push([hx + Math.cos(t) * r, hy - 40 * u + Math.sin(t) * r]); }
    p.stroke(pts, 3 * u, "#ffffff"); p.stroke(pts, 1.4 * u, INK);
  }
};

/** loose helmet prop card (lifted off the old soldier) */
export const helmetCard = (p) => {
  const H = headBlob(3, 118, 0), u = 2 * H.a / 100, hc = 560, light = rad(-120), thick = thickAngle(light), ow = 5 * u;
  galea(p, H, 300, hc, light, thick, ow, true, u);
  const bandY = hc - H.b * 0.42, bp = ellPts(300, bandY, H.a * 1.05, H.b * 0.66, 180, 360, 0, 48);
  // dark inside visible from below
  p.ell(300, bandY, H.a * 1.05, 0.12 * H.b, "#2a221e", 0);
  p.shadedFill(bp, "#8f8a7e", mul("#8f8a7e", [0.62, 0.64, 0.72]), light, H.a, 0.4);
  p.clip(bp, () => { for (let i = 0; i < 9; i++) p.ell(300 + Math.sin(i * 2.3) * 0.8 * H.a, bandY - (0.08 + 0.5 * ((i * 0.37) % 1)) * H.b, (4 + (i % 3) * 2) * u, (2.5 + (i % 2)) * u, "#8a4b22", 0); });
  p.poly(bp, null, ow * 0.9);
  p.band([[300 - H.a * 1.05, bandY], [300 + H.a * 1.05, bandY]], "#a88a4a", 7 * u, 1.8 * u, "round");
  cheeks(p, H, 300, hc, light, ow, true, u);
};

/** ZZZ for the sleeping guard */
export const fxZ = (p, t) => {
  const g = p.g; g.save(); g.font = "900 120px Arial Black, Arial"; g.lineJoin = "round";
  for (let i = 0; i < 3; i++) {
    const k = (t + i / 3) % 1, x = 220 + i * 70 + Math.sin(k * 6) * 20, y = 700 - k * 500, s = 0.5 + k * 0.7;
    g.save(); g.translate(x, y); g.scale(s, s); g.globalAlpha = Math.min(1, (1 - k) * 2.5);
    g.lineWidth = 16; g.strokeStyle = INK; g.strokeText("Z", 0, 0); g.fillStyle = "#ffffff"; g.fillText("Z", 0, 0); g.restore();
  }
  g.restore();
};
/** falling leaf */
export const fxLeaf = (p, col) => { p.poly([[300, 380], [420, 470], [300, 620], [180, 470]], col, 14); p.stroke([[300, 400], [300, 600]], 8); };
/** dust cloud puff (k 0..1 growth) */
export const fxDust = (p, k, col = "#e8dcc4") => {
  const g = p.g; g.save(); g.globalAlpha = Math.max(0, 1 - k * k);
  for (let i = 0; i < 7; i++) { const a = i / 7 * Math.PI * 2, r = 90 + 150 * k; p.ell(300 + Math.cos(a) * r, 520 + Math.sin(a) * r * 0.6, 120 + 60 * k, 100 + 50 * k, col, 12); }
  p.ell(300, 520, 170 + 110 * k, 140 + 80 * k, col, 0);
  g.restore();
};
export const fxDrip = (p) => p.ell(300, 500, 40, 64, "#9fd4ff", 10);
export const fxWood = (p, seed) => { p.poly([[200, 420], [400, 400], [420, 560], [230, 600]], "#5b3d22", 14); p.stroke([[240, 450], [380, 440]], 6, "#3a2614"); p.ell(330, 520, 26, 18, "#4d7a32", 0); };

export const headCenter = (seed = 3) => { const H = headBlob(seed, 118, 0), HH = 2 * H.b; return 975 - 1.38 * HH - 1.08 * HH - H.b; };


// ---------------- Colombian cast (our own designs) ----------------
Object.assign(OUTFITS, {
  costeno: { tunic: "#f6f1e4", pants: "#3a4060", skin: "#c48a5c", vueltiao: true, mochila: true, moustache: "#2a1c16" },
  guaA: { tunic: "#e8574a", pants: "#2f4d7a", skin: "#f0c39a", cap: "#2a6fb0", moustache: "#3a2618" },
  guaB: { tunic: "#f2c230", pants: "#4a3a2a", skin: SKIN, hair: "#3b2a20" },
  guaC: { tunic: "#3fae8f", pants: "#3a3a4a", skin: "#d9a07a", hair: "#1e1714", stout: true },
  guaD: { tunic: "#7b5ab8", skin: "#f5c9a0", dress: "#e98bb0", hair: "#5a3b2a" },
  pintA: { tunic: "#f2f0ea", splat: true, cap: "#d94a3a", pants: "#3d5a88", skin: "#e8b88f" },
  pintB: { tunic: "#9bd0e8", splat: true, cap: "#f2c230", pants: "#5a4a3a", skin: "#c99067", moustache: "#2a1c16" },
  pintC: { tunic: "#f2a65a", splat: true, hair: "#2b211c", pants: "#2f4d7a", skin: "#f0c39a" },
  penA: { tunic: "#d8cfc0", ruana: "#8a3b2f", pants: "#3a3a3a", skin: "#f0c39a", hair: "#3b2a20", moustache: "#3b2a20" },
  penB: { tunic: "#d8cfc0", ruana: "#3b5a7a", pants: "#4a3a2a", skin: "#d9a07a", hair: "#1e1714", stout: true },
  penC: { tunic: "#e6dccb", ruana: "#7a6a2a", dress: "#b84a5a", skin: SKIN, hair: "#2b211c" },
  penD: { tunic: "#d8cfc0", ruana: "#5a4a8a", pants: "#2a2a2a", skin: "#c48a5c", cap: "#3a3a3a" },
  penE: { tunic: "#d8cfc0", ruana: "#2f6a4a", pants: "#3a3a4a", skin: "#e8b88f", hair: "#5a3b2a", stout: true },
  turA: { tunic: "#ff8a5c", pants: "#2f4d7a", skin: "#f0c39a", cap: "#ffffff" },
  turB: { tunic: "#5cc0ff", skin: "#d9a07a", hair: "#1e1714", dress: "#f2c230" },
});

/** sombrero vueltiao: cream caña flecha with black rings and zig-zag bands */
const vueltiao = (p, H, cx, hc, u, ow, thick, light, tip) => {
  const g = p.g, BLK = "#2a2220", CRM = "#efe2bd", CRM2 = "#d9c697";
  const by = hc - 0.5 * H.b + tip * 20 * u, bx = 1.62 * H.a, bh = 0.27 * H.b;
  const ty = hc - 1.42 * H.b + tip * 20 * u, wb = 0.98 * H.a, wt = 0.8 * H.a;
  // brim
  const brim = ellPts(cx, by, bx, bh, 0, 360, 0, 72);
  p.shadedFill(brim, CRM, CRM2, light, bx, 0.3);
  p.clip(brim, () => {
    for (let k = 1; k <= 4; k++) p.stroke(ellPts(cx, by, bx * (0.62 + k * 0.09), bh * (0.62 + k * 0.09), 0, 360, 0, 72), (k % 2 ? 5 : 2.5) * u, BLK);
    for (let i = 0; i < 26; i++) { const a = i / 26 * Math.PI * 2, r1 = 0.7, r2 = 0.79; p.stroke([[cx + Math.cos(a) * bx * r1, by + Math.sin(a) * bh * r1], [cx + Math.cos(a + 0.12) * bx * r2, by + Math.sin(a + 0.12) * bh * r2]], 2 * u, BLK); }
  });
  p.inkRing(brim, ow * 0.85, thick);
  // crown
  const crown = [[cx - wb, by], ...ellPts(cx, ty + 0.12 * H.b, wt, 0.2 * H.b, 180, 360, 0, 30), [cx + wb, by]];
  p.shadedFill(crown, CRM, CRM2, light, wb, 0.35);
  p.clip(crown, () => {
    const n = 5;
    for (let i = 0; i < n; i++) {
      const y0 = ty + 0.05 * H.b + (by - ty) * i / n;
      if (i % 2 === 0) { p.poly([[cx - 2 * wb, y0], [cx + 2 * wb, y0], [cx + 2 * wb, y0 + (by - ty) / n * 0.55], [cx - 2 * wb, y0 + (by - ty) / n * 0.55]], BLK, 0);
        const zz = []; for (let k = -12; k <= 12; k++) zz.push([cx + k * 9 * u, y0 + (k % 2 ? 4 : 11) * u]); p.stroke(zz, 2.2 * u, CRM); }
    }
    p.stroke(ellPts(cx - 0.4 * wb, ty + 0.3 * H.b, 0.25 * wb, 0.2 * H.b, 200, 300, 0, 12), 4 * u, "#ffffff55");
  });
  p.inkRing(crown, ow * 0.85, thick);
  // front lip of the brim over the crown base
  const lip = ellPts(cx, by, bx * 0.66, bh * 0.66, 0, 180, 0, 30);
  p.poly([...lip], CRM, 0);
  p.stroke(ellPts(cx, by, bx * 0.66, bh * 0.66, 0, 180, 0, 30), 2.6 * u, BLK);
  p.stroke(ellPts(cx, by, bx * 0.75, bh * 0.75, 10, 170, 0, 30), 4 * u, BLK);
};

/** ruana: woollen poncho with stripes and fringe */
const ruanaOn = (p, O, tcx, T, chin, torsoBot, HH, u, ow, thick, light) => {
  const c = O.ruana, top = chin + 0.04 * HH, bot = torsoBot + 0.18 * HH;
  const pts = [[tcx - 0.45 * T.a, top], [tcx - 1.25 * T.a, top + 0.18 * HH], [tcx - 1.42 * T.a, bot], [tcx + 1.42 * T.a, bot], [tcx + 1.25 * T.a, top + 0.18 * HH], [tcx + 0.45 * T.a, top], [tcx, top + 0.3 * HH]];
  p.gradFill(pts, c, mul(c, SH_CLOTH), light);
  p.clip(pts, () => {
    for (const k of [0.18, 0.22, 0.8, 0.84]) p.band([[tcx - 2 * T.a, top + (bot - top) * k], [tcx + 2 * T.a, top + (bot - top) * k]], k < 0.5 ? "#f2e6c8" : mul(c, [0.55, 0.55, 0.6]), 4 * u, 0);
    for (let i = -6; i <= 6; i++) p.stroke([[tcx + i * 0.24 * T.a, top + 0.32 * HH], [tcx + i * 0.26 * T.a, bot]], 1 * u, mul(c, [0.8, 0.8, 0.85]));
  });
  p.inkRing(pts, ow, thick);
  for (let i = -14; i <= 14; i++) p.stroke([[tcx + i * 0.1 * T.a, bot], [tcx + i * 0.1 * T.a + 1 * u, bot + 10 * u]], 2.4 * u, mul(c, [0.7, 0.7, 0.75]));
};

/** mochila: strap across the chest, woven bag with a diamond pattern at the hip */
const mochilaOn = (p, tcx, T, chin, torsoBot, HH, u, ow) => {
  const s0 = [tcx + 0.7 * T.a, chin + 0.1 * HH], s1 = [tcx - 0.95 * T.a, torsoBot - 0.05 * HH];
  p.band([s0, s1], "#c23a2e", 7 * u, 1.6 * u, "round");
  for (let i = 0; i < 6; i++) { const t = (i + 0.5) / 6; p.dot(s0[0] + (s1[0] - s0[0]) * t, s0[1] + (s1[1] - s0[1]) * t, 1.8 * u, "#f2c230"); }
  const bx = tcx - 1.05 * T.a, by = torsoBot + 0.05 * HH, w = 30 * u, h = 36 * u;
  const bag = rrect(bx - w, by - h, bx + w, by + h, 10 * u);
  p.poly(bag, "#e8a33a", ow * 0.8);
  p.clip(bag, () => {
    const cols = ["#c23a2e", "#2a2220", "#2a7a6a"];
    for (let r = 0; r < 4; r++) { const y = by - h + (r + 0.5) * (2 * h / 4); const zz = []; for (let k = -6; k <= 6; k++) zz.push([bx + k * 6 * u, y + (k % 2 ? -5 : 5) * u]); p.stroke(zz, 3 * u, cols[r % 3]); }
  });
  p.poly(bag, null, ow * 0.8);
};

/** props held in a hand */
const holdItem = (p, item, hx, hy, side, u, opts) => {
  if (item === "tinto") {
    const w = 9 * u, h = 13 * u, x = hx, y = hy - 9 * u;
    p.poly([[x - w, y - h], [x + w, y - h], [x + w * 0.75, y + h * 0.4], [x - w * 0.75, y + h * 0.4]], "#ffffff", 2 * u);
    p.ell(x, y - h, w, 3 * u, "#5a2e14", 1.6 * u);
    p.dot(hx, hy, 5.5 * u);
    const ph = (opts.steam || 0);
    for (const dx of [-4, 4]) { const pts = []; for (let i = 0; i < 12; i++) pts.push([x + dx * u + Math.sin(i * 0.8 + ph + dx) * 3 * u, y - h - 4 * u - i * 2.6 * u]); const g = p.g; g.save(); g.globalAlpha = 0.7; p.stroke(pts, 2 * u, "#ffffff"); g.restore(); }
  } else if (item === "bucket") {
    const w0 = 15 * u, w1 = 12 * u, top = hy + 10 * u, bot = top + 30 * u;
    p.stroke(ellPts(hx, top, w0, 14 * u, 180, 360, 0, 16), 2.2 * u, "#5c5a57");
    p.poly([[hx - w0, top], [hx + w0, top], [hx + w1, bot], [hx - w1, bot]], "#c7cdd3", 2.6 * u);
    p.ell(hx, top, w0, 4 * u, "#ffffff", 2.2 * u);
    p.poly([[hx - w0 * 0.6, top + 1 * u], [hx - w0 * 0.3, top + 1 * u], [hx - w0 * 0.35, top + 14 * u], [hx - w0 * 0.55, top + 10 * u]], "#ffffff", 0);
    p.dot(hx, hy, 5.5 * u);
  } else if (item === "brush") {
    const ax = hx + side * 4 * u, ay = hy;
    p.band([[ax, ay + 8 * u], [ax + side * 10 * u, ay - 34 * u]], "#9a6a3a", 5 * u, 1.4 * u, "round");
    const bx = ax + side * 12 * u, by = ay - 44 * u;
    p.poly([[bx - 9 * u, by + 8 * u], [bx + 9 * u, by + 8 * u], [bx + 10 * u, by - 10 * u], [bx - 10 * u, by - 10 * u]], "#5c5a57", 2 * u);
    p.poly([[bx - 10 * u, by - 10 * u], [bx + 10 * u, by - 10 * u], [bx + 9 * u, by - 26 * u], [bx - 9 * u, by - 26 * u]], "#ffffff", 2 * u);
    p.dot(hx, hy, 5.5 * u);
  } else if (item === "rope") {
    p.stroke([[hx, hy], [hx - side * 4 * u, 0]], 3 * u, "#c9a66b");
    p.dot(hx, hy, 5.5 * u);
  }
};

/** dust/action cloud for the bololó */
export const fxBololo = (p, t) => {
  const g = p.g; g.save();
  for (let i = 0; i < 9; i++) { const a = i / 9 * 6.283 + t * 3, r = 150 + 30 * Math.sin(t * 20 + i); p.ell(300 + Math.cos(a) * r, 600 + Math.sin(a) * r * 0.55, 90, 70, "#efe3cc", 10); }
  p.ell(300, 600, 210, 150, "#efe3cc", 0);
  for (let i = 0; i < 4; i++) { const a = t * 9 + i * 1.6; p.stroke([[300 + Math.cos(a) * 120, 600 + Math.sin(a) * 60], [300 + Math.cos(a) * 230, 600 + Math.sin(a) * 120]], 14, INK); }
  g.font = "900 110px Arial Black, Arial"; g.lineJoin = "round"; g.lineWidth = 18; g.strokeStyle = INK; g.fillStyle = "#f2c230";
  const words = ["¡Ey!", "¡Bajen!", "¡Uy!"]; const w = words[Math.floor(t * 6) % 3];
  g.save(); g.translate(300, 380); g.rotate(Math.sin(t * 14) * 0.15); g.textAlign = "center"; g.strokeText(w, 0, 0); g.fillText(w, 0, 0); g.restore();
  g.restore();
};
/** anger squiggle */
export const fxAnger = (p) => { for (const [a, b] of [[0, 1], [1.57, 1], [3.14, 1], [4.71, 1]]) { const x = 300 + Math.cos(a + 0.78) * 60, y = 500 + Math.sin(a + 0.78) * 60; p.stroke([[x, y], [x + Math.cos(a + 0.78) * 50, y + Math.sin(a + 0.78) * 50]], 26, "#e8302c"); } };
