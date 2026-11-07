// Luces listas para usar (vienen de "La piedra que dice GI").
// Cada luz: sol (az°, el°, color, intensidad), cielo (skyTop -> skyHor), niebla, saturación, viñeta,
// colores del agua (waterDeep/waterShal/glint; los usa el escenario embalse) y shadowExt (tamaño de la sombra, m).
// Para variar una luz en una toma: lightFor = (S, f) => ({ ...LUCES[S.light], shadowExt: 40 })
export const LUCES = {
  dia: { az: 125, el: 48, sky: '#c4d6f2', ground: '#7a8a52', hemi: 1.15, sun: '#fff1dc', sunI: 2.5, fog: '#c8dcef', fogNear: 140, fogFar: 1300,
    skyTop: '#3a7fd6', skyHor: '#c3daf2', sat: 1.12, waterDeep: '#2c6c8c', waterShal: '#5aaec4', glint: '#effaff', vig: 0.2, shadowExt: 18 },
  hoy: { az: 125, el: 52, sky: '#c8daf4', ground: '#7a8a52', hemi: 1.2, sun: '#fff4e2', sunI: 2.55, fog: '#cfe2f2', fogNear: 160, fogFar: 1400,
    skyTop: '#3184dc', skyHor: '#cfe4f6', sat: 1.15, waterDeep: '#1f6a7e', waterShal: '#4fb0b8', glint: '#f2fdff', vig: 0.2, shadowExt: 18 },
  atardecer: { az: 20, el: 10, sky: '#9a90c8', ground: '#6a4c40', hemi: 1.0, sun: '#ffb46c', sunI: 2.9, fog: '#f0b88c', fogNear: 120, fogFar: 1100,
    skyTop: '#6f6eb0', skyHor: '#ffc27e', sunDisc: '#fff0c8', sunSize: 0.0035, sat: 1.12, gain: '#fff2e2', waterDeep: '#3d5a86', waterShal: '#d99a6e',
    glint: '#ffe2a8', vig: 0.28, shadowExt: 18 },
};
// alias en inglés (los usa el ejemplo de la piedra)
LUCES.day = LUCES.dia; LUCES.today = LUCES.hoy; LUCES.golden = LUCES.atardecer;
// tinte de tarjetas recomendado por luz (personajes un poco cálidos al atardecer)
export const tinteDe = (luz) => (luz === 'atardecer' || luz === 'golden') ? '#ffe2c8' : '#ffffff';
