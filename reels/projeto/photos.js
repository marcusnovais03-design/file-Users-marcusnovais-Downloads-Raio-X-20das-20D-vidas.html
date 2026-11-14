// Real photos (Wikimedia Commons) with FPV push-in + overlays
const IMG = {}, IMGP = {};
const PHOTOS = [];
let CREDITS = {};
function loadImg(k) {
  IMGP[k] = new Promise(res => { const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.onerror = () => res(); im.src = 'img/' + k + '.jpg'; });
}
CREDITS = window.CREDITS_SHORT || {};

// cover-fit photo with fast push-in toward a focal point
function drawPhoto(e, t) {
  const im = IMG[e.k]; const p = (t - e.a) / (e.b - e.a);
  if (e.fit) { // blurred cover background + whole photo centred, pushing in
    const c = Math.max(W / im.width, H / im.height) * 1.1;
    ctx.filter = 'blur(28px) brightness(.45) ' + (e.filter || ''); ctx.drawImage(im, (W - im.width * c) / 2, (H - im.height * c) / 2, im.width * c, im.height * c); ctx.filter = 'none';
    const z = lerp(e.z0 ?? 1.0, e.z1 ?? 1.25, Math.pow(p, e.pow ?? 1.2)); const w = W * 1.02 * z, h = im.height * w / im.width;
    ctx.filter = e.filter || 'none'; ctx.drawImage(im, W / 2 - w * (e.fx ?? .5) * 2 * .5 - (w * ((e.fx ?? .5) - .5)), (e.cy ?? 640) - h / 2, w, h); ctx.filter = 'none';
    if (e.tint) { ctx.fillStyle = e.tint; ctx.fillRect(0, 0, W, H); }
    HY = 900; CAMH = 2.2; return;
  }
  const z = lerp(e.z0 ?? 1.08, e.z1 ?? 1.5, Math.pow(p, e.pow ?? 1.25));
  const cover = Math.max(W / im.width, H / im.height) * z;
  const fx = e.fx ?? .5, fy = e.fy ?? .5;
  const dw = im.width * cover, dh = im.height * cover;
  // focal point drifts to screen centre-ish as we push in
  const sx = lerp(W * .5, W * (e.sx ?? .5), 0) - fx * dw + (e.dx || 0) * p * W;
  const sy = H * (e.sy ?? .42) - fy * dh + (e.dy || 0) * p * H;
  const x = clamp(sx, W - dw, 0), y = clamp(sy, H - dh, 0);
  ctx.save();
  if (e.rot) { ctx.translate(W / 2, H / 2); ctx.rotate(e.rot * (p - .5)); ctx.translate(-W / 2, -H / 2); }
  if (e.filter) ctx.filter = e.filter;
  ctx.drawImage(im, x, y, dw, dh);
  ctx.filter = 'none';
  ctx.restore();
  if (e.tint) { ctx.fillStyle = e.tint; ctx.fillRect(0, 0, W, H); }
  HY = 900; CAMH = 2.2;
}

