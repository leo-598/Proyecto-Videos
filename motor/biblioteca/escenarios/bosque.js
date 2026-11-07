// Escenario: BOSQUE de pinos y árboles redondos en un anillo, más arbustos opcionales.
// Opciones (por defecto, las de la piedra):
//   n: 160, dmin: 100, dmax: 400, semilla: 44
//   soloAntesDesde: 126   los árboles más lejos que esto solo existen "antes" (hoy los tapa el embalse). null = siempre.
//   evitar: [[x, z, radio], ...]          círculos sin árboles (plazas, pueblos)
//   evitarCaja: [[x0, x1, z0, z1], ...]   rectángulos sin árboles (vista del narrador)
//   arbustos: { n: 30, dmin: 92, dmax: 122, huecoGrados: 40 } o null
export const info = { nombre: 'bosque' };

export function crear(ctx, o = {}) {
  const { THREE, P, world, grupo, M, add } = ctx;
  const n = o.n ?? 160, dmin = o.dmin ?? 100, dmax = o.dmax ?? 400, lejos = o.soloAntesDesde === undefined ? 126 : o.soloAntesDesde;
  const evitar = o.evitar ?? [[-150, 72, 24], [160, 60, 40]];
  const caja = o.evitarCaja ?? [[-10, 50, 120, 260]];
  const arb = o.arbustos === undefined ? { n: 30, dmin: 92, dmax: 122, huecoGrados: 40 } : o.arbustos;
  const pine = (x, z, h = 6, y = 0, par = world) => { const g = new THREE.Group(); g.position.set(x, y, z); par.add(g); add(new THREE.CylinderGeometry(0.25, 0.35, h, 6), M.trunk, 0, h / 2, 0, g); add(new THREE.ConeGeometry(2.4, h * 0.9, 8), M.cypress, 0, h * 0.85, 0, g); return g; };
  const round = (x, z, h = 6, y = 0, par = world) => { const g = new THREE.Group(); g.position.set(x, y, z); par.add(g); add(new THREE.CylinderGeometry(0.3, 0.4, h, 6), M.trunk, 0, h / 2, 0, g); const c = add(new THREE.SphereGeometry(2.8, 10, 8), M.pine, 0, h + 1, 0, g); c.scale.y = 0.85; return g; };
  const r = P.rng(o.semilla ?? 44);
  for (let i = 0; i < n; i++) {
    const a = r() * 6.283, d = dmin + r() * (dmax - dmin); const x = Math.cos(a) * d, z = Math.sin(a) * d;
    if (evitar.some(([cx, cz, rr]) => Math.hypot(x - cx, z - cz) < rr)) continue;
    if (caja.some(([x0, x1, z0, z1]) => x > x0 && x < x1 && z > z0 && z < z1)) continue;
    (i % 3 ? pine : round)(x, z, 6 + r() * 6, 0, lejos !== null && d >= lejos ? grupo('antes') : world);
  }
  if (arb) for (let i = 0; i < arb.n; i++) {
    const a = r() * 6.283, d = arb.dmin + r() * (arb.dmax - arb.dmin); const deg = ((a * 180 / Math.PI) + 360) % 360;
    if (deg < arb.huecoGrados || 360 - deg < arb.huecoGrados) continue;
    add(new THREE.SphereGeometry(1.2 + r() * 1.4, 10, 8), M.bush, Math.cos(a) * d, 0.5, Math.sin(a) * d, world).scale.y = 0.7;
  }
  return {};
}
