import numpy as np, wave, sys
SR = 44100; DUR = 80.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def env(a, b, fi=.5, fo=.5):
    e = np.zeros(N); i0, i1 = int(a * SR), int(b * SR)
    seg = np.arange(i1 - i0) / SR; d = b - a
    e[i0:i1] = np.minimum(1, np.minimum(seg / max(fi, 1e-4), (d - seg) / max(fo, 1e-4)))
    return np.clip(e, 0, 1)

def lowpass(x, a):  # one-pole
    y = np.empty_like(x); acc = 0.0
    # vectorised via cumulative approach is complex; use FFT filter instead
    return x

def fft_lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))

def fft_hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))

def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); n = min(len(sig), N - i)
    if n <= 0: return
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan)); R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))

def saw(f, tt, harm=8):
    return sum(np.sin(2 * np.pi * f * k * tt) / k for k in range(1, harm + 1))

# ---------- 0-35: ancient war bed ----------
e = env(0, 35, 2.5, .02)
drone = (np.sin(2 * np.pi * 55 * t) + .6 * np.sin(2 * np.pi * 82.4 * t + 1) + .4 * np.sin(2 * np.pi * 110.3 * t)) * (0.6 + .4 * np.sin(2 * np.pi * .13 * t))
rumble = fft_lp(rng.standard_normal(N), 90) * 3
grow = np.clip(t / 35, 0, 1)
bed = (drone * .22 + rumble * .25) * e * (.5 + .5 * grow)
L += bed; R += bed
# tremolo strings (A minor cluster), crescendo, slight upward drift
for f, pan in [(220, -.4), (261.6, .3), (329.6, -.2), (440, .4), (493.9, 0)]:
    drift = 1 + .03 * np.clip((t - 10) / 25, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * drift) / SR
    s = sum(np.sin(ph * k) / k for k in range(1, 6))
    trem = .55 + .45 * np.sin(2 * np.pi * 7.5 * t + f)
    ee = env(6, 35, 4, .02) * np.clip((t - 6) / 29, 0, 1) ** 1.6
    sig = s * trem * ee * .06
    L += sig * (1 - max(0, pan)); R += sig * (1 + min(0, pan))
# war drums
def drum(strength=1.0, f0=70):
    n = int(SR * 1.6); tt = np.arange(n) / SR
    f = f0 * np.exp(-tt * 6) + 38
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 4.5)
    click = fft_lp(rng.standard_normal(n), 900)[:n] * np.exp(-tt * 40) * .6 if False else rng.standard_normal(n) * np.exp(-tt * 35) * .25
    return (body + click) * strength
for b in [5, 10, 15, 20, 25, 30]:
    add(drum(1.0), b - .02, .9)
    add(drum(.5, 90), b + 1.25, .5, -.3); add(drum(.5, 90), b + 2.5, .55, .3); add(drum(.4, 100), b + 3.75, .5)
for b in np.arange(20, 35, .625):  # faster pulse in modern wars
    add(drum(.25, 110), b, .5)
# explosions (WWI/WWII)
def boom(dur=2.2, g=1.0):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = rng.standard_normal(n); x = fft_lp(x, 300) * 6
    sub = np.sin(2 * np.pi * np.cumsum(60 * np.exp(-tt * 2) + 25) / SR)
    return (x * .5 + sub) * np.exp(-tt * 2.6) * g
for b in [21.2, 22.6, 23.9, 26.1, 27.8, 29.0]: add(boom(), b, .45, rng.uniform(-.5, .5))

# ---------- 35-36 silence (hard cut) ----------
# ---------- 36-40: electric hum + glitches ----------
e2 = env(36, 40, .05, .1)
hum = (np.sin(2 * np.pi * 60 * t) + .5 * np.sin(2 * np.pi * 120 * t) + .3 * np.sin(2 * np.pi * 180 * t)) * .12
L += hum * e2; R += hum * e2
whoosh = fft_hp(rng.standard_normal(N), 1500) * .25 * env(36, 40, 3.5, .05) * np.clip((t - 36) / 4, 0, 1)
L += whoosh; R += whoosh
def glitch(n_ms=60):
    n = int(SR * n_ms / 1000); x = np.sign(np.sin(2 * np.pi * rng.uniform(200, 2000) * np.arange(n) / SR)) * .3
    return x * (rng.random(n) > .3)
