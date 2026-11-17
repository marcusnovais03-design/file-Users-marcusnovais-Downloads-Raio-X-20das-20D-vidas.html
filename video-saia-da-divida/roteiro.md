# Reels: "Saia da dívida"

Vídeo vertical 1080x1920, 59 segundos, com gráficos animados e trilha de fundo.

- `out/reels-com-trilha.mp4`: versão com trilha, pronta para receber a voz.
- `out/reels-sem-audio.mp4`: só a imagem, caso prefira usar uma música do Instagram.

## Roteiro para gravar

Leia em tom de conversa, sem pressa. Cada fala tem uma janela de tempo; se sobrar espaço, tudo bem.

| Tempo | Na tela | Você fala |
|---|---|---|
| 0:00 – 0:04 | **8 em cada 10**, casinhas se acendendo | "Oito em cada dez famílias brasileiras têm dívidas." |
| 0:04 – 0:10 | Matéria do Banco Central + rosca chegando a **28,9%** + carimbo RECORDE | "E quase um terço de tudo o que elas ganham vai direto pra pagar dívida. É recorde." |
| 0:10 – 0:14 | Sua foto: **Quando a dívida aperta, a cabeça trava.** | "Quando a dívida aperta... a cabeça trava." |
| 0:14 – 0:20 | Close no rosto, a visão se fechando: **Modo sobrevivência** | "Com o dinheiro curto por muito tempo, o cérebro entra em modo sobrevivência. Só enxerga o problema de hoje." |
| 0:20 – 0:28 | **O ciclo da dívida** girando, barra de esperança caindo | "Aí começa o ciclo: falta dinheiro, você pega um empréstimo, a parcela aperta o mês... e falta dinheiro de novo." |
| 0:28 – 0:38 | Barras dos juros: **13,75%**, **64%**, **435,9%** | "E os juros alimentam esse ciclo. A Selic está em treze e setenta e cinco. O crédito pras famílias, sessenta e quatro por cento ao ano. E o rotativo do cartão... passa de quatrocentos e trinta por cento." |
| 0:38 – 0:45 | Curva subindo: **R$ 1.000 → R$ 5.359** | "Mil reais esquecidos no rotativo viram mais de cinco mil em um ano." |
| 0:45 – 0:52 | Sua foto sorrindo: **Dívida tem saída.** + 3 checks | "Mas dívida tem saída. Tudo numa folha só, prioridade certa e renegociação com estratégia." |
| 0:52 – 0:59 | Arte **Saia da Dívida** + botão | "Eu sou Marcus Novais, planejador financeiro CFP. Acessa o link na bio e clica em Saia das Dívidas." |

### Momentos de sincronia

- **0:07:** o carimbo RECORDE bate na tela. Fale "é recorde" logo depois.
- **0:30, 0:32 e 0:35:** cada barra de juros entra nesses segundos. Fale cada taxa quando a barra aparecer.
- **0:43:** a curva chega aos R$ 5.359. Fale "mais de cinco mil" nesse momento.
- **0:54:** o botão "Acesse o link na BIO" aparece.

## Como gravar e enviar

1. Grave no celular, num lugar silencioso, com o aparelho a um palmo da boca (o gravador de voz ou o WhatsApp servem).
2. Pode gravar tudo de uma vez ou fala por fala. Deixe um segundo de silêncio entre as falas.
3. Envie o arquivo de áudio (m4a, mp3, wav ou o áudio do WhatsApp). Eu encaixo cada fala no tempo certo, abaixo a trilha quando você fala e ajusto as cenas se alguma fala ficar mais longa.

## Legenda sugerida

> 😰 8 em cada 10 famílias brasileiras têm dívidas, e quase um terço da renda vai pra pagar essas dívidas. É recorde.
>
> 🧠 Quando o dinheiro aperta, o cérebro entra em modo sobrevivência e só enxerga o problema de hoje.
>
> 💳 E os juros alimentam o ciclo: no rotativo do cartão, R$ 1.000 viram mais de R$ 5.000 em um ano.
>
> ✅ Mas dívida tem saída.
>
> 👉 Acesse o link na BIO e clique em "Saia das Dívidas".
>
> #endividamento #saiadadivida #planejamentofinanceiro #educacaofinanceira #financaspessoais

## Fontes

- 81,6% das famílias endividadas: CNC/Peic, outubro de 2026.
- 28,9% da renda comprometida com dívidas, recorde desde 2011: Banco Central, junho de 2026.
- Selic de 13,75%: Copom, 4 de novembro de 2026.
- Crédito às famílias a 64% ao ano: Banco Central, divulgado em julho de 2026.
- Rotativo do cartão a 435,9% ao ano: Banco Central, fevereiro de 2026. R$ 1.000 sem pagamento por 12 meses = R$ 5.359.

## Como gerar de novo

- Imagem: `NODE_PATH=/opt/node-tools/node_modules node render.mjs`.
- Trilha: `python3 trilha.py`.
- Juntar as duas: `ffmpeg -i out/reels-sem-audio.mp4 -i out/trilha.wav -c:v copy -c:a aac -shortest out/reels-com-trilha.mp4`.
- Os tempos de cada cena estão na lista `SC`, no fim de `reels.html`.
