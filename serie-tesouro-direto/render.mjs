// Gera os Reels da série a partir de reels.html + episodios.json.
// Uso:
//   NODE_PATH=/opt/node-tools/node_modules node render.mjs 3            -> out/ep03-sem-audio.mp4 (+ out/ep03-cenas.json)
//   OUTDIR=pasta NODE_PATH=... node render.mjs 3 2.5 10 20              -> prévias PNG do EP 3 nesses segundos
import { createRequire } from 'module';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const dir = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;

// episodios.json -> episodios.js (para a página carregar via file://)
fs.writeFileSync(path.join(dir, 'episodios.js'), 'window.EPISODIOS=' + fs.readFileSync(path.join(dir, 'episodios.json'), 'utf8') + ';');

const [epArg, ...stills] = process.argv.slice(2);
const ep = +epArg;
const tag = 'ep' + String(ep).padStart(2, '0');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.join(dir, 'reels.html') + '?ep=' + ep);
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => fitAll());
const stage = page.locator('#stage');
fs.mkdirSync(path.join(dir, 'out'), { recursive: true });

if (stills.length) {
  const outdir = process.env.OUTDIR || path.join(dir, 'out');
  fs.mkdirSync(outdir, { recursive: true });
  for (const t of stills.map(Number)) {
    await page.evaluate(t => setT(t), t);
    await stage.screenshot({ path: path.join(outdir, `${tag}-${t}.png`) });
  }
} else {
  const total = await page.evaluate(() => TOTAL);
  fs.writeFileSync(path.join(dir, 'out', `${tag}-cenas.json`), JSON.stringify(await page.evaluate(() => SCENES)));
  const file = path.join(dir, 'out', `${tag}-sem-audio.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-r', String(FPS), '-movflags', '+faststart', file],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise(r => ff.on('close', r));
  const n = Math.round(total * FPS);
  for (let f = 0; f < n; f++) {
    await page.evaluate(t => setT(t), f / FPS);
    const buf = await stage.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await done;
  console.log('ok', file, total + 's');
}
await browser.close();
