const pptxgen = require("pptxgenjs");
const path = require("path");
const IMG = path.join(__dirname, "img");
const OUT = process.argv[2] || path.join(__dirname, "Revisao_de_Carteira_Layla.pptx");

const Y = "F7C100", G = "9B9B9B", DG = "595959", CARD = "EFEFEF", TX = "222222", MU = "666666",
  GREEN = "2E7D32", RED = "C62828", HEAD = "E6E6E6", LINE = "D9D9D9";
const F = "Calibri";
const FOOT = "Private Investimentos  |  Revisão de Carteira  |  Layla  |  Referência: 10/11/2026";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Revisão de Carteira - Layla";
pres.author = "Marcus Novais";
pres.theme = { headFontFace: F, bodyFontFace: F };

pres.defineSlideMaster({
  title: "CONTEUDO",
  background: { color: "FFFFFF" },
  objects: [
    { image: { path: path.join(IMG, "private_dark.png"), x: 7.95, y: 0.4, w: 1.55, h: 0.328 } },
    { text: { text: FOOT, options: { x: 0.5, y: 5.22, w: 6.5, h: 0.22, fontFace: F, fontSize: 7.5, italic: true, color: MU, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.28, w: 7.3, h: 0.6, fontFace: F, fontSize: 28, italic: true, color: TX, margin: 0, valign: "middle", align: "left" }, text: "" } },
  ],
  slideNumber: { x: 9.1, y: 5.18, w: 0.4, h: 0.22, fontFace: F, fontSize: 8, color: MU, align: "right" },
});

const T = (s, text, o) => s.addText(text, Object.assign({ fontFace: F, color: TX, margin: 0, isTextBox: true, valign: "top" }, o));
const card = (s, x, y, w, h, fill = CARD) => s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill } });
const fonte = (s, text) => T(s, text, { x: 0.5, y: 4.86, w: 9, h: 0.3, fontSize: 7.5, italic: true, color: MU, valign: "bottom" });
const content = (title) => { const s = pres.addSlide({ masterName: "CONTEUDO" }); s.addText(title, { placeholder: "title", align: "left" }); return s; };
const axis = () => ({
  catAxisLabelColor: DG, valAxisLabelColor: DG, catAxisLabelFontFace: F, valAxisLabelFontFace: F,
  catAxisLabelFontSize: 9, valAxisLabelFontSize: 9, dataLabelFontFace: F, dataLabelFontSize: 8.5, dataLabelColor: DG,
  legendFontFace: F, legendFontSize: 9, legendColor: DG, catAxisLineShow: true, catAxisLineColor: "BFBFBF",
});

// ---------- 1. Capa
{
  const s = pres.addSlide();
  s.background = { color: "1A1A1A" };
  s.addImage({ path: path.join(IMG, "cover.jpg"), x: 0, y: 0, w: 10, h: 5.625, sizing: { type: "cover", w: 10, h: 5.625 } });
  T(s, "Revisão de Carteira", { x: 0.5, y: 1.45, w: 7, h: 0.6, fontSize: 36, italic: true, color: "FFFFFF" });
  T(s, "Resultados de 2026 e proposta de diversificação internacional", { x: 0.5, y: 2.2, w: 7, h: 0.35, fontSize: 15, italic: true, color: "FFFFFF" });
  s.addShape(pres.shapes.LINE, { x: 6.6, y: 4.6, w: 2.9, h: 0, line: { color: Y, width: 1.25 } });
  T(s, "Layla", { x: 6.6, y: 4.75, w: 2.9, h: 0.3, fontSize: 14, italic: true, color: "FFFFFF" });
  s.addImage({ path: path.join(IMG, "private_white.png"), x: 0.5, y: 4.75, w: 1.8, h: 0.381 });
}

