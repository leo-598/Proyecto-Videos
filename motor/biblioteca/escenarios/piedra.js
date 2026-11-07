// Escenario: LA PIEDRA (monolito de granito tipo Peñol, ~182 m), centrada en (0, 0, 0).
//  - antes: arbustos en la cima.  hoy: torre-mirador en la cima.
//  - letras pintadas G + U (avance 0..1), guía de tiza "ATAPÉ" y hasta 4 cuerdas desde la cima.
// Estado por cuadro (lo devuelve worldAt de story.js):
//   W.g, W.u      avance de la G y del palito de la U (0..1)
//   W.guide       opacidad de la guía de tiza (0..1)
//   W.ropes       [[phi°, yAbajo, yArriba], ...] hasta 4 cuerdas
//   W.today       época (las letras se ven gastadas en 'hoy')
// Opciones: { letras: true, guia: 'ATAPÉ', cuerdas: 4 }
// Geometría exportada para cámaras y posiciones: surf(phi°, y, separación) da un punto sobre la cara.
export const RH = 182, R0 = 90;
export const Rof = (y) => R0 * Math.pow(Math.max(0, 1 - Math.pow(Math.max(0, y) / RH, 3)), 0.5) * (1 + 0.03 * Math.sin(y * 0.09));
export const surf = (phiDeg, y, out = 0) => { const p = phiDeg * Math.PI / 180, r = Rof(y) + out; return [r * Math.sin(p), y, r * Math.cos(p)]; };
export const MPD = 86 * Math.PI / 180; // metros por grado a la altura de las letras
export const G_C = [-9 * MPD, 95], U_X = 2.2;
export const gPts = (() => { const pts = []; for (let i = 0; i <= 120; i++) { const a = (40 + 290 * i / 120) * Math.PI / 180; pts.push([G_C[0] + Math.cos(a) * 7.5, G_C[1] + Math.sin(a) * 12.5]); } const e = pts[pts.length - 1]; pts.push([e[0], G_C[1] - 0.5], [G_C[0] + 1.8, G_C[1] - 0.5]); return pts; })();
export const uPts = [[U_X, 109.5], [U_X, 83]];
export const info = { nombre: 'piedra', epocas: true, alto: RH, luzSugerida: 'day' };

