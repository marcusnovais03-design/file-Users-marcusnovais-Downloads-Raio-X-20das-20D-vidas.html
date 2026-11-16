// Gera os slides do carrossel: PNG (1080x1350) para os estáticos e MP4 para os animados.
// Uso: NODE_PATH=/opt/node-tools/node_modules node render.mjs
import { createRequire } from 'module';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const dir = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(dir, 'out');
fs.mkdirSync(out, { recursive: true });
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.join(dir, 'slides.html'));
await page.evaluate(() => document.fonts.ready);
const info = await page.evaluate(() => [...document.querySelectorAll('.slide')].map(s => +s.dataset.video || 0));

for (let i = 0; i < info.length; i++) {
  const n = String(i + 1).padStart(2, '0');
  await page.evaluate(i => { show(i); setT(99); }, i);
  const el = page.locator('.slide.on');
  await el.screenshot({ path: path.join(out, `slide-${n}.png`) });
  if (!info[i]) { console.log('png', n); continue; }
  const file = path.join(out, `slide-${n}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise(r => ff.on('close', r));
  for (let f = 0; f < info[i] * FPS; f++) {
    await page.evaluate(t => setT(t), f / FPS);
    ff.stdin.write(await el.screenshot({ type: 'png' }));
  }
  ff.stdin.end();
  await done;
  console.log('mp4', n);
}
await browser.close();
