# Continuous crescendo score, 120 BPM (beat = .5 s), D minor. Layers enter one by one and keep growing to 72.9 s.
import numpy as np, wave, sys
SR = 44100; DUR = 80.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.default_rng(21); L = np.zeros(N); R = np.zeros(N); B = .5
def lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def add(sig, at, g=1.0, pan=0.0):
    i = int(round(at * SR)); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += sig[:n] * g * (1 - max(0, pan)); R[i:i + n] += sig[:n] * g * (1 + min(0, pan))
def T(d): return np.arange(int(SR * d)) / SR
def grow(a, b, p=1.0): return lambda x: float(np.clip((x - a) / (b - a), 0, 1)) ** p
MIDI = lambda m: 440 * 2 ** ((m - 69) / 12)
_c = {}
def stac(m, d=.22):  # short string note
    k = ('s', m, d)
    if k not in _c:
        tt = T(d + .25); f = MIDI(m); s = sum(np.sin(2 * np.pi * f * h * tt * (1 + .002 * (h % 2))) / h for h in range(1, 9))
        _c[k] = lp(s * np.minimum(1, tt / .008) * np.exp(-np.maximum(0, tt - d * .5) * 14), 3200)
    return _c[k]
def piano(m, d=3.0):
    k = ('p', m)
    if k not in _c:
        tt = T(d); f = MIDI(m); x = sum(a * np.sin(2 * np.pi * f * h * np.sqrt(1 + .0004 * h * h) * tt) * np.exp(-tt * (.9 + .4 * h)) for h, a in enumerate([1, .5, .3, .2, .12, .08], 1))
        _c[k] = x * np.minimum(1, tt / .004)
    return _c[k]
def kick(g=1.0, f0=140, f1=44, d=.5):
    tt = T(d); f = f1 + (f0 - f1) * np.exp(-tt * 30); return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8) * 1.8) * g
def taiko(g=1.0, f0=85):
    tt = T(.9); f = f0 * (1 + .5 * np.exp(-tt * 25)); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5) + rng.standard_normal(len(tt)) * np.exp(-tt * 60) * .2) * g
_sn = hp(rng.standard_normal(int(SR * .4)), 1500)
def snare(g=1.0): tt = T(.4); return (np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 28) * .5 + _sn * np.exp(-tt * 16)) * g
_hn = hp(rng.standard_normal(int(SR * .08)), 7500)
def hat(g=1.0): tt = T(.08); return _hn * np.exp(-tt * 80) * g
def braam(g=1.0, root=36.71, d=3.0):
    tt = T(d); s = np.zeros(len(tt))
    for mul, a in [(1, 1), (2, .7), (3, .45), (1.498, .5), (4, .25), (5, .15)]:
        for det in (-.004, .004): s += a * np.sin(2 * np.pi * root * mul * (1 + det) * tt + rng.uniform(0, 6))
    return lp(np.tanh(s * .9) * np.minimum(1, tt / .04) * np.exp(-tt * 1.2), 1800) * g
def whoosh(d, g): tt = T(d); return hp(rng.standard_normal(len(tt)), 900) * (tt / d) ** 2.5 * g

