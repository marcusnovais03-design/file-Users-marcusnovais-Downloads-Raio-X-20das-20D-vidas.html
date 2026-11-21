# Modelo oficial de carrossel — Marcus Novais

**Sempre usar este modelo** para carrosséis e slides (referência: carrossel "Apocalipse empresarial", arquivos `referencia-*.png`).

## Estrutura
- Formato **1080×1350**. Contador no canto superior direito (`01/09`), em negrito e espaçado.
- Rodapé em todos os slides: **"Marcus Novais | Planejador Financeiro, CFP®"** à esquerda e **"deslize →"** à direita. O último slide não tem "deslize".
- **Capa:** a sua foto (parede cinza) no alto, com degradê para azul-marinho. Embaixo vêm o *kicker* em **vermelho** (maiúsculas espaçadas), o título GRANDE em maiúsculas brancas com palavras de destaque em **dourado** e um subtítulo leve ("Veja o que está vindo 👉").
- **Slides claros:** fundo bege com grade fina. *Kicker* dourado-escuro, título azul-marinho com destaque em vermelho ou dourado, corpo em texto regular com palavras em **negrito** e trechos dourados.
- **Slides escuros:** fundo azul-marinho com grade. *Kicker* dourado, título branco com destaque dourado ou vermelho, lista com bolinhas douradas e divisórias.
- **Slides de dados** (gráficos e barras): também saem como **vídeo MP4 animado** (barras crescendo, linha sendo desenhada), além do PNG.
- **Último slide (CTA):** foto, título com destaque dourado e botão dourado "Acesse o link na BIO e me chame".
- Alternar claro e escuro ao longo do carrossel.

## Cores
| Uso | Cor |
|---|---|
| Fundo escuro | `#070D24` |
| Fundo claro | `#F2EFE8` |
| Título azul-marinho (fundo claro) | `#13205C` |
| Dourado (fundo escuro) | `#E3B65A` |
| Dourado (fundo claro) | `#A8741E` |
| Vermelho de destaque | `#E3141E` |

## Como gerar
`marcus_slides.py` tem as funções `cover`, `text_slide`, `bullets_slide` e `cta`. Exemplo de uso: `posts/dolar-carrossel/gerar.py`.
No texto: `[g]dourado[/g]`, `[r]vermelho[/r]`, `**negrito**`.

## Preferências do Marcus
- **Foto:** quando usar a foto dele, mostrar **a foto inteira**, com **pouca transparência ou degradê**. O degradê só serve para o texto ficar legível embaixo.
- **Gráficos animados:** quando a capa tiver dado (por exemplo, a cotação do dólar), a capa pode ser o gráfico animado com o título, em vez da foto. Nesse caso, a foto vai para o slide 2.
- **Sem aviso nem fontes nos slides:** não colocar "conteúdo educativo" nem as fontes dentro dos slides. O aviso pode ficar na legenda.
