# Instruções permanentes — conteúdo do Marcus Novais

## Quem é
Marcus Novais, assessor de investimentos da Private Investimentos XP, **Planejador Financeiro CFP® e CGA** (NÃO tem CFA — nunca mencionar). Produz conteúdo para Instagram com foco em captação de clientes: investimentos, planejamento financeiro 360, finanças pessoais, mercado e empreendedorismo. Responder sempre em português do Brasil.

## Modelo visual OBRIGATÓRIO para slides e carrosséis
**Sempre** usar o modelo definido em `modelo/README.md` (referência: carrossel "Apocalipse empresarial", arquivos `modelo/referencia-*.png`) e o gerador `modelo/marcus_slides.py`. Exemplo completo e aprovado: `posts/dolar-carrossel/gerar.py`.

Resumo do modelo:
- 1080×1350. Contador `01/07` no topo direito; rodapé "Marcus Novais | Planejador Financeiro, CFP®" + "deslize →" (sem "deslize" no último).
- Alternar slides **escuros** (azul-marinho `#070D24` com grade, kicker dourado, título branco) e **claros** (bege `#F2EFE8` com grade, kicker dourado-escuro, título azul-marinho), títulos em MAIÚSCULAS bem pesadas com destaques em dourado `[g]` ou vermelho `[r]`, corpo com **negrito**.
- **Foto do Marcus:** foto INTEIRA ocupando o slide, **transparência mínima** (só degradê leve na base + sombra no texto) — função `photo_light()`, foto `modelo/fotos/marcus-estudio.png`. Nunca escurecer a foto com fundo azul pesado.
- **Slides com dados** (gráficos, barras): gerar também versão **MP4 animada** (linha sendo desenhada / barras crescendo). Se o tema tem dado forte, a **capa pode ser o gráfico animado** com o título.
- Último slide: foto + pergunta + botão dourado "Acesse o link na BIO e me chame".
- **Não** colocar "conteúdo educativo" nem fontes dentro dos slides (aviso fica na legenda).

## Compliance (CVM/ANBIMA)
Sem recomendação de ativo específico nem promessa de rentabilidade; números só com fonte verificada; sugerir o aviso "Conteúdo educativo, não constitui recomendação de investimento" na legenda; não usar a marca XP como conteúdo oficial.

## Organização
- Pautas automáticas (a cada 3h): `pautas/AAAA-MM-DD_HHh.md`.
- Posts e carrosséis: `posts/<tema>/` com o `gerar.py` e as imagens/vídeos.
