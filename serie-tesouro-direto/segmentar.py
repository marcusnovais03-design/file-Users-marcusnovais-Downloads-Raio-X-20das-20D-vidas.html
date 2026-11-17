"""Divide a gravação de um episódio em N falas usando as maiores pausas.
Uso: python3 segmentar.py 1   -> imprime as falas encontradas e grava out/ep01-falas.json
"""
import json, re, sys, wave
import numpy as np

ep = int(sys.argv[1]); tag = f'ep{ep:02d}'
w = wave.open(f'voz/{tag}-bruto.wav'); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.
hop = int(.02 * sr); n = len(x) // hop
db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)]) + 1e-9)
thr = max(np.percentile(db, 10) + 14, -45)
voz = db > thr
# fecha buracos curtos (< 0,12 s) e remove estalos curtos (< 0,08 s)
def runs(mask):
    r = []; i = 0
    while i < len(mask):
        j = i
        while j < len(mask) and mask[j] == mask[i]: j += 1
        r.append([bool(mask[i]), i, j]); i = j
    return r
for v, a, b in runs(voz):
    if not v and a > 0 and b < len(voz) and (b - a) * .02 < .12: voz[a:b] = True
for v, a, b in runs(voz):
    if v and (b - a) * .02 < .08: voz[a:b] = False
fala = [(a * .02, b * .02) for v, a, b in runs(voz) if v]
# ignora estalos isolados no começo (trechos < 0,35 s antes de uma pausa)
while len(fala) > 1 and fala[0][1] - fala[0][0] < .35 and fala[1][0] - fala[0][1] > .5: fala.pop(0)
inicio, fim = fala[0][0], fala[-1][1]
gaps = [(fala[i+1][0] - fala[i][1], fala[i][1], fala[i+1][0]) for i in range(len(fala) - 1)]

roteiro = open('gravacao.md').read()
bloco = re.split(r'\n## ', roteiro)[ep].split('\n')
frases = [re.sub(r'^\d+\.\s*', '', l) for l in bloco if re.match(r'^\d+\.', l)]
N = len(frases)
# alinhamento: escolhe N-1 pausas que deixam cada trecho com duração proporcional ao texto
#  e favorece pausas longas (programação dinâmica)
cand = [g for g in gaps if g[0] >= .3]
fr = np.array([len(f) for f in frases], float)
total = sum(b - a for a, b in fala); esp = fr / fr.sum() * total
pts = [inicio] + [g[2] for g in cand]          # possíveis inícios de frase
ends = [g[1] for g in cand] + [fim]            # possíveis fins de frase
K = len(cand)
INF = 1e18
best = {}
def custo(i, j, k):  # frase k vai do início pts[i] ao fim ends[j-1]... (j>i)
    d = ends[j - 1] - pts[i]
    return ((d - esp[k]) / max(esp[k], 1.5)) ** 2
dp = [[INF] * (K + 2) for _ in range(N + 1)]; par = [[None] * (K + 2) for _ in range(N + 1)]
dp[0][0] = 0
for k in range(N):
    for i in range(K + 1):
        if dp[k][i] >= INF: continue
        rng = [K + 1] if k == N - 1 else range(i + 1, K + 1)
        for j in rng:
            bonus = 0 if j == K + 1 else -0.6 * min(cand[j - 1][0], 1.5)
            c = dp[k][i] + custo(i, j, k) + bonus
            if c < dp[k + 1][j]: dp[k + 1][j] = c; par[k + 1][j] = i
j = K + 1; idx = []
for k in range(N, 0, -1):
    i = par[k][j]; idx.append(i); j = i
idx = sorted(idx)[1:]
cortes = [cand[i - 1] for i in idx]
seg = []
for i in range(N):
    a = inicio if i == 0 else cortes[i-1][2]
    b = fim if i == N - 1 else cortes[i][1]
    seg.append((round(a, 2), round(b, 2)))
tot_c = sum(len(f) for f in frases); tot_t = sum(b - a for a, b in seg)
print(f'{tag}: {N} frases, fala de {inicio:.2f}s a {fim:.2f}s, limiar {thr:.0f} dB')
for i, ((a, b), f) in enumerate(zip(seg, frases)):
    esp = len(f) / tot_c * tot_t
    flag = '' if .6 < (b - a) / esp < 1.6 else '   <-- conferir'
    print(f'  {i+1}. {a:6.2f}-{b:6.2f} ({b-a:4.1f}s, esperado ~{esp:4.1f}s){flag}  {f[:55]}')
print('  pausas usadas:', [round(g[0], 2) for g in cortes], '| maior pausa não usada:', round(sorted(gaps, reverse=True)[N-1][0], 2) if len(gaps) >= N else None)
json.dump({'falas': seg, 'inicio': inicio, 'fim': fim, 'dur': len(x) / sr}, open(f'out/{tag}-falas.json', 'w'))
