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

1. Abra no Instagram um post ou reel do seu nicho e deixe os comentários abertos.
2. No quadro **Copiloto de Leads** (canto inferior direito), use:
   - **Ler TODOS os comentários**: rola só a lista de comentários do post, clica em "carregar mais" e "ver respostas" num ritmo humano (1 a 3 segundos por passo) e para sozinho no fim. O limite é de 6 minutos por post. O botão vira **Parar leitura**, e o que já foi lido é salvo.
   - **Capturar só os visíveis**: pega apenas o que está na tela.
   - **Ler curtidas / reposts (lista aberta)**: clique no número de curtidas ou de reposts do post para abrir a lista, depois neste botão. Ele rola a lista inteira.
   - **Capturar / enriquecer perfil**: na página de perfil do lead, salva nome, bio, seguidores, link e **e-mail e telefone públicos**.
3. No painel, filtre por score, segmento ou **"Com e-mail ou telefone"**. Selecione os leads e clique em **Qualificar com IA**.
4. Abra **Detalhes**, ajuste a mensagem sugerida, copie e envie pelo direct, ou clique no telefone para abrir o WhatsApp. Depois atualize o status.
5. Use **Exportar CSV** (inclui e-mail, telefone e link do WhatsApp) para levar os leads à planilha ou ao CRM.

### Sobre compartilhamentos e contatos

- **Compartilhamentos por direct não são públicos.** Nem o dono do post vê quem enviou. Os **reposts** aparecem quando o Instagram mostra a lista.
- **E-mail e telefone** vêm do que a pessoa deixou público: o texto da bio, o link da bio (WhatsApp `wa.me`, `mailto:`) e números escritos nos comentários. O botão "Contato" das contas comerciais só aparece no app de celular, não no navegador.

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
- E-mail e telefone são dados pessoais. Use-os só para o contato relacionado ao interesse que a pessoa demonstrou, e respeite quem pedir para não ser contatado.
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
