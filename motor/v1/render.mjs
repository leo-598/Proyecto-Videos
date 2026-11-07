// Render de cuadros del motor v1 (Windows, gráficos Intel por ANGLE/D3D11).
// Uso:  node motor/v1/render.mjs videos/<carpeta> [opciones]
//   --cuadros 0-59 | 0,200,500     qué cuadros (por defecto: todos, 0..TOTAL-1)
//   --previa                       540x960 y un cuadro de cada 3 -> out/previa/
//   --paso N                       un cuadro de cada N
//   --bloque 300                   cuadros por navegador (se reinicia entre bloques)
//   --calidad 0.96                 calidad JPEG
//   --modo shell|nuevo|visible     navegador: headless shell, headless nuevo o ventana visible (por defecto: shell, el más rápido en este equipo)
//   --rehacer                      no reanudar: vuelve a hacer los cuadros que ya existen
//   --salida <dir>                 carpeta de cuadros (por defecto <video>/out/frames o out/previa)
//   --web <dir>  --story <archivo> solo para pruebas (comparar con otro motor)
// Escribe el avance en out/render.log (previa: out/render_previa.log; con --salida: <salida>/render.log).
// La última línea dice: cuadros hechos, total y s/cuadro.
import { chromium } from 'playwright';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const video = path.resolve(args[0] || '.');
const opt = (k, d) => { const i = args.indexOf('--' + k); return i < 0 ? d : (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true); };
const previa = !!opt('previa', false);
const escala = previa ? 0.5 : +opt('escala', 1);
const paso = +opt('paso', previa ? 3 : 1);
const bloque = +opt('bloque', 300);
const calidad = +opt('calidad', 0.96);
const modo = opt('modo', 'shell');
const reanudar = !opt('rehacer', false);
const web = path.resolve(opt('web', path.join(AQUI, 'web')));
const story = path.resolve(opt('story', path.join(video, 'story.js')));
const biblio = path.resolve(AQUI, '..', 'biblioteca');
const salida = path.resolve(opt('salida', path.join(video, 'out', previa ? 'previa' : 'frames')));
// con --salida propia el registro va dentro de esa carpeta, para no ensuciar out/render.log del render final
const logf = opt('salida', null) ? path.join(salida, 'render.log') : path.join(path.dirname(salida), previa ? 'render_previa.log' : 'render.log');
fs.mkdirSync(salida, { recursive: true });
const log = (s) => { const l = `[${new Date().toISOString().slice(11, 19)}] ${s}`; console.log(l); fs.appendFileSync(logf, l + '\n'); };

// servidor: /story.js -> el del video, /biblioteca/* -> motor/biblioteca, el resto -> núcleo
const tipos = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = http.createServer((q, s) => {
  const u = decodeURIComponent(q.url.split('?')[0]);
  const p = u === '/story.js' ? story : u.startsWith('/biblioteca/') ? path.join(biblio, u.slice(12)) : path.join(web, u);
  if (!fs.existsSync(p) || fs.statSync(p).isDirectory()) { s.writeHead(404); return s.end(); }
  s.writeHead(200, { 'Content-Type': tipos[path.extname(p)] || 'application/octet-stream', 'Cache-Control': 'no-store' }); fs.createReadStream(p).pipe(s);
}).listen(0);
await new Promise((r) => srv.on('listening', r));
const url = `http://localhost:${srv.address().port}/index.html${escala !== 1 ? '?escala=' + escala : ''}`;

const lanzar = async () => {
  const gpu = ['--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-gpu-rasterization'];
  const o = modo === 'visible' ? { headless: false, args: [...gpu, '--window-position=0,0'] }
    : modo === 'shell' ? { headless: true, args: gpu } : { headless: true, channel: 'chromium', args: gpu };
  const b = await chromium.launch(o);
  const pg = await b.newPage({ viewport: { width: Math.round(1080 * escala), height: Math.round(1920 * escala) } });
  pg.on('pageerror', (e) => log('ERROR pagina: ' + e.message));
  pg.on('console', (m) => { const t = m.text(); if (/^ERR|error/i.test(t) && !/GL Driver Message/.test(t)) log('consola: ' + t); });
  await pg.goto(url);
  await pg.waitForFunction(() => window.ready || window.err, null, { timeout: 300000 });
  const err = await pg.evaluate(() => window.err);
  if (err) throw new Error('la página no cargó: ' + err);
  return { b, pg };
};

const nombre = (f) => path.join(salida, `f${String(f).padStart(4, '0')}.jpg`);
const hecho = (f) => { try { return fs.statSync(nombre(f)).size > 1000; } catch { return false; } };

// primer arranque: saber TOTAL y la tarjeta gráfica
let { b, pg } = await lanzar();
const TOTAL = await pg.evaluate(() => window.TOTAL);
const gpuName = await pg.evaluate(() => window.gpuInfo ? window.gpuInfo() : '(motor sin gpuInfo)');
let cuadros = [];
const spec = opt('cuadros', null);
if (spec && spec !== true) { for (const part of String(spec).split(',')) { if (part.includes('-')) { const [a, z] = part.split('-').map(Number); for (let f = a; f <= z; f += paso) cuadros.push(f); } else cuadros.push(+part); } }
else for (let f = 0; f < TOTAL; f += paso) cuadros.push(f);
const pendientes = reanudar ? cuadros.filter((f) => !hecho(f)) : cuadros;
log(`INICIO ${path.basename(video)} | ${previa ? 'PREVIA' : 'FINAL'} ${Math.round(1080 * escala)}x${Math.round(1920 * escala)} | modo ${modo} | GPU: ${gpuName}`);
log(`cuadros pedidos ${cuadros.length}, ya hechos ${cuadros.length - pendientes.length}, por hacer ${pendientes.length} | bloques de ${bloque}`);

const t0 = Date.now(); let hechos = 0, errores = 0, enBloque = 0, intentos = 0;
for (let i = 0; i < pendientes.length;) {
  const f = pendientes[i];
  try {
    if (enBloque >= bloque) { await b.close().catch(() => {}); ({ b, pg } = await lanzar()); enBloque = 0; log(`bloque nuevo (navegador reiniciado) en el cuadro ${f}`); }
    const d = await pg.evaluate(([f, q]) => { window.renderFrame(f); return document.getElementById('c').toDataURL('image/jpeg', q); }, [f, calidad]);
    fs.writeFileSync(nombre(f), Buffer.from(d.split(',')[1], 'base64'));
    hechos++; enBloque++; i++; intentos = 0;
    if (hechos % 30 === 0 || i === pendientes.length) log(`avance ${cuadros.length - pendientes.length + hechos}/${cuadros.length} | ${((Date.now() - t0) / hechos / 1000).toFixed(2)} s/cuadro`);
  } catch (e) {
    errores++; intentos++;
    log(`ERROR en el cuadro ${f}: ${String(e.message).split('\n')[0]} (intento ${intentos}/3)`);
    if (intentos >= 3) { log(`me rindo en el cuadro ${f}; vuelve a lanzar el render y seguirá desde aquí`); break; }
    await b.close().catch(() => {}); ({ b, pg } = await lanzar()); enBloque = 0;
  }
}
await b.close().catch(() => {}); srv.close();
const total = cuadros.length, listos = cuadros.filter(hecho).length;
log(`FIN | cuadros hechos ${listos}/${total} | ${hechos ? ((Date.now() - t0) / hechos / 1000).toFixed(2) : '0'} s/cuadro | errores ${errores}`);
process.exit(listos === total ? 0 : 1);
