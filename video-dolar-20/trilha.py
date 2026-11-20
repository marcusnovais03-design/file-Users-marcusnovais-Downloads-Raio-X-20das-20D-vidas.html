"""Trilha de fundo de um episódio. Uso: python3 trilha.py 3  -> out/ep03-trilha.wav (lê out/ep03-cenas.json)."""
import json, sys, wave
import numpy as np
ep = int(sys.argv[1]); tag = f'ep{ep:02d}'
cenas = json.load(open(f'out/{tag}-cenas.json'))
SR = 48000; TOTAL = cenas[-1]['e']
N = int(TOTAL * SR); t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(ep)

def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def add(i, s):
    s = s[:max(0, N - i)]; L[i:i+len(s)] += s; R[i:i+len(s)] += s

# progressão leve e positiva (C - G - Am - F), um tom diferente por episódio
base = [0, 2, -3, 5, -1, 3, -2, 4][ep - 1]
semi = lambda f, k: f * 2 ** (k / 12)
PROG = [[130.81, 164.81, 196.0], [98.0, 123.47, 146.83], [110.0, 130.81, 164.81], [87.31, 110.0, 130.81]]
seg = 4.0
for k in range(int(TOTAL // seg) + 1):
    a0 = k * seg
    if a0 >= TOTAL: break
    i0, i1 = int(a0 * SR), int(min(a0 + seg + 1.0, TOTAL) * SR)
    x = t[i0:i1]; env = np.minimum(1, (x - x[0]) / .8) * np.minimum(1, (x[-1] - x) / .8)
    for f in PROG[k % 4]:
        f = semi(f, base)
        L[i0:i1] += env * (np.sin(2*np.pi*f*x) + .2*np.sin(4*np.pi*f*x)) * .04
        R[i0:i1] += env * (np.sin(2*np.pi*f*1.003*x) + .2*np.sin(4*np.pi*f*1.002*x)) * .04
    # dedilhado em colcheias (~112 bpm)
    notas = [semi(f * 2, base) for f in PROG[k % 4]]
    for j, b in enumerate(np.arange(a0, min(a0 + seg, TOTAL), 60 / 112 / 2)):
        f = notas[j % 3] * (2 if j % 4 == 3 else 1); n = int(.35 * SR); xx = np.arange(n) / SR
        add(int(b * SR), .05 * np.sin(2*np.pi*f*xx) * np.exp(-xx / .09))
# batida suave
for b in np.arange(0.1, TOTAL - 1, 60 / 112):
    n = int(.25 * SR); xx = np.arange(n) / SR
    add(int(b * SR), .22 * np.sin(2*np.pi*(50 + 40*np.exp(-xx/.03))*xx) * np.exp(-xx / .07))
# whoosh nas trocas de cena
wh = lp(rng.normal(0, 1, int(.7 * SR)), .07); wh /= np.abs(wh).max(); xx = np.arange(len(wh)) / SR
for c in cenas[1:]:
    add(int((c['s'] - .4) * SR), wh * np.exp(-((xx - .4) / .13) ** 2) * .28)
# impacto na entrada do título e nos gráficos
def boom(at, amp=.5):
    n = int(1.1 * SR); xx = np.arange(n) / SR; f = 60 * np.exp(-xx / .45) + 34
    add(int(at * SR), amp * np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-xx / .4))
for c in cenas:
    if c['t'] == 'title': boom(c['s'] + .35)
    if c['t'] in ('hook',): boom(c['s'] + .5, .4)
    if c['t'] in ('bars', 'curve', 'coupons', 'annuity', 'mtm', 'iof'): boom(c['s'] + .9, .35)
fade = np.minimum(1, t / .3) * np.minimum(1, (TOTAL - t) / 1.5)
L *= fade; R *= fade
g = .5 / max(np.abs(L).max(), np.abs(R).max())
with wave.open(f'out/{tag}-trilha.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, R], 1) * g * 32767).astype(np.int16).tobytes())
print('ok', tag, TOTAL)
