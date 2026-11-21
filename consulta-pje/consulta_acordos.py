#!/usr/bin/env python3
"""
Consulta publicações de acordos/RPVs/precatórios no Comunica PJe (API pública do CNJ)
e gera uma planilha CSV com processo, partes, advogados e valor citado.

Uso (só precisa de Python 3.8+, sem bibliotecas extras):

    python3 consulta_acordos.py --inicio 2026-11-01 --fim 2026-11-20
    python3 consulta_acordos.py --tribunais TRF3 TRT2 TRT15 --inicio 2026-11-01 --fim 2026-11-20
    python3 consulta_acordos.py --termos "homologo o acordo" "requisição de pequeno valor" --saida nov.csv

Gera um CSV (abre direto no Excel) com uma linha por publicação.
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

API = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
ITENS_POR_PAGINA = 100

# Tribunais com jurisdição em SP
TRIBUNAIS_PADRAO = ["TRF3", "TRT2", "TRT15"]

# Termos buscados no texto da publicação (cada termo é uma consulta separada)
TERMOS_PADRAO = [
    "homologo o acordo",
    "acordo homologado",
    "requisição de pequeno valor",
    "precatório",
    "alvará de levantamento",
]

# Confirmação local: só mantém publicações cujo texto realmente fala de acordo/pagamento
REGEX_CONFIRMA = re.compile(
    r"homolog\w*\s+(?:o\s+)?acordo|acordo\s+homologad|requisi[çc][ãa]o\s+de\s+pequeno\s+valor|"
    r"\bRPV\b|precat[óo]rio|alvar[áa]\s+de\s+levantamento|libera[çc][ãa]o\s+d[eo]s?\s+valor",
    re.IGNORECASE,
)

REGEX_VALOR = re.compile(r"R\$\s?[\d\.]+,\d{2}")


def get_json(params, tentativas=5):
    url = API + "?" + urllib.parse.urlencode(params)
    espera = 2
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "consulta-acordos/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tentativas - 1:
                print(f"  HTTP {e.code}, aguardando {espera}s...", file=sys.stderr)
                time.sleep(espera)
                espera *= 2
                continue
            raise
        except urllib.error.URLError:
            if i < tentativas - 1:
                time.sleep(espera)
                espera *= 2
                continue
            raise


def consultar(tribunal, dia, termo, pausa):
    pagina = 1
    while True:
        params = {
            "siglaTribunal": tribunal,
            "dataDisponibilizacaoInicio": dia,
            "dataDisponibilizacaoFim": dia,
            "texto": termo,
            "pagina": pagina,
            "itensPorPagina": ITENS_POR_PAGINA,
        }
        dados = get_json(params)
        itens = dados.get("items") or []
        for it in itens:
            yield it
        total = dados.get("count") or 0
        if not itens or pagina * ITENS_POR_PAGINA >= total:
            break
        pagina += 1
        time.sleep(pausa)


def polo_legivel(p):
    return {"A": "Ativo", "P": "Passivo"}.get((p or "").upper(), p or "")


def linha(it):
    texto = re.sub(r"\s+", " ", it.get("texto") or "").strip()
    partes = it.get("destinatarios") or []
    advs = it.get("destinatarioadvogados") or []

    polo_ativo = [d.get("nome", "") for d in partes if (d.get("polo") or "").upper() == "A"]
    polo_passivo = [d.get("nome", "") for d in partes if (d.get("polo") or "").upper() == "P"]
    outros = [f'{d.get("nome","")} ({polo_legivel(d.get("polo"))})' for d in partes
              if (d.get("polo") or "").upper() not in ("A", "P")]

    advogados = []
    for a in advs:
        adv = a.get("advogado") or {}
        oab = f'OAB/{adv.get("uf_oab","")} {adv.get("numero_oab","")}'.strip()
        advogados.append(f'{adv.get("nome","")} - {oab}')

    valores = REGEX_VALOR.findall(texto)
    return {
        "data": it.get("data_disponibilizacao", ""),
        "tribunal": it.get("siglaTribunal", ""),
        "processo": it.get("numeroprocessocommascara") or it.get("numero_processo", ""),
        "classe": it.get("nomeClasse", ""),
        "orgao": it.get("nomeOrgao", ""),
        "tipo": it.get("tipoComunicacao", ""),
        "polo_ativo": " | ".join(polo_ativo),
        "polo_passivo": " | ".join(polo_passivo),
        "outras_partes": " | ".join(outros),
        "advogados": " | ".join(advogados),
        "valores_citados": " | ".join(dict.fromkeys(valores)),
        "maior_valor": max((float(v.replace("R$", "").replace(".", "").replace(",", ".").strip())
                            for v in valores), default=""),
        "link": it.get("link", ""),
        "trecho": texto[:600],
    }


def dias(inicio, fim):
    d = inicio
    while d <= fim:
        yield d.isoformat()
        d += timedelta(days=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    hoje = date.today()
    ap.add_argument("--inicio", default=hoje.replace(day=1).isoformat(), help="AAAA-MM-DD (padrão: dia 1 do mês)")
    ap.add_argument("--fim", default=hoje.isoformat(), help="AAAA-MM-DD (padrão: hoje)")
    ap.add_argument("--tribunais", nargs="+", default=TRIBUNAIS_PADRAO)
    ap.add_argument("--termos", nargs="+", default=TERMOS_PADRAO)
    ap.add_argument("--valor-minimo", type=float, default=0, help="só publicações que citem valor >= este (R$)")
    ap.add_argument("--pausa", type=float, default=1.0, help="segundos entre chamadas (não sobrecarregue a API)")
    ap.add_argument("--saida", default=f"acordos_{hoje.isoformat()}.csv")
    a = ap.parse_args()

    inicio = datetime.strptime(a.inicio, "%Y-%m-%d").date()
    fim = datetime.strptime(a.fim, "%Y-%m-%d").date()

    vistos, linhas = set(), []
    for trib in a.tribunais:
        for dia in dias(inicio, fim):
            for termo in a.termos:
                print(f"{trib} {dia} '{termo}'...", file=sys.stderr)
                try:
                    for it in consultar(trib, dia, termo, a.pausa):
                        if it.get("id") in vistos:
                            continue
                        vistos.add(it.get("id"))
                        if not REGEX_CONFIRMA.search(it.get("texto") or ""):
                            continue
                        l = linha(it)
                        if a.valor_minimo and (l["maior_valor"] == "" or l["maior_valor"] < a.valor_minimo):
                            continue
                        linhas.append(l)
                except Exception as e:
                    print(f"  erro: {e}", file=sys.stderr)
                time.sleep(a.pausa)

    linhas.sort(key=lambda l: (l["maior_valor"] if l["maior_valor"] != "" else -1), reverse=True)
    campos = list(linhas[0].keys()) if linhas else ["data", "tribunal", "processo"]
    with open(a.saida, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        w.writeheader()
        w.writerows(linhas)
    print(f"\n{len(linhas)} publicações salvas em {a.saida}", file=sys.stderr)


if __name__ == "__main__":
    main()