// ---------- 2. Resumo executivo
{
  const s = content("Resumo executivo");
  const k = [
    ["R$ 2,74 mi", "Patrimônio total bruto em 10/11/2026, após R$ 2,55 mi aportados ao longo do ano"],
    ["+9,90%", "Rentabilidade no ano, 90,07% do CDI (CDI: +11,05%), com volatilidade de 2,16%"],
    ["R$ 195,7 mil", "Ganho financeiro no ano, com 10 dos 11 meses positivos"],
    ["0%", "Exposição internacional: todo o patrimônio está em ativos brasileiros e em reais"],
  ];
  k.forEach(([v, d], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.1, 2.12, 2.3);
    T(s, v, { x: x + 0.2, y: 1.4, w: 1.8, h: 0.5, fontSize: 24, italic: true, color: i === 3 ? RED : TX, valign: "middle" });
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.2, y: 2.05, w: 0.42, h: 0.06, fill: { color: Y }, line: { color: Y } });
    T(s, d, { x: x + 0.2, y: 2.25, w: 1.78, h: 1.0, fontSize: 10, italic: true, color: DG });
  });
  T(s, [
    { text: "Leitura: ", options: { bold: true } },
    { text: "a carteira foi montada ao longo de 2026, com aportes concentrados entre abril e junho, e tem entregado retorno consistente com baixa oscilação. O ponto central desta revisão é a falta de diversificação geográfica. Propomos sair dos dois fundos Ibiuna e do Drys Shelter e direcionar cerca de R$ 146 mil (5,3% do patrimônio) para alocação internacional." },
  ], { x: 0.5, y: 3.65, w: 9, h: 0.9, fontSize: 11.5, italic: true });
}

// ---------- 3. Evolução patrimonial
{
  const s = content("Evolução patrimonial em 2026");
  const meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov"];
  const pat = [0.938, 0.951, 0.959, 1.202, 2.223, 2.614, 2.643, 2.666, 2.709, 2.729, 2.739];
  s.addChart(pres.charts.BAR, [{ name: "Patrimônio final (R$ mi)", labels: meses, values: pat }], Object.assign(axis(), {
    x: 0.4, y: 1.0, w: 5.6, h: 3.75, barDir: "col", chartColors: [Y], barGapWidthPct: 45,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: true, title: "Patrimônio no fim de cada mês (R$ milhões)", titleFontFace: F, titleFontSize: 10, titleColor: DG,
  }));
  card(s, 6.3, 1.05, 3.2, 3.6);
  const rows = [
    ["R$ 2,55 mi", "aportados no ano: R$ 940 mil (jan), R$ 238 mil (abr), R$ 1,0 mi (mai) e R$ 369 mil (jun)"],
    ["R$ 195,7 mil", "de ganho financeiro, o equivalente a 7,1% do patrimônio atual"],
    ["R$ 43,2 mil", "maior ganho mensal (setembro, +1,61%)"],
  ];
  rows.forEach(([v, d], i) => {
    const y = 1.25 + i * 1.1;
    T(s, v, { x: 6.5, y, w: 2.9, h: 0.38, fontSize: 18, italic: true });
    T(s, d, { x: 6.5, y: y + 0.4, w: 2.85, h: 0.6, fontSize: 9.5, italic: true, color: DG });
  });
  fonte(s, "Fonte: XPerformance, Relatório de Investimentos (referência 10/11/2026). Novembro até o dia 10.");
}

