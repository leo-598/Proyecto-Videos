// PLANTILLA DE ESCENARIO — copia este archivo como biblioteca/escenarios/<nombre>.js y rellénalo.
// Reglas: no importes nada del núcleo; todo llega en `ctx`. Unidades en metros, y = arriba, piso en y = 0.
// Lo que ofrece ctx:
//   THREE, P (texturas pintadas: P.rng(semilla), P.tex(canvas), P.grass/stone/planks/plaster/roof/dirt...),
//   T (dibujo 2D: T.Pen, T.fx*), scene, world (grupo raíz), grupo('hoy'|'antes'|<nombre>),
//   billboards (planos que miran a la cámara), M (materiales: plank, beam, wood, stone, grass, dirt,
//   plaster, plaster2, roof, trunk, cypress, pine, bush, hill, hillFar, mount, snow, iron, bronze, door, window, red),
//   toon({color|map}), texM(canvas, rx, ry), add(geo, mat, x, y, z, padre, {cast}), box(w,h,d), tbox(w,h,d,texel),
//   waterNd (material especial para agua), DECK (altura del piso = 0).
// Tinta: todo mesh recibe contorno; pon m.userData.ndSkip = true para que no lo tenga (calcomanías, nubes).
export const info = {
  nombre: 'plantilla',
  descripcion: 'qué es y para qué historias sirve',
  luzSugerida: 'dia',                       // dia | hoy | atardecer (biblioteca/luces.js)
  // puntos de cámara sugeridos: { pos, look, fov } listos para copiar en story.js
  camaras: {
    general: { pos: [0, 12, 60], look: [0, 4, 0], fov: 40 },
    personaje: { pos: [0, 1.6, 6], look: [0, 1.4, 0], fov: 36 },
  },
  puntos: { personaje: [0, 0, 0] },         // dónde poner personajes (piso)
};

export function crear(ctx, o = {}) {
  const { THREE, P, world, grupo, M, toon, add, tbox } = ctx;
  // 1) TERRENO
  const piso = add(new THREE.PlaneGeometry(400, 400), M.grass, 0, 0, 0, world, { cast: false }); piso.rotation.x = -Math.PI / 2;
  // 2) OBJETOS (usa P.rng(semilla) para lo aleatorio: así cada render sale igual)
  const r = P.rng(o.semilla ?? 1);
  for (let i = 0; i < (o.rocas ?? 8); i++) add(new THREE.SphereGeometry(0.6 + r(), 8, 6), M.stone, (r() - 0.5) * 30, 0.3, (r() - 0.5) * 30, world);
  // 3) ÉPOCAS (opcional): lo que va en grupo('hoy') solo se ve si worldAt devuelve today: true
  // add(tbox(4, 3, 4, 2), M.plaster, 10, 1.5, 0, grupo('hoy'));
  return {
    // 4) por cuadro (opcional): W es lo que devuelve worldAt(f) en story.js
    estado(W, f, cam) {},
    // 5) cuando cambia la luz (opcional): L es la luz de la toma
    luz(L, f) {},
  };
}
