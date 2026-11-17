"""Limpa a voz gravada e mistura com a trilha.

Uso: python3 mixar.py caminho/da/voz.m4a
Gera out/voz-limpa.wav e out/mix-final.wav (voz + trilha com ducking).
"""
import subprocess, sys, wave
import numpy as np

SR = 48000
OFFSET = 1.1   # segundos cortados do começo da gravação (silêncio antes da primeira fala)
VOZ = sys.argv[1]

# 1) limpeza: corta graves de manuseio, reduz ruído de fundo, dá presença, comprime e normaliza para -16 LUFS
FILTRO = ('highpass=f=80,lowpass=f=14000,'
          'afftdn=nr=20:nf=-50:tn=1,'
          'agate=threshold=0.012:ratio=4:range=0.06:attack=4:release=180:knee=3,'
          'equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3800:t=q:w=1.4:g=2.5,'
          'acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,'
          'loudnorm=I=-16:TP=-1.5:LRA=9')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(OFFSET), '-i', VOZ, '-ac', '1', '-ar', str(SR),
                '-af', FILTRO, 'out/voz-limpa.wav'], check=True)

def ler(p):
    with wave.open(p) as w:
        ch = w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.
    return x.reshape(-1, ch)

voz = ler('out/voz-limpa.wav')[:, 0]
bed = ler('out/trilha.wav')
n = len(bed)
v = np.zeros(n); v[:min(n, len(voz))] = voz[:n]

# 2) ducking: a trilha abaixa enquanto a voz fala
env = np.convolve(np.abs(v), np.ones(4800) / 4800, 'same')
duck = 1 - 0.6 * np.clip(env / 0.04, 0, 1)
duck = np.convolve(duck, np.ones(9600) / 9600, 'same')
mix = bed * 0.5 * duck[:, None] + v[:, None]
mix = mix / np.abs(mix).max() * 0.95
with wave.open('out/mix-final.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', round(n / SR, 2), 's')
