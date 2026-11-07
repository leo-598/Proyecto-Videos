// Escenario: PLAZA DE ZÓCALOS (pueblo tipo Guatapé). Anillo de casas de colores abierto hacia +x,
// piso de tierra con fuente, y más casas detrás (hacia -x).
// Opciones: { centro: [x, 0, z], semilla: 12, casasAnillo: 15, casasAtras: 14, abiertaHacia: 0 (grados) }
// Por defecto: centro [-150, 0, 72] (el de la piedra).
import { casas } from './casas.js';
export const info = { nombre: 'plaza_zocalos', radio: 18 };

export function crear(ctx, o = {}) {
  const { THREE, P, world, M, add } = ctx;
  const { casa } = casas(ctx);
  const C = o.centro ?? [-150, 0, 72], giro = o.abiertaHacia ?? 0;
  const r = P.rng(o.semilla ?? 12); let i = 0;
  for (let k = 0; k < (o.casasAnillo ?? 15); k++) { const a = (20 + giro + k * 18) * Math.PI / 180, d = 15 + r() * 3;
    const x = C[0] + Math.cos(a) * d, z = C[2] + Math.sin(a) * d; casa(x, z, 5 + r() * 2, 5, 4.5 + r() * 2.5, -a - Math.PI / 2, i++); }
  for (let k = 0; k < (o.casasAtras ?? 14); k++) casa(C[0] - 30 - r() * 60, C[2] + (r() - 0.5) * 90, 5 + r() * 2, 5, 4 + r() * 3, r() * 6, i++);
  const pf = add(new THREE.CircleGeometry(13, 32), M.dirt, C[0], 0.03, C[2], world, { cast: false }); pf.rotation.x = -Math.PI / 2;
  add(new THREE.CylinderGeometry(1.6, 1.8, 0.8, 16), M.stone, C[0] - 6, 0.4, C[2] + 5, world);
  return {};
}
