"""Prepara a voz de um episódio: tempos das cenas a partir das falas e voz limpa.
Uso: python3 voz.py 1   (depois de segmentar.py) -> out/ep01-tempos.json e out/ep01-voz.wav
"""
import json, subprocess, sys
ep = int(sys.argv[1]); tag = f'ep{ep:02d}'
F = json.load(open(f'out/{tag}-falas.json'))
OFFSET = max(0, F['inicio'] - 0.5)          # a primeira fala começa em 0,5 s do vídeo
ini = [a - OFFSET for a, b in F['falas']]
starts = [0] + [max(0, x - 0.3) for x in ini[1:]]
fim = F['fim'] - OFFSET + 2.2               # respiro depois da última fala
durs = [round(starts[i+1] - starts[i], 3) for i in range(len(starts) - 1)] + [round(fim - starts[-1], 3)]
json.dump(durs, open(f'out/{tag}-tempos.json', 'w'))
FILTRO = ('highpass=f=80,lowpass=f=14000,'
          'afftdn=nr=20:nf=-50:tn=1,'
          'agate=threshold=0.012:ratio=4:range=0.06:attack=4:release=180:knee=3,'
          'equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3800:t=q:w=1.4:g=2.5,'
          'acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,'
          'loudnorm=I=-16:TP=-1.5:LRA=9')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{OFFSET:.3f}', '-i', f'voz/{tag}.m4a', '-ac', '1', '-ar', '48000',
                '-af', FILTRO, f'out/{tag}-voz.wav'], check=True)
print(tag, 'offset', round(OFFSET, 2), 'cenas', durs, 'total', round(sum(durs), 2))
