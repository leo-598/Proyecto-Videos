// Escenario: PUEBLO CON IGLESIA BLANCA (tipo El Peñol): iglesia con torre y casas de zócalo alrededor.
// Opciones: { centro: [x, 0, z], semilla: 19, casas: 16, rotIglesia: -0.6 }   Por defecto: centro [160, 0, 60].
import { casas } from './casas.js';
export const info = { nombre: 'pueblo_iglesia', radio: 40 };

export function crear(ctx, o = {}) {
  const { THREE, P, world, M, add, tbox } = ctx;
  const { casa } = casas(ctx);
  const C = o.centro ?? [160, 0, 60];
  const ch = new THREE.Group(); ch.position.set(C[0] + 12, 0, C[2] - 10); ch.rotation.y = o.rotIglesia ?? -0.6; world.add(ch);
  add(tbox(10, 9, 18, 3), M.plaster, 0, 4.5, 0, ch); add(tbox(4, 18, 4, 3), M.plaster, 0, 9, 10, ch);
  add(new THREE.ConeGeometry(3.2, 5, 4), M.roof, 0, 20.5, 10, ch).rotation.y = Math.PI / 4;
  const rr = add(new THREE.ConeGeometry(10.5, 3.5, 4), M.roof, 0, 10.7, 0, ch); rr.rotation.y = Math.PI / 4; rr.scale.set(0.68, 1, 1.25);
  const r = P.rng(o.semilla ?? 19); for (let k = 0; k < (o.casas ?? 16); k++) casa(C[0] + (r() - 0.3) * 60, C[2] + (r() - 0.5) * 70, 5 + r() * 2, 5, 4 + r() * 2, r() * 6, k + 3);
  return {};
}
