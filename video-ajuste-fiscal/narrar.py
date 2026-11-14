"""Gera a narração (Kokoro TTS, pt-br) e a linha do tempo. Uso: python3 narrar.py <dir_modelos> <dir_saida>"""
import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from roteiro import FALAS
M, OUT = sys.argv[1], sys.argv[2]
VOZ, VEL, SR = 'pm_alex', 1.0, 48000
k = Kokoro(f'{M}/kokoro-v1.0.onnx', f'{M}/voices-v1.0.bin')
def trim(a, sr):
    idx = np.where(np.abs(a) > 0.01 * np.abs(a).max())[0]
    return a[max(idx[0] - int(0.02 * sr), 0): idx[-1] + int(0.10 * sr)]
t = 0.5; tl = []; clips = []; prev = 0
for fid, cap, txt, _ in FALAS:
    a, sr = k.create(txt, voice=VOZ, speed=VEL, lang='pt-br'); a = trim(a, sr)
    x = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    if cap != prev: t += 0.55          # respiro na troca de capítulo
    prev = cap
    tl.append({'id': fid, 'cap': cap, 't0': round(t, 3), 't1': round(t + len(x) / SR, 3)}); clips.append((t, x))
    print(f'{t:6.2f} {len(x)/SR:5.2f}s  {txt}')
    t += len(x) / SR + 0.32
total = t + 2.6
v = np.zeros(int(total * SR))
for t0, x in clips: i = int(t0 * SR); v[i:i + len(x)] += x
v = v / np.abs(v).max() * 0.89
sf.write(f'{OUT}/voz.wav', v, SR)
json.dump({'total': round(total, 3), 'falas': tl}, open(f'{OUT}/timeline.json', 'w'), indent=1)
print('total', total)
