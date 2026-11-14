"""Gera a narração (Piper TTS, voz brasileira nativa) e a linha do tempo.
Uso: python3 narrar.py <dir_modelos> <dir_saida> [voz]      voz = cadu (padrão), jeff ou faber
Espera <dir_modelos>/vits-piper-pt_BR-<voz>-medium/pt_BR-<voz>-medium.onnx (+ .json)."""
import sys, json, subprocess, numpy as np, soundfile as sf
from piper import PiperVoice, SynthesisConfig
from roteiro import FALAS
M, OUT = sys.argv[1], sys.argv[2]
VOZ = sys.argv[3] if len(sys.argv) > 3 else 'cadu'
RITMO = {'cadu': 0.95, 'jeff': 0.97, 'faber': 1.08}[VOZ]      # length_scale: maior = mais devagar
voice = PiperVoice.load(f'{M}/vits-piper-pt_BR-{VOZ}-medium/pt_BR-{VOZ}-medium.onnx')
SR = voice.config.sample_rate
CFG = SynthesisConfig(length_scale=RITMO, noise_scale=0.6, noise_w_scale=0.85)
def trim(a):
    idx = np.where(np.abs(a) > 0.012 * np.abs(a).max())[0]
    return a[max(idx[0] - int(0.02 * SR), 0): idx[-1] + int(0.10 * SR)]
t = 0.5; tl = []; clips = []; prev = 0
for fid, cap, txt, _ in FALAS:
    x = trim(np.concatenate([c.audio_float_array for c in voice.synthesize(txt, CFG)]))
    if cap != prev: t += 0.5           # respiro na troca de capítulo
    prev = cap
    tl.append({'id': fid, 'cap': cap, 't0': round(t, 3), 't1': round(t + len(x) / SR, 3)}); clips.append((t, x))
    print(f'{t:6.2f} {len(x)/SR:5.2f}s  {txt}')
    t += len(x) / SR + 0.28
total = t + 2.2
v = np.zeros(int(total * SR), np.float32)
for t0, x in clips: i = int(t0 * SR); v[i:i + len(x)] += x
sf.write(f'{OUT}/voz_crua.wav', v / np.abs(v).max() * 0.9, SR)
# tratamento: corta subgrave, encorpa os médios-graves, suaviza sibilância, comprime de leve
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/voz_crua.wav', '-af',
                'highpass=f=70,equalizer=f=160:t=q:w=0.9:g=2.5,equalizer=f=3200:t=q:w=1.2:g=1,equalizer=f=7500:t=q:w=1.5:g=-3,'
                'acompressor=threshold=-21dB:ratio=2.5:attack=8:release=140:makeup=2,alimiter=limit=0.9',
                '-ar', '48000', '-ac', '1', f'{OUT}/voz.wav'], check=True)
json.dump({'total': round(total, 3), 'voz': VOZ, 'falas': tl}, open(f'{OUT}/timeline.json', 'w'), indent=1)
print('total', total)
