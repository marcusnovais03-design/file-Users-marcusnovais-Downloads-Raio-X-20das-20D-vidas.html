// Gera o Reels 1080x1920 a partir de reels.html.
// Uso:
//   NODE_PATH=/opt/node-tools/node_modules node render.mjs                -> out/reels-sem-audio.mp4
//   OUTDIR=pasta NODE_PATH=... node render.mjs 3.5 9 13.5                 -> prévias PNG nesses segundos
import { createRequire } from 'module';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const dir = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.join(dir, 'reels.html'));
await page.evaluate(() => document.fonts.ready);
const stage = page.locator('#stage');

const stills = process.argv.slice(2).map(Number);
if (stills.length) {
  const outdir = process.env.OUTDIR || path.join(dir, 'out');
  fs.mkdirSync(outdir, { recursive: true });
  for (const t of stills) {
    await page.evaluate(t => setT(t), t);
    await stage.screenshot({ path: path.join(outdir, `p${t}.png`) });
  }
} else {
  const total = await page.evaluate(() => TOTAL);
  const file = path.join(dir, 'out', 'reels-sem-audio.mp4');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-r', String(FPS), '-movflags', '+faststart', file],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise(r => ff.on('close', r));
  const n = Math.round(total * FPS);
  for (let f = 0; f < n; f++) {
    await page.evaluate(t => setT(t), f / FPS);
    const buf = await stage.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 300 === 0) console.log('frame', f, '/', n);
  }
  ff.stdin.end();
  await done;
  console.log('ok', file);
}
await browser.close();