// ---------- overlays ----------
const OV = {
  dust: (c = [255, 225, 180], n = 160) => (t) => particles(301, n, t * 22, c, { size: .06, a: .55, speed: 1.4, yMin: 0, yMax: 12, add: true }),
  embers: (t) => { particles(302, 140, t * 14, [255, 150, 60], { size: .06, a: .9, speed: 1, yMin: 0, yMax: 18, vy: 1.2, wrapY: true, add: true, t }); },
  snow: (t) => particles(303, 300, t * 10, [235, 242, 255], { size: .05, a: .85, speed: .6, yMin: -1, yMax: 14, vy: -1.2, wrapY: true, drift: .5, t }),
  rain: (t) => {
    const r = rng(Math.floor(t * 30)); ctx.strokeStyle = 'rgba(200,215,235,.32)'; ctx.lineWidth = 1.6;
    for (let i = 0; i < 190; i++) { const x = r() * W, y = r() * H; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 7, y + 70); ctx.stroke(); }
  },
  arrows: (t) => {
    const r = rng(77); ctx.strokeStyle = 'rgba(15,12,10,.9)'; ctx.lineCap = 'round';
    for (let v = 0; v < 3; v++) {
      const ph = ((t - 15) * .55 + v * .33) % 1;
      for (let i = 0; i < 45; i++) {
        const ox = r() * 500 - 250, oy = r() * 160;
        const x = lerp(-200, W + 200, ph) + ox; const y = 420 + oy - Math.sin(ph * Math.PI) * 300;
        const ang = Math.atan2(-Math.cos(ph * Math.PI) * 300 * Math.PI, W + 400);
        ctx.lineWidth = 2.4; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - Math.cos(ang) * 36, y - Math.sin(ang) * 36); ctx.stroke();
      }
    }
  },
  blasts: (t) => {
    for (let i = 0; i < 3; i++) {
      const ph = ((t * .9 + i * .37) % 1.3) / 1.3; if (ph > .3) continue;
      const q = ph / .3; const x = 200 + hash(i * 7 + Math.floor(t * .9 + i * .37)) * 680, y = 600 + hash(i * 3) * 300;
      glow(x, y, 520 * (1 - q * .3), [255, 170, 90], (1 - q) * .8);
    }
  },
  planes: (t) => {
    for (let i = 0; i < 4; i++) {
      const ph = clamp(((t - 25) - i * .9) / 2.2); if (ph <= 0 || ph >= 1) continue;
      const x = lerp(-300, W + 300, ph) + i * 30, y = 420 - i * 60 - ph * 120, s = 24 + i * 9;
      ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = 'rgba(22,24,28,.95)'; DRAW.plane({ bank: -.12 }, t); ctx.restore();
    }
  },
  tunnel: (t, p) => { window.OVL = true; ctx.globalAlpha = .75; ctx.globalCompositeOperation = 'source-over'; S.find(s => s.a === 36).fn(t, p); ctx.globalAlpha = 1; window.OVL = false; },
  coins: (t, p) => {
    ctx.globalCompositeOperation = 'lighter';
    const rr = rng(462); const drain = clamp(p * 1.4);
    for (let i = 0; i < 380; i++) {
      const sx = rr() * W, sy = 300 + rr() * 1500, ph = (t * .6 + rr()) % 1;
      const x = lerp(sx, W / 2, eio(ph)), y = lerp(sy, 760, eio(ph)); const a = (1 - ph) * drain;
      ctx.strokeStyle = `rgba(255,${190 - ph * 60},90,${a * .8})`; ctx.lineWidth = 3 * (1 - ph) + .5;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(lerp(sx, W / 2, eio(Math.max(0, ph - .05))), lerp(sy, 760, eio(Math.max(0, ph - .05)))); ctx.stroke();
    }
    ctx.globalCompositeOperation = 'source-over';
    const vg = ctx.createRadialGradient(W / 2, 760, 0, W / 2, 760, 160); vg.addColorStop(0, 'rgba(0,0,0,.95)'); vg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  },
  alarm: (t) => { const al = Math.sin(t * 7) * .5 + .5; ctx.fillStyle = `rgba(255,20,30,${.08 + al * .14})`; ctx.fillRect(0, 0, W, H); },
  blackout: (t, p) => { // lights going out: progressive darkening in blocks
    const off = clamp((p - .45) / .5); const r = rng(909);
    ctx.fillStyle = 'rgba(0,0,0,.85)';
    for (let i = 0; i < 60; i++) { const th = r(); if (th > off) continue; const x = r() * W, y = r() * H * .8, w = 120 + r() * 300, h = 160 + r() * 500; ctx.fillRect(x - w / 2, y, w, h); }
    ctx.fillStyle = `rgba(0,0,0,${off * .45})`; ctx.fillRect(0, 0, W, H);
  },
  multi: (...fs) => (t, p) => fs.forEach(f => f(t, p)),
};

