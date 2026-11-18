const pptxgen = require("pptxgenjs");
const path = require("path");
const IMG = path.join(__dirname, "img");
const OUT = process.argv[2] || path.join(__dirname, "Revisao_de_Carteira_Marcos.pptx");

const Y = "F7C100", G = "9B9B9B", DG = "595959", CARD = "EFEFEF", TX = "222222", MU = "666666",
  GREEN = "2E7D32", RED = "C62828", HEAD = "E6E6E6", LINE = "D9D9D9";
const F = "Calibri";
const FOOT = "Private Investimentos  |  Revisão de Carteira  |  Marcos  |  Referência: 30/10/2026";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Revisão de Carteira - Marcos";
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

// ---------- 1. Capa
{
  const s = pres.addSlide();
  s.background = { color: "1A1A1A" };
  s.addImage({ path: path.join(IMG, "cover.jpg"), x: 0, y: 0, w: 10, h: 5.625, sizing: { type: "cover", w: 10, h: 5.625 } });
  T(s, "Revisão de Carteira", { x: 0.5, y: 1.45, w: 7, h: 0.6, fontSize: 36, italic: true, color: "FFFFFF" });
  T(s, "Início da carteira e próximos passos", { x: 0.5, y: 2.2, w: 7, h: 0.35, fontSize: 15, italic: true, color: "FFFFFF" });
  s.addShape(pres.shapes.LINE, { x: 6.6, y: 4.6, w: 2.9, h: 0, line: { color: Y, width: 1.25 } });
  T(s, "Marcos", { x: 6.6, y: 4.75, w: 2.9, h: 0.3, fontSize: 14, italic: true, color: "FFFFFF" });
  s.addImage({ path: path.join(IMG, "private_white.png"), x: 0.5, y: 4.75, w: 1.8, h: 0.381 });
}

// ---------- 2. Resumo executivo
{
  const s = content("Resumo executivo");
  const k = [
    ["R$ 150,6 mil", "Patrimônio total bruto em 30/10/2026"],
    ["R$ 150 mil", "Aportados em outubro, em duas entradas (16/10 e 26/10)"],
    ["93,98%", "Do CDI desde a entrada no fundo (+0,48%), com ganho de R$ 573,55 no mês"],
    ["99,95%", "Do patrimônio em um único ativo: o fundo XP CDI 94 CRA Set/27"],
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
    { text: "a carteira começou em outubro e todo o recurso foi para um fundo de crédito do agronegócio atrelado ao CDI, com vencimento em setembro de 2027. O início é sólido, com retorno próximo do CDI e baixa oscilação. O próximo passo é diversificar: criar uma reserva de liquidez e distribuir os novos aportes entre outras classes." },
  ], { x: 0.5, y: 3.65, w: 9, h: 0.9, fontSize: 11.5, italic: true });
  fonte(s, "Fonte: XPerformance (30/10/2026). As estatísticas de 12 e 24 meses do relatório refletem um saldo residual de R$ 29,39 anterior aos aportes e não foram consideradas.");
}

