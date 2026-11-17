"""Mistura voz limpa + trilha (com ducking). Uso: python3 mixar.py 1 -> out/ep01-mix.wav"""
import sys, wave
import numpy as np
ep = int(sys.argv[1]); tag = f'ep{ep:02d}'; SR = 48000
def ler(p):
    with wave.open(p) as w:
        ch = w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.
    return x.reshape(-1, ch)
voz = ler(f'out/{tag}-voz.wav')[:, 0]; bed = ler(f'out/{tag}-trilha.wav'); n = len(bed)
v = np.zeros(n); v[:min(n, len(voz))] = voz[:n]
env = np.convolve(np.abs(v), np.ones(4800) / 4800, 'same')
duck = 1 - 0.6 * np.clip(env / 0.04, 0, 1); duck = np.convolve(duck, np.ones(9600) / 9600, 'same')
mix = bed * 0.45 * duck[:, None] + v[:, None]; mix = mix / np.abs(mix).max() * 0.95
with wave.open(f'out/{tag}-mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', tag)
