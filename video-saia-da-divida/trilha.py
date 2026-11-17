"""Trilha de fundo do Reels (sem voz). Gera trilha.wav com a duração da linha do tempo de reels.html."""
import numpy as np, wave
SR = 48000
CENAS = [('s1', 0), ('s2', 4.5), ('s3', 10), ('s4', 14), ('s5', 20.5), ('s6', 28.5), ('s7', 38.5), ('s8', 45.5), ('s9', 52)]
TOTAL = 59.0
N = int(TOTAL * SR); t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(7)

def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y

# pad tenso (Dm - Bb - Gm - A) até a virada; depois maior (F - C - Bb - C) a partir de "dívida tem saída"
TENSO = [[73.42, 146.83, 174.61, 220.0], [58.27, 116.54, 146.83, 174.61], [49.0, 98.0, 116.54, 146.83], [55.0, 110.0, 138.59, 164.81]]
CLARO = [[87.31, 174.61, 220.0, 261.63], [65.41, 130.81, 164.81, 196.0], [58.27, 116.54, 146.83, 174.61], [65.41, 130.81, 164.81, 196.0]]
VIRADA = 45.5
seg = 4.0
for k in range(int(TOTAL // seg) + 1):
    a0 = k * seg
    if a0 >= TOTAL: break
    ch = (CLARO if a0 >= VIRADA else TENSO)[k % 4]
    i0, i1 = int(a0 * SR), int(min(a0 + seg + 1.2, TOTAL) * SR)
    x = t[i0:i1]; env = np.minimum(1, (x - x[0]) / 1.0) * np.minimum(1, (x[-1] - x) / 1.0)
    for f in ch:
        L[i0:i1] += env * (np.sin(2*np.pi*f*x) + .25*np.sin(4*np.pi*f*x + 1)) * .045
        R[i0:i1] += env * (np.sin(2*np.pi*f*1.003*x) + .25*np.sin(4*np.pi*f*1.002*x)) * .045

# batida de coração nas cenas de tensão (até a virada), acelerando no ciclo
def thump(at, amp=.28):
    i = int(at * SR); n = int(.3 * SR); x = np.arange(n) / SR
    s = amp * np.sin(2*np.pi*52*x) * np.exp(-x / .08); s = s[:N - i]
    L[i:i+len(s)] += s; R[i:i+len(s)] += s
b = 0.4
while b < VIRADA - .5:
    gap = 0.95 if not (20.5 <= b < 28.5) else 0.72
    thump(b); thump(b + .22, .18); b += gap

# whoosh nas trocas de cena
wh = lp(rng.normal(0, 1, int(.7 * SR)), .07); wh /= np.abs(wh).max()
for _, s in CENAS[1:]:
    i = int((s - .4) * SR); x = np.arange(len(wh)) / SR
    w = wh * np.exp(-((x - .4) / .13) ** 2) * .3; w = w[:N - i]
    L[i:i+len(w)] += w; R[i:i+len(w)] += w

# impactos: casas, carimbo RECORDE, barras dos juros, valor final da curva, botão do CTA
def boom(at, amp=.6):
    i = int(at * SR); n = int(1.2 * SR); x = np.arange(n) / SR
    f = 60 * np.exp(-x / .45) + 34; s = amp * np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-x / .4); s = s[:N - i]
    L[i:i+len(s)] += s; R[i:i+len(s)] += s
for h in [0.15, 4.5 + 3.2, 10 + 1.6, 28.5 + 2.0, 28.5 + 4.2, 28.5 + 6.6, 38.5 + 4.4, 45.6, 52 + 2.6]:
    boom(h)
# "plim" nos checks
for k in range(3):
    i = int((45.5 + 1.4 + k * .9) * SR); n = int(.5 * SR); x = np.arange(n) / SR
    s = .12 * (np.sin(2*np.pi*1046.5*x) + .5*np.sin(2*np.pi*1568*x)) * np.exp(-x / .12); s = s[:N - i]
    L[i:i+len(s)] += s; R[i:i+len(s)] += s

fade = np.minimum(1, t / .4) * np.minimum(1, (TOTAL - t) / 1.5)
L *= fade; R *= fade
g = .5 / max(np.abs(L).max(), np.abs(R).max())
st = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
with wave.open('out/trilha.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok', TOTAL)