// ---------- 3. Linha do tempo
{
  const s = content("Como a carteira foi montada");
  const ev = [
    ["16/10", "Entrada", "TED recebida: R$ 100.000,00", Y],
    ["16/10", "Aplicação", "XP CDI 94 CRA Set/27: R$ 99.923,19", Y],
    ["26/10", "Entrada", "Transferência recebida: R$ 50.000,00", Y],
    ["26/10", "Aplicação", "XP CDI 94 CRA Set/27: R$ 50.004,05", Y],
    ["30/10", "Posição", "R$ 150.602,94 (1.490 cotas + R$ 72,76 em caixa)", DG],
  ];
  const x0 = 1.35, x1 = 8.65, yL = 2.35;
  s.addShape(pres.shapes.LINE, { x: x0, y: yL, w: x1 - x0, h: 0, line: { color: "BFBFBF", width: 2 } });
  ev.forEach(([d, t, desc, c], i) => {
    const x = x0 + i * (x1 - x0) / (ev.length - 1);
    s.addShape(pres.shapes.OVAL, { x: x - 0.11, y: yL - 0.11, w: 0.22, h: 0.22, fill: { color: c }, line: { color: c } });
    const up = i % 2 === 0;
    const yy = up ? 1.15 : 2.65;
    T(s, d, { x: x - 0.8, y: yy, w: 1.6, h: 0.32, fontSize: 16, italic: true, align: "center" });
    T(s, t, { x: x - 0.8, y: yy + 0.34, w: 1.6, h: 0.22, fontSize: 9.5, bold: true, italic: true, align: "center", color: DG });
    T(s, desc, { x: x - 0.8, y: yy + 0.56, w: 1.6, h: 0.5, fontSize: 9.5, italic: true, align: "center", color: DG });
  });
  card(s, 0.5, 3.85, 9.0, 0.85);
  T(s, [
    { text: "Resumo: ", options: { bold: true } },
    { text: "R$ 150.000 aportados e R$ 149.927 aplicados no mesmo dia de cada entrada, sem recurso parado. O saldo restante, de R$ 72,76, ficou em caixa." },
  ], { x: 0.7, y: 4.0, w: 8.6, h: 0.6, fontSize: 11, italic: true, valign: "middle" });
  fonte(s, "Fonte: XPerformance, movimentações de outubro/2026.");
}

// ---------- 4. Onde está o patrimônio
{
  const s = content("Onde está o patrimônio");
  s.addChart(pres.charts.BAR, [
    { name: "Desde a entrada", labels: ["XP CDI 94 CRA Set/27", "CDI no período"], values: [0.48, 0.51] },
  ], Object.assign(axis(), {
    x: 0.4, y: 0.95, w: 4.3, h: 3.8, barDir: "col", chartColors: [Y, G], barGapWidthPct: 80,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00\"%\"",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 0.6,
    showTitle: true, title: "Rentabilidade desde a entrada (outubro, parcial)", titleFontFace: F, titleFontSize: 10, titleColor: DG,
  }));
  card(s, 5.0, 1.0, 4.5, 3.7);
  T(s, "XP CDI 94 CRA Set/27 FIAGRO RL", { x: 5.2, y: 1.15, w: 4.1, h: 0.3, fontSize: 13, bold: true, italic: true });
  const rows = [
    ["Saldo bruto", "R$ 150.500,79"],
    ["Participação", "99,95% da carteira"],
    ["Quantidade", "1.490 cotas"],
    ["Rentabilidade", "+0,48% (93,98% do CDI)"],
    ["Estratégia", "Pós-fixado: crédito do agronegócio (CRA)"],
    ["Vencimento", "Setembro de 2027"],
  ];
  rows.forEach(([a, b], i) => {
    const y = 1.6 + i * 0.47;
    T(s, a, { x: 5.2, y, w: 1.4, h: 0.3, fontSize: 10.5, italic: true, color: DG });
    T(s, b, { x: 6.6, y, w: 2.75, h: 0.3, fontSize: 10.5, italic: true, bold: true });
    if (i < rows.length - 1) s.addShape(pres.shapes.LINE, { x: 5.2, y: y + 0.39, w: 4.1, h: 0, line: { color: LINE, width: 0.5 } });
  });
  fonte(s, "Fonte: XPerformance (30/10/2026). CDI no período calculado a partir do %CDI informado. Rentabilidade com gross up. Caixa: R$ 72,76 (0,05%).");
}

