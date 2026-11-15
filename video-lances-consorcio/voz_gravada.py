#!/usr/bin/env python3
"""Usa uma gravação de voz (uma tomada, frases na ordem do roteiro) no lugar da voz sintética.
Corta a gravação nas pausas, mantém o ritmo natural dentro de cada cena e abre espaço entre as cenas
para a animação. Gera narracao.wav, timeline.json e narracao.srt no mesmo formato do narrar.py.
Uso: python3 voz_gravada.py <gravacao.wav mono 48k> <dir de saída> <trechos por frase, ex. 1,2,2,1,...>"""
import sys, json, os, subprocess, numpy as np, soundfile as sf
from roteiro import ROTEIRO, WIN, LEAD, TAIL
WAV, OUT, MAPA = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
SR = 48000
# limpeza leve: corta graves, reduz chiado, nivela o volume
tmp = f'{OUT}/_voz_limpa.wav'; os.makedirs(OUT, exist_ok=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', WAV, '-ac', '1', '-ar', str(SR), '-af',
                'highpass=f=85,afftdn=nr=8:nf=-45,acompressor=threshold=-20dB:ratio=3:attack=8:release=160:makeup=3', tmp], check=True)
x, sr = sf.read(tmp); assert sr == SR
raw, _ = sf.read(WAV); raw = raw if raw.ndim == 1 else raw.mean(1)
hop = int(0.01 * SR); n = len(raw) // hop
db = 20 * np.log10(np.sqrt((raw[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9); on = db > -38
segs, i = [], 0
while i < n:
    if on[i]:
        j = i
        while j < n and on[j]: j += 1
        segs.append([i, j]); i = j
    else: i += 1
m = []
for s in segs:
    if m and s[0] - m[-1][1] < 22: m[-1][1] = s[1]
    else: m.append(s)
m = [(a * 0.01, b * 0.01) for a, b in m if b - a >= 12]
ids = [(sid, leg) for _, falas in ROTEIRO for sid, _, leg in falas]
assert sum(MAPA) == len(m) and len(MAPA) == len(ids), (sum(MAPA), len(m), len(MAPA), len(ids))
rec, k = {}, 0
for (sid, leg), c in zip(ids, MAPA): rec[sid] = (m[k][0], m[k + c - 1][1]); k += c

seg, scenes, clips, t = {}, {}, [], 0.0
for name, falas in ROTEIRO:
    s0 = t; r0 = rec[falas[0][0]][0] - 0.06; r1 = rec[falas[-1][0]][1] + 0.16; off = s0 + LEAD - r0
    y = x[int(r0 * SR):int(r1 * SR)].copy(); f = int(0.04 * SR)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f); clips.append((s0 + LEAD, y))
    for sid, _, leg in falas: seg[sid] = {'s': round(rec[sid][0] + off, 3), 'e': round(rec[sid][1] + off, 3), 'cap': leg}
    end = seg[falas[-1][0]]['e'] + TAIL; sc = {'s': round(s0, 3)}
    if name in WIN:
        ref, side, d = WIN[name]; sc['win'] = round(seg[ref][side] + d, 3); end = max(end, sc['win'] + 1.5)
    if name == 'cta': end += 1.3
    sc['e'] = round(end, 3); scenes[name] = sc; t = end
TOTAL = round(t, 3)
voice = np.zeros(int(TOTAL * SR) + SR)
for st, y in clips: i = int(st * SR); voice[i:i + len(y)] += y
voice = voice[:int(TOTAL * SR)]; voice = voice / np.abs(voice).max() * 0.89
sf.write(f'{OUT}/narracao.wav', voice, SR); os.remove(tmp)
json.dump({'total': TOTAL, 'seg': seg, 'scenes': scenes}, open(f'{OUT}/timeline.json', 'w'), ensure_ascii=False, indent=1)
def ts(v):
    ms = int(round(v * 1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
with open(f'{OUT}/narracao.srt', 'w') as fh:
    for nn, (sid, v) in enumerate(seg.items(), 1): fh.write(f"{nn}\n{ts(v['s'])} --> {ts(v['e'])}\n{v['cap']}\n\n")
print('total', TOTAL); print(json.dumps(scenes))
