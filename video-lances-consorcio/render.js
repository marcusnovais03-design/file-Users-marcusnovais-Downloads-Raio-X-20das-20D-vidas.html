// Renderiza cena.html quadro a quadro. Uso: node render.js <timeline.json> <dir frames> [t1,t2,... para prévias]
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
(async () => {
  const [tlPath, out, stills] = process.argv.slice(2);
  const TL = JSON.parse(fs.readFileSync(tlPath)); fs.mkdirSync(out, { recursive: true });
  const FPS = 30, N = Math.round(TL.total * FPS), WORKERS = 4;
  const browser = await chromium.launch();
  const mk = async () => { const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    p.on('pageerror', e => { console.error('ERRO', e.message); process.exit(1); });
    await p.goto('file://' + path.resolve(__dirname, 'cena.html')); await p.evaluate(tl => window.setup(tl), TL); return p; };
  if (stills) {
    const p = await mk();
    for (const t of stills.split(',').map(Number)) { await p.evaluate(t => window.renderAt(t), t); await p.screenshot({ path: `${out}/still_${t.toFixed(2)}.jpg`, type: 'jpeg', quality: 80 }); }
  } else {
    let next = 0;
    await Promise.all([...Array(WORKERS)].map(async () => { const p = await mk();
      while (next < N) { const i = next++; await p.evaluate(t => window.renderAt(t), i / FPS);
        await p.screenshot({ path: `${out}/f_${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 96 });
        if (i % 300 === 0) console.log(i, '/', N); } }));
  }
  await browser.close();
})();
