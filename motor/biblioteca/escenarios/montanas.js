// Escenario: MONTAÑAS ANDINAS verdes a lo lejos (anillo de 18 montañas + 14 colinas medias).
// Opciones: { montanas: 18, colinas: 14, distancia: 560 }
export const info = { nombre: 'montanas' };

export function crear(ctx, o = {}) {
  const { THREE, P, world, M, add } = ctx;
  const nm = o.montanas ?? 18, nc = o.colinas ?? 14, D = o.distancia ?? 560;
  for (let i = 0; i < nm; i++) { const r = P.rng(100 + i); const a = i / nm * 6.283 + r() * 0.3, d = D + r() * 260, hh = 110 + r() * 150, r_ = 160 + r() * 90; const m = add(new THREE.SphereGeometry(1, 16, 10), i % 2 ? M.hill : M.hillFar, Math.cos(a) * d, -hh * 0.25, Math.sin(a) * d, world, { cast: false }); m.scale.set(r_, hh, r_ * 0.8); }
  for (let i = 0; i < nc; i++) { const r = P.rng(300 + i); const a = r() * 6.283, d = D * 300 / 560 + r() * 180; const h = add(new THREE.SphereGeometry(40 + r() * 40, 20, 10), i % 2 ? M.hill : M.hillFar, Math.cos(a) * d, -14, Math.sin(a) * d, world, { cast: false }); h.scale.y = 0.45 + r() * 0.25; }
  return {};
}
