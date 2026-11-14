# Beat-driven suspense score, 96 BPM (beat = 0.625 s -> 5 s = 8 beats, scene cuts land on the grid)
import numpy as np, wave, sys
SR = 44100; DUR = 80.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)
B = 60 / 96  # beat

def fft_lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def fft_hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def add(sig, at, gain=1.0, pan=0.0):
    i = int(round(at * SR)); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan)); R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))
def tt_(d): return np.arange(int(SR * d)) / SR

# ---------- instruments ----------
def kick(g=1.0, f0=150, f1=42, d=.55):
    tt = tt_(d); f = f1 + (f0 - f1) * np.exp(-tt * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    s += rng.standard_normal(len(tt)) * np.exp(-tt * 180) * .3
    return np.tanh(s * 1.8) * g
def tom(g=1.0, f0=110):
    tt = tt_(.8); f = f0 * (1 + .6 * np.exp(-tt * 20))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6) + rng.standard_normal(len(tt)) * np.exp(-tt * 50) * .15) * g
_snare_noise = fft_hp(rng.standard_normal(int(SR * .5)), 1200)
def snare(g=1.0):
    tt = tt_(.5); body = np.sin(2 * np.pi * 185 * tt) * np.exp(-tt * 25)
    return (body * .6 + _snare_noise * np.exp(-tt * 14) * .9) * g
_hat_noise = fft_hp(rng.standard_normal(int(SR * .12)), 7000)
def hat(g=1.0, d=.06):
    n = int(SR * d); tt = np.arange(n) / SR; return _hat_noise[:n] * np.exp(-tt * 70) * g
def tick(g=1.0):
    tt = tt_(.04); return (np.sin(2 * np.pi * 2900 * tt) * np.exp(-tt * 260) + rng.standard_normal(len(tt)) * np.exp(-tt * 500) * .2) * g
def braam(g=1.0, root=36.7, d=3.0):  # big trailer brass-like hit
    tt = tt_(d); s = np.zeros(len(tt))
    for mul, a in [(1, 1), (2, .7), (3, .45), (1.498, .5), (2.996, .3), (4, .25), (5, .15)]:
        for det in (-.004, .004):
            s += a * np.sin(2 * np.pi * root * mul * (1 + det) * tt + rng.uniform(0, 6))
    s = np.tanh(s * .9) * np.minimum(1, tt / .03) * np.exp(-tt * 1.1)
    return fft_lp(s, 1800) * g
def sub_note(f, d, g=1.0):
    tt = tt_(d); s = np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * 2 * f * tt)
    return np.tanh(s * 1.5) * np.minimum(1, tt / .005) * np.exp(-tt * 3.5) * g
def boom(g=1.0, d=2.4):
    tt = tt_(d); x = fft_lp(rng.standard_normal(len(tt)), 260) * 6
    sub = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-tt * 2.5) + 28) / SR)
    return (x * .5 + sub) * np.exp(-tt * 2.6) * g
def glitch(ms):
    n = int(SR * ms / 1000); x = np.sign(np.sin(2 * np.pi * rng.uniform(250, 2400) * np.arange(n) / SR)) * .3
    return x * (rng.random(n) > .35)
def whoosh(d=1.2, g=1.0, rev=False):
    tt = tt_(d); e = (tt / d) ** 2.5; e = e[::-1] if rev else e
    return fft_hp(rng.standard_normal(len(tt)), 900) * e * g

# ---------- 0-35: epic suspense march (D minor) ----------
D2, F2, A1, C2, Bb1 = 73.4, 87.3, 55.0, 65.4, 58.3
pad = np.zeros(N)
for f, a in [(146.8, 1), (174.6, .7), (220, .6), (293.7, .35)]:
    pad += a * (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t + 1)) * (.6 + .4 * np.sin(2 * np.pi * 6.4 * t + f))  # string tremolo
