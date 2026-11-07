// Escenario: EMBALSE / VALLE con dos épocas.
//  - antes (W.today = false): todo el valle es pasto.
//  - hoy (W.today = true): agua animada + una isla de pasto + colinas verdes que salen del agua.
// Opciones (todas opcionales; por defecto, las de la piedra):
//   isla: { x, z, radio }   colinas: { n, semilla, dmin, dmax }   agua: { y }
// Colores del agua: los toma de la luz (waterDeep, waterShal, glint) si la luz los trae.
export const info = { nombre: 'embalse', epocas: true, luzSugerida: 'today' };

export function crear(ctx, o = {}) {
  const { THREE, P, scene, world, grupo, M, add, waterNd } = ctx;
  const isla = { x: 0, z: 0, radio: 128, ...(o.isla || {}) };
  const col = { n: 22, semilla: 71, dmin: 230, dmax: 650, ...(o.colinas || {}) };
  const waterU = { t: { value: 0 }, deep: { value: new THREE.Color('#2f6f8f') }, shal: { value: new THREE.Color('#5fa8bf') }, glint: { value: new THREE.Color('#e9f6ff') } };
  const waterMat = new THREE.ShaderMaterial({
    uniforms: { ...THREE.UniformsUtils.clone(THREE.UniformsLib.fog), ...waterU }, fog: true,
    vertexShader: `#include <fog_pars_vertex>
    varying vec3 vW; void main(){ vec4 w = modelMatrix*vec4(position,1.); vW = w.xyz; vec4 mvPosition = viewMatrix*w; gl_Position = projectionMatrix*mvPosition;
    #include <fog_vertex>
    }`,
    fragmentShader: `#include <fog_pars_fragment>
    uniform float t; uniform vec3 deep, shal, glint; varying vec3 vW;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
    float noise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); return mix(mix(hash(i),hash(i+vec2(1,0)),f.x), mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x), f.y); }
    void main(){ vec2 p = vW.xz*.05 + vec2(t*.05, t*.03);
      float n = noise(p) * .6 + noise(p*2.3 + 7.) * .4;
      vec3 c = mix(deep, shal, .3 + .45*n);
      float streak = smoothstep(.74, .8, noise(vW.xz*vec2(.12,.5) + vec2(t*.3, 0.)));
      c = mix(c, glint, streak*.6);
      gl_FragColor = vec4(c,1.);
      #include <fog_fragment>
    }`,
  });
  const water = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), waterMat); water.rotation.x = -Math.PI / 2; water.position.y = o.agua?.y ?? -0.3;
  water.userData.nd = waterNd; water.receiveShadow = false; scene.add(water);
  const grassBig = M.grass.clone(); grassBig.map = M.grass.map.clone(); grassBig.map.repeat.set(220, 220); grassBig.map.needsUpdate = true;
  const grassMid = M.grass.clone(); grassMid.map = M.grass.map.clone(); grassMid.map.repeat.set(40, 40); grassMid.map.needsUpdate = true;
  const groundPast = add(new THREE.PlaneGeometry(3000, 3000), grassBig, 0, 0, 0, world, { cast: false }); groundPast.rotation.x = -Math.PI / 2;
  const hoy = grupo('hoy');
  add(new THREE.CylinderGeometry(isla.radio, isla.radio + 6, 2, 64), grassMid, isla.x, -0.95, isla.z, hoy, { cast: false });
  const colinas = () => { const r = P.rng(col.semilla); for (let i = 0; i < col.n; i++) { const a = r() * 6.283, d = col.dmin + r() * (col.dmax - col.dmin), rr = 18 + r() * 45; const h = add(new THREE.SphereGeometry(rr, 18, 10), M.hill, Math.cos(a) * d, -rr * 0.55, Math.sin(a) * d, hoy, { cast: false }); h.scale.y = 0.55; } };
  colinas();
  return {
    luz(L) { if (L.waterDeep) waterU.deep.value.set(L.waterDeep); if (L.waterShal) waterU.shal.value.set(L.waterShal); if (L.glint) waterU.glint.value.set(L.glint); },
    estado(W, f) { groundPast.visible = !W.today; waterU.t.value = f / 30; },
  };
}
