# Reels: "Previdência é melhor que fundo, CDB e caixinha?"

Vídeo vertical 1080x1920, 64 s, só gráficos e texto, com @mnovais.
- `out/previdencia-x-fundo-cdb-caixinha.mp4`: com trilha.
- `out/previdencia-sem-musica.mp4`: sem som.

## Resultado (R$ 500/mês, 100% do CDI, CDI de 12% a.a., valores líquidos)

| Anos | Aportado | Previdência | Caixinha | CDB 3 anos | Fundo DI |
|---|---|---|---|---|---|
| 10 | R$ 60.000 | R$ 100.561 | R$ 104.165 | R$ 102.309 | R$ 100.053 |
| 20 | R$ 120.000 | R$ 409.835 | R$ 408.889 | R$ 376.467 | R$ 356.593 |
| 30 | R$ 180.000 | R$ 1.339.088 | R$ 1.336.363 | R$ 1.111.739 | R$ 1.014.373 |

Na sucessão (30 anos), com 10% de ITCMD e custos de inventário nos demais: Previdência R$ 1.339.088 · Caixinha R$ 1.202.727 · CDB R$ 1.000.565 · Fundo R$ 912.936.

Premissas: VGBL com tabela regressiva (35% a 10% por aporte); fundo DI de longo prazo com come-cotas de 15% em maio e novembro; CDB reaplicado a cada 3 anos com 15% de IR no vencimento; caixinha com IR regressivo só no resgate. Cálculo em `simular.py` (aceita outro CDI: `python3 simular.py 0.1365`).

## Roteiro para narrar (opcional)

1. Previdência privada é melhor que fundo, CDB e caixinha? Fiz a conta.
2. R$ 500 por mês, por 30 anos, tudo rendendo 100% do CDI. Previdência com taxa de 0,2% ao ano e fundo com 0,3%.
3. Depois de 30 anos, já sem imposto: previdência, R$ 1,34 milhão. Caixinha, quase igual. CDB, R$ 1,11 milhão. Fundo, R$ 1,01 milhão.
4. A previdência sai na frente porque o IR cai para 10% depois de 10 anos e só é cobrado no resgate. O fundo tem come-cotas a cada 6 meses e o CDB paga IR a cada vencimento.
5. Sendo honesto: no rendimento, a caixinha empata. A grande diferença aparece se você faltar.
6. A previdência não entra em inventário. Nos outros, a família perde uma parte com imposto e custos.
7. E no PGBL, quem faz a declaração completa ainda deduz até 12% da renda no IR.
8. Pra quem é? Pra quem pensa no longo prazo e na família. Comenta PREVIDÊNCIA.
