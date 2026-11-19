"""R$ 500 por mês, 100% do CDI bruto em todos. Valores líquidos se resgatar tudo no mês indicado.
- Previdência (VGBL, tabela regressiva): taxa de adm. 0,20% a.a.; IR só no resgate, por aporte: 35% (<2a), 30%, 25%, 20%, 15%, 10% (>10a). Sem come-cotas.
- Fundo DI longo prazo: taxa de adm. 0,30% a.a.; come-cotas de 15% em maio e novembro; no resgate, só o rendimento desde o último come-cotas.
- CDB de 3 anos: sem taxa; cada aporte vence em 3 anos, paga 15% de IR e é reaplicado em novo CDB de 3 anos.
- Caixinha (CDB com liquidez diária): sem taxa; IR regressivo só no resgate (22,5% ... 15% após 2 anos).
Uso: python3 simular.py [CDI_aa]   (padrão 12%)"""
import json, sys
CDI = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12
A, N = 500.0, 30 * 12
m = lambda r: (1 + r) ** (1 / 12) - 1
c = m(CDI); cp = m((1 + CDI) * (1 - 0.002) - 1) if False else (1 + c) * (1 - 0.002) ** (1/12) - 1; cf = (1 + c) * (1 - 0.003) ** (1/12) - 1
ir_prev = lambda mes: .35 if mes < 24 else .30 if mes < 48 else .25 if mes < 72 else .20 if mes < 96 else .15 if mes < 120 else .10
ir_rf = lambda mes: .225 if mes <= 6 else .20 if mes <= 12 else .175 if mes <= 24 else .15
prev, caixa, cdb = [], [], []          # lotes: [principal, saldo, idade]
fundo_cotas = 0.0; fundo_base = 0.0     # saldo e base de IR do fundo
serie = {k: [] for k in ['aportado', 'prev', 'fundo', 'cdb', 'caixinha']}
for t in range(1, N + 1):
    for L in (prev, caixa, cdb): L.append([A, A, 0])
    fundo_cotas += A; fundo_base += A
    for L in prev: L[1] *= 1 + cp; L[2] += 1
    for L in caixa: L[1] *= 1 + c; L[2] += 1
    for L in cdb:
        L[1] *= 1 + c; L[2] += 1
        if L[2] == 36: L[1] -= (L[1] - L[0]) * .15; L[0] = L[1]; L[2] = 0   # vence, paga IR, reaplica
    fundo_cotas *= 1 + cf
    if t % 6 == 0:                      # come-cotas semestral (maio/novembro)
        g = fundo_cotas - fundo_base
        if g > 0: fundo_cotas -= g * .15; fundo_base = fundo_cotas
    liq = lambda L, f: sum(s - max(0, s - p) * f(i) for p, s, i in L)
    serie['aportado'].append(A * t)
    serie['prev'].append(sum(s - (s - p) * ir_prev(i) for p, s, i in prev))
    serie['caixinha'].append(liq(caixa, ir_rf))
    serie['cdb'].append(liq(cdb, ir_rf))
    serie['fundo'].append(fundo_cotas - max(0, fundo_cotas - fundo_base) * .15)
for anos in (5, 10, 20, 30):
    i = anos * 12 - 1
    print(f"{anos:2d} anos | aportado R$ {serie['aportado'][i]:>9,.0f} | Prev R$ {serie['prev'][i]:>10,.0f} | Caixinha R$ {serie['caixinha'][i]:>10,.0f} | CDB 3a R$ {serie['cdb'][i]:>10,.0f} | Fundo R$ {serie['fundo'][i]:>10,.0f}")
json.dump({'cdi': CDI, **{k: [round(v) for v in s[11::12]] for k, s in serie.items()}}, open('resultado.json', 'w'))