// ---------- schedule ----------
function P(a, b, k, cfg = {}) { PHOTOS.push({ a, b, k, ...cfg }); if (!cfg.vid) loadImg(k); }
// video clips: pre-extracted JPEG frames in vid/<k>/0001.jpg.. at 30 fps
async function prepare(t) {
  const e = PHOTOS.find(x => t >= x.a && t < x.b); if (!e || !e.vid) return;
  const n = Math.min(e.nf - 1, Math.floor((t - e.a) * 30 * (e.rate || 1)));
  const src = `vid/${e.k}/${String(n + 1).padStart(4, '0')}.jpg`;
  if (IMG[e.k] && IMG[e.k]._src === src) return;
  await new Promise(r => { const im = new Image(); im.onload = () => { im._src = src; IMG[e.k] = im; r(); }; im.onerror = r; im.src = src; });
}
window.prepare = prepare;
const SEPIA = 'sepia(.55) contrast(1.15) brightness(.9)';
P(0, 5, 's1', { fit: true, z0: 1.05, z1: 1.45, fx: .5, cy: 660, filter: 'contrast(1.1) brightness(.85)', ov: OV.dust() });
P(5, 7.5, 's2a', { fit: true, z0: 1.1, z1: 1.5, cy: 660, fx: .5, fy: .5, filter: SEPIA, ov: OV.dust([240, 205, 150], 220) });
P(7.5, 10, 's2b', { fit: true, z0: 1.1, z1: 1.5, cy: 660, fx: .5, fy: .55, filter: SEPIA, ov: OV.dust([240, 205, 150], 220) });
P(10, 12.5, 's3a', { z0: 1.05, z1: 1.45, fx: .5, fy: .5, filter: 'contrast(1.15) saturate(.8) brightness(.85)', ov: OV.embers });
P(12.5, 15, 's3b', { z0: 1.05, z1: 1.45, fx: .5, fy: .5, filter: 'contrast(1.15) saturate(.8) brightness(.85)', ov: OV.embers });
P(15, 17.5, 's4a', { z0: 1.05, z1: 1.5, fx: .5, fy: .5, filter: 'contrast(1.15) saturate(.7) brightness(.8)', ov: OV.multi(OV.arrows, OV.embers) });
P(17.5, 20, 's4b', { z0: 1.05, z1: 1.6, fx: .5, fy: .5, filter: 'contrast(1.15) saturate(.7) brightness(.8)', ov: OV.multi(OV.arrows, OV.embers) });
P(20, 25, 's5', { z0: 1.05, z1: 1.6, fx: .5, fy: .5, filter: 'grayscale(1) contrast(1.25) brightness(.85)', ov: OV.multi(OV.blasts, OV.dust([150, 140, 120], 140)) });
P(25, 30, 's6', { z0: 1.0, z1: 1.4, fx: .3, fy: .55, filter: 'grayscale(.6) contrast(1.2) brightness(.85)', ov: OV.multi(OV.planes, OV.dust([230, 235, 240], 120)) });
P(30, 35, 's7', { z0: 1.0, z1: 1.35, fx: .5, fy: .5, pow: 1, filter: 'saturate(.5) contrast(1.15) brightness(.75) hue-rotate(-10deg)', tint: 'rgba(20,40,90,.25)', ov: OV.snow });
P(36, 38, 's8a', { z0: 1.05, z1: 1.6, fx: .5, fy: .5, filter: 'saturate(.6) brightness(.6) contrast(1.2)', tint: 'rgba(0,30,80,.35)', ov: OV.tunnel });
P(38, 40, 's8b', { z0: 1.05, z1: 1.7, fx: .5, fy: .5, filter: 'saturate(.6) brightness(.6) contrast(1.2)', tint: 'rgba(0,30,80,.35)', ov: OV.tunnel });
P(40, 44, 'uk2', { z0: 1.05, z1: 1.45, fx: .5, fy: .5, filter: 'saturate(.7) contrast(1.1) brightness(.85)', tint: 'rgba(80,120,140,.12)' });
P(44, 46.5, 'btc', { z0: 1.05, z1: 1.5, fx: .5, fy: .5, filter: 'saturate(.8) contrast(1.15) brightness(.75)', ov: OV.multi(OV.alarm, OV.coins) });
P(46.5, 49, 'btc2', { z0: 1.05, z1: 1.5, fx: .5, fy: .5, filter: 'saturate(.8) contrast(1.15) brightness(.75)', ov: OV.multi(OV.alarm, OV.coins) });
P(49, 53, 'fr', { z0: 1.05, z1: 1.4, fx: .5, fy: .5, pow: 1, filter: 'saturate(.7) contrast(1.15) brightness(.65)', tint: 'rgba(10,20,50,.3)', ov: OV.multi(OV.rain, OV.alarm) });
P(53, 57, 'jp2', { z0: 1.05, z1: 1.45, fx: .5, fy: .5, filter: 'contrast(1.1) brightness(.8)', ov: OV.alarm });
P(57, 63, 'air', { z0: 1.05, z1: 1.45, fx: .5, fy: .5, pow: 1, filter: 'saturate(.8) contrast(1.1) brightness(.8)', tint: 'rgba(120,30,30,.18)' });
P(63, 65.5, 'br', { z0: 1.0, z1: 1.35, fx: .5, fy: .5, pow: 1, filter: 'contrast(1.1) brightness(1.05)', ov: OV.blackout });