// ---------- 4. Rentabilidade mensal
{
  const s = content("Rentabilidade mês a mês frente ao CDI");
  const meses = ["Jan*", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov*"];
  const cart = [-0.24, 1.51, 0.98, 0.48, 1.11, 0.92, 1.13, 0.90, 1.61, 0.72, 0.37];
  const cdi = [0.22, 1.00, 1.21, 1.09, 1.07, 1.11, 1.22, 1.10, 1.08, 1.07, 0.31];
  s.addChart(pres.charts.BAR, [
    { name: "Carteira", labels: meses, values: cart },
    { name: "CDI", labels: meses, values: cdi },
  ], Object.assign(axis(), {
    x: 0.4, y: 0.95, w: 6.0, h: 3.85, barDir: "col", chartColors: [Y, G], barGapWidthPct: 60,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 7,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "t",
  }));
  const st = [["10", "meses positivos"], ["1", "mês negativo (jan, -0,24%)"], ["4", "meses acima do CDI"], ["2,16%", "volatilidade anualizada"]];
  st.forEach(([v, d], i) => {
    const x = 6.65 + (i % 2) * 1.45, y = 1.05 + Math.floor(i / 2) * 1.2;
    card(s, x, y, 1.35, 1.05);
    T(s, v, { x: x + 0.15, y: y + 0.12, w: 1.1, h: 0.4, fontSize: 20, italic: true });
    T(s, d, { x: x + 0.15, y: y + 0.55, w: 1.1, h: 0.45, fontSize: 9, italic: true, color: DG });
  });
  T(s, "A distância para o CDI vem sobretudo da marcação a mercado dos títulos IPCA+ e dos fundos com desempenho fraco, tratados nesta revisão.",
    { x: 6.65, y: 3.55, w: 2.85, h: 1.0, fontSize: 10, italic: true, color: DG });
  fonte(s, "Fonte: XPerformance (10/11/2026). CDI mensal calculado a partir do %CDI informado. *Janeiro parcial (início da carteira) e novembro até o dia 10. Rentabilidade com gross up para ativos isentos.");
}

// ---------- 5. Composição
{
  const s = content("Composição da carteira por estratégia");
  const cls = ["Pós-fixado", "Inflação", "Multimercado", "Pré-fixado", "Fundos listados", "Alternativo", "RV Brasil", "Caixa", "Internacional"];
  const pct = [39.86, 26.75, 18.96, 7.72, 3.92, 2.51, 0.21, 0.08, 0];
  s.addChart(pres.charts.BAR, [{ name: "% do patrimônio", labels: cls.slice().reverse(), values: pct.slice().reverse() }], Object.assign(axis(), {
    x: 0.4, y: 0.95, w: 5.4, h: 3.85, barDir: "bar", chartColors: [Y], barGapWidthPct: 40,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00\"%\"",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMaxVal: 46,
  }));
  card(s, 6.1, 1.05, 3.4, 3.7);
  const items = [
    ["Pós-fixado: R$ 1,09 mi", "R$ 951 mil estão em previdência (Mag Cash e Brave), além de Drys Shelter e Ibiuna Credit."],
    ["Inflação: R$ 732 mil", "Títulos IPCA+ entre 7,0% e 10,2% ao ano: NTN-B, CDB, CRA, CRI, debênture e fundo."],
    ["Multimercado: R$ 519 mil", "Quase tudo no Genoa Capital Cruise Prev."],
    ["Internacional: R$ 0", "Nenhuma posição fora do Brasil ou em outra moeda."],
  ];
  items.forEach(([h, d], i) => {
    const y = 1.2 + i * 0.86;
    T(s, h, { x: 6.3, y, w: 3.05, h: 0.26, fontSize: 11, bold: true, italic: true, color: i === 3 ? RED : TX });
    T(s, d, { x: 6.3, y: y + 0.27, w: 3.05, h: 0.55, fontSize: 9.5, italic: true, color: DG });
  });
  fonte(s, "Fonte: XPerformance, composição por estratégia em 10/11/2026 (saldo bruto).");
}

// ---------- 6. Performance por classe
{
  const s = content("Desempenho por classe frente aos índices");
  const H = (t, a = "right") => ({ text: t, options: { bold: true, fill: { color: HEAD }, align: a } });
  const n = (v, bold) => ({ text: v, options: { align: "right", bold: !!bold, color: v.startsWith("-") ? RED : TX } });
  const L = (t) => ({ text: t, options: { align: "left" } });
  const data = [
    ["Pós-fixado", "R$ 1.091.331", "39,86%", "+0,25%", "+10,29%", "CDI", "+11,05%"],
    ["Inflação", "R$ 732.233", "26,75%", "+0,68%", "+7,64%", "IPCA", "+3,96%"],
    ["Multimercado", "R$ 518.948", "18,96%", "+0,32%", "+5,00%", "CDI", "+11,05%"],
    ["Pré-fixado", "R$ 211.235", "7,72%", "+0,31%", "+10,78%", "CDI", "+11,05%"],
    ["Fundos listados", "R$ 107.378", "3,92%", "0,00%", "0,00%", "CDI", "+11,05%"],
    ["Alternativo", "R$ 68.604", "2,51%", "-0,76%", "+16,28%", "CDI", "+11,05%"],
    ["RV Brasil", "R$ 5.837", "0,21%", "+2,67%", "-12,97%", "Ibovespa", "-4,21%"],
  ];
  const rows = [[H("Classe", "left"), H("Saldo bruto"), H("% carteira"), H("Mês"), H("Ano"), H("Índice", "left"), H("Índice no ano")]]
    .concat(data.map(r => [L(r[0]), n(r[1]), n(r[2]), n(r[3]), n(r[4], true), L(r[5]), n(r[6])]));
  s.addTable(rows, { x: 0.5, y: 1.0, w: 9.0, colW: [1.6, 1.45, 1.1, 1.0, 1.1, 1.25, 1.5], fontFace: F, fontSize: 10, color: TX,
    border: { type: "solid", pt: 0.5, color: LINE }, rowH: 0.32, valign: "middle", margin: [0, 0.07, 0, 0.07] });
  T(s, [
    { text: "Destaques: ", options: { bold: true } },
    { text: "o Alternativo (XP Ouro Bidirecional, +16,28%) e o Pré-fixado (+10,78%, perto do CDI). A classe Inflação, a +7,64%, segue com o dobro do IPCA, apesar da marcação a mercado. " },
    { text: "Atenção: ", options: { bold: true } },
    { text: "RV Brasil (Ibiuna Long Biased) caiu 12,97%, contra -4,21% do Ibovespa. Fundos listados (KDLG11) aparecem zerados no relatório." },
  ], { x: 0.5, y: 3.75, w: 9, h: 0.95, fontSize: 10.5, italic: true });
  fonte(s, "Fonte: XPerformance (10/11/2026). Rentabilidade com gross up para ativos isentos. Mês = novembro até o dia 10.");
}

// ---------- 7. Destaques e atenção
{
  const s = content("Ativos em destaque e pontos de atenção");
  const col = (x, titulo, cor, linhas) => {
    card(s, x, 1.0, 4.4, 3.7);
    T(s, titulo, { x: x + 0.25, y: 1.15, w: 3.9, h: 0.32, fontSize: 14, bold: true, italic: true, color: cor });
    linhas.forEach(([nome, v, d], i) => {
      const y = 1.65 + i * 0.75;
      T(s, nome, { x: x + 0.25, y, w: 2.75, h: 0.28, fontSize: 10.5, bold: true, italic: true });
      T(s, v, { x: x + 3.0, y, w: 1.15, h: 0.28, fontSize: 12, bold: true, italic: true, align: "right", color: cor });
      T(s, d, { x: x + 0.25, y: y + 0.29, w: 3.9, h: 0.38, fontSize: 9, italic: true, color: DG });
    });
  };
  col(0.5, "Destaques", GREEN, [
    ["XP Ouro Bidirecional", "+16,28%", "Alternativo, 150,61% do CDI no ano"],
    ["NTN-B mai/2027 (IPCA + 8,39%)", "+12,91%", "117,41% do CDI no ano"],
    ["CRI MRV Flex jun/2035 (IPCA + 10,20%)", "+12,73%", "116,50% do CDI no ano"],
    ["Genoa Capital Cruise Prev", "163,51% CDI", "R$ 516 mil, 18,86% da carteira, +5,01% no ano"],
  ]);
  col(5.1, "Pontos de atenção", RED, [
    ["Ibiuna Long Biased", "-12,97%", "8,76 p.p. abaixo do Ibovespa no ano: proposta de saída"],
    ["Ibiuna Credit Debêntures Incentivadas", "-1,00%", "-31,62% do CDI no ano: proposta de saída"],
    ["Debênture Aegea Rio set/2042", "-27,23%", "Marcação a mercado de papel longo; taxa contratada mantida se levado ao vencimento, sem evento de crédito"],
    ["Drys Shelter", "48,73% CDI", "No mês; 96,82% do CDI no ano: fonte de recursos"],
  ]);
  fonte(s, "Fonte: XPerformance, posição detalhada em 10/11/2026 (precificação de renda fixa a mercado). Rentabilidade no ano, exceto quando indicado.");
}

// ---------- 8. Saída do Ibiuna
{
  const s = content("Saída dos fundos Ibiuna");
  s.addChart(pres.charts.BAR, [
    { name: "Fundo no ano", labels: ["Ibiuna Credit Debêntures", "Ibiuna Long Biased"], values: [-1.00, -12.97] },
    { name: "Índice de referência no ano", labels: ["Ibiuna Credit Debêntures", "Ibiuna Long Biased"], values: [11.05, -4.21] },
  ], Object.assign(axis(), {
    x: 0.4, y: 0.95, w: 4.9, h: 3.85, barDir: "col", chartColors: [G, Y], barGapWidthPct: 70,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00\"%\"",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: true, legendPos: "t",
  }));
  const H = (t, a = "right") => ({ text: t, options: { bold: true, fill: { color: HEAD }, align: a } });
  const r = (t, c) => ({ text: t, options: { align: "right", color: c || TX } });
  s.addTable([
    [H("Fundo", "left"), H("Saldo"), H("Ano"), H("Índice"), H("Diferença")],
    [{ text: "Ibiuna Credit Deb. Incent.", options: { align: "left" } }, r("R$ 19.415"), r("-1,00%", RED), r("CDI +11,05%"), r("-12,05 p.p.", RED)],
    [{ text: "Ibiuna Long Biased", options: { align: "left" } }, r("R$ 5.837"), r("-12,97%", RED), r("Ibov -4,21%"), r("-8,76 p.p.", RED)],
    [{ text: "Total", options: { align: "left", bold: true } }, { text: "R$ 25.252", options: { align: "right", bold: true } }, r(""), r(""), r("")],
  ], { x: 5.55, y: 1.05, w: 3.95, colW: [1.2, 0.65, 0.55, 0.78, 0.77], fontFace: F, fontSize: 8.5, color: TX,
    border: { type: "solid", pt: 0.5, color: LINE }, rowH: 0.36, valign: "middle", margin: [0, 0.05, 0, 0.05] });
  T(s, [
    { text: "Por que sair\n", options: { bold: true, fontSize: 12 } },
    { text: "Os dois fundos ficaram bem abaixo dos seus índices no ano. São posições pequenas (0,92% da carteira): quando acertam, pouco mudam o resultado, mas pesam quando erram. A saída também tira um gestor da carteira e simplifica o acompanhamento." },
  ], { x: 5.55, y: 2.75, w: 3.95, h: 1.9, fontSize: 10, italic: true, color: DG });
  fonte(s, "Fonte: XPerformance (10/11/2026). Ibiuna Credit é isento de IR: rentabilidade com gross up. Antes do resgate, confirmar prazo de cotização e liquidação de cada fundo.");
}

// ---------- 9. Drys como fonte
{
  const s = content("Drys Shelter como fonte de recursos");
  s.addChart(pres.charts.BAR, [{ name: "Saldo (R$ mil)", labels: ["Ibiuna Credit", "Drys Shelter", "Brave Prev", "Mag Cash Prev"], values: [19.4, 120.8, 316.9, 634.2] }],
    Object.assign(axis(), {
      x: 0.4, y: 0.95, w: 5.0, h: 3.8, barDir: "bar", chartColors: [G, G, Y, Y], barGapWidthPct: 45,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "\"R$ \"0.0\" mil\"",
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMaxVal: 780,
      showTitle: true, title: "Composição do pós-fixado (cinza = proposta de saída)", titleFontFace: F, titleFontSize: 10, titleColor: DG,
    }));
  const k = [["R$ 120,8 mil", "saldo no Drys Shelter, 4,41% da carteira"], ["96,82%", "do CDI no ano (+10,64%)"], ["48,73%", "do CDI no mês"]];
  k.forEach(([v, d], i) => {
    const y = 1.0 + i * 0.85;
    card(s, 5.7, y, 3.8, 0.72);
    T(s, v, { x: 5.9, y: y + 0.12, w: 1.6, h: 0.45, fontSize: 18, italic: true, valign: "middle" });
    T(s, d, { x: 7.5, y: y + 0.12, w: 1.9, h: 0.45, fontSize: 9.5, italic: true, color: DG, valign: "middle" });
  });
  T(s, "O Drys tem entregado perto do CDI, mas sem papel único na carteira. O pós-fixado já soma 39,9%, com R$ 951 mil em previdência de liquidez diária. Usar o Drys como fonte reduz o excesso de pós-fixado e de crédito privado e financia a diversificação sem mexer nos títulos IPCA+ e prefixados, que têm taxa travada.",
    { x: 5.7, y: 3.6, w: 3.8, h: 1.15, fontSize: 9.5, italic: true });
  fonte(s, "Fonte: XPerformance (10/11/2026). O resgate do Drys deve respeitar o prazo de cotização do fundo; há incidência de IR sobre o ganho.");
}

// ---------- 10. Por que internacional
{
  const s = content("A necessidade de alocação internacional");
  card(s, 0.5, 1.0, 2.9, 3.7);
  T(s, "Exposição atual fora do Brasil", { x: 0.7, y: 1.2, w: 2.5, h: 0.3, fontSize: 11, italic: true, color: DG });
  T(s, "0%", { x: 0.7, y: 1.6, w: 2.5, h: 0.9, fontSize: 54, italic: true, color: TX });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 2.6, w: 0.42, h: 0.06, fill: { color: Y }, line: { color: Y } });
  T(s, "Os R$ 2,74 milhões estão em ativos brasileiros, em reais e expostos ao mesmo risco-país.",
    { x: 0.7, y: 2.8, w: 2.5, h: 1.0, fontSize: 10.5, italic: true, color: DG });
  const cards = [
    ["Concentração em um só país", "Juros, inflação, fiscal e política do Brasil movem toda a carteira ao mesmo tempo."],
    ["Moeda forte", "O dólar subiu 5,60% em 2026. Ter parte do patrimônio em dólar protege o poder de compra em momentos de estresse."],
    ["Acesso ao mercado global", "O Brasil representa menos de 1% do índice global de ações (MSCI ACWI). Setores como tecnologia e saúde quase não existem na bolsa local."],
    ["Descorrelação", "Ativos globais costumam reagir de forma diferente às crises locais e reduzem a oscilação do conjunto."],
  ];
  cards.forEach(([h, d], i) => {
    const x = 3.65 + (i % 2) * 2.95, y = 1.0 + Math.floor(i / 2) * 1.9;
    card(s, x, y, 2.85, 1.8);
    s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.2, w: 0.42, h: 0.42, fill: { color: Y }, line: { color: Y } });
    T(s, String(i + 1), { x: x + 0.2, y: y + 0.2, w: 0.42, h: 0.42, fontSize: 14, italic: true, align: "center", valign: "middle" });
    T(s, h, { x: x + 0.75, y: y + 0.2, w: 1.95, h: 0.42, fontSize: 11, bold: true, italic: true, valign: "middle" });
    T(s, d, { x: x + 0.2, y: y + 0.75, w: 2.5, h: 0.95, fontSize: 9.5, italic: true, color: DG });
  });
  fonte(s, "Fontes: XPerformance (variação do dólar no ano até 10/11/2026); MSCI, composição do índice ACWI por país.");
}