pe = np.clip((t - .5) / 4, 0, 1) * np.clip((35 - t) / .03, 0, 1) * (t < 35) * (.35 + .65 * np.clip(t / 35, 0, 1))
L += pad * pe * .035; R += pad * pe * .035
bassline = [D2, D2, D2, F2, D2, D2, C2, Bb1]
nb = 0
for i in range(int(35 / (B / 2))):  # eighth-note ostinato
    at = i * B / 2
    if at < 1.25: continue
    f = bassline[(i // 2) % 8]
    acc = 1.0 if i % 2 == 0 else .55
    add(sub_note(f, B / 2 + .05, .32 * acc * (.6 + .4 * at / 35)), at)
for k in range(int(35 / B)):
    at = k * B
    if at < 2.5: continue
    bar_pos = k % 4
    g = .55 + .45 * (at / 35)
    if bar_pos in (0, 2): add(kick(g * .9), at)
    if at >= 15 and bar_pos in (1, 3): add(tom(g * .5, 95), at, pan=.3 if bar_pos == 1 else -.3)
    if at >= 20: add(hat(.25 * g), at + B / 2)
    if at >= 25: add(snare(.35 * g), at + B * .75) if bar_pos == 3 else None
for b in [5, 10, 15, 20, 25, 30]:
    add(braam(.55), b - .01); add(whoosh(.9, .35), b - .9)
# tom fill into each era
for b in [10, 20, 30]:
    for j, o in enumerate([-B, -B * .75, -B * .5, -B * .25]): add(tom(.45, 140 - j * 15), b + o, pan=(-.4 + j * .25))
# build to the cut
add(whoosh(2.2, .55), 32.8)

# ---------- 35-36: silence ----------
# ---------- 36-40: electric suspense, half-time ----------
hum = (np.sin(2 * np.pi * 60 * t) + .5 * np.sin(2 * np.pi * 120 * t)) * .07 * ((t >= 36.05) & (t < 40))
L += hum; R += hum
add(braam(.5, 32.7, 4), 36.05)
for k in range(8):
    add(tick(.4), 36.05 + k * B / 2, pan=.3 if k % 2 else -.3)
add(whoosh(1.5, .5), 38.5)

# ---------- 40-68: thriller beat ----------
for k in range(int(28 / (B / 4))):  # 16th grid
    at = 40 + k * B / 4
    if at >= 68: break
    s16 = k % 16
    prog = (at - 40) / 28
    if s16 in (0, 6, 10) or (prog > .5 and s16 == 14): add(kick(.95), at)
    if s16 in (4, 12): add(snare(.55 + .2 * prog), at, pan=-.05)
    add(hat(.13 + (.12 if s16 % 4 == 2 else 0) + .08 * prog, .05 if s16 % 4 else .09), at, pan=.35)
    if s16 % 2 == 0: add(tick(.18 + .12 * prog), at + B / 8, pan=-.4)
    if s16 in (0, 3, 6, 8, 11, 14):
        f = [D2, D2, F2, D2, C2, Bb1][[0, 3, 6, 8, 11, 14].index(s16)]
        add(sub_note(f / 2 * 2, B / 2, .34), at)
pulse = np.sin(2 * np.pi * 36.7 * t) * .12 * ((t >= 40) & (t < 68))
L += pulse; R += pulse
for b in [40, 46, 51, 55, 59, 63]:
    add(braam(.6), b - .01); add(boom(.6), b - .01)
    add(whoosh(.7, .35), b - .7)
for g_ in np.sort(rng.uniform(40, 68, 45)): add(glitch(rng.uniform(20, 80)), g_, .18, rng.uniform(-.8, .8))
# extra drama: glitch stutter at the card machine failure
for k in range(10): add(glitch(30), 64.6 + k * .07, .3)

# ---------- 68-72.9: riser + accelerating snare roll ----------
add(braam(.75, 29.1, 4), 68)
rt = 68.0; k = 0
while rt < 72.85:
    gap = np.interp(rt, [68, 72.8], [B / 2, B / 8]); prog = (rt - 68) / 4.85
    add(snare(.15 + .5 * prog), rt); add(kick(.3 + .5 * prog) if k % 2 == 0 else np.zeros(1), rt)
    rt += gap; k += 1
riser = fft_hp(rng.standard_normal(N), 900) * np.clip((t - 68) / 4.9, 0, 1) ** 2 * .35 * ((t >= 68) & (t < 72.9))
sweep = np.sin(2 * np.pi * np.cumsum(np.interp(t, [68, 72.9], [70, 480])) / SR) * .14 * np.clip((t - 68) / 4.9, 0, 1) * ((t >= 68) & (t < 72.9))
L += riser + sweep; R += riser + sweep
add(kick(1.0, 170, 38, .9), 71.6); add(braam(.8, 36.7, 1.4), 71.6)

# ---------- 73.6+: piano note ----------
def piano(f, dur=6.4):
    tt = tt_(dur); x = np.zeros(len(tt))
    for k_, a in enumerate([1, .55, .35, .22, .15, .1, .06], start=1):
        x += a * np.sin(2 * np.pi * f * k_ * np.sqrt(1 + .0004 * k_ * k_) * tt) * np.exp(-tt * (0.6 + .35 * k_))
    return x * np.minimum(1, tt / .004)
add(piano(73.4) * .7 + piano(146.8) * .35 + piano(110) * .2, 73.6, .6)
add(kick(.35, 90, 36, 1.2), 73.6)
sh = sum(np.sin(2 * np.pi * f * t) for f in [880, 1174.7]) * .01 * np.clip((t - 74) / 2, 0, 1) * np.clip((79.8 - t) / 1.5, 0, 1)
L += sh; R += sh

# ---------- reverb ----------
def reverb(x, secs=2.2, mix=.22, seed=1):
    n = int(SR * secs); tt = np.arange(n) / SR
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 3.6); ir[0] = 0; ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << (len(x) + n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return x * (1 - mix) + y * mix * 1.3
L = reverb(L, seed=1); R = reverb(R, seed=2)
def mute(a, b, fade=.015):
    i0, i1 = int(a * SR), int(b * SR); f = int(fade * SR)
    for ch in (L, R): ch[i0:i0 + f] *= np.linspace(1, 0, f); ch[i0 + f:i1] = 0
mute(35.0, 36.0); mute(72.95, 73.6)
fo = np.clip((80 - t) / 1.2, 0, 1); L *= fo; R *= fo
mx = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / mx * 2.0) / np.tanh(2.0) * .9; R = np.tanh(R / mx * 2.0) / np.tanh(2.0) * .9
st = np.empty(N * 2); st[0::2] = L; st[1::2] = R
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