for g in np.sort(rng.uniform(36, 68, 70)): add(glitch(rng.uniform(20, 90)), g, .25, rng.uniform(-.8, .8))

# ---------- 40-68: ticking clock + heartbeat + impacts ----------
tick_t = 40.0
while tick_t < 68:
    n = int(SR * .03); tt = np.arange(n) / SR
    tk = np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 300) + rng.standard_normal(n) * np.exp(-tt * 400) * .3
    add(tk, tick_t, .35, .3 if int(tick_t * 10) % 2 else -.3)
    tick_t += np.interp(tick_t, [40, 68], [.5, .2])
hb = 40.2
while hb < 68:
    n = int(SR * .4); tt = np.arange(n) / SR
    thump = np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 14)
    add(thump, hb, .9); add(thump * .7, hb + .22, .9)
    hb += np.interp(hb, [40, 68], [.95, .6])
pulse = np.sin(2 * np.pi * 41 * t) * (.5 + .5 * np.sin(2 * np.pi * .5 * t)) * .18 * env(40, 68, 1, .05)
L += pulse; R += pulse
for b in [40, 46, 51, 55, 59, 63]:
    add(boom(2.6, 1.0), b - .01, .9)
    n = int(SR * .5); tt = np.arange(n) / SR
    add(fft_hp(rng.standard_normal(n), 3000) * np.exp(-tt * 10) * .5, b, .6)

# ---------- 68-72.9: riser to the question ----------
e3 = env(68, 72.9, .1, .01)
ris = fft_hp(rng.standard_normal(N), 800) * np.clip((t - 68) / 4.9, 0, 1) ** 2 * .45
sweep = np.sin(2 * np.pi * np.cumsum(np.interp(t, [68, 72.9], [80, 420])) / SR) * .18 * np.clip((t - 68) / 4.9, 0, 1)
strings2 = sum(np.sin(2 * np.pi * f * t) for f in [220, 233.1, 329.6]) * .05 * (.5 + .5 * np.sin(2 * np.pi * 11 * t))
L += (ris + sweep + strings2) * e3; R += (ris + sweep + strings2) * e3
add(boom(2.0, 1.0), 68, .8)
add(drum(1.0, 60), 71.6, 1.0)

# ---------- 73.6+: single piano note with long reverb ----------
def piano(f, dur=6.5):
    n = int(SR * dur); tt = np.arange(n) / SR
    x = np.zeros(n)
    for k, a in enumerate([1, .55, .35, .22, .15, .1, .06], start=1):
        fk = f * k * np.sqrt(1 + .0004 * k * k)
        x += a * np.sin(2 * np.pi * fk * tt) * np.exp(-tt * (0.6 + .35 * k))
    x *= np.minimum(1, tt / .004)
    return x
note = piano(110) * .7 + piano(220) * .35 + piano(164.8) * .2
add(note, 73.6, .55)
shimmer = sum(np.sin(2 * np.pi * f * t) for f in [880, 1318.5]) * .012 * env(74, 79.8, 2, 1.5)
L += shimmer; R += shimmer

# ---------- reverb (FFT convolution with noise IR) ----------
def reverb(x, secs=2.8, mix=.28, seed=1):
    n = int(SR * secs); tt = np.arange(n) / SR
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-tt * 3.2); ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n; size = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return x * (1 - mix) + y * mix * 1.4
L = reverb(L, seed=1); R = reverb(R, seed=2)

# enforce hard silences after reverb (dramatic cuts)
def mute(a, b, fade=.02):
    i0, i1 = int(a * SR), int(b * SR); f = int(fade * SR)
    for ch in (L, R):
        ch[i0:i0 + f] *= np.linspace(1, 0, f); ch[i0 + f:i1] = 0
mute(35.0, 36.0); mute(72.95, 73.6)
fo = np.clip((80 - t) / 1.2, 0, 1); L *= fo; R *= fo
fi = np.clip(t / .3, 0, 1); L *= fi; R *= fi

# soft-clip + normalise
mx = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / mx * 1.6) / np.tanh(1.6) * .89; R = np.tanh(R / mx * 1.6) / np.tanh(1.6) * .89
st = np.empty(N * 2); st[0::2] = L; st[1::2] = R
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok')