// ---------- 11. Proposta
{
  const s = content("Proposta de realocação");
  const H = (t, a = "right") => ({ text: t, options: { bold: true, fill: { color: HEAD }, align: a } });
  const L = (t, b) => ({ text: t, options: { align: "left", bold: !!b } });
  const R = (t, b) => ({ text: t, options: { align: "right", bold: !!b } });
  T(s, "Saídas", { x: 0.5, y: 1.0, w: 4, h: 0.3, fontSize: 13, bold: true, italic: true });
  s.addTable([
    [H("Ativo", "left"), H("Saldo"), H("% carteira")],
    [L("Drys Shelter FIC FIF RF CP LP"), R("R$ 120.820"), R("4,41%")],
    [L("Ibiuna Credit Deb. Incentivadas"), R("R$ 19.415"), R("0,71%")],
    [L("Ibiuna Long Biased"), R("R$ 5.837"), R("0,21%")],
    [L("Total", true), R("R$ 146.072", true), R("5,33%", true)],
  ], { x: 0.5, y: 1.35, w: 4.1, colW: [2.2, 1.05, 0.85], fontFace: F, fontSize: 9.5, color: TX,
    border: { type: "solid", pt: 0.5, color: LINE }, rowH: 0.3, valign: "middle", margin: [0, 0.06, 0, 0.06] });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 4.72, y: 2.0, w: 0.4, h: 0.32, fill: { color: Y }, line: { color: Y } });
  T(s, "Entrada: Internacional", { x: 5.25, y: 1.0, w: 4.2, h: 0.3, fontSize: 13, bold: true, italic: true });
  const dest = [["RF Global · 50%", "≈ R$ 73 mil", "Títulos do Tesouro americano e bonds de grau de investimento"], ["RV Global · 50%", "≈ R$ 73 mil", "ETFs de ações globais diversificados"]];
  dest.forEach(([h, v, d], i) => {
    const x = 5.25 + i * 2.15;
    card(s, x, 1.35, 2.05, 1.5);
    T(s, h, { x: x + 0.15, y: 1.45, w: 1.8, h: 0.28, fontSize: 10.5, bold: true, italic: true });
    T(s, v, { x: x + 0.15, y: 1.75, w: 1.8, h: 0.38, fontSize: 17, italic: true });
    T(s, d, { x: x + 0.15, y: 2.18, w: 1.8, h: 0.6, fontSize: 8.5, italic: true, color: DG });
  });
  T(s, "Antes e depois, nas classes afetadas", { x: 0.5, y: 3.0, w: 4.5, h: 0.28, fontSize: 11, bold: true, italic: true });
  s.addChart(pres.charts.BAR, [
    { name: "Hoje", labels: ["Pós-fixado", "RV Brasil", "Internacional"], values: [39.86, 0.21, 0] },
    { name: "Após a realocação", labels: ["Pós-fixado", "RV Brasil", "Internacional"], values: [34.74, 0, 5.33] },
  ], Object.assign(axis(), {
    x: 0.4, y: 3.25, w: 4.3, h: 1.6, barDir: "bar", chartColors: [G, Y], barGapWidthPct: 40,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00\"%\"", dataLabelFontSize: 8,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMaxVal: 48, showLegend: true, legendPos: "r",
  }));
  card(s, 5.25, 3.0, 4.25, 1.75);
  T(s, [
    { text: "Como fazer\n", options: { bold: true } },
    { text: "Veículo: conta global XP (dolarização efetiva do recurso) ou fundos e ETFs globais sem hedge cambial, investidos a partir do Brasil.\n" },
    { text: "Entrada em 2 ou 3 parcelas, para diluir o preço do câmbio." },
  ], { x: 5.45, y: 3.12, w: 3.9, h: 1.55, fontSize: 9.5, italic: true, color: DG, paraSpaceAfter: 4 });
  fonte(s, "Proposta sujeita à análise de perfil (suitability) e à aprovação da cliente. Valores com base nos saldos brutos de 10/11/2026; os valores líquidos dependem do IR e da cotização de cada fundo.");
}

