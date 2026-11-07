// Escenario: MUELLE de madera (tablones, pilotes y barandas). Mide 5 x 9 m; la cubierta queda a y = 0.5.
// Opciones: { x, z, rotY, epoca: 'hoy' | 'antes' | 'siempre' }   (por defecto el de la piedra: 20, 172, hoy)
export const info = { nombre: 'muelle', puntoNarrador: [0, 0.5, -2] };

export function crear(ctx, o = {}) {
  const { THREE, world, grupo, M, add, tbox } = ctx;
  const ep = o.epoca ?? 'hoy';
  const padre = ep === 'siempre' ? world : grupo(ep);
  const dock = new THREE.Group(); dock.position.set(o.x ?? 20, 0, o.z ?? 172); dock.rotation.y = o.rotY ?? 0; padre.add(dock);
  add(tbox(5, 0.3, 9, 1.2), M.plank, 0, 0.35, 0, dock); M.plank.map.rotation = Math.PI / 2;
  for (const x of [-2.2, 2.2]) for (const z of [-4, 0, 4]) add(new THREE.CylinderGeometry(0.16, 0.18, 2.2, 8), M.wood, x, -0.6, z, dock);
  for (const x of [-2.3, 2.3]) add(tbox(0.12, 0.9, 9, 1), M.beam, x, 0.95, 0, dock);
  return {};
}
