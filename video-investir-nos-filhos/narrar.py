import numpy as np, soundfile as sf, wave
from kokoro_onnx import Kokoro
k = Kokoro('kokoro-v1.0.onnx', 'voices-v1.0.bin')
V = 'pm_alex'
# (início, fim da janela, texto, alinhar_fim_em)  alinhar = tempo em que a fala deve terminar (opcional)
L = [(0.2, 3.6, 'Seu filho pode completar vinte anos...', None),
     (3.6, 6.8, 'com mais de três milhões e meio no nome dele.', None),
     (6.9, 10.8, 'E o segredo não é dinheiro. É tempo.', None),
     (10.9, 15.2, 'Quando você começa cedo, quem trabalha pesado são os juros compostos.', None),
     (15.3, 18.4, 'Faz a conta comigo: vinte anos, dez por cento ao ano.', None),
     (18.5, 24.8, 'Cem reais por mês. Você coloca vinte e quatro mil, e ele recebe setenta e um mil.', 18.4 + 5.1),
     (24.9, 31.2, 'Quinhentos por mês: cento e vinte mil investidos viram trezentos e cinquenta e nove mil.', 24.8 + 5.1),
     (31.3, 37.6, 'Mil reais por mês: setecentos e dezoito mil.', 31.2 + 5.0),
     (37.7, 44.0, 'Dois mil e quinhentos por mês: quase um milhão e oitocentos mil.', 37.6 + 5.0),
     (44.1, 50.4, 'E cinco mil por mês: três milhões, quinhentos e noventa mil reais.', 44.0 + 5.0),
     (50.5, 56.0, 'Em todos os cenários, dois terços do valor final vieram dos juros. Não do seu bolso.', None),
     (56.1, 61.0, 'O melhor dia pra começar foi quando ele nasceu. O segundo melhor? Hoje.', None),
     (61.1, 66.3, 'Comenta filho, que eu te mando a simulação do seu caso.', None)]
SR = 48000; TOTAL = 66.5
voice = np.zeros(int(TOTAL * SR))
def trim(a, sr):
    th = 0.01 * np.abs(a).max(); idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0] - int(0.02 * sr), 0): idx[-1] + int(0.08 * sr)]
for t0, t1, txt, endat in L:
    sp = 1.05
    while True:
        a, sr = k.create(txt, voice=V, speed=sp, lang='pt-br')
        a = trim(a, sr); d = len(a) / sr
        if d <= (t1 - t0) - 0.1 or sp >= 1.35: break
        sp += 0.05
    st = t0
    if endat: st = max(t0, endat - d)
    # reamostra 24k -> 48k
    x = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    i = int(st * SR); voice[i:i + len(x)] += x[:len(voice) - i]
    print(f'{st:5.2f}-{st+d:5.2f} (janela {t0}-{t1}) speed {sp:.2f}  {txt}')
voice = voice / np.abs(voice).max() * 0.89
sf.write('../narracao_masculina.wav', voice, SR)
bed, bsr = sf.read('../trilha.wav'); bed = bed[:len(voice)]
# ducking: baixa a trilha onde há voz
env = np.convolve(np.abs(voice), np.ones(4800) / 4800, 'same')
duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
duck = np.convolve(duck, np.ones(9600) / 9600, 'same')
mix = bed * 0.55 * duck[:, None] + voice[:, None]
mix = mix / np.abs(mix).max() * 0.95
sf.write('../mix_voz.wav', mix, SR)