export function crear(ctx, o = {}) {
  const { THREE, P, world, grupo, M, toon, add, tbox, grad } = ctx;
  const rockGeo = (ph0, ph1, y0, y1, nu, nv, out = 0) => {
    const pos = [], uv = [], idx = [];
    for (let j = 0; j <= nv; j++) for (let i = 0; i <= nu; i++) {
      const u = i / nu, v = j / nv, ph = (ph0 + (ph1 - ph0) * u) * Math.PI / 180, y = y0 + (y1 - y0) * v, r = Rof(y) + out;
      pos.push(r * Math.sin(ph), y, r * Math.cos(ph)); uv.push(u, v);
    }
    for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) { const a = j * (nu + 1) + i, b = a + 1, c = a + nu + 1, d = c + 1; idx.push(a, b, d, a, d, c); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
  };
  // granito: gris con vetas de agua, líquenes y la grieta con la escalera en zigzag
  const rockCanvas = (() => {
    const c = document.createElement('canvas'); c.width = 4096; c.height = 2048; const g = c.getContext('2d'), r = P.rng(5);
    const grd = g.createLinearGradient(0, 0, 0, 2048); grd.addColorStop(0, '#b4aea4'); grd.addColorStop(0.6, '#a39d93'); grd.addColorStop(1, '#8e887d'); g.fillStyle = grd; g.fillRect(0, 0, 4096, 2048);
    for (let i = 0; i < 260; i++) { const x = r() * 4096, y = r() * 1800, w = 8 + r() * 40, h = 120 + r() * 700; const gg = g.createLinearGradient(0, y, 0, y + h); gg.addColorStop(0, 'rgba(70,64,58,0.0)'); gg.addColorStop(0.3, `rgba(70,64,58,${0.15 + r() * 0.25})`); gg.addColorStop(1, 'rgba(70,64,58,0)'); g.fillStyle = gg; g.beginPath(); g.ellipse(x, y + h / 2, w, h / 2, 0, 0, 7); g.fill(); }
    for (let i = 0; i < 900; i++) { g.fillStyle = `hsla(${70 + r() * 40},${20 + r() * 20}%,${40 + r() * 20}%,${0.25 + r() * 0.3})`; g.beginPath(); g.ellipse(r() * 4096, 1300 + r() * 748, 6 + r() * 30, 4 + r() * 16, r() * 3, 0, 7); g.fill(); }
    for (let i = 0; i < 2500; i++) { g.fillStyle = r() < 0.5 ? 'rgba(255,255,255,0.18)' : 'rgba(40,36,32,0.18)'; g.fillRect(r() * 4096, r() * 2048, 2 + r() * 3, 2 + r() * 3); }
    const ux = (ph) => (ph + 180) / 360 * 4096, vy = (y) => (1 - y / RH) * 2048;
    g.strokeStyle = '#3c3530'; g.lineWidth = 26; g.beginPath(); for (let y = 2; y < 176; y += 4) { const x = ux(48 + Math.sin(y * 0.07) * 1.5); y === 2 ? g.moveTo(x, vy(y)) : g.lineTo(x, vy(y)); } g.stroke();
    g.strokeStyle = '#f2efe8'; g.lineWidth = 9; g.beginPath(); for (let k = 0; k < 44; k++) { const y = 2 + k * 4, x = ux(48 + Math.sin(y * 0.07) * 1.5) + (k % 2 ? 34 : -34); k ? g.lineTo(x, vy(y)) : g.moveTo(x, vy(y)); } g.stroke();
    g.strokeStyle = '#2a2420'; g.lineWidth = 3; g.stroke();
    return c;
  })();
  const rockMat = toon({ map: P.tex(rockCanvas) });
  rockMat.map.wrapS = THREE.RepeatWrapping;
  add(rockGeo(-180, 180, 0, RH, 160, 70), rockMat, 0, 0, 0, world);
  // cima: arbustos (antes) / torre-mirador (hoy)
  const tufts = grupo('antes');
  { const r = P.rng(8); for (let i = 0; i < 18; i++) { const a = r() * 6.28, d = r() * 26; const y = RH * Math.pow(1 - Math.pow(d / R0, 2), 0.33) - 1; add(new THREE.SphereGeometry(1.6 + r() * 2, 8, 6), M.bush, Math.cos(a) * d, Math.min(RH, y + 1), Math.sin(a) * d, tufts); } }
  const tower = new THREE.Group(); tower.position.set(0, RH - 2, 0); grupo('hoy').add(tower);
  add(tbox(14, 6, 12, 3), M.plaster, 0, 3, 0, tower); add(tbox(10, 5, 9, 3), M.plaster2, 0, 8.5, 0, tower); add(tbox(6, 5, 6, 3), M.plaster, 0, 13.5, 0, tower);
  add(new THREE.ConeGeometry(5, 3, 4), M.roof, 0, 17.5, 0, tower).rotation.y = Math.PI / 4;

  // letras pintadas: parche de alta resolución sobre G + U
  let drawLetters = () => {}, guide = null;
  if (o.letras !== false) {
    const LET = { ph0: -17, ph1: 14, y0: 72, y1: 118 };
    const letC = document.createElement('canvas'); letC.width = 2048; letC.height = 2048; const letG = letC.getContext('2d');
    const letTex = P.tex(letC); letTex.wrapS = letTex.wrapT = THREE.ClampToEdgeWrapping;
    const letMat = new THREE.MeshToonMaterial({ gradientMap: grad, map: letTex, transparent: true, alphaTest: 0.08, polygonOffset: true, polygonOffsetFactor: -2, depthWrite: false });
    const letMesh = add(rockGeo(LET.ph0, LET.ph1, LET.y0, LET.y1, 40, 40, 0.12), letMat, 0, 0, 0, world, { cast: false }); letMesh.userData.ndSkip = true; letMesh.renderOrder = 1;
    const LX0 = LET.ph0 * MPD, LX1 = LET.ph1 * MPD;
    const lpx = (X, Y) => [(X - LX0) / (LX1 - LX0) * 2048, (1 - (Y - LET.y0) / (LET.y1 - LET.y0)) * 2048];
    const plen = (pts) => { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; };
    const partial = (pts, k) => { const L = plen(pts) * k, out = [pts[0]]; let acc = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); if (acc + d >= L) { const t = (L - acc) / d; out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t]); return out; } acc += d; out.push(pts[i]); } return out; };
    let letKey = '';
    drawLetters = (gk, uk, guideK, weather) => {
      const key = [gk.toFixed(3), uk.toFixed(3), guideK.toFixed(2), weather].join(); if (key === letKey) return; letKey = key;
      const g = letG; g.clearRect(0, 0, 2048, 2048); g.lineCap = 'round'; g.lineJoin = 'round';
      const pxm = 2048 / (LX1 - LX0);
      if (guideK > 0) {
        g.save(); g.globalAlpha = 0.55 * guideK; g.strokeStyle = '#fdf6e0'; g.lineWidth = 0.35 * pxm; g.setLineDash([1.2 * pxm, 0.9 * pxm]);
        for (const off of [-1.9, 1.9]) { g.beginPath(); gPts.forEach((p, i) => { const q = lpx(p[0] + off * Math.cos(Math.atan2(p[1] - G_C[1], p[0] - G_C[0])) * (i < 121 ? 1 : 0), p[1] + off * Math.sin(Math.atan2(p[1] - G_C[1], p[0] - G_C[0])) * (i < 121 ? 1 : 0)); i ? g.lineTo(...q) : g.moveTo(...q); }); g.stroke(); }
        g.beginPath(); const u0 = lpx(U_X - 1.9, 110), u1 = lpx(U_X - 1.9, 88); g.moveTo(...u0); g.lineTo(...u1);
        for (let i = 0; i <= 20; i++) { const a = Math.PI + Math.PI * i / 20; g.lineTo(...lpx(U_X + 7 + Math.cos(a) * 8.9, 88 + Math.sin(a) * 6)); } g.lineTo(...lpx(U_X + 15.9, 110)); g.stroke();
        g.restore();
      }
      const col = weather ? '#ece8de' : '#ffffff', w = 3.4 * pxm;
      const strokeP = (pts) => { if (pts.length < 2) return; g.beginPath(); pts.forEach((p, i) => { const q = lpx(...p); i ? g.lineTo(...q) : g.moveTo(...q); }); g.stroke(); };
      g.strokeStyle = 'rgba(40,34,30,0.35)'; g.lineWidth = w + 0.5 * pxm; strokeP(partial(gPts, gk)); if (uk > 0) strokeP(partial(uPts, uk));
      g.strokeStyle = col; g.lineWidth = w; if (gk > 0) strokeP(partial(gPts, gk)); if (uk > 0) strokeP(partial(uPts, uk));
      const r = P.rng(3); g.fillStyle = col;
      const drip = (pts, k) => { const pp = partial(pts, k); for (let i = 0; i < pp.length; i += 6) { if (r() < 0.45) { const [x, y] = lpx(...pp[i]); const l = (1 + r() * 2.5) * pxm * Math.min(1, k * 3); g.beginPath(); g.roundRect(x - 0.25 * pxm, y, 0.5 * pxm, l + w * 0.4, 0.25 * pxm); g.fill(); } } };
      if (gk > 0.05) drip(gPts, gk); if (uk > 0.05) drip(uPts, uk);
      if (weather) { g.globalCompositeOperation = 'destination-out'; for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(0,0,0,${0.2 + r() * 0.4})`; g.beginPath(); g.ellipse(r() * 2048, r() * 2048, 6 + r() * 20, 4 + r() * 12, 0, 0, 7); g.fill(); } g.globalCompositeOperation = 'source-over'; }
      letTex.needsUpdate = true;
    };
    // guía de tiza para el resto del nombre (baja resolución, solo antes)
    const guideC = document.createElement('canvas'); guideC.width = 2048; guideC.height = 512;
    { const g = guideC.getContext('2d'); g.strokeStyle = '#fdf6e0'; g.globalAlpha = 0.6; g.lineWidth = 8; g.setLineDash([22, 16]); g.font = '900 470px Arial Black, Arial'; g.textBaseline = 'middle'; g.textAlign = 'center';
      const txt = [...(o.guia ?? 'ATAPÉ')]; txt.forEach((ch, i) => g.strokeText(ch, (i + 0.5) / txt.length * 2048, 262)); }
    const guideTex = P.tex(guideC); guideTex.wrapS = guideTex.wrapT = THREE.ClampToEdgeWrapping;
    guide = add(rockGeo(14, 89, 79, 112, 40, 20, 0.1), new THREE.MeshBasicMaterial({ map: guideTex, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, fog: true }), 0, 0, 0, world, { cast: false });
    guide.userData.ndSkip = true; guide.renderOrder = 1;
  }
  // cuerdas desde la cima por la cara (tubos que siguen la superficie)
  const ropeMat = toon({ color: '#c9a66b' });
  const ropes = [];
  const makeRope = () => { const m = new THREE.Mesh(new THREE.BufferGeometry(), ropeMat); m.castShadow = true; world.add(m); ropes.push(m); return m; };
  const setRope = (m, ph, yLow, yTop = RH - 30) => {
    const r0 = Rof(yLow - 1.9) + 1.3, pts = [];
    for (let k = 0; k <= 24; k++) { const y = yLow + (yTop - yLow) * k / 24, t = Math.min(1, k / 4), e = t * t * (3 - 2 * t); pts.push(new THREE.Vector3(...surf(ph, y, (r0 - Rof(y)) * (1 - e) + 0.5 * e))); }
    m.geometry.dispose(); m.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, 0.06, 5, false);
  };
  for (let i = 0; i < (o.cuerdas ?? 4); i++) makeRope();

  return {
    estado(W) {
      drawLetters(W.g || 0, W.u || 0, W.guide || 0, !!W.today);
      if (guide) { guide.visible = (W.guide || 0) > 0.01; guide.material.opacity = W.guide || 0; }
      ropes.forEach((m, i) => { const R_ = (W.ropes || [])[i]; m.visible = !!R_; if (R_) { const k = R_.join(); if (m.userData.k !== k) { m.userData.k = k; setRope(m, R_[0], R_[1], R_[2]); } } });
    },
  };
}
