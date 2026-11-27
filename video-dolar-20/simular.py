"""Simulação: R$ 100 mil em 100% CDI x 80% CDI + 20% em dólar (S&P 500 convertido em reais).

Fontes (pasta dados/):
- CDI mensal: Banco Central, série SGS 4390
- Dólar comercial venda, fim de mês: Banco Central, série SGS 3696
- IPCA mensal: Banco Central, série SGS 433
- S&P 500 (média mensal, sem dividendos): github.com/datasets/s-and-p-500 (dados de Robert Shiller)

Rebalanceamento anual para manter 80/20. Sem impostos e sem custos.
Uso: python3 simular.py  -> imprime os resultados e grava dados/resultado.json
"""
import csv, json
import numpy as np

cdi = {d['data'][3:]: float(d['valor']) / 100 for d in json.load(open('dados/cdi_mensal.json'))}
usd = {d['data'][3:]: float(d['valor']) for d in json.load(open('dados/dolar_mensal.json'))}
ipca = {d['data'][3:]: float(d['valor']) / 100 for d in json.load(open('dados/ipca_mensal.json'))}
sp = {}
for r in csv.DictReader(open('dados/sp500.csv')):
    y, m, _ = r['Date'].split('-'); sp[f'{m}/{y}'] = float(r['SP500'])

def meses(a, b):
    (y, m), out = a, []
    while (y, m) <= b:
        out.append(f'{m:02d}/{y}'); m += 1
        if m > 12: y, m = y + 1, 1
    return out

def sim(ini, fim, w, ext='sp', reb=12):
    M = meses(ini, fim); br, ex = 1e5 * (1 - w), 1e5 * w; V = [1e5]; inf = 1.0
    for i in range(1, len(M)):
        k, kp = M[i], M[i - 1]
        br *= 1 + cdi[k]
        ex *= usd[k] / usd[kp] * (sp[k] / sp[kp] if ext == 'sp' else 1)
        inf *= 1 + ipca.get(k, 0)
        if i % reb == 0:
            t = br + ex; br, ex = t * (1 - w), t * w
        V.append(br + ex)
    V = np.array(V); r = V[1:] / V[:-1] - 1
    return dict(M=M, V=V, final=V[-1], real=V[-1] / inf, aa=(V[-1] / V[0]) ** (12 / (len(M) - 1)) - 1,
                vol=r.std() * np.sqrt(12), dd=(V / np.maximum.accumulate(V) - 1).min())

INI, FIM = (2006, 10), (2026, 9)
res = {}
for nome, w, e in [('cdi', 0, 'sp'), ('sp20', .2, 'sp'), ('usd20', .2, 'usd')]:
    s = sim(INI, FIM, w, e); res[nome] = s
    print(f"{nome:6s} final R$ {s['final']:>10,.0f} | real R$ {s['real']:>9,.0f} | {s['aa']*100:5.2f}% a.a. | vol {s['vol']*100:4.1f}% | maior queda {s['dd']*100:5.1f}%")
crises = []
for a, b, nome in [((2002, 4), (2002, 10), 'Eleição 2002'), ((2008, 6), (2009, 2), 'Crise 2008'),
                   ((2015, 1), (2015, 12), 'Recessão 2015'), ((2020, 1), (2020, 3), 'Covid 2020')]:
    M = meses(a, b); fx = usd[M[-1]] / usd[M[0]] - 1
    c = sim(a, b, 0, reb=999)['final'] / 1e5 - 1; s20 = sim(a, b, .2, reb=999)['final'] / 1e5 - 1
    crises.append([nome, round(fx * 100, 1)]); print(f'{nome:14s} dólar {fx*100:+5.1f}% | 100% CDI {c*100:+5.1f}% | 80/20 {s20*100:+5.1f}%')
# séries para o gráfico (um ponto a cada 2 meses)
idx = list(range(0, len(res['cdi']['M']), 2)) + [len(res['cdi']['M']) - 1]
json.dump({'cdi': [round(res['cdi']['V'][i]) for i in idx], 'sp20': [round(res['sp20']['V'][i]) for i in idx],
           'finais': {k: round(v['final']) for k, v in res.items()}, 'crises': crises,
           'inicio': res['cdi']['M'][0], 'fim': res['cdi']['M'][-1]}, open('dados/resultado.json', 'w'))