// ---------- 5. Cenário de referência
{
  const s = content("Cenário de referência");
  s.addChart(pres.charts.BAR, [{ name: "Últimos 12 meses", labels: ["CDI", "Ibovespa", "IPCA", "Dólar"], values: [14.25, 12.29, 4.63, 0.69] }],
    Object.assign(axis(), {
      x: 0.4, y: 0.95, w: 4.6, h: 3.8, barDir: "col", chartColors: [Y, G, G, G], barGapWidthPct: 60,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00\"%\"",
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, valAxisMinVal: 0,
      showTitle: true, title: "Índices nos últimos 12 meses", titleFontFace: F, titleFontSize: 10, titleColor: DG,
    }));
  const H = (t, a = "right") => ({ text: t, options: { bold: true, fill: { color: HEAD }, align: a } });
  const n = (v) => ({ text: v, options: { align: "right", color: v.startsWith("-") ? RED : TX } });
  const L = (t) => ({ text: t, options: { align: "left" } });
  const d = [["CDI", "1,07%", "11,70%", "14,25%"], ["Ibovespa", "-9,88%", "4,22%", "12,29%"], ["IPCA", "0,14%", "4,10%", "4,63%"], ["Dólar", "4,64%", "-1,48%", "0,69%"]];
  s.addTable([[H("Índice", "left"), H("Outubro"), H("Ano"), H("12 meses")]].concat(d.map(r => [L(r[0]), n(r[1]), n(r[2]), n(r[3])])),
    { x: 5.3, y: 1.05, w: 4.2, colW: [1.2, 1.0, 1.0, 1.0], fontFace: F, fontSize: 10, color: TX,
      border: { type: "solid", pt: 0.5, color: LINE }, rowH: 0.32, valign: "middle", margin: [0, 0.07, 0, 0.07] });
  T(s, "Com o CDI em 14,25% nos últimos 12 meses, os juros pós-fixados seguem atrativos, e o fundo de CRA aproveita esse cenário. Ao mesmo tempo, outubro mostrou a volatilidade dos outros mercados: a bolsa caiu 9,88% e o dólar subiu 4,64%. Esses movimentos reforçam a importância de diversificar com critério.",
    { x: 5.3, y: 2.85, w: 4.2, h: 1.8, fontSize: 10.5, italic: true, color: DG });
  fonte(s, "Fonte: XPerformance, índices de referência em 30/10/2026.");
}

// ---------- 6. Diagnóstico
{
  const s = content("Diagnóstico da carteira");
  const col = (x, titulo, cor, linhas) => {
    card(s, x, 1.0, 4.4, 3.7);
    T(s, titulo, { x: x + 0.25, y: 1.15, w: 3.9, h: 0.32, fontSize: 14, bold: true, italic: true, color: cor });
    linhas.forEach(([h, d], i) => {
      const y = 1.6 + i * 0.77;
      T(s, h, { x: x + 0.25, y, w: 3.9, h: 0.28, fontSize: 11, bold: true, italic: true });
      T(s, d, { x: x + 0.25, y: y + 0.29, w: 3.9, h: 0.42, fontSize: 9.5, italic: true, color: DG });
    });
  };
  col(0.5, "Pontos fortes", GREEN, [
    ["Retorno atrelado ao CDI", "Aproveita o juro alto, com 93,98% do CDI desde a entrada."],
    ["Prazo definido", "Vencimento em setembro de 2027, com horizonte claro de retorno."],
    ["Baixa oscilação", "Crédito pós-fixado tende a variar pouco no dia a dia."],
    ["Recurso alocado rápido", "Os dois aportes foram aplicados no mesmo dia, sem dinheiro parado."],
  ]);
  col(5.1, "Pontos de atenção", RED, [
    ["Concentração em um só ativo", "99,95% do patrimônio depende de um único fundo e de um único setor (agro)."],
    ["Liquidez", "Sem reserva de liquidez diária. A saída antes do vencimento depende da venda das cotas."],
    ["Sem proteção contra a inflação", "Não há títulos IPCA+ para preservar o poder de compra no longo prazo."],
    ["Sem diversificação", "Não há prefixado, renda variável nem exposição internacional."],
  ]);
  fonte(s, "Fonte: XPerformance (30/10/2026), posição detalhada e composição por estratégia.");
}

// ---------- 7. Próximos passos
{
  const s = content("Próximos passos");
  const st = [
    ["Objetivos e perfil", "Alinhar prazos, metas e tolerância a risco para definir a carteira-alvo (suitability)."],
    ["Reserva de liquidez", "Separar uma parte dos próximos aportes em ativos de liquidez diária atrelados ao CDI."],
    ["Diversificar os novos aportes", "Distribuir entre inflação (IPCA+), prefixado e alocação internacional, conforme a política definida."],
    ["Acompanhar o fundo de CRA", "Manter a posição até o vencimento (set/2027) e acompanhar o %CDI no relatório mensal."],
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
