#!/usr/bin/env python3
"""Gera a narração (Kokoro, voz pm_alex) e a timeline que sincroniza a animação.
Uso: python3 narrar.py <dir com kokoro-v1.0.onnx e voices-v1.0.bin> <dir de saída>"""
import sys, json, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

MODELS, OUT = sys.argv[1], sys.argv[2]
k = Kokoro(f'{MODELS}/kokoro-v1.0.onnx', f'{MODELS}/voices-v1.0.bin')
VOICE, SPEED, SR = 'pm_alex', 1.12, 48000

# cena -> [(id, texto falado, legenda)]
ROTEIRO = [
 ('intro', [
  ('i1', 'Todo mês, tem gente cruzando a linha de chegada do consórcio, com a carta de crédito na mão.',
         'Todo mês, tem gente cruzando a linha de chegada do consórcio, com a carta de crédito na mão.'),
  ('i2', 'Mas existem quatro pistas pra chegar lá. E em uma delas, a concorrência é bem menor.',
         'Mas existem 4 pistas pra chegar lá. E em uma delas, a concorrência é bem menor.')]),
 ('sorteio', [
  ('s1', 'Pista um: o sorteio.', 'Pista 1: o sorteio.'),
  ('s2', 'Aqui, você não paga nada a mais.', 'Aqui, você não paga nada a mais.'),
  ('s3', 'Todo mundo com a parcela em dia concorre, com a mesma chance.',
         'Todo mundo com a parcela em dia concorre, com a mesma chance.'),
  ('s4', 'É pura sorte.', 'É pura sorte.')]),
 ('livre', [
  ('l1', 'Pista dois: o lance livre.', 'Pista 2: o lance livre.'),
  ('l2', 'Funciona como um leilão.', 'Funciona como um leilão.'),
  ('l3', 'Você oferta o percentual da carta que quiser, e leva quem der o maior lance.',
         'Você oferta o percentual da carta que quiser, e leva quem der o maior lance.'),
  ('l4', 'Por isso, costuma ser a pista mais disputada.', 'Por isso, costuma ser a pista mais disputada.')]),
 ('fixo', [
  ('f1', 'Pista três: o lance fixo.', 'Pista 3: o lance fixo.'),
  ('f2', 'O percentual já vem definido pela administradora.', 'O percentual já vem definido pela administradora.'),
  ('f3', 'Por exemplo, trinta por cento.', 'Por exemplo, 30%.'),
  ('f4', 'Todo mundo oferta o mesmo valor, e o desempate é por sorteio.',
         'Todo mundo oferta o mesmo valor, e o desempate é por sorteio.')]),
 ('fidelidade', [
  ('d1', 'Pista quatro: o lance fidelidade.', 'Pista 4: o lance fidelidade.'),
  ('d2', 'É uma pista reservada pra quem já está há mais tempo no grupo, com as parcelas em dia.',
         'É uma pista reservada pra quem já está há mais tempo no grupo, com as parcelas em dia.'),
  ('d3', 'Como pouca gente pode entrar, a concorrência é bem menor.',
         'Como pouca gente pode entrar, a concorrência é bem menor.')]),
 ('recap', [
  ('r1', 'E qual é a melhor pista?', 'E qual é a melhor pista?'),
  ('r2', 'Depende do seu caixa, do seu prazo, e das regras do seu grupo.',
         'Depende do seu caixa, do seu prazo e das regras do seu grupo.')]),
 ('cta', [
  ('c1', 'Comenta lance, que eu te ajudo a montar a sua estratégia.',
         'Comenta LANCE que eu te ajudo a montar a sua estratégia.')]),
]
# contemplação (cruzar a linha) em cada pista: (frase de referência, 's'|'e', deslocamento)
WIN = {'sorteio': ('s4', 'e', 0.5), 'livre': ('l3', 'e', 0.35), 'fixo': ('f4', 'e', 0.7), 'fidelidade': ('d3', 'e', 0.35)}
LEAD, GAP, TAIL = 0.45, 0.24, 0.55

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
