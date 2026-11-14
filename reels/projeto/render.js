const { chromium } = require('playwright'); const { spawn } = require('child_process');
(async () => {
  const [a, b, out] = [+process.argv[2], +process.argv[3], process.argv[4]];
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const br = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] }); const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto('file://' + __dirname + '/index.html'); await pg.evaluate(() => window.ready);
  for (let f = a; f < b; f++) {
    const d = await pg.evaluate(async t => { await prepare(t); render(t); return document.getElementById('c').toDataURL('image/jpeg', .93); }, f / 30);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(out, f);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await br.close();
})();
