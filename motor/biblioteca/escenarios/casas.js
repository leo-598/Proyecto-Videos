// Ayudante (no es un escenario): casa de pueblo antioqueño con zócalo pintado, balcones y techo de teja.
// Lo usan plaza_zocalos.js y pueblo_iglesia.js. Los materiales se crean una sola vez por render.
export function casas(ctx) {
  if (ctx._casas) return ctx._casas;
  const { THREE, P, world, M, toon, add, box, tbox } = ctx;
  const zocalo = (seed, wallHue, band) => {
    const c = document.createElement('canvas'); c.width = 256; c.height = 256; const g = c.getContext('2d'), r = P.rng(seed);
    g.fillStyle = `hsl(${wallHue},55%,82%)`; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 30; i++) { g.fillStyle = `hsla(${wallHue},40%,74%,0.4)`; g.beginPath(); g.ellipse(r() * 256, r() * 190, 10 + r() * 25, 6 + r() * 12, 0, 0, 7); g.fill(); }
    g.fillStyle = band; g.fillRect(0, 186, 256, 70); g.strokeStyle = '#2a2220'; g.lineWidth = 3; g.strokeRect(0, 186, 256, 70);
    for (let k = 0; k < 4; k++) { const x = 12 + k * 62; g.fillStyle = ['#f2c230', '#ffffff', '#e8574a', '#3fae8f'][(k + seed) % 4]; g.beginPath(); g.roundRect(x, 198, 46, 46, 8); g.fill(); g.stroke(); g.fillStyle = band; g.beginPath(); g.arc(x + 23, 221, 11, 0, 7); g.fill(); g.stroke(); }
    return c;
  };
  const WALL = [[10, '#2f8fd0'], [45, '#e8574a'], [190, '#f2c230'], [330, '#3fae8f'], [55, '#7b5ab8'], [160, '#e8574a'], [20, '#2a7a6a'], [280, '#f2a65a']];
  const zMats = WALL.map(([h, b], i) => toon({ map: P.tex(zocalo(i + 3, h, b), 1, 1) }));
  const balcCols = ['#2f8fd0', '#e8574a', '#3fae8f', '#f2c230', '#7b5ab8'].map((c) => toon({ color: c }));
  /** casa(x, z, ancho, fondo, alto, rotY, i, padre) — i elige colores de pared, zócalo y puertas */
  const casa = (x, z, w, d, h, rot, i, padre = world) => {
    const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rot; padre.add(g);
    add(new THREE.BoxGeometry(w, h, d), zMats[i % zMats.length], 0, h / 2, 0, g);
    const rf = add(new THREE.ConeGeometry(Math.hypot(w, d) / 2 + 0.7, 1.8, 4), M.roof, 0, h + 0.9, 0, g); rf.rotation.y = Math.PI / 4; rf.scale.set(w / Math.hypot(w, d) * 1.414, 1, d / Math.hypot(w, d) * 1.414);
    add(box(1.0, 2.1, 0.12), balcCols[(i + 1) % 5], 0, 1.05, d / 2 + 0.04, g, { cast: false });
    for (const s of [-1, 1]) { add(box(0.9, 1.0, 0.12), balcCols[(i + 2) % 5], s * w * 0.3, h * 0.66, d / 2 + 0.04, g, { cast: false }); }
    if (h > 5.5) add(tbox(w * 0.8, 0.15, 0.9, 1), M.wood, 0, h * 0.55, d / 2 + 0.45, g);
    return g;
  };
  return (ctx._casas = { casa, zMats, balcCols });
}
