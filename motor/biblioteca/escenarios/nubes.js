// Escenario: NUBES pintadas (planos lejanos que siempre miran a la cámara; sin niebla ni tinta).
// Opciones: { n: 14, semilla: 90, distancia: 750, altura: 220 }
export const info = { nombre: 'nubes' };

export function crear(ctx, o = {}) {
  const { THREE, P, T, scene, billboards } = ctx;
  const r = P.rng(o.semilla ?? 90), D = o.distancia ?? 750, Y = o.altura ?? 220;
  for (let i = 0; i < (o.n ?? 14); i++) {
    const c = document.createElement('canvas'); c.width = 600; c.height = 400; const pen = new T.Pen(c.getContext('2d')); pen.ol = 0;
    pen.g.translate(300, 200); pen.g.scale(1.4, 1.2); pen.g.translate(-300, -200); T.fxCloud(pen, i + 1);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 0.667), new THREE.MeshBasicMaterial({ map: P.tex(c), transparent: true, fog: false, depthWrite: false }));
    const a = r() * Math.PI * 2, d = D + r() * 250; m.position.set(Math.cos(a) * d, Y + r() * 200, Math.sin(a) * d); m.scale.setScalar(200 + r() * 160);
    m.userData.ndSkip = true; m.renderOrder = -1; scene.add(m); billboards.push(m);
  }
  return {};
}
