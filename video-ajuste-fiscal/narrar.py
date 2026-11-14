"""Gera a narração e a linha do tempo.
Uso: python3 narrar.py <dir_modelos> <dir_saida> [voz]
  voz = alex (padrão; Kokoro TTS, espera kokoro-v1.0.onnx e voices-v1.0.bin em <dir_modelos>)
        cadu, jeff ou faber (Piper TTS; espera <dir_modelos>/vits-piper-pt_BR-<voz>-medium/pt_BR-<voz>-medium.onnx + .json)"""
import sys, json, subprocess, numpy as np, soundfile as sf
from roteiro import FALAS
M, OUT = sys.argv[1], sys.argv[2]
VOZ = sys.argv[3] if len(sys.argv) > 3 else 'alex'
if VOZ == 'alex':
    from kokoro_onnx import Kokoro
    _k = Kokoro(f'{M}/kokoro-v1.0.onnx', f'{M}/voices-v1.0.bin'); SR = 24000
    def falar(txt): return _k.create(txt, voice='pm_alex', speed=1.0, lang='pt-br')[0]
else:
    from piper import PiperVoice, SynthesisConfig
    RITMO = {'cadu': 1.0, 'jeff': 0.97, 'faber': 1.08}[VOZ]      # length_scale: maior = mais devagar
    voice = PiperVoice.load(f'{M}/vits-piper-pt_BR-{VOZ}-medium/pt_BR-{VOZ}-medium.onnx')
    SR = voice.config.sample_rate
    CFG = SynthesisConfig(length_scale=RITMO, noise_scale=0.6, noise_w_scale=0.85)
    def falar(txt): return np.concatenate([c.audio_float_array for c in voice.synthesize(txt, CFG)])
def trim(a):
    idx = np.where(np.abs(a) > 0.012 * np.abs(a).max())[0]
    return a[max(idx[0] - int(0.02 * SR), 0): idx[-1] + int(0.10 * SR)]
t = 0.5; tl = []; clips = []; prev = 0
for fid, cap, txt, _ in FALAS:
    x = trim(falar(txt))
    if cap != prev: t += 0.5           # respiro na troca de capítulo
    prev = cap
    tl.append({'id': fid, 'cap': cap, 't0': round(t, 3), 't1': round(t + len(x) / SR, 3)}); clips.append((t, x))
    print(f'{t:6.2f} {len(x)/SR:5.2f}s  {txt}')
    t += len(x) / SR + 0.28
total = t + 2.2
v = np.zeros(int(total * SR), np.float32)
for t0, x in clips: i = int(t0 * SR); v[i:i + len(x)] += x
sf.write(f'{OUT}/voz_crua.wav', v / np.abs(v).max() * 0.9, SR)
# tratamento leve: corta subgrave, encorpa os médios-graves, realça a dicção, comprime de leve
FILTRO = 'highpass=f=60' if VOZ == 'alex' else ('highpass=f=70,equalizer=f=160:t=q:w=0.9:g=2,equalizer=f=3500:t=q:w=1.2:g=1.5,'
          'acompressor=threshold=-20dB:ratio=2:attack=15:release=160:makeup=1.5,alimiter=limit=0.9')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/voz_crua.wav', '-af', FILTRO,
                '-ar', '48000', '-ac', '1', f'{OUT}/voz.wav'], check=True)
json.dump({'total': round(total, 3), 'voz': VOZ, 'falas': tl}, open(f'{OUT}/timeline.json', 'w'), indent=1)
print('total', total)
