#!/usr/bin/env python3
"""Gera a narração (Kokoro, voz pm_alex) e a timeline que sincroniza a animação.
Uso: python3 narrar.py <dir com kokoro-v1.0.onnx e voices-v1.0.bin> <dir de saída>"""
import sys, json, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

MODELS, OUT = sys.argv[1], sys.argv[2]
k = Kokoro(f'{MODELS}/kokoro-v1.0.onnx', f'{MODELS}/voices-v1.0.bin')
VOICE, SPEED, SR = 'pm_alex', 1.12, 48000

from roteiro import ROTEIRO, WIN, LEAD, GAP, TAIL

def trim(a, sr):
    th = 0.012 * np.abs(a).max(); idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0] - int(0.02 * sr), 0): idx[-1] + int(0.09 * sr)]

clips, seg, scenes, t = [], {}, {}, 0.0
for name, falas in ROTEIRO:
    s0 = t; t += LEAD
    for sid, txt, leg in falas:
        a, sr = k.create(txt, voice=VOICE, speed=SPEED, lang='pt-br')
        a = trim(a, sr)
        x = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
        d = len(x) / SR
        seg[sid] = {'s': round(t, 3), 'e': round(t + d, 3), 'cap': leg}
        clips.append((t, x)); t += d + GAP
    end = t - GAP + TAIL
    sc = {'s': round(s0, 3)}
    if name in WIN:
        ref, side, off = WIN[name]
        sc['win'] = round(seg[ref][side] + off, 3)
        end = max(end, sc['win'] + 1.5)
    if name == 'cta': end += 1.3
    sc['e'] = round(end, 3); scenes[name] = sc; t = end
TOTAL = round(t, 3)

voice = np.zeros(int(TOTAL * SR) + SR)
for st, x in clips:
    i = int(st * SR); voice[i:i + len(x)] += x
voice = voice[:int(TOTAL * SR)]
voice = voice / np.abs(voice).max() * 0.89
os.makedirs(OUT, exist_ok=True)
sf.write(f'{OUT}/narracao.wav', voice, SR)
json.dump({'total': TOTAL, 'seg': seg, 'scenes': scenes}, open(f'{OUT}/timeline.json', 'w'), ensure_ascii=False, indent=1)

def ts(x):
    ms = int(round(x * 1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
with open(f'{OUT}/narracao.srt', 'w') as f:
    for n, (sid, v) in enumerate(seg.items(), 1):
        f.write(f"{n}\n{ts(v['s'])} --> {ts(v['e'])}\n{v['cap']}\n\n")
print('total', TOTAL); print(json.dumps(scenes))
