// ===== "A 3ª GUERRA NÃO FAZ BARULHO" — procedural FPV documentary reel =====
const W = 1080, H = 1920, FPS = 30, DUR = 80;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const tmp = document.createElement('canvas'); tmp.width = W; tmp.height = H;
const tctx = tmp.getContext('2d');

// ---------- utils ----------
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
const eo = t => 1 - Math.pow(1 - clamp(t), 3);
const mix = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
const rgb = (c, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// ---------- grain ----------
const grains = [];
for (let g = 0; g < 4; g++) {
  const c = document.createElement('canvas'); c.width = 360; c.height = 640;
  const x = c.getContext('2d'); const id = x.createImageData(360, 640); const r = rng(99 + g);
  for (let i = 0; i < id.data.length; i += 4) { const v = r() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  x.putImageData(id, 0, 0); grains.push(c);
}

// ---------- camera / projection ----------
const F = 820;           // focal length (px)
let HY = 900;            // horizon line
let CAMH = 2.2;          // camera height above ground (world units)
let SHAKE = [0, 0];
function proj(x, y, z) { // y: height above ground (up positive)
  return [W / 2 + x * F / z + SHAKE[0], HY + (CAMH - y) * F / z + SHAKE[1], F / z];
}

// ---------- sky / ground ----------
function sky(top, mid, hor, sunX, sunY, sunC, sunR, sunA) {
  const g = ctx.createLinearGradient(0, 0, 0, HY + 40);
  g.addColorStop(0, rgb(top)); g.addColorStop(.6, rgb(mid)); g.addColorStop(1, rgb(hor));
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, HY + 60);
  if (sunA > 0) {
    const r = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, sunR);
    r.addColorStop(0, rgb(sunC, sunA)); r.addColorStop(.12, rgb(sunC, sunA * .7)); r.addColorStop(1, rgb(sunC, 0));
    ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = r; ctx.fillRect(0, 0, W, H); ctx.globalCompositeOperation = 'source-over';
  }
}
function ground(near, far, camZ, stripeC, stripeA, spacing = 6) {
  const g = ctx.createLinearGradient(0, HY, 0, H);
  g.addColorStop(0, rgb(far)); g.addColorStop(1, rgb(near));
  ctx.fillStyle = g; ctx.fillRect(0, HY, W, H - HY);
  // rushing transverse stripes + texture streaks
  ctx.strokeStyle = rgb(stripeC, stripeA);
  for (let k = 0; k < 40; k++) {
    const z = k * spacing - (camZ % spacing) + 1.2;
    if (z < 1) continue;
    const y = HY + CAMH * F / z + SHAKE[1];
    if (y > H + 50) continue;
    ctx.globalAlpha = clamp(1 - z / 200) * .9;
    ctx.lineWidth = clamp(30 / z, .5, 10);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }
  ctx.globalAlpha = 1;
}
function groundStreaks(camZ, col, a, seed, n = 80, spread = 40) {
  const r = rng(seed);
  ctx.strokeStyle = rgb(col, a); ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const x = (r() - .5) * spread; const len = 1 + r() * 4; const per = 60;
    let z = ((r() * per - camZ) % per + per) % per + 1;
    const z2 = z + len;
    const [x1, y1, s1] = proj(x, 0, z); const [x2, y2] = proj(x, 0, z2);
    ctx.lineWidth = clamp(s1 * .08, .5, 14);
    ctx.globalAlpha = clamp(1 - z / per);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  }
  ctx.globalAlpha = 1;
}

// ---------- 3D particle streaks ----------
function particles(seed, n, camZ, col, opts = {}) {
  const r = rng(seed); const depth = opts.depth || 70; const spreadX = opts.sx || 40, yMin = opts.yMin ?? -1, yMax = opts.yMax ?? 18;
  const vy = opts.vy || 0, size = opts.size || .06, streak = opts.streak ?? .9, t = opts.t || 0, drift = opts.drift || 0;
  ctx.lineCap = 'round';
  if (opts.add) ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const x0 = (r() - .5) * spreadX + Math.sin(t * 1.3 + i) * drift; const y0 = lerp(yMin, yMax, r()); const zz = r() * depth; const ph = r();
    let z = ((zz - camZ) % depth + depth) % depth + .6;
    let y = y0 + vy * ((t + ph * 10) % 10);
    if (opts.wrapY) y = ((y - yMin) % (yMax - yMin) + (yMax - yMin)) % (yMax - yMin) + yMin;
    const [ax, ay, s] = proj(x0, y, z);
    const [bx, by] = proj(x0, y - vy * .04, z + streak * (opts.speed || 1));
    const a = clamp(1 - z / depth) * (opts.a || 1);
    ctx.strokeStyle = rgb(col, a); ctx.lineWidth = clamp(s * size, .6, opts.maxW || 9);
    ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
  }
  ctx.globalCompositeOperation = 'source-over';
}

// ---------- world objects ----------
// each object: {x, z, type, s(seed), h, vz}
function drawWorld(objs, camZ, t, fogC, objC, fogNear = 15, fogFar = 170) {
  const list = [];
  for (const o of objs) {
    const z = o.z + (o.vz || 0) * t - camZ;
    if (z < .8 || z > fogFar + 40) continue;
    list.push([z, o]);
  }
  list.sort((a, b) => b[0] - a[0]);
  for (const [z, o] of list) {
    const [sx, sy, s] = proj(o.x, o.y || 0, z);
    if (sx < -s * 80 || sx > W + s * 80) continue;
    const fog = clamp((z - fogNear) / (fogFar - fogNear));
    const col = mix(o.c || objC, fogC, fog * .92);
    const alpha = clamp((fogFar + 40 - z) / 40);
    ctx.save(); ctx.globalAlpha = alpha; ctx.translate(sx, sy); ctx.scale(s, s);
    ctx.fillStyle = rgb(col); ctx.strokeStyle = rgb(col);
    DRAW[o.type](o, t, col, z);
    ctx.restore();
  }
  ctx.globalAlpha = 1;
}
function poly(pts) { ctx.beginPath(); ctx.moveTo(pts[0], pts[1]); for (let i = 2; i < pts.length; i += 2) ctx.lineTo(pts[i], pts[i + 1]); ctx.closePath(); ctx.fill(); }
function circ(x, y, r) { ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); }
function glow(x, y, r, c, a) {
  if (!isFinite(x) || !isFinite(y) || !isFinite(r) || r <= 0) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, rgb(c, a)); g.addColorStop(.3, rgb(c, a * .45)); g.addColorStop(1, rgb(c, 0));
  const op = ctx.globalCompositeOperation; ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.globalCompositeOperation = op;
}
function smoke(x, y, t, seed, scale, col, a) {
  const r = rng(seed);
  for (let i = 0; i < 9; i++) {
    const ph = (t * .25 + r()) % 1; const yy = y - ph * 14 * scale; const xx = x + (r() - .5) * 2 * scale + ph * 5 * scale;
    ctx.globalAlpha = a * (1 - ph) * .55; ctx.fillStyle = rgb(col); circ(xx, yy, (1.2 + ph * 4) * scale);
  }
  ctx.globalAlpha = 1;
}

