const { DEFAULT_CONFIG, scoreLead } = window.LeadScoring;

const state = {
  leads: {},
  config: structuredClone(DEFAULT_CONFIG),
  optout: [],
  selected: new Set(),
  open: new Set(),
  busy: false
};

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const STATUS = { novo: "Novo", abordado: "Abordado", respondeu: "Respondeu", reuniao: "Reunião marcada", cliente: "Cliente", descartado: "Descartado" };

async function load() {
  const data = await chrome.storage.local.get(["leads", "config", "optout"]);
  state.leads = data.leads || {};
  state.config = { ...structuredClone(DEFAULT_CONFIG), ...(data.config || {}) };
  state.optout = data.optout || [];
}

function send(msg) {
  return new Promise((resolve) => chrome.runtime.sendMessage(msg, (r) => resolve(r || { ok: false, error: chrome.runtime.lastError?.message })));
}

// ---------- Tabs ----------
document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === t));
  document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === "tab-" + t.dataset.tab));
  try { localStorage.setItem("copiloto_tab", t.dataset.tab); } catch (e) { /* ignore */ }
}));

// ---------- Leads ----------
function leadScore(l) {
  return l.ai ? l.ai.score : (l.local?.score ?? scoreLead(l, state.config).score);
}

function filtered() {
  const q = $("#fBusca").value.trim().toLowerCase();
  const seg = $("#fSegmento").value;
  const st = $("#fStatus").value;
  const it = $("#fIntencao").value;
  const min = Number($("#fScore").value) || 0;
  const orig = $("#fOrigem").value;

  return Object.values(state.leads).filter((l) => {
    const local = l.local || scoreLead(l, state.config);
    if (q) {
      const hay = [l.username, l.fullName, l.bio, ...(l.comments || []).map((c) => c.text + " " + c.postAuthor)].join(" ").toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (seg && !(local.segmentos || []).includes(seg) && l.ai?.segmento !== seg) return false;
    if (st && l.status !== st) return false;
    if (it === "sem" && l.ai) return false;
    if (it && it !== "sem" && l.ai?.intencao !== it) return false;
    if (leadScore(l) < min) return false;
    const tipos = new Set((l.comments || []).map((c) => c.tipo));
    if (orig === "comentario" && !tipos.has("comentario")) return false;
    if (orig === "curtida" && (tipos.has("comentario") || !tipos.has("curtida"))) return false;
    return true;
  }).sort((a, b) => leadScore(b) - leadScore(a) || (b.updatedAt || "").localeCompare(a.updatedAt || ""));
}

function renderKpis() {
  const all = Object.values(state.leads);
  $("#kTotal").textContent = all.length;
  $("#kQuentes").textContent = all.filter((l) => leadScore(l) >= 60).length;
  $("#kAbordados").textContent = all.filter((l) => ["abordado", "respondeu", "reuniao", "cliente"].includes(l.status)).length;
  $("#kReunioes").textContent = all.filter((l) => ["reuniao", "cliente"].includes(l.status)).length;
  $("#subtitle").textContent = state.config.meuArroba ? `${state.config.meuArroba} · captação qualificada` : "Instagram · captação qualificada";
}

function renderSegmentFilter() {
  const sel = $("#fSegmento");
  const cur = sel.value;
  sel.innerHTML = '<option value="">Todos os segmentos</option>' +
    state.config.segmentos.map((s) => `<option value="${esc(s.nome)}">${esc(s.nome)}</option>`).join("");
  sel.value = cur;
}

function lastComment(l) {
  const cs = (l.comments || []).filter((c) => c.tipo === "comentario" && c.text);
  return cs[cs.length - 1] || (l.comments || [])[l.comments.length - 1];
}

function rowHtml(l) {
  const local = l.local || scoreLead(l, state.config);
  const sc = leadScore(l);
  const c = lastComment(l);
  const nInter = (l.comments || []).length;
  const segs = l.ai && l.ai.segmento && l.ai.segmento !== "nenhum" ? [l.ai.segmento] : (local.segmentos || []);
  const intent = l.ai ? `<span class="pill ${esc(l.ai.intencao)}">${esc({ alta: "Alta", media: "Média", baixa: "Baixa" }[l.ai.intencao] || l.ai.intencao)}</span>`
                      : `<span class="pill sem">não avaliado</span>`;
  const interacao = c
    ? (c.tipo === "curtida"
        ? `<span class="tag">curtiu</span>`
        : `<q>${esc(c.text.length > 220 ? c.text.slice(0, 220) + "…" : c.text)}</q>`)
    : "";
  return `
  <tr class="lead" data-u="${esc(l.username)}">
    <td><input type="checkbox" class="sel" ${state.selected.has(l.username) ? "checked" : ""}></td>
    <td class="user">
      <b><a href="https://www.instagram.com/${esc(l.username)}/" target="_blank" rel="noopener">@${esc(l.username)}</a></b>
      ${l.fullName ? `<span class="name">${esc(l.fullName)}</span>` : ""}
      ${l.bio ? `<div class="bio">${esc(l.bio.slice(0, 120))}${l.bio.length > 120 ? "…" : ""}</div>` : ""}
    </td>
    <td class="comment">${interacao}
      ${c ? `<span class="src">post de @${esc(c.postAuthor || "?")}${nInter > 1 ? ` · +${nInter - 1} interações` : ""}</span>` : ""}
    </td>
    <td>${segs.map((s) => `<span class="tag">${esc(s)}</span>`).join("") || '<span class="muted">—</span>'}</td>
    <td><span class="score">${sc}</span><div class="bar"><i style="width:${sc}%"></i></div>
      <span class="muted small">${l.ai ? "IA" : "palavras"}</span></td>
    <td>${intent}</td>
    <td><select class="st">${Object.entries(STATUS).map(([k, v]) => `<option value="${k}" ${l.status === k ? "selected" : ""}>${v}</option>`).join("")}</select></td>
    <td class="actions">
      <button class="btn sm tog">${state.open.has(l.username) ? "Fechar" : "Detalhes"}</button>
    </td>
  </tr>
  ${state.open.has(l.username) ? detailHtml(l, local) : ""}`;
}

function detailHtml(l, local) {
  const ai = l.ai;
  const hist = (l.comments || []).map((c) => `<li>${c.tipo === "curtida" ? "Curtiu" : `“${esc(c.text)}”`}
      <span class="muted small">— <a href="${esc(c.postUrl)}" target="_blank" rel="noopener">post de @${esc(c.postAuthor || "?")}</a> · ${new Date(c.capturedAt).toLocaleDateString("pt-BR")}</span></li>`).join("");
  return `
  <tr class="detail" data-u="${esc(l.username)}"><td></td><td colspan="7">
    <div class="detailgrid">
      <div>
        <h4>Mensagem sugerida</h4>
        ${ai ? `<textarea class="msgbox">${esc(ai.mensagem)}</textarea>
          <div class="row" style="margin-top:8px">
            <button class="btn primary sm copy">Copiar mensagem</button>
            <a class="btn sm" href="https://www.instagram.com/${esc(l.username)}/" target="_blank" rel="noopener">Abrir perfil</a>
            <button class="btn sm requal">Qualificar de novo</button>
          </div>`
        : `<p class="muted">Ainda não qualificado pela IA.</p>
          <div class="row"><button class="btn primary sm requal">Qualificar com IA</button>
          <a class="btn sm" href="https://www.instagram.com/${esc(l.username)}/" target="_blank" rel="noopener">Abrir perfil</a></div>`}
        <h4 style="margin-top:16px">Anotações</h4>
        <textarea class="notes msgbox" style="min-height:70px" placeholder="Ex.: respondeu, tem consultório em Goiânia, reunião dia 12…">${esc(l.notes)}</textarea>
      </div>
      <div>
        ${ai ? `
          <p class="kv"><b>Perfil provável:</b> ${esc(ai.perfil_provavel)}</p>
          <p class="kv"><b>Produto sugerido:</b> ${esc(ai.produto_sugerido)}</p>
          <p class="kv"><b>Por quê:</b> ${esc(ai.justificativa)}</p>
          ${ai.cuidados ? `<p class="kv warn"><b>Atenção:</b> ${esc(ai.cuidados)}</p>` : ""}` : ""}
        <p class="kv"><b>Pontuação por palavras:</b> ${local.score} — ${esc((local.motivos || []).join("; ") || "sem sinais")}</p>
        ${l.followers ? `<p class="kv"><b>Seguidores:</b> ${esc(l.followers)} · <b>Posts:</b> ${esc(l.posts || "-")}</p>` : ""}
        ${l.externalLink ? `<p class="kv"><b>Link:</b> <a href="${esc(l.externalLink)}" target="_blank" rel="noopener">${esc(l.externalLink)}</a></p>` : ""}
        <h4>Histórico de interações</h4>
        <ul class="history">${hist}</ul>
        <div class="row" style="margin-top:12px">
          <button class="btn sm danger optout">Não contatar (excluir e bloquear)</button>
        </div>
      </div>
    </div>
  </td></tr>`;
}

function renderLeads() {
  const list = filtered();
  $("#rows").innerHTML = list.map(rowHtml).join("");
  $("#empty").hidden = Object.keys(state.leads).length > 0;
  const visible = new Set(list.map((l) => l.username));
  [...state.selected].forEach((u) => { if (!state.leads[u]) state.selected.delete(u); });
  $("#selCount").textContent = `${state.selected.size} selecionados · ${list.length} visíveis`;
  $("#selAll").checked = list.length > 0 && list.every((l) => state.selected.has(l.username));
  renderKpis();
  return visible;
}

async function updateLead(u, patch) {
  const { leads } = await chrome.storage.local.get("leads");
  if (!leads?.[u]) return;
  Object.assign(leads[u], patch, { updatedAt: new Date().toISOString() });
  await chrome.storage.local.set({ leads });
}

$("#rows").addEventListener("click", async (e) => {
  const tr = e.target.closest("tr");
  if (!tr) return;
  const u = tr.dataset.u;
  if (e.target.classList.contains("sel")) {
    e.target.checked ? state.selected.add(u) : state.selected.delete(u);
    $("#selCount").textContent = `${state.selected.size} selecionados`;
  } else if (e.target.classList.contains("tog")) {
    state.open.has(u) ? state.open.delete(u) : state.open.add(u);
    renderLeads();
  } else if (e.target.classList.contains("copy")) {
    const txt = tr.querySelector(".msgbox").value;
    await navigator.clipboard.writeText(txt);
    e.target.textContent = "Copiado ✓";
    setTimeout(() => (e.target.textContent = "Copiar mensagem"), 1500);
  } else if (e.target.classList.contains("requal")) {
    await runQualify([u]);
  } else if (e.target.classList.contains("optout")) {
    if (!confirm(`Excluir @${u} e nunca mais capturar este perfil?`)) return;
    await addOptout(u);
  }
});

$("#rows").addEventListener("change", async (e) => {
  const tr = e.target.closest("tr");
  if (!tr) return;
  const u = tr.dataset.u;
  if (e.target.classList.contains("st")) await updateLead(u, { status: e.target.value });
  else if (e.target.classList.contains("notes")) await updateLead(u, { notes: e.target.value });
  else if (e.target.classList.contains("msgbox") && state.leads[u]?.ai) {
    await updateLead(u, { ai: { ...state.leads[u].ai, mensagem: e.target.value } });
  }
});

["#fBusca", "#fSegmento", "#fStatus", "#fIntencao", "#fScore", "#fOrigem"].forEach((s) =>
  $(s).addEventListener("input", renderLeads));

$("#selAll").addEventListener("change", (e) => {
  filtered().forEach((l) => (e.target.checked ? state.selected.add(l.username) : state.selected.delete(l.username)));
  renderLeads();
});

function showStatus(text) {
  const s = $("#status");
  s.hidden = !text;
  s.textContent = text || "";
}

async function runQualify(usernames) {
  if (state.busy) return;
  if (!state.config.apiKey) {
    showStatus("Cadastre sua chave da API da Anthropic na aba Configuração para usar a qualificação com IA.");
    return;
  }
  if (usernames.length > 30 && !confirm(`Qualificar ${usernames.length} leads com IA? Cada lead é uma chamada à API (custo baixo, mas não zero).`)) return;
  state.busy = true;
  $("#bQualify").disabled = true;
  showStatus(`Qualificando ${usernames.length} lead(s)… você pode continuar usando o painel.`);
  const r = await send({ type: "qualify", usernames });
  state.busy = false;
  $("#bQualify").disabled = false;
  if (!r.ok) { showStatus("Erro: " + r.error); return; }
  showStatus(`${r.erros.length ? "Concluído com avisos" : "✓ Concluído"}: ${r.qualificados} qualificado(s).` +
    (r.erros.length ? `\n${r.erros.slice(0, 5).join("\n")}` : ""));
}

$("#bQualify").addEventListener("click", () => {
  const list = state.selected.size ? [...state.selected] : filtered().filter((l) => !l.ai).slice(0, 20).map((l) => l.username);
  if (!list.length) { showStatus("Selecione leads ou ajuste os filtros: não há leads pendentes de qualificação."); return; }
  if (!state.selected.size) showStatus(`Nenhum selecionado: qualificando os ${list.length} melhores ainda não avaliados.`);
  runQualify(list);
});

$("#bDelete").addEventListener("click", async () => {
  if (!state.selected.size) return showStatus("Nenhum lead selecionado.");
  if (!confirm(`Excluir ${state.selected.size} lead(s)? Esta ação não pode ser desfeita.`)) return;
  const { leads } = await chrome.storage.local.get("leads");
  state.selected.forEach((u) => delete leads[u]);
  state.selected.clear();
  await chrome.storage.local.set({ leads });
});

$("#bExport").addEventListener("click", () => {
  const list = state.selected.size ? [...state.selected].map((u) => state.leads[u]).filter(Boolean) : filtered();
  const cols = ["username", "link", "nome", "bio", "seguidores", "score", "intencao_ia", "segmento", "produto_sugerido", "perfil_provavel", "justificativa", "ultimo_comentario", "post_origem", "status", "anotacoes", "mensagem_sugerida", "capturado_em"];
  const cell = (v) => {
    let s = String(v ?? "");
    if (/^[=+\-@]/.test(s)) s = "'" + s; // evita fórmula no Excel
    return '"' + s.replace(/"/g, '""') + '"';
  };
  const lines = list.map((l) => {
    const c = lastComment(l) || {};
    const local = l.local || scoreLead(l, state.config);
    return [
      "@" + l.username, `https://www.instagram.com/${l.username}/`, l.fullName, l.bio, l.followers, leadScore(l),
      l.ai?.intencao, l.ai?.segmento || local.segmentoNome, l.ai?.produto_sugerido, l.ai?.perfil_provavel, l.ai?.justificativa,
      c.tipo === "curtida" ? "(curtiu)" : c.text, c.postUrl, STATUS[l.status] || l.status, l.notes, l.ai?.mensagem, l.createdAt
    ].map(cell).join(";");
  });
  const csv = "﻿" + [cols.join(";"), ...lines].join("\r\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  a.download = `leads-instagram-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
});

// ---------- Configuração ----------
function renderConfig() {
  const c = state.config;
  $("#cArroba").value = c.meuArroba || "";
  $("#cAtuacao").value = c.minhaAtuacao || "";
  $("#cTom").value = c.tom || "";
  $("#cKey").value = c.apiKey || "";
  $("#cModel").value = c.model || "claude-opus-5-5";
  renderSegs();
  renderOptout();
}

function renderSegs() {
  const list = $("#segList");
  list.innerHTML = "";
  state.config.segmentos.forEach((s, i) => {
    const node = $("#tplSeg").content.firstElementChild.cloneNode(true);
    node.dataset.i = i;
    node.classList.toggle("off", !s.ativo);
    node.querySelector(".sAtivo").checked = !!s.ativo;
    node.querySelector(".sNome").value = s.nome;
    node.querySelector(".sProduto").value = s.produto || "";
    node.querySelector(".sPalavras").value = (s.palavras || []).join(", ");
    list.appendChild(node);
  });
}

function readSegs() {
  return [...document.querySelectorAll("#segList .seg")].map((n, i) => ({
    id: state.config.segmentos[i]?.id || "seg_" + Date.now() + "_" + i,
    nome: n.querySelector(".sNome").value.trim() || "Sem nome",
    produto: n.querySelector(".sProduto").value.trim(),
    ativo: n.querySelector(".sAtivo").checked,
    palavras: n.querySelector(".sPalavras").value.split(",").map((p) => p.trim()).filter(Boolean)
  }));
}

$("#segList").addEventListener("click", (e) => {
  if (!e.target.classList.contains("sDel")) return;
  const i = Number(e.target.closest(".seg").dataset.i);
  state.config.segmentos = readSegs();
  state.config.segmentos.splice(i, 1);
  renderSegs();
});
$("#segList").addEventListener("change", (e) => {
  if (e.target.classList.contains("sAtivo")) e.target.closest(".seg").classList.toggle("off", !e.target.checked);
});
$("#bAddSeg").addEventListener("click", () => {
  state.config.segmentos = readSegs();
  state.config.segmentos.push({ id: "seg_" + Date.now(), nome: "", produto: "", ativo: true, palavras: [] });
  renderSegs();
  document.querySelector("#segList .seg:last-child .sNome").focus();
});
$("#bResetSeg").addEventListener("click", () => {
  if (!confirm("Restaurar os segmentos padrão? Suas edições de segmentos serão perdidas.")) return;
  state.config.segmentos = structuredClone(DEFAULT_CONFIG.segmentos);
  renderSegs();
});

$("#bSave").addEventListener("click", async () => {
  let arroba = $("#cArroba").value.trim();
  if (arroba && !arroba.startsWith("@")) arroba = "@" + arroba;
  const config = {
    ...state.config,
    meuArroba: arroba,
    minhaAtuacao: $("#cAtuacao").value.trim(),
    tom: $("#cTom").value.trim(),
    apiKey: $("#cKey").value.trim(),
    model: $("#cModel").value,
    segmentos: readSegs()
  };
  await chrome.storage.local.set({ config });
  await send({ type: "rescoreAll" });
  $("#saveMsg").textContent = "Salvo ✓ — pontuações recalculadas";
  setTimeout(() => ($("#saveMsg").textContent = ""), 2500);
});

function renderOptout() {
  $("#optoutList").innerHTML = state.optout.map((u) => `<span class="chip">@${esc(u)} <button data-u="${esc(u)}" title="Remover">×</button></span>`).join("") ||
    '<span class="muted small">Vazia.</span>';
}

async function addOptout(u) {
  u = u.toLowerCase().replace(/^@/, "").trim();
  if (!u) return;
  const data = await chrome.storage.local.get(["optout", "leads"]);
  const optout = new Set(data.optout || []);
  optout.add(u);
  const leads = data.leads || {};
  delete leads[u];
  state.selected.delete(u);
  await chrome.storage.local.set({ optout: [...optout], leads });
}

$("#bOptout").addEventListener("click", async () => { await addOptout($("#cOptout").value); $("#cOptout").value = ""; });
$("#optoutList").addEventListener("click", async (e) => {
  const u = e.target.dataset?.u;
  if (!u) return;
  const { optout } = await chrome.storage.local.get("optout");
  await chrome.storage.local.set({ optout: (optout || []).filter((x) => x !== u) });
});

// ---------- Atualização ao vivo (capturas feitas no Instagram aparecem aqui) ----------
chrome.storage.onChanged.addListener(async (changes) => {
  await load();
  if (changes.leads || changes.optout) { renderLeads(); renderOptout(); }
  if (changes.config) { renderSegmentFilter(); renderKpis(); }
});

(async function init() {
  await load();
  renderSegmentFilter();
  renderConfig();
  renderLeads();
  try {
    const tab = localStorage.getItem("copiloto_tab");
    if (tab) document.querySelector(`.tab[data-tab="${tab}"]`)?.click();
  } catch (e) { /* ignore */ }
  if (!state.config.apiKey && !Object.keys(state.leads).length) document.querySelector('.tab[data-tab="guia"]').click();
})();
