// Renderiza o Reels (1080x1920, 30 fps): node render.js [saida.mp4]   |   node render.js --still 12.5 quadro.png
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'), fs = require('fs');
const FPS = 30;

(async () => {
  const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'dados.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(d => { window.setup(d); return document.fonts.ready; }, data);
  const total = await page.evaluate(() => window.TOTAL);

  if (process.argv[2] === '--still') {
    await page.evaluate(t => window.render(t), parseFloat(process.argv[3]));
    await page.screenshot({ path: process.argv[4] });
    return browser.close();
  }
  const out = process.argv[2] || path.join(__dirname, 'sp500-vs-cdi.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
    '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(total * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 97 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('ok', out, n, 'frames');
})();
