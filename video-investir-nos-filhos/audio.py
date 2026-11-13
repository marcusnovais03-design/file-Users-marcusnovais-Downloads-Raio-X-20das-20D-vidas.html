import numpy as np, wave
SR = 48000
SCENES = [('s1', 3.6), ('s2', 3.2), ('s3', 4.0), ('s4', 4.4), ('s5', 3.2),
          ('c0', 6.4), ('c1', 6.4), ('c2', 6.4), ('c3', 6.4), ('c4', 6.4),
          ('s10', 5.6), ('s11', 5.0), ('s12', 5.5)]
ST = {}; t = 0
for n, d in SCENES: ST[n] = t; t += d
TOTAL = t
N = int(TOTAL * SR); tt = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(1)

def lp(x, a):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y

# --- pad: acordes lentos (Am - F - C - G) ---
chords = [[110, 130.81, 164.81], [87.31, 110, 130.81], [65.41, 130.81, 164.81, 196.0], [98.0, 123.47, 146.83]]
seg = 8.0
pad = np.zeros(N); pad2 = np.zeros(N)
for ci in range(int(TOTAL // seg) + 1):
    ch = chords[ci % 4]
    a, b = int(ci * seg * SR), int(min((ci + 1) * seg + 1.5, TOTAL) * SR)
    if a >= N: break
    x = tt[a:b]; env = np.minimum(1, (x - x[0]) / 1.5) * np.minimum(1, (x[-1] - x) / 1.5)
    for f in ch:
        pad[a:b] += env * (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2 * f * x + 1)) * 0.05
        pad2[a:b] += env * (np.sin(2 * np.pi * f * 1.003 * x) + 0.3 * np.sin(2 * np.pi * 2.01 * f * x)) * 0.05
trem = 0.8 + 0.2 * np.sin(2 * np.pi * 0.15 * tt)
L += pad * trem; R += pad2 * trem
# sub pulso (batida de coração) nos gráficos
for k in range(5):
    s0 = ST[f'c{k}']
    for b in np.arange(s0, s0 + 6.4, 0.8):
        i = int(b * SR); n = int(0.35 * SR); x = np.arange(n) / SR
        th = 0.25 * np.sin(2 * np.pi * 55 * x) * np.exp(-x / 0.09)
        L[i:i + n] += th[:N - i]; R[i:i + n] += th[:N - i]

# --- whoosh nas transições ---
noise = rng.normal(0, 1, int(0.6 * SR))
wh = lp(noise, 0.08); wh = wh / np.abs(wh).max()
for n, d in SCENES[1:]:
    i = int((ST[n] - 0.35) * SR); x = np.arange(len(wh)) / SR
    env = np.exp(-((x - 0.35) / 0.12) ** 2) * 0.35
    seg_ = wh * env
    L[i:i + len(seg_)] += seg_ * 0.9; R[i:i + len(seg_)] += seg_[::-1] * 0.0 + seg_ * 1.0

# --- boom nos impactos ---
HITS = [ST['s2'] + 0.45, ST['s3'] + 2.55, ST['s4'] + 2.75, ST['s10'] + 0.55,
        ST['s11'] + 3.6, ST['s12'] + 0.55] + [ST[f'c{k}'] + 4.6 for k in range(5)]
for h in HITS:
    i = int(h * SR); n = int(1.4 * SR); x = np.arange(n) / SR
    f = 62 * np.exp(-x / 0.5) + 32
    ph = 2 * np.pi * np.cumsum(f) / SR
    b = 0.65 * np.sin(ph) * np.exp(-x / 0.45)
    click = np.zeros(n); click[:400] = rng.normal(0, 1, 400) * np.exp(-np.arange(400) / 60) * 0.25
    s = (b + click)[:N - i]
    L[i:i + len(s)] += s; R[i:i + len(s)] += s

# --- tique-taque do relógio (cena do TEMPO) ---
for b in np.arange(ST['s3'] + 0.1, ST['s3'] + 2.5, 0.42):
    i = int(b * SR); n = 900
    c = rng.normal(0, 1, n) * np.exp(-np.arange(n) / 120) * 0.18
    c = c - lp(c, 0.3)
    L[i:i + n] += c; R[i:i + n] += c

# fade in/out e normaliza
fade = np.minimum(1, tt / 0.5) * np.minimum(1, (TOTAL - tt) / 1.2)
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
g = 0.5 / peak       # pico em -6 dB, deixando espaço para a voz
st = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
with wave.open('trilha.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok', TOTAL)
