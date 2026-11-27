"""R$ 50 mil convertidos em dólar em 18/11/2016: dólar parado x 60% Treasuries (ETF SHY, 1-3 anos) + 40% S&P 500 (ETF SPY).
Preços ajustados por dividendos e juros (Yahoo Finance), rebalanceamento anual, sem IR, IOF e custos.
Dólar: PTAX venda do Banco Central (18/11/2016 = 3,3917); hoje R$ 5,83."""
import json, datetime as dt
def serie(t):
    r=json.load(open(f'dados/{t}.json'))['chart']['result'][0]
    return [(dt.datetime.fromtimestamp(a+3*3600,dt.UTC).strftime('%Y-%m'),b) for a,b in zip(r['timestamp'],r['indicators']['adjclose'][0]['adjclose'])]
dedup=lambda x:[r for k,r in enumerate(x) if k==len(x)-1 or x[k+1][0]!=r[0]]
spy=dedup(serie('SPY')); shy=dedup(serie('SHY'))
i0=[k for k,(m,_) in enumerate(spy) if m=='2016-11'][0]
spy=spy[i0:]; shy=shy[i0:]                      # nov/2016 ... 18/11/2026 (último ponto = hoje)
USD0, USD1 = 3.3917, 5.83
ptax={d['data'][3:]:float(d['valor']) for d in json.load(open('dados/dolar_mensal.json'))}
U0=50000/USD0
a, b = U0*.6, U0*.4                              # SHY, SPY
pts=[]
for k in range(1,len(spy)):
    a*=shy[k][1]/shy[k-1][1]; b*=spy[k][1]/spy[k-1][1]
    if k%12==0: t=a+b; a,b=t*.6,t*.4
    m=spy[k][0]; fx=USD1 if k==len(spy)-1 else ptax.get(m[5:]+'/'+m[:4])
    pts.append((m, (a+b)*fx, U0*fx))
inv=a+b
out={'usd_ini':round(U0), 'usd_inv':round(inv), 'brl_parado':round(U0*USD1), 'brl_inv':round(inv*USD1),
     'anual':[p for p in pts if p[0].endswith('-11')]}
json.dump(out,open('dados/resultado.json','w'))
print(f"US$ inicial {U0:,.0f} | investido vira US$ {inv:,.0f} ({(inv/U0-1)*100:.0f}%)")
print(f"Dólar parado: R$ {U0*USD1:,.0f} | Investido: R$ {inv*USD1:,.0f} | diferença R$ {(inv-U0)*USD1:,.0f}")
print(f"SPY total {spy[-1][1]/spy[0][1]*100-100:.0f}% | SHY total {shy[-1][1]/shy[0][1]*100-100:.0f}% (em US$)")
for p in out['anual']: print(p[0], round(p[1]), round(p[2]))