END = 72.9
# chords per 4 s: Dm | Dm | Bb | C   (roots as midi)
CH = [(38, [62, 65, 69]), (38, [62, 65, 69]), (34, [58, 62, 65]), (36, [60, 64, 67])]
def chord(x): return CH[int(x // 4) % 4]
# 1) drone + pad (whole piece, swelling)
g_pad = np.clip(t / 60, 0, 1) ** 1.3 * .9 + .1
pad = np.zeros(N)
for ci in range(int(END // 4) + 1):
    root, notes = CH[ci % 4]; a = ci * 4; i0, i1 = int(a * SR), min(N, int((a + 4.3) * SR)); tt = t[i0:i1] - a
    e = np.minimum(1, tt / .6) * np.minimum(1, (4.3 - tt) / .5)
    s = sum(np.sin(2 * np.pi * MIDI(m) * tt * d) for m in notes + [root + 12] for d in (.997, 1.003)) + 1.5 * np.sin(2 * np.pi * MIDI(root) * tt)
    pad[i0:i1] += s * e * (.7 + .3 * np.sin(2 * np.pi * 5.5 * tt))
pad *= g_pad * (t < END); L += pad * .022; R += pad * .022
# 2) piano motif from the start (fades as the rest takes over)
motif = [74, 77, 76, 74, 81, 77, 76, 72]
for i in range(int(40 / 1.0)):
    at = .5 + i * 1.0
    if at > 34.5 and at < 36.2: continue
    add(piano(motif[i % 8] if at < 20 else motif[i % 8] + (0 if i % 2 else 12)), at, .44 * (1 - .5 * grow(15, 40)(at)), pan=(-.3 if i % 2 else .3))
# 3) heartbeat pulse from 4 s
gk = grow(4, 60)
at = 4.0
while at < END:
    full = at >= 40
    if at < 35 or at >= 36:
        if full or int(round(at / B)) % 2 == 0: add(kick(.35 + .65 * gk(at)), at)
    at += B
# 4) string ostinato 8ths from 10 s, octave up from 25 s, 16ths from 57 s
pat = [0, 0, 1, 0, 2, 0, 1, 0]
gs = grow(10, 66, 1.2)
at = 10.0
while at < END:
    step = B / 4 if at >= 57 else B / 2
    if not (35 <= at < 36):
        root, notes = chord(at); idx = int(round(at / step)); m = notes[pat[idx % 8]] - 12
        acc = 1.0 if idx % (4 if at >= 57 else 2) == 0 else .6
        g = (.05 + .22 * gs(at)) * acc
        add(stac(m), at, g, -.25)
        if at >= 25: add(stac(m + 12), at, g * (.3 + .6 * grow(25, 60)(at)), .25)
        if at >= 49: add(stac(m + 24, .12), at, g * .45 * grow(49, 68)(at), 0)
    at += step
# 5) bass from 15 s
gb = grow(15, 62)
at = 15.0
while at < END:
    if not (35 <= at < 36):
        root, _ = chord(at); tt = T(.5); f = MIDI(root)
        add(np.tanh((np.sin(2 * np.pi * f * tt) + .4 * np.sin(4 * np.pi * f * tt)) * 1.5) * np.minimum(1, tt / .005) * np.exp(-tt * 4), at, .12 + .26 * gb(at))
    at += B
# 6) taikos from 20 s (denser over time), snare backbeat from 40 s, hats from 30 s
at = 20.0
while at < END:
    if not (35 <= at < 36):
        k = int(round(at / (B / 2))) % 8; g = .25 + .6 * grow(20, 66)(at)
        if k in (0, 3, 6) or (at >= 49 and k == 5): add(taiko(g, 85 if k == 0 else 110), at, pan=(.3 if k == 3 else -.3 if k == 6 else 0))
        if at >= 30: add(hat(.08 + .2 * grow(30, 68)(at)), at, pan=.4)
        if at >= 57: add(hat(.14), at + B / 4, pan=-.4)
        if at >= 40 and k == 4: add(snare(.3 + .45 * grow(40, 68)(at)), at)
    at += B / 2
# 7) hits on every scene change, each a bit bigger
cuts = [5, 10, 15, 20, 25, 30, 36, 40, 44, 49, 53, 57, 63, 68]
for i, c in enumerate(cuts):
    g = .22 + .6 * i / len(cuts); add(braam(g), c - .01); add(whoosh(.8, .25 + .2 * i / len(cuts)), c - .8)
# 8) 35-36: breath (held high note + sub), not silence
tt = T(1.1); add((np.sin(2 * np.pi * MIDI(86) * tt) * .05 + np.sin(2 * np.pi * 36.7 * tt) * .25) * np.minimum(1, tt / .1) * np.minimum(1, (1.1 - tt) / .15), 34.95)
# 9) final riser 63 -> 72.9 + snare roll 68 ->
m = (t >= 63) & (t < END); pr = np.clip((t - 63) / 9.9, 0, 1)
ris = hp(rng.standard_normal(N), 1000) * pr ** 2.2 * .3 * m + np.sin(2 * np.pi * np.cumsum(np.interp(t, [63, END], [110, 660])) / SR) * .1 * pr ** 2 * m
L += ris; R += ris
at = 68.0
while at < END - .05:
    p = (at - 68) / 4.9; add(snare(.12 + .5 * p), at); at += np.interp(at, [68, END], [B / 2, B / 8])
add(kick(1.0, 170, 38, .9), 71.6); add(braam(.9, 36.71, 1.3), 71.6)
# 10) ending: piano note
add(piano(50, 6.2) * .7 + piano(62, 6.2) * .35 + piano(57, 6.2) * .2, 73.6, .6)
# master crescendo
master = np.where(t < END, .62 + .38 * np.clip(t / 68, 0, 1) ** 1.2, 1.0); L *= master; R *= master
def reverb(x, seed, secs=2.4, mix=.22):
    n = int(SR * secs); tt = np.arange(n) / SR; ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 3.4); ir[0] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << (len(x) + n - 1).bit_length(); y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return x * (1 - mix) + y * mix * 1.3
L = reverb(L, 1); R = reverb(R, 2)
i0, i1 = int(72.95 * SR), int(73.6 * SR); f = int(.015 * SR)
for ch in (L, R): ch[i0:i0 + f] *= np.linspace(1, 0, f); ch[i0 + f:i1] = 0
fo = np.clip((80 - t) / 1.2, 0, 1) * np.clip(t / .4, 0, 1); L *= fo; R *= fo
mx = max(np.abs(L).max(), np.abs(R).max()); L = np.tanh(L / mx * 1.7) / np.tanh(1.7) * .9; R = np.tanh(R / mx * 1.7) / np.tanh(1.7) * .9
st = np.empty(N * 2); st[0::2] = L; st[1::2] = R
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