// ---------- 12. Próximos passos
{
  const s = content("Próximos passos");
  const st = [
    ["Resgatar os fundos Ibiuna", "Ibiuna Credit Debêntures e Ibiuna Long Biased (R$ 25,3 mil), confirmando prazo de cotização e liquidação."],
    ["Resgatar o Drys Shelter", "R$ 120,8 mil, respeitando a cotização do fundo e considerando o IR sobre o ganho."],
    ["Montar a posição internacional", "Definir o veículo (conta global ou fundos e ETFs) e entrar em parcelas: 50% RF Global e 50% RV Global."],
    ["Acompanhar a carteira", "Monitorar a Debênture Aegea e a marcação dos IPCA+, e incluir a posição internacional no relatório mensal."],
  ];
  st.forEach(([h, d], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.05 + Math.floor(i / 2) * 1.85;
    card(s, x, y, 4.4, 1.6);
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.32, w: 0.55, h: 0.55, fill: { color: Y }, line: { color: Y } });
    T(s, String(i + 1), { x: x + 0.3, y: y + 0.32, w: 0.55, h: 0.55, fontSize: 18, italic: true, align: "center", valign: "middle" });
    T(s, h, { x: x + 1.05, y: y + 0.3, w: 3.15, h: 0.3, fontSize: 12, bold: true, italic: true });
    T(s, d, { x: x + 1.05, y: y + 0.63, w: 3.15, h: 0.85, fontSize: 10, italic: true, color: DG });
  });
}

pres.writeFile({ fileName: OUT }).then(f => console.log("wrote", f));
