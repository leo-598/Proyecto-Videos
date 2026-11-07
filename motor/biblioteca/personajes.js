// Personajes: tarjetas 2D dibujadas por el núcleo (T.romanFront). Aquí solo hay ayudantes y el reparto.
// Un personaje = una clave del reparto (texto) o un objeto de vestuario nuevo (ver VESTUARIO).
// Los personajes nuevos se definen como objetos aquí o en story.js: no hace falta tocar el núcleo.

/** Reparto colombiano incluido en el núcleo (claves para tarjeta()). */
export const REPARTO = {
  costeno: 'narrador costeño: sombrero vueltiao, mochila, bigote, camisa blanca',
  guaA: 'aldeano de Guatapé: camisa roja, gorra azul, bigote', guaB: 'aldeano: camisa amarilla',
  guaC: 'aldeano robusto: camisa verde', guaD: 'aldeana: vestido rosado',
  pintA: 'pintor: camisa blanca manchada, gorra roja', pintB: 'pintor: camisa celeste, gorra amarilla, bigote', pintC: 'pintora: camisa naranja',
  penA: 'peñolense con ruana roja, bigote', penB: 'peñolense robusto, ruana azul', penC: 'peñolense con ruana ocre y falda',
  penD: 'peñolense con ruana morada y gorra', penE: 'peñolense robusto, ruana verde',
  turA: 'turista: camiseta naranja, gorra blanca', turB: 'turista: camiseta celeste, falda amarilla',
};
/** Campos de un vestuario nuevo (todos opcionales salvo tunic):
 *  tunic, pants, dress, skin, hair, cap, moustache, beard, brows, ruana, apron, toga, cape,
 *  vueltiao (sombrero), mochila, splat (manchas de pintura), stout (robusto), helmet/armor/spear/shield (romano) */
export const VESTUARIO = ['tunic', 'pants', 'dress', 'skin', 'hair', 'cap', 'moustache', 'beard', 'brows', 'ruana', 'apron', 'toga', 'cape', 'vueltiao', 'mochila', 'splat', 'stout'];
export const EXPRESIONES = ['neutral', 'smile', 'grin', 'laugh', 'whistle', 'nervous', 'shock', 'relief', 'dazed', 'pained', 'lick', 'snore', 'stern', 'stubborn', 'squint'];
export const BRAZOS = ['hang', 'up', 'point', 'wave', 'thumb', 'hip', 'cross', 'belly', 'cheek', 'temple', 'lift', 'reach'];
export const OBJETOS = ['tinto', 'bucket', 'brush', 'rope'];

const q = (x, n = 2) => Math.round(x * 10 ** n) / 10 ** n;
/** parpadeo natural (0 abierto, 0.5 medio, 1 cerrado); cada semilla parpadea a su ritmo */
export const parpadeo = (f, seed) => { const per = 38 + (seed * 17) % 31, ph = (f + seed * 13) % per; return ph < 2 ? 0.5 : ph < 4 ? 1 : 0; };
/** rebote suave de respiración (en fracción de la altura de la cabeza) */
export const respira = (f, seed, a = 0.008) => q(Math.max(0, Math.sin((f + seed * 7) * 0.16)) * a, 3);
/** tarjeta(T, quien, opciones, [x, y, z], extra) -> actor para actorsAt.
 *  quien: clave del REPARTO o un objeto de vestuario.
 *  opciones: expr, L, R (brazos), holdL, holdR (objetos), look (-1..1), facing, headTilt°, tilt°, bob, blink, step (0..1 caminar), seed, steam
 *  extra: s (escala), flip, yaw, tint, alpha, ground (altura del piso para la sombra), blob:false, shadow:false, order */
export const tarjeta = (T, quien, o, pos, extra = {}) => ({ key: (typeof quien === 'string' ? quien : JSON.stringify(quien)) + JSON.stringify(o), draw: (p) => T.romanFront(p, quien, o), x: pos[0], y: pos[1], z: pos[2], ...extra });
/** efecto 2D (puff, chispas, enojo...) como actor sin sombra */
export const efecto = (key, draw, pos, s, extra = {}) => ({ key, draw, x: pos[0], y: pos[1], z: pos[2], s, blob: false, shadow: false, order: 5, ...extra });
