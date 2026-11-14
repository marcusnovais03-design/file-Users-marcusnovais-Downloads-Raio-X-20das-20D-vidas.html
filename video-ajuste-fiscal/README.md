# Vídeo: "O governo precisa de ajuste fiscal?"

Reels vertical 1080x1920, 30 fps, cerca de 2min42s. Explicação desenhada à mão (papel bege, traço escuro, destaque laranja), com legenda palavra a palavra e narração em português.

## Como gerar

```bash
pip install piper-tts soundfile numpy pillow
# voz (uma vez): baixar e extrair em <modelos>/
#   https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-cadu-medium.tar.bz2
python3 narrar.py <modelos> <saida> cadu   # voz.wav + timeline.json (vozes: cadu, jeff, faber)
python3 mixar.py <saida>                # mix.wav (voz + trilha)
python3 render.py <saida>               # video_mudo.mp4
python3 render.py <saida> --horizontal  # versão 1920x1080 -> video_mudo_h.mp4
ffmpeg -i <saida>/video_mudo.mp4 -i <saida>/mix.wav -c:v copy -c:a aac -b:a 192k -shortest ajuste-fiscal.mp4
```

- `roteiro.py`: falas, legendas e capítulos. Mudar um texto aqui e rodar os três passos refaz tudo: os desenhos seguem o tempo de cada fala.
- `render.py`: desenhos de cada capítulo (função `build`), assinatura (`ASSINATURA`).
- Formato Reels: tudo o que importa fica entre y=150 e y=1490, fora da área coberta pela legenda e pelos botões do Instagram. Para a capa, use um quadro por volta de 0:06.
- Para usar a sua própria voz, grave a narração, salve como `<saida>/voz.wav` e ajuste os tempos em `timeline.json`.

## Roteiro

| Capítulo | Narração | Na tela |
|---|---|---|
| 00 A pergunta | Toda semana alguém repete que o governo precisa fazer ajuste fiscal. Mas será que isso é mesmo necessário? | Balança pendendo para os gastos |
| 01 A conta | Pense no orçamento do governo como o de uma casa. De um lado, o que entra: os impostos. Do outro, o que sai: os gastos. O problema é que, de cada cem reais gastos, sem contar os juros, noventa e dois já são obrigatórios. Aposentadorias, salários, saúde e educação. Sobra muito pouco espaço para cortar. | Casa, barra 92% obrigatório, 8% livre |
| 02 O buraco | E ainda falta a maior conta: os juros da dívida. Em doze meses, o setor público pagou um trilhão e duzentos bilhões de reais, só de juros. A arrecadação não cobre tudo isso. Então, o governo toma mais dinheiro emprestado. | Arrecada x gasta, bloco de juros, −9,5% do PIB |
| 03 A dívida | Resultado: a dívida pública já chega a oitenta e três por cento do PIB. Mais de onze trilhões de reais. E continua subindo. | 82,9% do PIB, curva subindo |
| 04 A inflação | Governo gastando demais aquece a economia, e pressiona os preços. A inflação está em quatro vírgula seis por cento em doze meses, acima do teto da meta. E inflação é um imposto invisível. O salário é o mesmo, mas o carrinho volta mais vazio. Quem mais sofre é quem ganha menos. | IPCA 4,63% x meta 3% e teto 4,5%, carrinhos |
| 05 Os juros | Para segurar os preços, o Banco Central mantém os juros lá em cima. A Selic está em treze vírgula setenta e cinco por cento ao ano. Juro alto encarece o financiamento da casa, o cartão, e o crédito das empresas. E freia o emprego. | Selic 13,75%, financiamento, cartão, empresas |
| 06 O círculo | E tem mais: juro alto aumenta a conta da própria dívida. Isso vira um círculo vicioso. Mais gasto, mais dívida, mais juros. | Gasto → dívida → juros |
| 07 Resumindo | Então, ajuste fiscal não é cortar por cortar. É fazer a conta fechar. Para a dívida parar de crescer, a inflação ceder, e os juros poderem cair. Sem ele, quem paga é você: no preço, no crédito, e nos seus investimentos. | Balança equilibrada |
| 08 Seu dinheiro | E o seu dinheiro, nesse cenário? Algumas classes de investimento tendem a se beneficiar. Com juros altos, a renda fixa pós-fixada paga mais. Com a Selic atual, rende mais de um por cento ao mês, antes dos impostos. Contra a inflação, os títulos atrelados ao IPCA protegem o seu poder de compra: pagam a inflação, mais um juro real. E, como o risco fiscal costuma pressionar o câmbio, ter uma parte no exterior, em dólar, ajuda a diversificar. A dose certa de cada um depende do seu perfil, e dos seus objetivos. | Três quadros: renda fixa pós-fixada, títulos IPCA, dólar e exterior |
| Fim | Ajuste fiscal não é ideologia. É aritmética. Quer proteger os seus investimentos? Me chama no direct. | Cartela escura |

## Números usados (conferidos em 14/nov/2026)

| Dado | Valor | Referência |
|---|---|---|
| Selic | 13,75% a.a., mantida no Copom de 4/nov/2026 | Banco Central |
| IPCA em 12 meses | 4,63% (out/2026); meta 3%, teto 4,5% | IBGE |
| Dívida bruta (DBGG) | 82,9% do PIB, R$ 11,1 trilhões (set/2026); alta de 4,3 pontos em 2026 | Banco Central, estatísticas fiscais |
| Juros nominais em 12 meses | R$ 1,205 trilhão, 8,99% do PIB (setor público consolidado) | Banco Central |
| Déficit primário em 12 meses | R$ 70,1 bilhões, 0,52% do PIB | Banco Central |
| Déficit nominal ("o buraco") | cerca de 9,5% do PIB (0,52% + 8,99%) | cálculo |
| Despesas obrigatórias | 92,4% das despesas primárias em 2026 | PLOA 2027 |
| Renda fixa pós-fixada | Selic de 13,75% a.a. equivale a 1,08% ao mês, bruto | cálculo |

Observações:

- As despesas obrigatórias, sozinhas, não superam a arrecadação: são cerca de 90% da receita líquida. A conta só deixa de fechar quando entram os juros. Por isso o vídeo diz "92 de cada 100 reais gastos, sem contar os juros" e mostra o buraco depois de somar os juros.
- No gráfico "arrecada x gasta" as alturas das barras são esquemáticas. Os números escritos são os oficiais.
- Na curva da dívida, só os pontos inicial (78,6%, dez/25) e final (82,9%, set/26) são dados. O traçado entre eles é ilustrativo.
- Os valores vieram de notícias que citam os boletins oficiais. Vale conferir nos sites do BC e do IBGE antes de publicar.

## Sugestão de legenda

> Toda semana alguém fala em ajuste fiscal. Mas por que isso importa pra você?
>
> De cada R$ 100 que o governo gasta (sem juros), R$ 92 já são obrigatórios. Some R$ 1,2 trilhão de juros por ano e a conta não fecha: a dívida já está em 82,9% do PIB.
>
> O resultado aparece na inflação acima da meta, na Selic de 13,75% e no crédito caro. Ajuste fiscal não é ideologia. É aritmética.
>
> Quer entender como esse cenário afeta a sua carteira? Me chama no direct. 📊
>
> *Conteúdo educativo. Não é recomendação de investimento. Fontes: Banco Central, IBGE e PLOA 2027.*

## Créditos

Fonte manuscrita: Caveat (SIL Open Font License). Voz: Piper TTS, voz brasileira `pt_BR-cadu-medium`.
