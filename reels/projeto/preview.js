const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] }); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('console', m => console.log('console', m.text())); pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto('file://' + __dirname + '/index.html'); await pg.evaluate(() => window.ready);
  const out = process.argv[2]; require('fs').mkdirSync(out, { recursive: true });
  for (const t of process.argv.slice(3).map(Number)) {
    const d = await pg.evaluate(async t => { await prepare(t); render(t); return document.getElementById('c').toDataURL('image/jpeg', .85); }, t);
    require('fs').writeFileSync(`${out}/f_${String(t.toFixed(1)).padStart(5,'0')}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
  }
  await b.close();
})();
