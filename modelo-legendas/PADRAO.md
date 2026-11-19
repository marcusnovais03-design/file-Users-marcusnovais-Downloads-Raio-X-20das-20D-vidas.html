# Padrão de legendas (modelo de referência)

Formato: vertical 9:16, saída **sem áudio**. Todo o texto fica fixo na tela; não há animação palavra por palavra.
Medidas tomadas no modelo de 576x1024; aplicar em proporção.

1. **Título** (aparece desde o início e fica até o fim)
   - Serifada condensada branca (fonte: `fonts/InstrumentSerif-Regular.ttf`), sem fundo, com sombra leve.
   - Duas linhas centralizadas, com a palavra-chave em CAIXA ALTA ("1 MILHÃO").
   - Opcional: uma linha do título pode ir dentro de uma caixa amarela (#F5C400) com texto preto (`titulo_destaque`).
   - Posição: cerca de 18% a 24% da altura, ocupando uns 62% da largura.
2. **Caixas de conteúdo** (aparecem desde o início e ficam até o fim)
   - Fundo branco sólido, cantos retos, texto preto em serifada regular (fonte: `fonts/SourceSerif4-Regular.ttf`).
   - Cada caixa tem 2 linhas centralizadas, padding de uns 12px e largura ajustada ao texto (cerca de 65% da tela).
   - As caixas ficam empilhadas e centralizadas, com espaço de uns 25px entre elas, começando em cerca de 55% da altura.
   - Os números usam seta "→" (ex.: "Com 45 anos terá → R$ 83.486,37").
3. **Rodapé "Leia a legenda"**
   - Serifada branca pequena, sem fundo, centralizada a uns 86% da altura.
   - Entra em corte seco por volta de 60% da duração (3,4s num vídeo de 5,6s).

## Padrão aprovado (usar sempre)
- Linha 2 do título dentro de uma caixa amarela (#F5C400) com texto preto: `"titulo_destaque": 1`.
- "Leia a legenda" também numa caixa amarela com texto preto: `"rodape_destaque": true`.
- O vídeo final sai sempre sem som e sem música.
- Modelo de configuração: `video-debentures-cra-cri/texto.json`.