const DRAW = {
  hunter(o, t) {
    const sw = Math.sin(t * 9 + o.s * 6);
    ctx.lineCap = 'round'; ctx.lineWidth = .16;
    ctx.beginPath(); ctx.moveTo(0, -.95); ctx.lineTo(.35 * sw, 0); ctx.moveTo(0, -.95); ctx.lineTo(-.35 * sw, 0); ctx.stroke();
    ctx.lineWidth = .26; ctx.beginPath(); ctx.moveTo(0, -.95); ctx.lineTo(.12, -1.5); ctx.stroke();
    circ(.15, -1.68, .13);
    ctx.lineWidth = .06; ctx.beginPath(); ctx.moveTo(-.6, -.9); ctx.lineTo(1.3, -2.3); ctx.stroke();
    poly([1.3, -2.3, 1.18, -2.1, 1.38, -2.16]);
    ctx.lineWidth = .1; ctx.beginPath(); ctx.moveTo(.1, -1.4); ctx.lineTo(.5 + .2 * sw, -1.1); ctx.stroke();
  },
  acacia(o) {
    const h = o.h || 5; poly([-.15, 0, .15, 0, .1, -h * .7, -.1, -h * .7]);
    ctx.lineWidth = .15; ctx.beginPath(); ctx.moveTo(0, -h * .55); ctx.lineTo(-1.2, -h * .9); ctx.moveTo(0, -h * .6); ctx.lineTo(1.3, -h * .92); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0, -h * .95, 3.4, .55, 0, 0, Math.PI * 2); ctx.fill();
  },
  hill(o) { const w = o.w || 40, h = o.h || 8; ctx.beginPath(); ctx.moveTo(-w, 0); ctx.quadraticCurveTo(-w * .3, -h * 1.6, 0, -h); ctx.quadraticCurveTo(w * .4, -h * .5, w, 0); ctx.fill(); },
  fire(o, t) { const f = .8 + .2 * Math.sin(t * 17 + o.s * 9) + .1 * Math.sin(t * 31); glow(0, -.6, 3.2 * f, [255, 140, 40], .9); glow(0, -.4, 1.2 * f, [255, 220, 140], .9); },
  chariot(o, t) {
    const b = Math.sin(t * 14 + o.s * 5) * .05;
    ctx.save(); ctx.translate(0, b);
    // horses
    for (let k = 0; k < 2; k++) {
      const ox = 1.8 + k * .3, g = Math.sin(t * 14 + k * 2 + o.s);
      ctx.beginPath(); ctx.ellipse(ox, -1.3, .9, .35, 0, 0, Math.PI * 2); ctx.fill();
      poly([ox + .7, -1.4, ox + 1.25, -2.05, ox + 1.55, -1.95, ox + 1.0, -1.25]);
      ctx.lineWidth = .1; ctx.beginPath();
      ctx.moveTo(ox - .6, -1.1); ctx.lineTo(ox - .7 - .3 * g, 0); ctx.moveTo(ox - .4, -1.1); ctx.lineTo(ox - .3 + .3 * g, 0);
      ctx.moveTo(ox + .5, -1.1); ctx.lineTo(ox + .7 + .3 * g, 0); ctx.moveTo(ox + .65, -1.1); ctx.lineTo(ox + .45 - .3 * g, 0); ctx.stroke();
    }
    ctx.lineWidth = .06; ctx.beginPath(); ctx.moveTo(.5, -1.0); ctx.lineTo(1.5, -1.3); ctx.stroke();
    poly([-.6, -.6, .6, -.6, .6, -1.5, -.6, -1.2]);
    ctx.lineWidth = .08; ctx.beginPath(); ctx.arc(0, -.55, .55, 0, Math.PI * 2); ctx.stroke();
    for (let k = 0; k < 6; k++) { const a = k * Math.PI / 3 + t * 12; ctx.beginPath(); ctx.moveTo(0, -.55); ctx.lineTo(Math.cos(a) * .55, -.55 + Math.sin(a) * .55); ctx.stroke(); }
    ctx.lineWidth = .22; ctx.beginPath(); ctx.moveTo(-.1, -1.4); ctx.lineTo(-.05, -2.2); ctx.stroke(); circ(-.03, -2.38, .16);
    ctx.lineWidth = .05; ctx.beginPath(); ctx.moveTo(-.3, -1.6); ctx.lineTo(-.4, -3.3); ctx.stroke();
    ctx.restore();
  },
  soldier(o, t, col) {
    const b = Math.abs(Math.sin(t * 6 + o.s * 3)) * .05;
    ctx.save(); ctx.translate(0, -b);
    circ(0, -1.75, .17); poly([-.18, -1.9, .18, -1.9, 0, -2.15]);
    ctx.fillStyle = rgb(mix([150, 30, 25], col, .55)); ctx.fillRect(-.42, -1.55, .84, 1.15);
    ctx.fillStyle = rgb(mix([200, 160, 80], col, .6)); circ(0, -1.0, .1);
    ctx.fillStyle = rgb(col); ctx.lineWidth = .05; ctx.beginPath(); ctx.moveTo(.45, -.4); ctx.lineTo(.6, -2.6); ctx.stroke();
    ctx.fillRect(-.3, -.42, .2, .42); ctx.fillRect(.1, -.42, .2, .42);
    ctx.restore();
  },
  siege(o) {
    const h = o.h || 9; poly([-1.6, 0, 1.6, 0, 1.2, -h, -1.2, -h]);
    ctx.fillRect(-1.6, -h - .6, 3.2, .6);
    for (let k = 0; k < 5; k++) { ctx.globalAlpha *= 1; ctx.fillRect(-1.9, -k * h / 4.5 - 1, 3.8, .18); }
    circ(-1.3, -.2, .5); circ(1.3, -.2, .5);
  },
  catapult(o, t) {
    poly([-1.5, 0, 1.5, 0, 1.3, -.6, -1.3, -.6]);
    ctx.lineWidth = .2; ctx.beginPath(); ctx.moveTo(-.8, -.6); ctx.lineTo(0, -2.2); ctx.lineTo(.8, -.6); ctx.stroke();
    const a = -0.4 - .9 * clamp(Math.sin(t * 2 + o.s * 4)); ctx.lineWidth = .14; ctx.beginPath(); ctx.moveTo(0, -1.9); ctx.lineTo(Math.cos(a - 1.2) * 3, -1.9 + Math.sin(a - 1.2) * 3); ctx.stroke();
  },
  fortress(o, t, col) {
    const w = o.w || 30, h = o.h || 9;
    ctx.beginPath(); ctx.moveTo(-w * 1.4, 0); ctx.quadraticCurveTo(0, -h * 1.1, w * 1.4, 0); ctx.fill();
    const top = -h * .8;
    ctx.fillRect(-w * .5, top - h * .6, w, h * .6);
    for (let i = -5; i <= 5; i++) ctx.fillRect(i * w * .1 - .6, top - h * .6 - 1.2, 1.2, 1.2);
    for (const tx of [-.5, -.15, .2, .5]) ctx.fillRect(tx * w - 1.5, top - h * 1.1, 3, h * 1.1);
    glow(w * .1, top - h * .5, 16, [255, 110, 30], .75 + .15 * Math.sin(t * 9));
    glow(-w * .3, top - h * .4, 10, [255, 130, 40], .55 + .15 * Math.sin(t * 7));
    smoke(w * .1, top - h * .8, t, 5, 3.4, [40, 34, 30], .9);
    smoke(-w * .3, top - h * .6, t + 3, 7, 2.6, [45, 38, 34], .8);
  },
  castle(o, t, col) {
    const w = o.w || 70, h = o.h || 16, gate = o.gate ?? 1;
    // wall with gate opening at center
    const gw = 4, gh = 7;
    ctx.beginPath();
    ctx.moveTo(-w, 0); ctx.lineTo(-w, -h);
    for (let x = -w; x < w; x += 2.4) { ctx.lineTo(x, -h - 1.4); ctx.lineTo(x + 1.2, -h - 1.4); ctx.lineTo(x + 1.2, -h); ctx.lineTo(x + 2.4, -h); }
    ctx.lineTo(w, 0); ctx.lineTo(gw / 2, 0); ctx.lineTo(gw / 2, -gh); ctx.quadraticCurveTo(0, -gh - 2.4, -gw / 2, -gh); ctx.lineTo(-gw / 2, 0); ctx.closePath(); ctx.fill();
    for (const tx of [-w, -w * .45, -9, 9, w * .45, w]) {
      ctx.fillRect(tx - 3.2, -h - 9, 6.4, h + 9);
      for (let k = 0; k < 3; k++) ctx.fillRect(tx - 3.2 + k * 2.4, -h - 10.6, 1.4, 1.6);
      ctx.fillStyle = 'rgba(255,170,80,.55)'; ctx.fillRect(tx - .3, -h - 5, .6, 1.4); ctx.fillStyle = rgb(col);
    }
    // portcullis (rising)
    ctx.save(); ctx.beginPath(); ctx.rect(-gw / 2, -gh - 3, gw, gh + 3); ctx.clip();
    ctx.fillStyle = 'rgba(255,200,130,.35)'; ctx.fillRect(-gw / 2, -gh - 3, gw, gh + 3);
    ctx.strokeStyle = rgb(col); ctx.lineWidth = .25; const up = gate * gh;
    for (let x = -gw / 2 + .5; x < gw / 2; x += .8) { ctx.beginPath(); ctx.moveTo(x, -gh - 3); ctx.lineTo(x, -up + 0); ctx.stroke(); }
    for (let y = -gh; y < -up; y += .9) { ctx.beginPath(); ctx.moveTo(-gw / 2, y); ctx.lineTo(gw / 2, y); ctx.stroke(); }
    ctx.restore();
    glow(0, -3, 7, [255, 190, 110], .4);
  },
  post(o, t) {
    ctx.lineWidth = .14; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(.1, -1.3); ctx.stroke();
    ctx.lineWidth = .03; ctx.beginPath();
    for (let k = 0; k < 3; k++) { const y = -.35 - k * .4; ctx.moveTo(0, y); for (let x = .3; x <= 3; x += .3) ctx.lineTo(x, y + (Math.round(x / .3) % 2 ? -.12 : .12)); }
    ctx.stroke();
  },
  deadtree(o) {
    ctx.lineCap = 'round'; ctx.lineWidth = .35; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(.3, -6); ctx.stroke();
    ctx.lineWidth = .15; ctx.beginPath(); ctx.moveTo(.2, -3.4); ctx.lineTo(-1.6, -5.1); ctx.moveTo(.25, -4.6); ctx.lineTo(1.7, -6.3); ctx.moveTo(.3, -5.5); ctx.lineTo(-.6, -7); ctx.stroke();
  },
  mound(o) { ctx.beginPath(); ctx.ellipse(0, 0, o.w || 6, o.h || 1.2, 0, Math.PI, 0); ctx.fill(); },
  blast(o, t) {
    const p = ((t + o.s * 3) % 2.2) / 2.2; if (p > .55) return;
    const q = p / .55;
    glow(0, -2, 14 * (1 - q * .4), [255, 170, 80], (1 - q) * 1.1);
    const r = rng(o.s * 1000 | 0); ctx.fillStyle = 'rgba(30,24,20,.9)';
    for (let i = 0; i < 26; i++) { const a = -Math.PI * r(); const d = q * (6 + r() * 10); circ(Math.cos(a) * d * .6, -Math.abs(Math.sin(a) * d * 1.4) + q * q * 6, .25 + r() * .5); }
    ctx.globalAlpha *= .5 * (1 - q); smoke(0, -1, q * 3, o.s * 7, 3, [60, 52, 45], 1);
  },
  ship(o, t, col) {
    const L = 46, roll = Math.sin(t * 1.2 + o.s * 4) * .02;
    ctx.rotate(roll);
    poly([-L / 2, -1, L / 2 + 3, -3.2, L / 2 - 2, 1.2, -L / 2 + 2, 1.2]);
    poly([-14, -3, 14, -3, 12, -5.6, -12, -5.6]);
    poly([-5, -5.6, 5, -5.6, 3.5, -12, -3.5, -12]);
    ctx.fillRect(-1, -17, 2, 6); ctx.fillRect(-.15, -22, .3, 6);
    for (const tx of [-17, -11, 11, 17]) { poly([tx - 2, -3, tx + 2, -3, tx + 1.6, -4.4, tx - 1.6, -4.4]); ctx.fillRect(tx + (tx > 0 ? 1 : -4), -4.1, 3, .4); }
    poly([3, -12, 7, -12, 6.4, -17, 3.4, -17]);
    smoke(5, -17, t, o.s * 11 | 0, 3.2, [35, 36, 40], 1);
    const fp = (t * .7 + o.s) % 1; if (fp < .12) { glow(19, -4, 9, [255, 200, 120], (1 - fp / .12) * 1.2); }
  },
  plane(o, t, col) {
    ctx.rotate(o.bank || 0);
    poly([-4.5, 0, 4.5, -.3, 5.2, .1, 4.2, .5, -4.5, .5]);
    poly([-1, .1, 1.6, .1, .6, 5.5, -.6, 5.5]); poly([-1, .1, 1.6, .1, .6, -5.5, -.6, -5.5]);
    poly([-4.4, 0, -3.2, 0, -3.8, 1.8, -4.6, 1.8]); poly([-4.4, 0, -3.2, 0, -3.8, -1.8, -4.6, -1.8]);
    poly([-4.5, 0, -3.4, 0, -4.6, -1.8]);
  },
  silo(o, t) {
    const op = o.open ?? 0;
    ctx.fillStyle = 'rgba(20,24,32,1)'; ctx.beginPath(); ctx.ellipse(0, 0, 4, 1.2, 0, 0, Math.PI * 2); ctx.fill();
    glow(0, 0, 6, [255, 40, 30], .35 + .3 * Math.sin(t * 6));
    ctx.fillStyle = 'rgba(70,76,86,1)'; ctx.save(); ctx.translate(op * 5, 0); ctx.beginPath(); ctx.ellipse(0, 0, 4, 1.2, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  },
  radar(o, t) {
    ctx.fillRect(-.3, -6, .6, 6); poly([-2, 0, 2, 0, .3, -3, -.3, -3]);
    const a = Math.sin(t * .8 + o.s * 3) * 1;
    ctx.save(); ctx.translate(0, -7); ctx.scale(Math.cos(a), 1);
    ctx.beginPath(); ctx.ellipse(0, 0, 4.5, 3.2, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    glow(0, -10.5, 2.2, [255, 40, 40], (Math.sin(t * 5 + o.s * 9) > .3) ? .9 : .1);
  },
  pylon(o, t) { ctx.fillRect(-.15, -9, .3, 9); glow(0, -9.2, 2, [255, 50, 40], (Math.sin(t * 4 + o.s * 9) > 0) ? .9 : .15); },
  airliner(o, t, col) {
    const L = 36;
    ctx.beginPath(); ctx.moveTo(-L / 2, -3.6); ctx.lineTo(L / 2 - 3, -3.6); ctx.quadraticCurveTo(L / 2 + 1, -3.2, L / 2, -2); ctx.quadraticCurveTo(L / 2 - 1, -1, L / 2 - 4, -1); ctx.lineTo(-L / 2 + 3, -1.2); ctx.lineTo(-L / 2, -3.6); ctx.fill();
    poly([-L / 2 + 1, -3.6, -L / 2 + 5, -3.6, -L / 2 + 2.2, -10.5, -L / 2, -10.5]);
    poly([-2, -1.8, 4, -1.8, -4, .6, -7, .6]);
    ctx.fillRect(-1, -1.2, .25, 1.2); ctx.fillRect(L / 2 - 6, -1.2, .25, 1.2);
    ctx.fillStyle = 'rgba(255,225,170,.5)'; for (let x = -L / 2 + 6; x < L / 2 - 5; x += 1.1) ctx.fillRect(x, -3.1, .45, .45);
    glow(-L / 2 + 1, -10.4, 2, [255, 40, 40], (Math.sin(t * 3 + o.s * 9) > .6) ? 1 : 0);
  },
  ctower(o, t) {
    ctx.fillRect(-1.2, -26, 2.4, 26); poly([-4, -26, 4, -26, 3, -30, -3, -30]); ctx.fillRect(-3.4, -32, 6.8, 2);
    ctx.fillStyle = 'rgba(120,220,255,.35)'; ctx.fillRect(-3.2, -29.6, 6.4, 3);
    glow(0, -33, 3, [255, 40, 40], Math.sin(t * 2.5) > .2 ? 1 : .1);
  },
  terminal(o, t) {
    const w = o.w || 60; ctx.fillRect(-w / 2, -8, w, 8);
    poly([-w / 2, -8, w / 2, -8, w / 2 - 4, -10, -w / 2 + 4, -10]);
    for (let x = -w / 2 + 1; x < w / 2 - 1; x += 1.6) { const on = hash(x * 3 + o.s) > .2; ctx.fillStyle = on ? 'rgba(255,215,150,.55)' : 'rgba(0,0,0,.2)'; ctx.fillRect(x, -6.5, 1, 4); }
    ctx.fillStyle = `rgba(255,40,30,${.65 + .3 * Math.sin(t * 7)})`; ctx.fillRect(-6, -7.6, 12, 1.2);
  },
  building(o, t) {
    const w = o.w || 10, h = o.h || 30;
    ctx.fillRect(-w / 2, -h, w, h);
    if (o.ant) ctx.fillRect(-.2, -h - 8, .4, 8);
    const off = o.off || 0; // fraction of lights out
    for (let y = -h + 1.2; y < -1; y += 1.6) for (let x = -w / 2 + .7; x < w / 2 - .6; x += 1.3) {
      const hv = hash(x * 7.3 + y * 1.7 + o.s * 13);
      if (hv < .45) continue;
      const out = hv < .45 + off * .55;
      if (out) continue;
      ctx.fillStyle = o.neon && hv > .92 ? 'rgba(255,60,120,.9)' : `rgba(${o.wc || '255,214,150'},${.35 + hv * .5})`; ctx.fillRect(x, y, .7, .8);
    }
    if (o.sign) { ctx.fillStyle = o.sign; ctx.fillRect(-w / 2 + .5, -h * .35, w - 1, 1.4); }
  },
  person(o, t) {
    circ(0, -1.62, .14); poly([-.25, -1.45, .25, -1.45, .2, -.8, -.2, -.8]); ctx.fillRect(-.2, -.8, .16, .8); ctx.fillRect(.04, -.8, .16, .8);
    if (o.phone) glow(.15, -1.25, .7, [255, 50, 50], .8 + .2 * Math.sin(t * 12 + o.s * 5));
  },
  shelf(o, t) {
    const L = 8; ctx.fillRect(-.1, -2.4, .2, 2.4);
    const r = rng(o.s * 1000 | 0);
    for (let k = 0; k < 4; k++) {
      const y = -.25 - k * .6; ctx.fillRect(-.1, y, .2, .05);
      for (let i = 0; i < 6; i++) { if (r() < (o.empty || .5)) continue; ctx.fillStyle = `hsl(${r() * 360},40%,${30 + r() * 20}%)`; ctx.fillRect(-.12, y - .38, .24, .36); ctx.fillStyle = 'rgba(0,0,0,0)'; }
    }
  },
};

// ---------- text ----------
function tokens(str) { // *italic* segments
  const out = []; let it = false;
  for (const part of str.split('*')) { if (part) for (const w of part.split(/(\s+)/)) if (w) out.push({ w, it }); it = !it; }
  return out;
}
function richLines(str, size, maxW) {
  const toks = tokens(str); const lines = [[]]; let lw = 0;
  for (const tk of toks) {
    ctx.font = `${tk.it ? 'italic ' : ''}500 ${size}px PF`;
    const w = ctx.measureText(tk.w).width;
    if (/^\s+$/.test(tk.w)) { if (lw > 0) { lines[lines.length - 1].push({ ...tk, wd: w }); lw += w; } continue; }
    const prevWs = !lines[lines.length - 1].length || /^\s+$/.test(lines[lines.length - 1].at(-1).w);
    if (lw + w > maxW && lw > 0 && prevWs) { while (lines[lines.length - 1].length && /^\s+$/.test(lines[lines.length - 1].at(-1).w)) lines[lines.length - 1].pop(); lines.push([]); lw = 0; }
    lines[lines.length - 1].push({ ...tk, wd: w }); lw += w;
  }
  return lines;
}
function drawRich(str, x, yBottom, size, maxW, a, align = 'left', gold = [214, 176, 116]) {
  const lines = richLines(str, size, maxW); const lh = size * 1.12;
  let y = yBottom - (lines.length - 1) * lh;
  for (const ln of lines) {
    let tw = ln.reduce((s, k) => s + k.wd, 0); let cx = align === 'center' ? x - tw / 2 : x;
    for (const tk of ln) {
      ctx.font = `${tk.it ? 'italic ' : ''}500 ${size}px PF`;
      ctx.fillStyle = tk.it ? rgb(gold, a) : `rgba(246,240,230,${a})`;
      ctx.fillText(tk.w, cx, y); cx += tk.wd;
    }
    y += lh;
  }
  return yBottom - (lines.length - 1) * lh - size; // top
}
function wrapPlain(str, font, maxW) {
  ctx.font = font; const words = str.split(' '); const lines = []; let cur = '';
  for (const w of words) { const t = cur ? cur + ' ' + w : w; if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
  if (cur) lines.push(cur); return lines;
}
function textBlock(b, t) {
  const p = (t - b.a) / (b.b - b.a); if (p < 0 || p > 1) return;
  const din = .55, dout = .4, dur = b.b - b.a;
  const ai = clamp((t - b.a) / din), ao = clamp((b.b - t) / dout); const a = Math.min(eo(ai), ao);
  const rise = (1 - eo(ai)) * 30;
  const X = 84, MAXW = b.maxW || 840, size = b.size || 92;
  ctx.save(); ctx.translate(0, rise);
  ctx.textBaseline = 'alphabetic';
  // legibility gradient
  const g = ctx.createLinearGradient(0, 900, 0, 1700); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(.45, `rgba(0,0,0,${.55 * a})`); g.addColorStop(1, `rgba(0,0,0,${.7 * a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 900, W, 1020 - rise);
  let bottom = b.y || 1430;
  let capH = 0, capLines = [];
  if (b.cap) { capLines = wrapPlain(b.cap, '400 40px IN', MAXW); capH = capLines.length * 52 + 34; }
  const titleBottom = bottom - capH;
  let top = b.title ? drawRich(b.title, b.align === 'center' ? W / 2 : X, titleBottom, size, MAXW, a, b.align) : titleBottom;
  if (b.cap) {
    ctx.font = '400 40px IN'; ctx.fillStyle = `rgba(235,230,222,${a * .92})`;
    const ca = clamp((t - b.a - .5) / .5) * a; ctx.fillStyle = `rgba(235,230,222,${ca * .92})`;
    capLines.forEach((l, i) => ctx.fillText(l, X, titleBottom + 70 + i * 52));
  }
  if (b.stamp) {
    const n = Math.floor(clamp((t - b.a) / .9) * b.stamp.length);
    ctx.font = '500 32px MO'; ctx.fillStyle = `rgba(214,176,116,${a})`;
    const s = b.stamp.slice(0, n) + ((Math.floor(t * 3) % 2 && n < b.stamp.length) ? '▌' : '');
    const sy = top - 34;
    ctx.fillRect(X, sy - 50, 70, 3);
    if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '4px';
    ctx.fillText(s, X, sy);
    if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '0px';
  }
  ctx.restore();
}

// ---------- post fx ----------
function vignette(a = .75) {
  const g = ctx.createRadialGradient(W / 2, H * .5, H * .25, W / 2, H * .5, H * .78);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function speedLines(a, t, col = [255, 245, 230]) {
  if (a <= 0) return; const r = rng(Math.floor(t * 30) + 7);
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 40; i++) {
    const ang = r() * Math.PI * 2; const r0 = 380 + r() * 500, r1 = r0 + 200 + r() * 600;
    ctx.strokeStyle = rgb(col, a * r() * .35); ctx.lineWidth = 1 + r() * 3;
    ctx.beginPath(); ctx.moveTo(W / 2 + Math.cos(ang) * r0, HY + Math.sin(ang) * r0); ctx.lineTo(W / 2 + Math.cos(ang) * r1, HY + Math.sin(ang) * r1); ctx.stroke();
  }
  ctx.globalCompositeOperation = 'source-over';
}
function zoomBlur(strength) { // cheap radial blur via scaled self-blends
  if (strength <= 0) return;
  tctx.clearRect(0, 0, W, H); tctx.drawImage(cv, 0, 0);
  for (let i = 1; i <= 3; i++) {
    const s = 1 + strength * .035 * i; ctx.globalAlpha = .28;
    ctx.drawImage(tmp, W / 2 - W * s / 2, HY - HY * s, W * s, H * s);
  }
  ctx.globalAlpha = 1;
}
function glitch(amt, t) {
  if (amt <= 0) return;
  const r = rng(Math.floor(t * 24) * 31 + 3);
  tctx.clearRect(0, 0, W, H); tctx.drawImage(cv, 0, 0);
  const n = Math.floor(3 + amt * 14);
  for (let i = 0; i < n; i++) {
    const y = r() * H, h = 8 + r() * 120 * amt, dx = (r() - .5) * 160 * amt;
    ctx.drawImage(tmp, 0, y, W, h, dx, y, W, h);
  }
  ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = .22 * amt;
  ctx.drawImage(tmp, 10 * amt, 0); ctx.globalAlpha = .18 * amt; ctx.drawImage(tmp, -10 * amt, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = `rgba(255,30,40,${.12 * amt})`; ctx.fillRect(0, r() * H, W, 4 + r() * 20);
}
function grade(c, a) { ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = rgb(c, a); ctx.fillRect(0, 0, W, H); ctx.globalCompositeOperation = 'source-over'; }
function grain(t, a = .07) {
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = a;
  const g = grains[Math.floor(t * 24) % 4]; const ox = hash(Math.floor(t * 24)) * 40;
  ctx.drawImage(g, -ox, -ox, W + 80, H + 80); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
}
function flash(a, c = [255, 240, 220]) { if (a <= 0) return; ctx.fillStyle = rgb(c, clamp(a)); ctx.fillRect(0, 0, W, H); }
function fadeBlack(a) { if (a <= 0) return; ctx.fillStyle = `rgba(0,0,0,${clamp(a)})`; ctx.fillRect(0, 0, W, H); }

// ---------- scene builders ----------
function scatter(seed, n, f) { const r = rng(seed); const out = []; for (let i = 0; i < n; i++) { const o = f(r, i); if (o) out.push(o); } return out; }
function sideX(r, min, max) { return (r() < .5 ? -1 : 1) * lerp(min, max, r()); }

const OBJ = {};
OBJ.s1 = [
  ...scatter(11, 110, (r) => ({ type: 'hunter', x: sideX(r, 1.6, 14), z: 6 + r() * 150, vz: 12 + r() * 6, s: r() })),
  ...scatter(12, 16, (r) => ({ type: 'acacia', x: sideX(r, 8, 40), z: 10 + r() * 190, h: 4 + r() * 3, s: r() })),
  ...scatter(13, 7, (r) => ({ type: 'fire', x: sideX(r, 4, 20), z: 40 + r() * 130, s: r() })),
  { type: 'hill', x: -70, z: 230, w: 90, h: 16 }, { type: 'hill', x: 80, z: 240, w: 110, h: 22 },
];
OBJ.s2 = [
  ...scatter(21, 40, (r) => ({ type: 'chariot', x: sideX(r, 2.4, 16), z: 4 + r() * 120, vz: 20 + r() * 4, s: r() })),
  ...scatter(22, 30, (r) => ({ type: 'hunter', x: sideX(r, 6, 26), z: 20 + r() * 160, vz: 8, s: r() })),
  { type: 'hill', x: -40, z: 220, w: 140, h: 10 }, { type: 'hill', x: 90, z: 230, w: 120, h: 14 },
];
OBJ.s3 = [
  ...scatter(31, 480, (r, i) => { const row = Math.floor(i / 12), col = i % 12; const side = col < 6 ? -1 : 1; const cc = col % 6; return { type: 'soldier', x: side * (2.2 + cc * 1.05), z: 5 + row * 2.3 + r() * .2, vz: 3, s: r() }; }),
  ...scatter(32, 6, (r) => ({ type: 'siege', x: sideX(r, 16, 30), z: 30 + r() * 120, h: 8 + r() * 4, vz: 2 })),
  ...scatter(33, 6, (r) => ({ type: 'catapult', x: sideX(r, 10, 26), z: 20 + r() * 100, s: r() })),
  { type: 'fortress', x: 8, z: 190, w: 34, h: 12 },
];
OBJ.s4 = [
  { type: 'castle', x: 0, z: 125, w: 80, h: 18 },
  ...scatter(41, 70, (r) => ({ type: 'soldier', x: sideX(r, 3, 30), z: 8 + r() * 100, vz: 6, s: r() })),
  ...scatter(42, 6, (r) => ({ type: 'fire', x: sideX(r, 6, 30), z: 30 + r() * 80, s: r() })),
];
OBJ.s5 = [
  ...scatter(51, 60, (r, i) => ({ type: 'post', x: (i % 2 ? -1 : 1) * (3 + r() * 14), z: 3 + Math.floor(i / 2) * 5 + r() * 2 })),
  ...scatter(52, 14, (r) => ({ type: 'deadtree', x: sideX(r, 6, 34), z: 15 + r() * 160 })),
  ...scatter(53, 40, (r) => ({ type: 'mound', x: sideX(r, 2, 40), z: 5 + r() * 170, w: 3 + r() * 6, h: .6 + r() * 1.2 })),
  ...scatter(54, 12, (r) => ({ type: 'blast', x: sideX(r, 6, 40), z: 30 + r() * 120, s: r() })),
];
OBJ.s6 = [
  ...scatter(61, 7, (r) => ({ type: 'ship', x: sideX(r, 30, 90), z: 50 + r() * 150, vz: 4, s: r() })),
];
OBJ.s7 = [
  { type: 'silo', x: 0, z: 70 }, { type: 'silo', x: -26, z: 120 }, { type: 'silo', x: 30, z: 150 },
  ...scatter(71, 5, (r) => ({ type: 'radar', x: sideX(r, 18, 50), z: 40 + r() * 130, s: r() })),
  ...scatter(72, 18, (r) => ({ type: 'pylon', x: sideX(r, 8, 40), z: 10 + r() * 160, s: r() })),
];
OBJ.air = [
  ...scatter(81, 14, (r, i) => ({ type: 'airliner', x: (i % 2 ? -1 : 1) * (22 + r() * 30), z: 40 + i * 14 + r() * 6, s: r() })),
  { type: 'ctower', x: -60, z: 170, s: 1 }, { type: 'terminal', x: 50, z: 210, w: 120, s: 2 }, { type: 'terminal', x: -80, z: 240, w: 100, s: 3 },
];
OBJ.paris = [
  ...scatter(91, 26, (r, i) => ({ type: 'building', x: (i % 2 ? -1 : 1) * (9 + r() * 2), z: 6 + Math.floor(i / 2) * 9, w: 8, h: 16 + r() * 4, s: r(), off: r() * .5, sign: (i === 5) ? 'rgba(255,60,50,.9)' : null })),
  ...scatter(92, 24, (r) => ({ type: 'person', x: sideX(r, 2.5, 5), z: 4 + r() * 90, s: r(), phone: true })),
];
OBJ.tokyo = [
  ...scatter(93, 40, (r, i) => ({ type: 'building', x: (i % 2 ? -1 : 1) * (10 + r() * 30), z: 10 + Math.floor(i / 2) * 9, w: 8 + r() * 8, h: 25 + r() * 50, s: r(), neon: true, wc: '170,210,255' })),
];
OBJ.sp = [
  ...scatter(94, 40, (r, i) => ({ type: 'building', x: (i % 2 ? -1 : 1) * (10 + r() * 22), z: 10 + Math.floor(i / 2) * 8, w: 9 + r() * 7, h: 30 + r() * 45, s: r(), ant: r() < .3 })),
];
OBJ.shelf = [
  ...scatter(95, 40, (r, i) => ({ type: 'shelf', x: (i % 2 ? -1.8 : 1.8), z: 2 + Math.floor(i / 2) * 1.2, s: r(), empty: .55 + r() * .4 })),
  ...scatter(96, 20, (r, i) => ({ type: 'shelf', x: (i % 2 ? -1.8 : 1.8), z: 2 + Math.floor(i / 2) * 1.2, s: r(), empty: .6 })),
];
OBJ.city = [
  ...scatter(97, 60, (r, i) => ({ type: 'building', x: (r() - .5) * 140, z: 30 + r() * 160, w: 8 + r() * 10, h: 15 + r() * 50, s: r(), off: 1 })),
];

// ---------- scenes ----------
const S = [];
function scene(a, b, fn) { S.push({ a, b, fn }); }

// helpers used in era scenes
function era(t, p, cfg) {
  HY = cfg.hy ?? 900; CAMH = cfg.camh ?? 2.2;
  const camZ = cfg.speed * (t - cfg.t0) + (cfg.z0 || 0);
  sky(cfg.top, cfg.mid, cfg.hor, W / 2 + (cfg.sunDX || 0), HY - (cfg.sunH ?? 120), cfg.sunC || [255, 220, 170], cfg.sunR || 900, cfg.sunA ?? .8);
  if (cfg.preSky) cfg.preSky(t, p, camZ);
  if (cfg.ocean) cfg.ocean(t, camZ);
  else { ground(cfg.gNear, cfg.gFar, camZ, cfg.stripe || [0, 0, 0], cfg.stripeA ?? .12); groundStreaks(camZ, cfg.streak || [255, 230, 190], cfg.streakA ?? .25, 5, 90); }
  drawWorld(cfg.objs, camZ, t - cfg.t0, cfg.fog, cfg.obj, cfg.fogNear ?? 12, cfg.fogFar ?? 190);
  if (cfg.post) cfg.post(t, p, camZ);
  if (cfg.part) particles(cfg.part.seed, cfg.part.n, camZ, cfg.part.c, { ...cfg.part, t });
}

// S1 — pre-history (0-5): descend from clouds into misty savanna at dawn
scene(0, 5, (t, p) => {
  const d = eio(clamp(p / .42));
  era(t, p, {
    t0: 0, speed: 26, hy: lerp(1500, 880, d), camh: lerp(30, 2.0, d),
    top: [30, 48, 80], mid: [170, 118, 76], hor: [235, 180, 125], sunH: lerp(320, 70, d), sunR: 900, sunA: .6,
    gNear: [44, 38, 26], gFar: [180, 150, 110], stripeA: .1, streak: [255, 220, 170], streakA: .2,
    objs: OBJ.s1, fog: [230, 195, 150], obj: [22, 18, 14], fogFar: 210,
    part: { seed: 101, n: 160, c: [255, 225, 180], size: .05, a: .5, speed: 1.2, yMin: 0, yMax: 12, add: true },
    post: (t, p) => { // cloud layer during descent
      const ca = 1 - clamp(p / .38);
      if (ca > 0) { const r = rng(4); for (let i = 0; i < 40; i++) { const x = r() * W * 1.6 - W * .3, y = r() * H; const s = (180 + r() * 400) * (1 + p * 3); ctx.globalAlpha = ca * .55; ctx.fillStyle = 'rgba(250,225,190,1)'; ctx.beginPath(); ctx.ellipse(W / 2 + (x - W / 2) * (1 + p * 2.2), H * .45 + (y - H * .45) * (1 + p * 2.2), s, s * .35, 0, 0, 7); ctx.fill(); } ctx.globalAlpha = 1; }
    },
  });
});
// S2 — chariots, desert, harsh sun (5-10)
scene(5, 10, (t, p) => {
  SHAKE = [Math.sin(t * 40) * 3, Math.cos(t * 33) * 3];
  era(t, p, {
    t0: 5, speed: 24, hy: 860, camh: 1.6, top: [80, 104, 130], mid: [190, 160, 120], hor: [235, 205, 160], sunDX: 160, sunH: 380, sunR: 800, sunA: .55,
    gNear: [80, 58, 34], gFar: [190, 160, 115], stripe: [80, 55, 30], stripeA: .18, streak: [255, 230, 190], streakA: .35,
    objs: OBJ.s2, fog: [235, 210, 170], obj: [30, 22, 14], fogFar: 200,
    part: { seed: 102, n: 220, c: [240, 205, 150], size: .07, a: .55, speed: 1.6, yMin: 0, yMax: 4 },
  });
});
// S3 — Roman legion, burning fortress (10-15)
scene(10, 15, (t, p) => {
  SHAKE = [Math.sin(t * 25) * 1.5, Math.cos(t * 21) * 1.5];
  era(t, p, {
    t0: 10, speed: 18, hy: 860, camh: 2.6, top: [70, 78, 88], mid: [150, 140, 128], hor: [205, 190, 170], sunDX: -200, sunH: 300, sunR: 700, sunA: .5,
    gNear: [52, 48, 36], gFar: [150, 140, 118], stripeA: .14, streak: [210, 200, 170], streakA: .25,
    objs: OBJ.s3, fog: [175, 165, 150], obj: [26, 24, 22], fogFar: 220,
    part: { seed: 103, n: 120, c: [255, 160, 70], size: .05, a: .8, speed: 1, yMin: 1, yMax: 16, vy: .8, wrapY: true, add: true },
  });
});
// S4 — medieval castle, arrows, rush through gate (15-20)
scene(15, 20, (t, p) => {
  const gate = clamp((p - .2) / .5);
  OBJ.s4[0].gate = eio(gate);
  const sp = lerp(10, 34, eio(clamp((p - .3) / .7)));
  const camZ0 = 0;
  // integrate speed manually: approx with eased distance
  const dist = 124.2 * (.35 * p + .65 * p * p * p);
  era(t, p, {
    t0: 15, speed: 0, z0: dist, hy: 940, camh: 2.4, top: [48, 56, 70], mid: [120, 118, 118], hor: [190, 175, 155], sunA: .25, sunH: 500,
    gNear: [40, 40, 32], gFar: [125, 118, 100], stripeA: .14, streakA: .18, streak: [200, 190, 160],
    objs: OBJ.s4, fog: [160, 155, 145], obj: [22, 22, 24], fogFar: 220,
    part: { seed: 104, n: 90, c: [255, 170, 80], size: .04, a: .7, speed: 1, yMin: 1, yMax: 20, vy: .5, wrapY: true, add: true },
    post: (t, p) => { // arrow volleys arcing across the sky
      const r = rng(77); ctx.strokeStyle = 'rgba(20,18,16,.85)'; ctx.lineCap = 'round';
      for (let v = 0; v < 3; v++) {
        const ph = ((t - 15) * .55 + v * .33) % 1;
        for (let i = 0; i < 45; i++) {
          const ox = r() * 500 - 250, oy = r() * 160;
          const x = lerp(-200, W + 200, ph) + ox; const y = 520 + oy - Math.sin(ph * Math.PI) * 360;
          const ang = Math.atan2(-Math.cos(ph * Math.PI) * 360 * Math.PI, W + 400);
          ctx.lineWidth = 2.2; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - Math.cos(ang) * 34, y - Math.sin(ang) * 34); ctx.stroke();
        }
      }
    },
  });
});
// S5 — WWI trenches (20-25)
scene(20, 25, (t, p) => {
  const k = Math.max(0, Math.sin(t * 6.3)) ** 8; SHAKE = [Math.sin(t * 60) * 6 * k, Math.cos(t * 53) * 6 * k];
  era(t, p, {
    t0: 20, speed: 20, hy: 880, camh: 1.5, top: [52, 54, 56], mid: [108, 102, 92], hor: [156, 140, 118], sunA: .2,
    gNear: [34, 28, 22], gFar: [104, 92, 76], stripe: [20, 16, 12], stripeA: .25, streak: [120, 100, 80], streakA: .35,
    objs: OBJ.s5, fog: [130, 120, 105], obj: [22, 19, 16], fogFar: 200,
    part: { seed: 105, n: 120, c: [120, 110, 95], size: .1, a: .5, speed: 1.3, yMin: 0, yMax: 6 },
  });
});
// S6 — WWII ocean, battleships, fighters (25-30)
scene(25, 30, (t, p) => {
  SHAKE = [Math.sin(t * 30) * 2, Math.cos(t * 26) * 2];
  era(t, p, {
    t0: 25, speed: 30, hy: 860, camh: 1.8, top: [46, 54, 66], mid: [110, 118, 126], hor: [170, 172, 170], sunDX: -150, sunH: 200, sunR: 800, sunA: .35,
    objs: OBJ.s6, fog: [150, 155, 158], obj: [36, 38, 44], fogFar: 230, fogNear: 30,
    ocean: (t, camZ) => {
      const g = ctx.createLinearGradient(0, HY, 0, H); g.addColorStop(0, 'rgb(118,126,132)'); g.addColorStop(1, 'rgb(28,36,46)'); ctx.fillStyle = g; ctx.fillRect(0, HY, W, H - HY);
      for (let k = 0; k < 60; k++) {
        const z = k * 2.4 - (camZ % 2.4) + 1; const y = HY + CAMH * F / z + SHAKE[1]; if (y > H + 40) continue;
        ctx.strokeStyle = `rgba(220,230,235,${clamp(1 - z / 140) * .35})`; ctx.lineWidth = clamp(14 / z, .5, 6);
        ctx.beginPath(); for (let x = 0; x <= W; x += 30) ctx.lineTo(x, y + Math.sin(x * .01 + z + t * 3) * 10 / z * 6); ctx.stroke();
      }
      particles(106, 200, camZ, [235, 240, 245], { size: .05, a: .5, speed: 2.2, yMin: 0, yMax: .6, t });
    },
    post: (t, p) => { // fighter planes overhead
      for (let i = 0; i < 4; i++) {
        const ph = clamp(((t - 25) - i * .9) / 2.2); if (ph <= 0 || ph >= 1) continue;
        const x = lerp(-300, W + 300, ph) + i * 30, y = 560 - i * 70 - ph * 120, s = 22 + i * 8;
        ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = 'rgba(28,30,34,.95)'; DRAW.plane({ bank: -.12 }, t); ctx.restore();
      }
      const r = rng(9); ctx.fillStyle = 'rgba(40,40,44,.45)'; for (let i = 0; i < 14; i++) { const x = r() * W, y = 300 + r() * 450; circ(x, y, 6 + r() * 4); } // flak
    },
  });
});
// S7 — Cold War: snowy night, silo opening, radar; speed slows (30-35)
scene(30, 35, (t, p) => {
  const dist = 22 * (t - 30) - 10 * (t - 30) * (t - 30) / 5 * .9;
  OBJ.s7[0].open = eio(clamp((p - .25) / .6));
  era(t, p, {
    t0: 30, speed: 0, z0: dist, hy: 920, camh: lerp(2, 7, eio(p)), top: [6, 10, 22], mid: [22, 30, 50], hor: [52, 62, 84], sunA: 0,
    gNear: [60, 66, 78], gFar: [110, 118, 132], stripe: [255, 255, 255], stripeA: .06, streak: [230, 240, 255], streakA: .2,
    objs: OBJ.s7, fog: [55, 64, 86], obj: [14, 16, 22], fogFar: 200,
    part: { seed: 107, n: 260, c: [235, 242, 255], size: .05, a: .8, speed: .6, yMin: -1, yMax: 14, vy: -1.1, wrapY: true, drift: .5 },
    post: (t, p) => { const r = rng(5); ctx.fillStyle = 'rgba(255,255,255,.7)'; for (let i = 0; i < 120; i++) { const x = r() * W, y = r() * HY * .8; ctx.globalAlpha = .3 + .5 * hash(i + Math.floor(t * 3)); ctx.fillRect(x, y, 2, 2); } ctx.globalAlpha = 1; },
  });
});
// black beat 35-36 handled in render
// S8 — dive into fiber optic tunnel / data center (36-40)
scene(36, 40, (t, p) => {
  if (!window.OVL) { ctx.fillStyle = '#02040a'; ctx.fillRect(0, 0, W, H); } HY = 960;
  const cz = (t - 36) * 40;
  ctx.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 50; k++) {
    const z = ((k * 3 - cz) % 150 + 150) % 150 + 1; const r = 700 * 4 / z * 3; const a = clamp(1 - z / 150);
    ctx.strokeStyle = `rgba(40,150,255,${a * .55})`; ctx.lineWidth = clamp(30 / z, .5, 8);
    ctx.beginPath(); ctx.arc(W / 2, HY, r, 0, Math.PI * 2); ctx.stroke();
  }
  const rr = rng(808);
  for (let i = 0; i < 260; i++) {
    const ang = rr() * Math.PI * 2, rad = 2 + rr() * 9, zz = rr() * 150; const z = ((zz - cz * 1.5) % 150 + 150) % 150 + .8;
    const x1 = W / 2 + Math.cos(ang) * rad * F / z, y1 = HY + Math.sin(ang) * rad * F / z;
    const x2 = W / 2 + Math.cos(ang) * rad * F / (z + 5), y2 = HY + Math.sin(ang) * rad * F / (z + 5);
    ctx.strokeStyle = rr() < .1 ? `rgba(255,60,70,${clamp(1 - z / 150)})` : `rgba(120,210,255,${clamp(1 - z / 150) * .9})`; ctx.lineWidth = clamp(18 / z, .6, 6);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  }
  ctx.font = '500 28px MO';
  for (let i = 0; i < 70; i++) {
    const ang = rr() * Math.PI * 2, zz = rr() * 150; const z = ((zz - cz) % 150 + 150) % 150 + 2; const rad = 4 + rr() * 6;
    const s = clamp(F / z / 30, .3, 5); ctx.fillStyle = `rgba(120,220,255,${clamp(1 - z / 150) * .7})`;
    ctx.save(); ctx.translate(W / 2 + Math.cos(ang) * rad * F / z, HY + Math.sin(ang) * rad * F / z); ctx.scale(s, s); ctx.fillText(rr() < .5 ? '01101' : '10010', 0, 0); ctx.restore();
  }
  glow(W / 2, HY, 260, [120, 200, 255], .35 + .1 * Math.sin(t * 9));
  ctx.globalCompositeOperation = 'source-over';
});
// 9A — US airports frozen (40-46)
scene(40, 46, (t, p) => {
  const dist = 14 * (t - 40);
  era(t, p, {
    t0: 40, speed: 0, z0: dist, hy: lerp(1150, 860, eio(clamp(p / .3))), camh: lerp(40, 6, eio(clamp(p / .35))), top: [30, 34, 56], mid: [120, 84, 90], hor: [235, 140, 100], sunDX: 220, sunH: 30, sunC: [255, 140, 90], sunR: 900, sunA: .55,
    gNear: [26, 26, 30], gFar: [70, 64, 70], stripe: [255, 230, 120], stripeA: .0, streakA: .0,
    objs: OBJ.air, fog: [150, 110, 110], obj: [20, 22, 28], fogFar: 260, fogNear: 30,
    preSky: () => { },
    post: (t, p, camZ) => {
      // runway lines + edge lights
      for (let k = 0; k < 60; k++) {
        const z = k * 5 - (camZ % 5) + 1; if (z < 1) continue;
        const [x1, y1, s] = proj(0, 0, z); const [x2, y2] = proj(0, 0, z + 2.4);
        ctx.strokeStyle = `rgba(240,240,230,${clamp(1 - z / 260) * .8})`; ctx.lineWidth = clamp(s * .25, .5, 30); ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
        for (const sx of [-12, 12]) { const [lx, ly, ls] = proj(sx, 0, z); glow(lx, ly, clamp(ls * 1.1, 2, 60), [255, 200, 120], clamp(1 - z / 260) * .8); }
      }
    },
  });
});
// 9B — vault of coins draining (46-51)
scene(46, 51, (t, p) => {
  ctx.fillStyle = '#07060a'; ctx.fillRect(0, 0, W, H); HY = 900; CAMH = 3;
  const camZ = (t - 46) * 9; const drain = clamp((p - .1) / .8);
  // floor
  const g = ctx.createLinearGradient(0, HY, 0, H); g.addColorStop(0, '#120e08'); g.addColorStop(1, '#2a1e0c'); ctx.fillStyle = g; ctx.fillRect(0, HY, W, H - HY);
  const r = rng(461); const stacks = [];
  for (let i = 0; i < 70; i++) stacks.push({ x: sideX(r, 2.5, 22), z: 4 + r() * 90, h: 2 + r() * 10, s: r() });
  stacks.sort((a, b) => (b.z - camZ) - (a.z - camZ));
  for (const s of stacks) {
    const z = s.z - camZ; if (z < .8) continue;
    const hh = s.h * (1 - drain * (.4 + .6 * hash(s.s * 99)));
    const [bx, by, sc] = proj(s.x, 0, z); const a = clamp(1 - z / 95);
    const n = Math.max(1, Math.floor(hh / .25));
    for (let k = 0; k < n; k++) {
      const yy = by - k * .25 * sc; const lum = 150 + 80 * hash(k + s.s * 50);
      ctx.fillStyle = `rgba(${lum + 40},${lum},${60},${a})`; ctx.beginPath(); ctx.ellipse(bx, yy, .9 * sc, .3 * sc, 0, 0, 7); ctx.fill();
    }
  }
  // coins dissolving into streams of light flowing to a dark point
  ctx.globalCompositeOperation = 'lighter';
  const rr = rng(462);
  for (let i = 0; i < 380; i++) {
    const sx = rr() * W, sy = 500 + rr() * 1300, ph = ((t - 46) * .6 + rr()) % 1; if (drain <= 0) continue;
    const x = lerp(sx, W / 2, eio(ph)), y = lerp(sy, HY - 40, eio(ph)); const a = (1 - ph) * drain;
    ctx.strokeStyle = `rgba(255,${190 - ph * 60},90,${a * .8})`; ctx.lineWidth = 3 * (1 - ph) + .5;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(lerp(sx, W / 2, eio(Math.max(0, ph - .05))), lerp(sy, HY - 40, eio(Math.max(0, ph - .05)))); ctx.stroke();
  }
  ctx.globalCompositeOperation = 'source-over';
  const vg = ctx.createRadialGradient(W / 2, HY - 40, 0, W / 2, HY - 40, 140); vg.addColorStop(0, 'rgba(0,0,0,1)'); vg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  const al = (Math.sin((t - 46) * 7) * .5 + .5); ctx.fillStyle = `rgba(255,20,30,${.12 + al * .16})`; ctx.fillRect(0, 0, W, H);
});
// 9C — Paris, rain, bank, phones red (51-55)
scene(51, 55, (t, p) => {
  era(t, p, {
    t0: 51, speed: 11, hy: 880, camh: 1.7, top: [10, 14, 24], mid: [30, 36, 52], hor: [70, 72, 90], sunA: 0,
    gNear: [16, 18, 24], gFar: [60, 60, 74], stripe: [255, 200, 150], stripeA: .05, streak: [255, 210, 160], streakA: .15,
    objs: OBJ.paris, fog: [40, 44, 60], obj: [14, 15, 20], fogFar: 140,
    part: { seed: 109, n: 420, c: [190, 205, 230], size: .02, a: .55, speed: .3, yMin: -1, yMax: 16, vy: -9, wrapY: true, streak: 0 },
    post: (t) => { // rain: vertical streaks in screen space
      const r = rng(Math.floor(t * 30)); ctx.strokeStyle = 'rgba(190,205,230,.25)'; ctx.lineWidth = 1.5;
      for (let i = 0; i < 160; i++) { const x = r() * W, y = r() * H; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 6, y + 60); ctx.stroke(); }
      // wet street reflections
      ctx.globalCompositeOperation = 'lighter'; const g = ctx.createLinearGradient(0, HY, 0, H); g.addColorStop(0, 'rgba(255,60,50,.08)'); g.addColorStop(1, 'rgba(255,60,50,0)'); ctx.fillStyle = g; ctx.fillRect(0, HY, W, H - HY); ctx.globalCompositeOperation = 'source-over';
    },
  });
});
// 9D — Tokyo neon → crisis room (55-59)
scene(55, 59, (t, p) => {
  if (p < .45) {
    era(t, p, {
      t0: 55, speed: 30, hy: 1100, camh: 30, top: [6, 6, 18], mid: [24, 16, 40], hor: [80, 40, 90], sunA: 0,
      gNear: [10, 10, 20], gFar: [40, 30, 60], stripeA: 0, streakA: 0,
      objs: OBJ.tokyo, fog: [50, 34, 70], obj: [10, 10, 18], fogFar: 220,
    });
  } else {
    const q = (p - .45) / .55; ctx.fillStyle = '#05070c'; ctx.fillRect(0, 0, W, H);
    const s = 1 + q * .25; ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-W / 2, -H / 2);
    const r = rng(551);
    for (let row = 0; row < 3; row++) for (let col = 0; col < 3; col++) {
      const x = 90 + col * 310, y = 420 + row * 230, w = 280, h = 200;
      ctx.fillStyle = '#0b1220'; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = 'rgba(255,50,60,.8)'; ctx.lineWidth = 2;
      const pts = []; for (let i = 0; i < 9; i++) pts.push([x + 20 + r() * (w - 40), y + 20 + r() * (h - 40)]);
      for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) if (r() < .25) { ctx.globalAlpha = .4 + .6 * hash(i * j + Math.floor(t * 6)); ctx.beginPath(); ctx.moveTo(...pts[i]); ctx.lineTo(...pts[j]); ctx.stroke(); }
      ctx.globalAlpha = 1; ctx.fillStyle = 'rgba(255,70,80,1)'; for (const pp of pts) circ(pp[0], pp[1], 4 + 3 * Math.sin(t * 8 + pp[0]));
      ctx.fillStyle = 'rgba(255,60,60,.9)'; ctx.font = '500 18px MO'; ctx.fillText('ALERT ' + (1000 + Math.floor(r() * 8999)), x + 12, y + 26);
    }
    glow(W / 2, 760, 700, [255, 40, 50], .25);
    ctx.fillStyle = '#020306';
    for (let i = 0; i < 7; i++) { const x = 120 + i * 140; ctx.beginPath(); ctx.arc(x, 1300, 50, 0, 7); ctx.fill(); ctx.fillRect(x - 85, 1340, 170, 600); }
    ctx.fillRect(0, 1420, W, 520);
    ctx.restore();
  }
});
// 9E — UK supermarket aisle, half empty (59-63)
scene(59, 63, (t, p) => {
  era(t, p, {
    t0: 59, speed: 6, hy: 920, camh: 1.6, top: [200, 205, 208], mid: [190, 195, 198], hor: [175, 180, 182], sunA: 0,
    gNear: [140, 142, 140], gFar: [190, 192, 190], stripe: [255, 255, 255], stripeA: .25, streak: [255, 255, 255], streakA: .1,
    objs: OBJ.shelf, fog: [200, 204, 206], obj: [70, 74, 80], fogFar: 50, fogNear: 4,
    post: (t, p, camZ) => {
      for (let k = 0; k < 30; k++) { const z = k * 2.5 - (camZ % 2.5) + 1; const [x, y, s] = proj(0, 3.2, z); ctx.fillStyle = `rgba(255,255,255,${clamp(1 - z / 50)})`; ctx.fillRect(x - s * .8, y - s * .06, s * 1.6, s * .12); }
      ctx.fillStyle = 'rgba(0,0,0,.25)'; ctx.fillRect(0, 0, W, 520 - p * 60);
      // cold fluorescent tint
      ctx.fillStyle = 'rgba(120,160,170,.12)'; ctx.fillRect(0, 0, W, H);
      // shopper silhouette holding banknotes
      const sx = 760, sy = 1700; ctx.save(); ctx.translate(sx, sy); ctx.scale(260, 260); ctx.fillStyle = 'rgba(20,22,26,.95)'; DRAW.person({}, t); ctx.fillStyle = 'rgba(120,170,120,.95)'; ctx.fillRect(-.45, -1.2, .3, .16); ctx.restore();
    },
  });
});
// 9F — São Paulo night → card machine glitch (63-68)
scene(63, 68, (t, p) => {
  if (p < .5) {
    const off = clamp((p - .1) / .35);
    for (const o of OBJ.sp) o.off = off * hash(o.s * 77);
    era(t, p, {
      t0: 63, speed: 26, hy: 1150, camh: 26, top: [8, 10, 20], mid: [26, 30, 50], hor: [90, 70, 80], sunA: 0,
      gNear: [10, 10, 16], gFar: [40, 36, 46], stripeA: 0, streakA: 0,
      objs: OBJ.sp, fog: [50, 44, 60], obj: [10, 11, 16], fogFar: 210,
      post: (t, p, camZ) => { for (let k = 0; k < 40; k++) { const z = k * 4 - (camZ % 4) + 1; if (z < 1) continue; const [x, y, s] = proj(-3, 0, z), [x2, y2] = proj(3, 0, z); glow(x, y, clamp(s * 1.2, 2, 50), [255, 200, 120], clamp(1 - z / 160) * (1 - off * .8)); glow(x2, y2, clamp(s * 1.2, 2, 50), [255, 60, 50], clamp(1 - z / 160) * (1 - off * .8)); } },
    });
  } else {
    const q = (p - .5) / .5; ctx.fillStyle = '#0a0806'; ctx.fillRect(0, 0, W, H);
    glow(W / 2, 600, 900, [255, 170, 90], .18);
    const s = 1 + q * .18; ctx.save(); ctx.translate(W / 2, 980); ctx.scale(s, s); ctx.rotate(-.06);
    ctx.fillStyle = '#16161a'; roundRect(-260, -470, 520, 940, 50); ctx.fill();
    ctx.fillStyle = '#26262c'; roundRect(-230, -440, 460, 420, 20); ctx.fill();
    const dead = q > .55;
    if (!dead) { // QR code
      const r = rng(Math.floor(t * (q > .3 ? 20 : 1)));
      ctx.fillStyle = '#e8e8e8'; ctx.fillRect(-150, -400, 300, 300); ctx.fillStyle = '#111';
      for (let i = 0; i < 21; i++) for (let j = 0; j < 21; j++) if (r() < .5 || ((i < 7 && j < 7) || (i > 13 && j < 7) || (i < 7 && j > 13))) ctx.fillRect(-140 + i * 13.3, -390 + j * 13.3, 13.3, 13.3);
      ctx.fillStyle = '#fff'; ctx.font = '600 30px IN'; ctx.textAlign = 'center'; ctx.fillText(q > .3 ? 'ERRO DE CONEXÃO' : 'PAGUE COM PIX', 0, -50); ctx.textAlign = 'left';
    } else { ctx.fillStyle = '#050505'; roundRect(-230, -440, 460, 420, 20); ctx.fill(); ctx.fillStyle = 'rgba(255,60,60,.9)'; ctx.font = '600 34px IN'; ctx.textAlign = 'center'; ctx.fillText('SEM CONEXÃO', 0, -220); ctx.textAlign = 'left'; }
    ctx.fillStyle = '#202026'; for (let i = 0; i < 4; i++) for (let j = 0; j < 3; j++) { roundRect(-180 + j * 130, 40 + i * 100, 100, 70, 14); ctx.fill(); }
    ctx.restore();
  }
});
// 10 — dark city, golden shield forms (68-73)
scene(68, 73, (t, p) => {
  era(t, p, {
    t0: 68, speed: 3, z0: 40, hy: 1180, camh: 20, top: [2, 3, 8], mid: [8, 10, 18], hor: [22, 22, 30], sunA: 0,
    gNear: [4, 4, 8], gFar: [14, 14, 20], stripeA: 0, streakA: 0,
    objs: OBJ.city, fog: [18, 18, 26], obj: [6, 6, 10], fogFar: 200,
  });
  // one lit home
  glow(W / 2, 1230, 120, [255, 200, 120], .9); ctx.fillStyle = 'rgba(255,214,150,1)'; ctx.fillRect(W / 2 - 10, 1222, 20, 16);
  // shield forming from particles
  const q = eio(clamp((p - .05) / .6)); const r = rng(1010);
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 900; i++) {
    const u = r() * 2 - 1, v = r(); // param over shield
    const hw = 280 * (v < .55 ? 1 : Math.sqrt(Math.max(0, 1 - (v - .55) / .45)));
    const tx = W / 2 + u * hw, ty = 560 + v * 720;
    const sx = r() * W, sy = r() * H; const x = lerp(sx, tx, q), y = lerp(sy, ty, q);
    ctx.fillStyle = `rgba(255,${190 + r() * 50},${110 + r() * 40},${.25 + .5 * r()})`; ctx.fillRect(x, y, 3, 3);
  }
  if (q > .6) {
    const a = (q - .6) / .4; ctx.strokeStyle = `rgba(255,205,130,${a * .9})`; ctx.lineWidth = 6;
    ctx.beginPath(); ctx.moveTo(W / 2 - 280, 560); ctx.lineTo(W / 2 + 280, 560); ctx.lineTo(W / 2 + 280, 560 + 400); ctx.quadraticCurveTo(W / 2 + 260, 1200, W / 2, 1290); ctx.quadraticCurveTo(W / 2 - 260, 1200, W / 2 - 280, 960); ctx.closePath(); ctx.stroke();
    glow(W / 2, 900, 700, [255, 190, 110], a * .35);
  }
  ctx.globalCompositeOperation = 'source-over';
});
// 11 — Earth network, verse (73-80)
scene(73, 80, (t, p) => {
  ctx.fillStyle = '#010104'; ctx.fillRect(0, 0, W, H);
  const r = rng(2020); for (let i = 0; i < 300; i++) { ctx.fillStyle = `rgba(255,255,255,${r() * .6})`; ctx.fillRect(r() * W, r() * H, 1.5, 1.5); }
  const R = 560, cx = W / 2, cy = 1900 - p * 260;
  const g = ctx.createRadialGradient(cx - 150, cy - 200, 50, cx, cy, R); g.addColorStop(0, '#0d1a2c'); g.addColorStop(1, '#03060c'); ctx.fillStyle = g; circ(cx, cy, R);
  glow(cx, cy, R * 1.3, [80, 140, 255], .18);
  ctx.globalCompositeOperation = 'lighter';
  const nr = rng(2021); const pts = [];
  for (let i = 0; i < 90; i++) { const a = nr() * Math.PI * 2, d = Math.sqrt(nr()) * R * .96; const rot = t * .05; pts.push([cx + Math.cos(a + rot) * d, cy + Math.sin(a + rot) * d * .9]); }
  ctx.strokeStyle = 'rgba(255,200,120,.22)'; ctx.lineWidth = 1.5;
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) { const dx = pts[i][0] - pts[j][0], dy = pts[i][1] - pts[j][1]; if (dx * dx + dy * dy < 170 * 170) { ctx.beginPath(); ctx.moveTo(...pts[i]); ctx.lineTo(...pts[j]); ctx.stroke(); } }
  for (const pp of pts) { ctx.fillStyle = 'rgba(255,215,150,.9)'; circ(pp[0], pp[1], 2.5); }
  // golden dust + ray from above
  const lr = ctx.createLinearGradient(W / 2, 0, W / 2, 1200); lr.addColorStop(0, 'rgba(255,220,160,.22)'); lr.addColorStop(1, 'rgba(255,220,160,0)');
  ctx.fillStyle = lr; ctx.beginPath(); ctx.moveTo(W / 2 - 60, 0); ctx.lineTo(W / 2 + 60, 0); ctx.lineTo(W / 2 + 380, 1300); ctx.lineTo(W / 2 - 380, 1300); ctx.fill();
  const dr = rng(2022); for (let i = 0; i < 120; i++) { const x = dr() * W, y = (dr() * H - t * 20 * (1 + dr())) % H; ctx.fillStyle = `rgba(255,215,150,${dr() * .7})`; circ(x, (y + H) % H, 1 + dr() * 2.5); }
  ctx.globalCompositeOperation = 'source-over';
});

function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }

// ---------- text timeline ----------
const TX = [
  { a: .9, b: 4.8, stamp: 'PRÉ-HISTÓRIA', title: 'Durante milênios, a guerra teve um *rosto*.' },
  { a: 5.4, b: 9.8, stamp: 'ANTIGUIDADE', title: 'Lanças. *Bigas.*', cap: 'Exércitos que se viam de longe.' },
  { a: 10.4, b: 14.8, stamp: 'ROMA', title: 'Legiões. *Catapultas.*' },
  { a: 15.4, b: 19.6, stamp: 'IDADE MÉDIA', title: 'Muralhas que levavam *anos* para cair.' },
  { a: 20.4, b: 24.8, stamp: '1ª GUERRA MUNDIAL', title: 'Depois, as *trincheiras…*' },
  { a: 25.4, b: 29.8, stamp: '2ª GUERRA MUNDIAL', title: '…os navios, os *aviões…*' },
  { a: 30.4, b: 34.8, stamp: 'GUERRA FRIA', title: '…e a bomba que mudou *tudo*.' },
  { a: 36.6, b: 39.8, stamp: 'GUERRA CIBERNÉTICA', title: 'Hoje, a guerra não faz *barulho*.' },
  { a: 40.4, b: 43.8, stamp: 'REINO UNIDO', title: '“Guardem *dinheiro vivo*.”', cap: 'Governo pede 3 dias de água, comida, rádio e cédulas em casa.', size: 84 },
  { a: 44.3, b: 48.8, stamp: 'CORRETORA DE CRIPTO', title: 'US$ 6,3 bilhões em *~20 minutos*.', cap: 'O FBI aponta hackers da Coreia do Norte.', size: 84 },
  { a: 49.3, b: 52.8, stamp: 'FRANÇA', title: '€ 100 milhões *desviados*.', cap: 'Ataque hacker ao banco Crédit Mutuel Arkéa. Aplicativos fora do ar por horas.', size: 92 },
  { a: 53.3, b: 56.8, stamp: 'JAPÃO', title: 'Pacote de *emergência*: ¥10 bilhões.', cap: 'Contra uma onda de invasões a empresas e órgãos públicos.', size: 84 },
  { a: 57.4, b: 62.8, stamp: 'ESTADOS UNIDOS · 15H54', title: 'Todos os voos dos EUA *no chão*.', cap: 'Mais de 4 horas parados. Milhares de cancelamentos. Nem foi um ataque: bastou uma pane.', size: 84 },
  { a: 63.3, b: 67.8, stamp: 'BRASIL', title: '*55,2%* dos pagamentos passam pelo Pix.', cap: 'Em julho de 2025, bastou invadir um único fornecedor.', size: 84 },
  { a: 68.5, b: 70.9, title: 'A 3ª Guerra não derruba a sua casa.', size: 80, align: 'center', y: 1560 },
  { a: 70.9, b: 72.9, title: 'Ela tira o seu *acesso* ao dinheiro.', size: 80, align: 'center', y: 1560 },
];
const VERSE = [
  { a: 74.0, t: '“…muitos correrão de uma', y: 760 },
  { a: 74.6, t: 'parte para outra,', y: 850 },
  { a: 75.6, t: 'e a ciência se *multiplicará*.”', y: 960 },
];


// ---------- timeline graphic ----------
const TL_ERA = [[0, 'PRÉ-HIST.'], [5, '1500 a.C.'], [10, '50 a.C.'], [15, '1200'], [20, '1914'], [25, '1942'], [30, '1962'], [36, '2026']].map((n, i) => ({ t: n[0], l: n[1], x: 110 + i * 860 / 7 }));
const TL_CY = [[40, '22 OUT', 0], [44, '29 OUT', 7], [49, '04 NOV', 13], [53, '06 NOV', 15], [57, '13 NOV', 22]].map(n => ({ t: n[0], l: n[1], x: 110 + n[2] / 22 * 690 }));
TL_CY.push({ t: 63, l: 'BRASIL', x: 960, dashed: true });
function drawTL(nodes, t, alpha, head) {
  if (alpha <= 0) return;
  const Y = 345; let ci = 0; for (let i = 0; i < nodes.length; i++) if (t >= nodes[i].t) ci = i;
  const prevX = ci > 0 ? nodes[ci - 1].x : nodes[0].x;
  const mx = lerp(prevX, nodes[ci].x, eio(clamp((t - nodes[ci].t) / .7)));
  ctx.save(); ctx.globalAlpha = alpha;
  const g = ctx.createLinearGradient(0, 0, 0, 520); g.addColorStop(0, 'rgba(0,0,0,.72)'); g.addColorStop(.7, 'rgba(0,0,0,.45)'); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 520);
  ctx.font = '500 27px MO'; ctx.textAlign = 'left'; ctx.fillStyle = 'rgba(214,176,116,.95)';
  if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '5px'; ctx.fillText(head, 84, 222); if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '0px';
  const x0 = nodes[0].x, last = nodes[nodes.length - 1];
  ctx.lineCap = 'round'; ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,.28)';
  const solidEnd = last.dashed ? nodes[nodes.length - 2].x : last.x;
  ctx.beginPath(); ctx.moveTo(x0, Y); ctx.lineTo(solidEnd, Y); ctx.stroke();
  if (last.dashed) { ctx.setLineDash([10, 12]); ctx.beginPath(); ctx.moveTo(solidEnd, Y); ctx.lineTo(last.x, Y); ctx.stroke(); ctx.setLineDash([]); }
  ctx.strokeStyle = 'rgba(226,186,120,1)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x0, Y); ctx.lineTo(mx, Y); ctx.stroke();
  ctx.textAlign = 'center';
  nodes.forEach((n, i) => {
    const cur = i === ci, done = i < ci || (cur && t - n.t > .5); const up = i % 2 === 1;
    const k = cur ? eo(clamp((t - n.t - .35) / .45)) : 0;
    ctx.strokeStyle = 'rgba(255,255,255,.2)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(n.x, Y); ctx.lineTo(n.x, Y + (up ? -24 : 24)); ctx.stroke();
    ctx.beginPath(); ctx.arc(n.x, Y, 8 + 5 * k, 0, 7);
    if (done) { ctx.fillStyle = 'rgba(226,186,120,1)'; ctx.fill(); } else { ctx.fillStyle = '#0a0a0c'; ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,.5)'; ctx.stroke(); }
    const fs = 25 + 17 * k; ctx.font = `500 ${fs}px MO`;
    ctx.fillStyle = k > 0 ? `rgba(${lerp(200, 255, k)},${lerp(200, 226, k)},${lerp(200, 170, k)},1)` : (done ? 'rgba(226,186,120,.75)' : 'rgba(255,255,255,.5)');
    ctx.fillText(n.l, clamp(n.x, 90, W - 90), up ? Y - 38 - 6 * k : Y + 56 + 12 * k);
  });
  ctx.globalAlpha = alpha; glow(mx, Y, 46 + 8 * Math.sin(t * 6), [255, 200, 120], .55);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(mx, Y, 5, 0, 7); ctx.fill();
  ctx.restore(); ctx.textAlign = 'left';
}
function timeline(t) {
  if (t < 40) drawTL(TL_ERA, t, Math.min(clamp((t - .6) / .6), clamp((40 - t) / .25)), 'A HISTÓRIA DA GUERRA');
  else if (t < 68) drawTL(TL_CY, t, Math.min(clamp((t - 40) / .4), clamp((68 - t) / .4)), 'OUT — NOV 2026 · A GUERRA SEM ROSTO');
}

// ---------- master render ----------
function render(t) {
  SHAKE = [0, 0];
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  ctx.textAlign = 'left';
  if (t >= 35 && t < 36) { // black silence beat
    if (t < 35.15) flash(1 - (t - 35) / .15, [255, 255, 255]);
    return;
  }
  const sc = S.find(s => t >= s.a && t < s.b) || S[S.length - 1];
  const p = (t - sc.a) / (sc.b - sc.a);
  const ph = PHOTOS.find(e => t >= e.a && t < e.b);
  if (ph && IMG[ph.k]) { drawPhoto(ph, t); if (ph.ov) ph.ov(t, (t - ph.a) / (ph.b - ph.a)); }
  else sc.fn(t, p);

  // grading per era
  if (t < 20) grade([255, 190, 120], .22);
  else if (t < 30) grade([140, 150, 165], .2);
  else if (t < 36) grade([80, 110, 170], .25);
  else if (t < 68) grade([60, 90, 140], .15);

  // speed / motion feel
  const into = (x, a) => clamp(1 - Math.abs(t - x) / a);
  const bounds = [5, 10, 15, 20, 25, 30, 36, 40, 44, 49, 53, 57, 63, 68, 73];
  let tr = 0; for (const b of bounds) tr = Math.max(tr, into(b, .35));
  if (t < 35) zoomBlur(.6 + tr * 1.6);
  else if (t >= 36 && t < 40) zoomBlur(1.2);
  else zoomBlur(tr * 1.5);
  if (t < 35 || (t > 36 && t < 46)) speedLines(.5 + tr, t);

  vignette(t > 73 ? .6 : .8);

  // glitch in cyber section
  let gl = 0;
  if (t >= 36 && t < 40) gl = .35 + .6 * (hash(Math.floor(t * 8)) > .7 ? 1 : 0);
  if (t >= 40 && t < 68) gl = hash(Math.floor(t * 10)) > .86 ? .7 : 0;
  for (const b of [40, 44, 49, 53, 57, 63, 68]) gl = Math.max(gl, into(b, .22) * 1.2);
  if (t >= 64.6 && t < 66) gl = Math.max(gl, .6);
  glitch(gl, t);

  timeline(t);
  // text
  for (const b of TX) textBlock(b, t);
  // big question
  if (t >= 71.6 && t < 73) {
    const a = Math.min(eo((t - 71.6) / .35), clamp((73 - t) / .12));
    ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = 'rgba(0,0,0,.55)'; ctx.fillRect(0, 0, W, H);
    drawRich('Você está *preparado*?', W / 2, 1000, 120, 900, a, 'center', [236, 196, 128]); ctx.restore();
  }
  if (t >= 73.8) {
    const fo = clamp((79.4 - t) / .6);
    for (const v of VERSE) { const a = Math.min(eo((t - v.a) / .8), fo); if (a > 0) drawRich(v.t, W / 2, v.y, 76, 980, a, 'center', [236, 196, 128]); }
    const a = Math.min(eo((t - 77) / .8), fo);
    if (a > 0) { ctx.font = '500 34px MO'; ctx.fillStyle = `rgba(214,176,116,${a})`; ctx.textAlign = 'center'; if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '8px'; ctx.fillText('DANIEL 12:4', W / 2, 1120); if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '0px'; ctx.fillRect(W / 2 - 40, 1050, 80, 3); ctx.textAlign = 'left'; }
  }

  // transitions
  for (const b of [5, 10, 15, 20, 25, 30]) flash(into(b, .12) * .85, [255, 236, 210]);
  for (const b of [40, 44, 49, 53, 57, 63]) flash(into(b, .08) * .5, [255, 60, 70]);
  flash(into(68, .1) * .6, [255, 220, 170]);
  fadeBlack(clamp((t - 34.4) / .6) * (t < 35 ? 1 : 0));
  fadeBlack(clamp(1 - (t - 36) / .3) * (t >= 36 && t < 36.3 ? 1 : 0));
  fadeBlack(t < .5 ? 1 - t / .5 : 0);
  fadeBlack(clamp((t - 72.9) / .1) * (t < 73.3 ? 1 : 0) + clamp(1 - (t - 73.3) / .6) * (t >= 73.3 ? 1 : 0) * (t < 73.9 ? 1 : 0));
  fadeBlack(clamp((t - 79.4) / .6));

  grain(t, t > 36 && t < 68 ? .09 : .07);
}
window.render = render;
window.ready = Promise.all(Object.values(IMGP)).then(() => document.fonts.ready).then(() => Promise.all(['500 40px PF', 'italic 500 40px PF', '400 40px IN', '500 40px MO'].map(f => document.fonts.load(f))));

