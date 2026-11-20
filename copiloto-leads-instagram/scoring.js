// Pontuação local (sem IA, gratuita e instantânea).
// Usada pelo service worker (importScripts) e pelo painel (<script>).
(function (global) {
  const DEFAULT_CONFIG = {
    meuArroba: "",
    minhaAtuacao:
      "Assessor de investimentos (Private, XP Investimentos), CFP e CGA. Planejamento financeiro 360: investimentos, previdência, sucessão patrimonial, proteção e organização financeira para famílias e empresários.",
    tom: "próximo, educado e consultivo, sem parecer venda",
    apiKey: "",
    model: "claude-opus-5-5",
    segmentos: [
      {
        id: "consorcio",
        nome: "Consórcios",
        produto: "Consórcio imobiliário/veículos/pesados como alavancagem patrimonial sem juros",
        ativo: true,
        palavras: ["consórcio", "consorcio", "carta de crédito", "carta contemplada", "contemplação", "contemplado", "lance", "comprar imóvel", "comprar apartamento", "comprar casa", "comprar carro", "financiamento", "financiar", "alavancagem", "sem juros"]
      },
      {
        id: "previdencia",
        nome: "Previdência",
        produto: "Previdência PGBL/VGBL: eficiência tributária, aposentadoria e planejamento sucessório",
        ativo: true,
        palavras: ["previdência", "previdencia", "pgbl", "vgbl", "aposentadoria", "aposentar", "inss", "dedução", "deducao", "imposto de renda", "restituição", "12% da renda", "tabela regressiva", "renda na aposentadoria"]
      },
      {
        id: "sucessao",
        nome: "Sucessão patrimonial",
        produto: "Planejamento sucessório: holding, previdência, seguro de vida, doação e testamento",
        ativo: true,
        palavras: ["sucessão", "sucessao", "sucessório", "herança", "heranca", "herdeiro", "inventário", "inventario", "holding", "testamento", "doação", "doacao", "itcmd", "partilha", "seguro de vida", "família", "patrimônio familiar"]
      },
      {
        id: "investimentos",
        nome: "Investimentos (Tesouro Direto, CDB, renda fixa)",
        produto: "Tesouro Direto, CDB, LCI/LCA, CRI/CRA, debêntures e carteira diversificada",
        ativo: true,
        palavras: ["investir", "investimento", "tesouro direto", "tesouro selic", "tesouro ipca", "tesouro", "cdb", "lci", "lca", "cri", "cra", "debênture", "debenture", "renda fixa", "selic", "cdi", "rendimento", "rentabilidade", "poupança", "poupanca", "onde investir", "liquidez diária", "fii", "ações", "dividendos"]
      },
      {
        id: "credito_garantia",
        nome: "Crédito com garantia",
        produto: "Crédito com garantia de investimentos/imóvel: taxas menores sem resgatar a carteira",
        ativo: true,
        palavras: ["crédito", "credito", "empréstimo", "emprestimo", "garantia", "home equity", "taxa de juros", "capital de giro", "dívida", "divida", "trocar dívida", "portabilidade", "juros altos", "cheque especial", "cartão de crédito", "sem resgatar"]
      },
      {
        id: "medicos",
        nome: "Médicos",
        produto: "Organização PJ x PF, previdência, proteção de renda (DIT), reserva e investimentos recorrentes",
        ativo: true,
        palavras: ["médico", "médica", "medico", "medica", "plantão", "plantao", "plantonista", "consultório", "consultorio", "clínica", "clinica", "residência médica", "residente", "crm", "cirurgião", "cirurgiã", "pediatra", "anestesista", "medicina", "pj", "pejotização"]
      },
      {
        id: "empresarios",
        nome: "Empresários",
        produto: "Caixa da empresa, pró-labore x dividendos, crédito, sucessão e separação PF/PJ",
        ativo: true,
        palavras: ["empresa", "empresário", "empresario", "empresária", "empresaria", "sócio", "socio", "sócia", "faturamento", "pró-labore", "pro labore", "cnpj", "meu negócio", "minha empresa", "caixa da empresa", "vender a empresa", "lucro", "distribuição de lucros", "indústria", "agro", "fazenda"]
      },
      {
        id: "alta_renda",
        nome: "Investidores R$ 1 milhão+",
        produto: "Atendimento Private: carteira sofisticada, offshore, fundos exclusivos, planejamento 360",
        ativo: true,
        palavras: ["milhão", "milhao", "milhões", "milhoes", "1mm", "private", "patrimônio", "patrimonio", "offshore", "exterior", "dólar", "dolar", "fundo exclusivo", "family office", "wealth", "carteira grande", "diversificar patrimônio", "imóveis", "alugueis", "aluguéis", "renda passiva", "venda de imóvel", "venda da empresa"]
      }
    ]
  };

  const INTENT_WORDS = [
    "como faço", "como faz", "como funciona", "quero", "queria", "gostaria", "preciso", "quanto", "vale a pena",
    "me ajuda", "me ajudem", "dúvida", "duvida", "interesse", "interessado", "interessada", "onde", "qual",
    "indica", "indicação", "recomenda", "posso", "consigo", "tenho", "estou pensando", "pensando em",
    "minha empresa", "meu negócio", "meus filhos", "meu pai", "minha mãe", "info", "informações", "dm", "direct", "chama"
  ];
  const SPAM_WORDS = ["sigam", "siga meu", "segue lá", "promoção", "promo", "ganhe", "link na bio", "confira meu", "sorteio", "pix", "renda extra", "trader", "sinal", "forex", "cripto garantid"];

  function norm(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  function hasWord(text, word) {
    const esc = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp("(^|[^a-z0-9])" + esc + "($|[^a-z0-9])").test(text);
  }

  function leadText(lead) {
    const comments = (lead.comments || []).map((c) => c.text).join(" \n ");
    return [comments, lead.fullName, lead.bio].filter(Boolean).join(" \n ");
  }

  function scoreLead(lead, config) {
    const cfg = config || DEFAULT_CONFIG;
    const text = norm(leadText(lead));
    const commentsText = norm((lead.comments || []).map((c) => c.text).join(" "));
    let score = 0;
    const motivos = [];

    // Origem: comentar vale mais que curtir
    const hasComment = (lead.comments || []).some((c) => c.tipo !== "curtida" && c.text && c.text.trim().length > 0);
    if (hasComment) { score += 20; motivos.push("comentou"); }
    else if ((lead.comments || []).length) { score += 5; motivos.push("curtiu"); }

    // Segmentos
    let best = null;
    const todos = [];
    for (const seg of cfg.segmentos || []) {
      if (!seg.ativo) continue;
      const hits = [...new Set((seg.palavras || []).map(norm).filter((p) => p && hasWord(text, p)))];
      if (hits.length) todos.push(seg.nome);
      if (hits.length && (!best || hits.length > best.hits.length)) best = { seg, hits };
    }
    if (best) {
      score += Math.min(35, 12 * best.hits.length);
      motivos.push(`${best.seg.nome}: ${best.hits.slice(0, 4).join(", ")}`);
    }

    // Intenção (pergunta / desejo)
    const intentHits = INTENT_WORDS.filter((w) => hasWord(commentsText, norm(w)));
    if (intentHits.length) { score += Math.min(30, 10 * intentHits.length); motivos.push("sinal de intenção"); }
    if (commentsText.includes("?")) { score += 10; motivos.push("fez pergunta"); }

    // Comentário com conteúdo
    const words = commentsText.replace(/@\S+/g, "").split(/\s+/).filter((w) => /[a-z]/.test(w));
    if (words.length >= 8) score += 5;
    if (hasComment && words.length === 0) { score -= 10; motivos.push("só emoji/marcação"); }

    // Perfil enriquecido
    if (lead.bio) score += 5;

    // Spam
    if (SPAM_WORDS.some((w) => text.includes(norm(w)))) { score -= 30; motivos.push("possível spam"); }

    score = Math.max(0, Math.min(100, score));
    return {
      score,
      segmentoId: best ? best.seg.id : null,
      segmentoNome: best ? best.seg.nome : null,
      segmentos: todos,
      motivos
    };
  }

  global.LeadScoring = { DEFAULT_CONFIG, scoreLead, norm, hasWord };
})(globalThis);
