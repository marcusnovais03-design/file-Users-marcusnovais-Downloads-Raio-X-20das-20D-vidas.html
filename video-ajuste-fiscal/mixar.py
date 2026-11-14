"""Trilha suave (pad sintetizado) + narração -> mix.wav. Uso: python3 mixar.py <dir_saida>"""
import sys, json, numpy as np, soundfile as sf
OUT = sys.argv[1]; SR = 48000
v, _ = sf.read(f'{OUT}/voz.wav'); N = len(v); tt = np.arange(N) / SR; TOTAL = N / SR
tl = json.load(open(f'{OUT}/timeline.json'))
chords = [[130.81, 164.81, 196.0, 246.94], [110.0, 130.81, 164.81, 196.0], [87.31, 130.81, 174.61, 220.0], [98.0, 123.47, 146.83, 196.0]]
L = np.zeros(N); R = np.zeros(N); seg = 7.0
for ci in range(int(TOTAL // seg) + 1):
    a, b = int(ci * seg * SR), int(min((ci + 1) * seg + 2.0, TOTAL) * SR)
    if a >= N: break
    x = tt[a:b]; env = np.minimum(1, (x - x[0]) / 2.0) * np.minimum(1, (x[-1] - x) / 2.0)
    for f in chords[ci % 4]:
        L[a:b] += env * (np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x + 1))
        R[a:b] += env * (np.sin(2 * np.pi * f * 1.004 * x) + 0.25 * np.sin(4.02 * np.pi * f * x))
# notas de 'piano elétrico' discretas na troca de capítulo
rng = np.random.default_rng(2); seen = set()
for f in tl['falas']:
    if f['cap'] in seen: continue
    seen.add(f['cap']); i = int(max(0, f['t0'] - 0.4) * SR); n = int(2.5 * SR); x = np.arange(n) / SR
    for k, fr in enumerate((523.25, 659.25, 783.99)):
        j = i + int(k * 0.09 * SR); s = 1.6 * np.sin(2 * np.pi * fr * x) * np.exp(-x / 0.6) * np.minimum(1, x / 0.005)
        m = min(n, N - j); L[j:j + m] += s[:m]; R[j:j + m] += s[:m]
bed = np.stack([L, R], 1); bed *= (np.minimum(1, tt / 1.0) * np.minimum(1, (TOTAL - tt) / 2.0))[:, None]
bed = bed / np.abs(bed).max()
env = np.convolve(np.abs(v), np.ones(4800) / 4800, 'same')
duck = np.convolve(1 - 0.5 * np.clip(env / 0.05, 0, 1), np.ones(9600) / 9600, 'same')
mix = bed * 0.16 * duck[:, None] + v[:, None]
sf.write(f'{OUT}/mix.wav', mix / np.abs(mix).max() * 0.95, SR)
print('ok', TOTAL)
