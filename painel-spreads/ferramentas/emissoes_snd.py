# Busca a taxa de emissão das debêntures no SND (debentures.com.br) pelo código CETIP.
# Uso: python3 emissoes_snd.py export_xp.csv saida.json
import csv, sys, json, re, time, html, subprocess, os
src = sys.argv[1]; out = sys.argv[2]
rows = list(csv.reader(open(src, encoding='utf-8-sig'), delimiter=';'))[1:]
debs = [(r[9].strip(), r[2]) for r in rows if r[0].startswith('DEB')]
res = json.load(open(out)) if os.path.exists(out) else {}
def txt(u):
    b = subprocess.run(['curl','-s','-m','25',u],capture_output=True).stdout
    t = html.unescape(re.sub(r'<[^>]*>',' ',b.decode('latin1')))
    return re.sub(r'\s+',' ',t)
for tk, ix in debs:
    if tk in res: continue
    t = txt(f"https://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_d.asp?tip_deb=publicas&selecao={tk}")
    g = lambda p: (re.search(p, t) or [None,None])[1]
    res[tk] = {"idx": ix, "tipo": g(r'Tipo de Remunera\S*: ([^:]+?) Tipo de Corre'), "spread": g(r'Taxa de Juros/Spread: ([\d.,-]+)'),
               "perc": g(r'% Multiplicador/Rentabilidade: ([\d.,-]+)'), "emissao": g(r'Emiss\S+: (\d{2}/\d{2}/\d{4}) Vencimento'), "achou": ("Ativo: "+tk) in t}
    json.dump(res, open(out,'w'))
    time.sleep(0.3)
print(len(res))
