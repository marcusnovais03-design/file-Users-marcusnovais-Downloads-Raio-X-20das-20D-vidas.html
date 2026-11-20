# Copiloto de Leads – Instagram

Extensão do Google Chrome que transforma quem **comentou ou curtiu** posts do seu nicho em uma lista de **leads qualificados**, com segmento, pontuação, perfil provável e **mensagem de abordagem sugerida**.

Você navega no Instagram normalmente. O copiloto **só lê o que já está na sua tela** quando você clica num botão. Ele não rola a página, não clica, não segue ninguém e não manda mensagens sozinho. Isso reduz bastante o risco de bloqueio da conta.

## Instalação (5 minutos)

1. Baixe esta pasta `copiloto-leads-instagram` para o seu computador (ou descompacte o `.zip`).
2. No Chrome, abra `chrome://extensions`.
3. Ligue o **Modo do desenvolvedor**, no canto superior direito.
4. Clique em **Carregar sem compactação** e selecione a pasta `copiloto-leads-instagram`.
5. Fixe a extensão na barra (ícone de quebra-cabeça → alfinete). Clicar no ícone abre o **painel de leads**.
6. No painel, aba **Configuração**:
   - seu @ e uma descrição do que você faz;
   - **chave da API da Anthropic** (crie em console.anthropic.com → API Keys). Sem a chave, a pontuação por palavras-chave funciona; só a qualificação com IA fica desligada;
   - revise os segmentos e as palavras-chave e clique em **Salvar**.

## Uso diário

1. Abra no Instagram um post com bastante comentário de um perfil ou tema do seu nicho.
2. Clique em *ver mais comentários* algumas vezes, você mesmo.
3. No quadro **Copiloto de Leads** (canto inferior direito), clique em:
   - **Capturar comentários visíveis**: pega o @ e o texto de quem comentou. É o sinal mais forte.
   - **Capturar curtidas (janela aberta)**: com a lista de curtidas aberta, pega os @. É um sinal fraco.
   - **Capturar / enriquecer perfil**: na página de perfil de um lead, salva nome, bio, seguidores e link.
4. No painel: filtre por score e segmento, selecione os leads e clique em **Qualificar com IA**.
5. Abra **Detalhes**, ajuste a mensagem sugerida, copie e envie pelo direct. Depois atualize o status (Abordado → Respondeu → Reunião → Cliente).
6. Use **Exportar CSV** para levar os leads para a planilha ou o CRM. O arquivo abre direto no Excel.

## Segmentos pré-configurados

Consórcios · Previdência · Sucessão patrimonial · Investimentos (Tesouro Direto, CDB, renda fixa) · Crédito com garantia · Médicos · Empresários · Investidores R$ 1 milhão+

Todos podem ser editados, desligados ou ampliados na aba Configuração.

## Como a pontuação funciona

- **Palavras-chave (grátis, instantâneo):** dá pontos para quem comentou, menciona termos de um segmento, faz pergunta ou mostra intenção ("quero", "como faço", "minha empresa"). Tira pontos de spam e de comentários só com emoji ou marcação.
- **IA (Claude):** lê o comentário e a bio e devolve intenção (alta, média ou baixa), score de 0 a 100, perfil provável, produto sugerido, justificativa, alertas e a mensagem de direct. Por padrão usa o Claude Opus 5.5. Para volumes grandes, troque para Sonnet ou Haiku na Configuração e pague menos.

A mensagem é gerada com regras de compliance: sem promessa de rentabilidade, sem recomendar produto antes do suitability e sem urgência artificial. **A revisão final é sempre sua.** Valide o modelo de abordagem com o compliance do seu escritório.

## Privacidade e LGPD

- Todos os dados ficam **apenas no seu navegador** (`chrome.storage.local`). Não existe servidor.
- Só o texto do lead vai para a API da Anthropic, e só quando você clica em qualificar.
- A lista **Não contatar** exclui o lead e impede que ele seja capturado de novo.
- Exclua periodicamente os leads descartados.

## Limitações

- O Instagram muda o HTML com frequência. Se a captura parar de achar comentários, o ajuste é feito em `content.js`.
- Ao remover a extensão, os dados salvos são apagados. Exporte o CSV antes.

## Arquivos

| Arquivo | Função |
|---|---|
| `manifest.json` | Configuração da extensão (Manifest V3) |
| `content.js` | Quadro flutuante e leitura da tela do Instagram |
| `background.js` | Armazenamento e chamada à IA |
| `scoring.js` | Segmentos padrão e pontuação por palavras-chave |
| `dashboard.html/.css/.js` | Painel de leads e configuração |
