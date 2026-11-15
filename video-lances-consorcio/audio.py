#!/usr/bin/env python3
"""Trilha (sintetizada) + mixagem com a narração. Uso: python3 audio.py <dir com narracao.wav e timeline.json>"""
import sys, json, numpy as np, soundfile as sf
D = sys.argv[1]; TL = json.load(open(f'{D}/timeline.json')); SR = 48000
TOTAL = TL['total']; N = int(TOTAL * SR); tt = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(3)
def add(buf, t0, x, gain=1.0):
    i = int(t0 * SR)
    if i < 0 or i >= N: return
    x = x[:N - i]; buf[i:i + len(x)] += x * gain
BPM = 126; beat = 60 / BPM
# acordes (Am F C G), um por compasso
chords = [[220, 261.63, 329.63], [174.61, 220, 261.63], [196, 261.63, 329.63], [196, 246.94, 293.66]]
bar = beat * 4
for b in range(int(TOTAL / bar) + 1):
    ch = chords[b % 4]; n = int((bar + 0.3) * SR); x = np.arange(n) / SR
    env = np.minimum(1, x / 0.25) * np.minimum(1, (x[-1] - x) / 0.3)
    for k, f in enumerate(ch):
        add(L, b * bar, env * np.sin(2 * np.pi * f * x) * 0.035); add(R, b * bar, env * np.sin(2 * np.pi * f * 1.004 * x + k) * 0.035)
    # baixo pulsando em colcheias
    for e in range(8):
        n2 = int(beat / 2 * SR); y = np.arange(n2) / SR
        s = np.sin(2 * np.pi * ch[0] / 2 * y) * np.exp(-y / 0.16) * 0.11
        add(L, b * bar + e * beat / 2, s); add(R, b * bar + e * beat / 2, s)
# bumbo + chimbal (passos da corrida)
n = int(0.3 * SR); y = np.arange(n) / SR
kick = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-y / 0.03)) / SR) * np.exp(-y / 0.11) * 0.30
hn = int(0.05 * SR); hat = np.diff(rng.normal(0, 1, hn + 1)) * np.exp(-np.arange(hn) / SR / 0.012) * 0.03
for i in range(int(TOTAL / beat) + 1):
    add(L, i * beat, kick); add(R, i * beat, kick)
    add(L, i * beat + beat / 2, hat, 0.8); add(R, i * beat + beat / 2, hat, 1.0)
# whoosh nas trocas de cena
wn = int(0.7 * SR); w = rng.normal(0, 1, wn); w = np.cumsum(w); w -= np.convolve(w, np.ones(400) / 400, 'same'); w /= np.abs(w).max()
wy = np.arange(wn) / SR; w *= np.exp(-((wy - 0.35) / 0.13) ** 2) * 0.22
for k, sc in TL['scenes'].items():
    if sc['s'] > 0: add(L, sc['s'] - 0.35, w); add(R, sc['s'] - 0.33, w)
# sininho de contemplação
for sc in TL['scenes'].values():
    if 'win' in sc:
        for j, f in enumerate([659.25, 783.99, 1046.5, 1318.5]):
            n3 = int(1.2 * SR); y = np.arange(n3) / SR
            s = (np.sin(2 * np.pi * f * y) + 0.4 * np.sin(2 * np.pi * 2 * f * y)) * np.exp(-y / 0.3) * 0.10
            add(L, sc['win'] + j * 0.085, s); add(R, sc['win'] + j * 0.085 + 0.004, s)
fade = np.minimum(1, tt / 0.4) * np.minimum(1, (TOTAL - tt) / 1.0)
bed = np.stack([L, R], 1) * fade[:, None]; bed = bed / np.abs(bed).max() * 0.5
voice, _ = sf.read(f'{D}/narracao.wav'); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
env = np.convolve(np.abs(voice), np.ones(4800) / 4800, 'same')
duck = 1 - 0.6 * np.clip(env / 0.05, 0, 1); duck = np.convolve(duck, np.ones(9600) / 9600, 'same')
mix = bed * 0.5 * duck[:, None] + voice[:, None]; mix = mix / np.abs(mix).max() * 0.95
sf.write(f'{D}/trilha.wav', bed, SR); sf.write(f'{D}/mix.wav', mix, SR); print('ok', TOTAL)
