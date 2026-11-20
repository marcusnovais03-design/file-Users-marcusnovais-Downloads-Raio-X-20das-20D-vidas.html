// Copiloto de Leads – roda dentro do instagram.com.
// Ele NÃO navega, NÃO rola a página e NÃO clica em nada sozinho.
// Só lê o que já está visível na sua tela quando você clica num botão.
(function () {
  if (window.__copilotoLeads) return;
  window.__copilotoLeads = true;

  const RESERVED = new Set([
    "explore", "reels", "reel", "p", "accounts", "direct", "stories", "tv", "about", "legal",
    "developer", "web", "challenge", "emails", "privacy", "terms", "session", "login", "signup",
    "your_activity", "notifications", "create", "lite", "graphql", "api", "static", "help"
  ]);
  const NOISE = [
    /^responder$/i, /^reply$/i, /^curtir$/i, /^like$/i, /^ver tradução$/i, /^see translation$/i,
    /^ver respostas/i, /^view replies/i, /^ocultar respostas/i, /^hide replies/i, /^editado$/i, /^edited$/i,
    /^verificado$/i, /^verified$/i, /^seguir$/i, /^follow$/i, /^seguindo$/i, /^following$/i, /^•$/,
    /^\d+\s*(s|min|h|d|sem|w|m|a|y)$/i, /^\d+[.,]?\d*\s*(mil\s*)?(curtidas?|likes?)$/i,
    /^\d+\s*(respostas?|replies)$/i, /^autor$/i, /^author$/i, /^fixado$/i, /^pinned$/i,
    /^curtido pelo autor$/i, /^liked by author$/i, /^mais$/i, /^more$/i, /^…\s*mais$/i
  ];

  function usernameFromHref(href) {
    if (!href) return null;
    let path = href;
    try { path = new URL(href, location.origin).pathname; } catch (e) { /* ignore */ }
    const m = path.match(/^\/([A-Za-z0-9._]{1,30})\/?$/);
    if (!m) return null;
    const u = m[1].toLowerCase();
    return RESERVED.has(u) ? null : u;
  }

  function textLinks(root) {
    const out = [];
    root.querySelectorAll("a[href]").forEach((a) => {
      const u = usernameFromHref(a.getAttribute("href"));
      if (!u) return;
      const t = (a.textContent || "").trim().toLowerCase().replace(/^@/, "");
      if (t === u) out.push({ a, u });
    });
    return out;
  }

  function currentPostInfo() {
    const url = location.href.split("?")[0];
    const isPost = /\/(p|reel|reels|tv)\/[^/]+/.test(location.pathname);
    let author = null;
    const root = activeRoot();
    const header = root.querySelector("header");
    if (header) {
      const l = textLinks(header)[0];
      if (l) author = l.u;
    }
    if (!author) {
      const pathUser = location.pathname.match(/^\/([A-Za-z0-9._]+)\/(p|reel)\//);
      if (pathUser) author = pathUser[1].toLowerCase();
    }
    return { url, isPost, author };
  }

  function activeRoot() {
    const dialogs = [...document.querySelectorAll('div[role="dialog"]')].filter((d) => d.offsetParent !== null || d.getClientRects().length);
    if (dialogs.length) return dialogs[dialogs.length - 1];
    return document.querySelector("main") || document.body;
  }

  // Lê cada nó de texto separadamente (não depende do layout/innerText),
  // ignorando botões, horários e o próprio link do @.
  function textPieces(el) {
    const out = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const p = n.parentElement;
      if (!p || p.closest("button, time, script, style, svg, [role='button']")) continue;
      const t = n.nodeValue.replace(/\s+/g, " ").trim();
      if (!t) continue;
      const a = p.closest("a[href]");
      if (a && el.contains(a) && usernameFromHref(a.getAttribute("href"))) {
        // menções @fulano dentro do comentário continuam; o link do autor não
        if (!t.startsWith("@")) continue;
      }
      out.push(t);
    }
    return out;
  }

  function cleanLines(el, username) {
    return textPieces(el)
      .filter((l) => l.toLowerCase().replace(/^@/, "") !== username && !NOISE.some((r) => r.test(l)));
  }

  // ---------- Captura de comentários ----------
  function captureComments() {
    const root = activeRoot();
    const post = currentPostInfo();
    const links = textLinks(root);
    const seenBlocks = new Set();
    const results = new Map();

    for (const { a, u } of links) {
      // Sobe até o maior bloco que só contém links de texto deste mesmo usuário
      let block = a;
      for (let i = 0; i < 10 && block.parentElement && block.parentElement !== root; i++) {
        const parent = block.parentElement;
        const others = textLinks(parent).filter((x) => x.u !== u);
        if (others.length) break;
        block = parent;
      }
      if (seenBlocks.has(block)) continue;
      seenBlocks.add(block);

      const lines = cleanLines(block, u);
      const text = lines.join(" ").replace(/\s+/g, " ").trim();
      if (!text) continue;
      if (post.author && u === post.author) continue; // legenda/respostas do dono do post
      if (text.length > 1500) continue; // bloco grande demais = não é comentário

      const prev = results.get(u);
      if (prev) { if (!prev.text.includes(text)) prev.text += " | " + text; }
      else results.set(u, { username: u, text, tipo: "comentario" });
    }

    return { post, items: [...results.values()] };
  }

  // ---------- Leitura completa: rola SÓ a lista de comentários do post aberto ----------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const humanDelay = () => sleep(1200 + Math.random() * 1600);
  let reading = false;
  let stopRequested = false;

  function isScrollable(el) {
    if (!el || el === document.body || el === document.documentElement) return false;
    const st = getComputedStyle(el);
    return /(auto|scroll)/.test(st.overflowY) && el.scrollHeight > el.clientHeight + 20;
  }

  function findCommentScroller() {
    const root = activeRoot();
    const post = currentPostInfo();
    // Parte de um comentário (link de @ que não é do autor) e sobe até achar a área com rolagem
    const starts = textLinks(root).filter((x) => x.u !== post.author).map((x) => x.a);
    const counts = new Map();
    for (const a of starts.slice(0, 15)) {
      let el = a.parentElement;
      while (el && el !== document.body) {
        if (isScrollable(el)) { counts.set(el, (counts.get(el) || 0) + 1); break; }
        el = el.parentElement;
      }
    }
    let best = null, n = 0;
    counts.forEach((c, el) => { if (c > n) { best = el; n = c; } });
    return best;
  }

  const LOAD_MORE = /carregar mais coment|load more comments|ver mais coment|view more comments|ver todos os \d+ coment|view all \d+ comments/i;
  const SHOW_REPLIES = /^(ver|view)\s+(todas as\s+|all\s+)?(\d+\s+)?(respostas?|repl(y|ies))/i;

  function clickables(root) {
    return [...root.querySelectorAll('button, [role="button"], svg[aria-label]')];
  }

  function clickLoadMore(root) {
    for (const el of clickables(root)) {
      const label = (el.getAttribute("aria-label") || "") + " " + (el.textContent || "");
      if (LOAD_MORE.test(label)) {
        const target = el.closest('button, [role="button"]') || el.parentElement || el;
        target.click();
        return true;
      }
    }
    return false;
  }

  function clickShowReplies(root, max) {
    let n = 0;
    for (const el of clickables(root)) {
      if (n >= max) break;
      const t = (el.textContent || "").trim();
      if (SHOW_REPLIES.test(t) && !el.dataset.copilotoClicked) {
        el.dataset.copilotoClicked = "1";
        el.click();
        n++;
      }
    }
    return n;
  }

  // mode: "comments" (comentários do post) ou "list" (janela de curtidas/reposts aberta)
  async function readAll({ mode, replies }) {
    const post = currentPostInfo();
    const isList = mode === "list";
    if (isList) {
      const chk = captureLikes();
      if (chk.erro) { say(chk.erro, "err"); return; }
    } else if (!post.isPost) { say("Abra um post ou reel e deixe os comentários abertos.", "err"); return; }

    const scroller = findCommentScroller();
    const root = activeRoot();
    const all = new Map();
    const merge = () => {
      const got = isList ? captureLikes().items : captureComments().items;
      for (const it of got) {
        const prev = all.get(it.username);
        if (!prev) all.set(it.username, it);
        else if (it.text && !prev.text.includes(it.text)) prev.text += " | " + it.text;
      }
    };
    const nome = isList ? "perfis" : "comentários";

    reading = true;
    stopRequested = false;
    setReadingUI(true, mode);
    const started = Date.now();
    const MAX_MS = 6 * 60 * 1000; // no máximo 6 minutos por post
    let idle = 0;

    try {
      merge();
      while (!stopRequested && idle < 4 && Date.now() - started < MAX_MS && all.size < 2000) {
        const before = all.size;
        const h0 = scroller ? scroller.scrollHeight : document.body.scrollHeight;

        if (!isList) {
          clickLoadMore(root);
          if (replies) clickShowReplies(root, 3);
        }
        if (scroller) scroller.scrollTop = scroller.scrollHeight;
        else window.scrollBy(0, 600);

        await humanDelay();
        merge();

        // Só conta como progresso se apareceu gente nova ou a lista cresceu
        const h1 = scroller ? scroller.scrollHeight : document.body.scrollHeight;
        idle = (all.size > before || h1 > h0) ? 0 : idle + 1;
        say(`Lendo… ${all.size} ${nome} encontrados${stopRequested ? " (parando)" : ""}`);
      }
    } finally {
      reading = false;
      setReadingUI(false, mode);
    }

    const items = [...all.values()];
    if (!items.length) { say(`Nenhum ${isList ? "perfil" : "comentário"} encontrado. Abra a ${isList ? "lista" : "área de comentários"} e tente de novo.`, "err"); return; }
    const res = await send({ type: "saveCaptures", post, items });
    const motivo = stopRequested ? "interrompido" : (Date.now() - started >= MAX_MS ? "limite de tempo" : "fim da lista");
    if (res.ok) say(`✓ ${items.length} ${nome} lidos (${motivo}) · ${res.novos} novos · ${res.atualizados} atualizados`, "ok");
    else say(res.error, "err");
  }

  // ---------- Captura da lista de curtidas (janela "Curtidas" aberta por você) ----------
  function captureLikes() {
    const root = activeRoot();
    const post = currentPostInfo();
    if (root === document.querySelector("main") || root === document.body) {
      return { post, items: [], erro: "Abra a lista de curtidas ou reposts do post (clique no número de curtidas/reposts) antes de capturar." };
    }
    const titulo = textPieces(root).slice(0, 6).join(" ").toLowerCase();
    const tipo = /repost|republica|compartilh/.test(titulo) ? "repost" : "curtida";
    const items = new Map();
    for (const { a, u } of textLinks(root)) {
      if (items.has(u)) continue;
      let block = a;
      for (let i = 0; i < 6 && block.parentElement; i++) {
        const others = textLinks(block.parentElement).filter((x) => x.u !== u);
        if (others.length) break;
        block = block.parentElement;
      }
      const lines = cleanLines(block, u);
      items.set(u, { username: u, fullName: lines[0] || "", text: "", tipo });
    }
    if (post.author) items.delete(post.author);
    return { post, items: [...items.values()] };
  }

  // ---------- Captura de perfil (você abriu o perfil do lead) ----------
  function captureProfile() {
    const m = location.pathname.match(/^\/([A-Za-z0-9._]{1,30})\/?$/);
    const u = m ? m[1].toLowerCase() : null;
    if (!u || RESERVED.has(u)) return { erro: "Abra a página de um perfil (instagram.com/usuario) para capturar." };

    const header = document.querySelector("main header") || document.querySelector("header");
    const raw = header ? textPieces(header).join("\n") : "";
    const lines = (header ? cleanLines(header, u) : []).filter((l) => !/^(enviar mensagem|message|mensagem|seguir de volta|follow back|opções|options|editar perfil|edit profile|ver arquivo|view archive)$/i.test(l));

    let followers = null, following = null, posts = null;
    const countRe = /([\d.,]+\s*(mil|mi|k|m)?)\s*(seguidores|followers|seguindo|following|publicações|posts|publicação)/gi;
    let c;
    while ((c = countRe.exec(raw))) {
      const kind = c[3].toLowerCase();
      if (/seguidores|followers/.test(kind)) followers = c[1].trim();
      else if (/seguindo|following/.test(kind)) following = c[1].trim();
      else posts = c[1].trim();
    }

    // Meta tag só é confiável se for do perfil atual (o Instagram é SPA)
    const og = document.querySelector('meta[property="og:description"]')?.content || "";
    let fullName = "";
    const nm = og.match(/(?:from|de)\s+(.+?)\s+\(@([A-Za-z0-9._]+)\)/i);
    if (nm && nm[2].toLowerCase() === u) fullName = nm[1];

    const bioLines = lines.filter((l) => !/(seguidores|followers|seguindo|following|publica|posts)/i.test(l) && l !== fullName);
    const unwrap = (h) => { try { const x = new URL(h); return /l\.instagram\.com$/.test(x.hostname) && x.searchParams.get("u") ? x.searchParams.get("u") : h; } catch (e) { return h; } };
    const links = header ? [...header.querySelectorAll("a[href]")].map((a) => unwrap(a.href)).filter((h) => !/^https?:\/\/(www\.)?instagram\.com/.test(h)) : [];
    const link = links.find((h) => /^https?:/.test(h)) || null;

    return {
      profile: {
        username: u,
        fullName: fullName || bioLines[0] || "",
        bio: bioLines.join(" · ").slice(0, 800),
        followers, following, posts,
        externalLink: link || "",
        links,
        rawText: raw.slice(0, 3000)
      }
    };
  }

  // ---------- Painel flutuante (Shadow DOM para não brigar com o CSS do Instagram) ----------
  const host = document.createElement("div");
  host.style.cssText = "position:fixed;right:16px;bottom:16px;z-index:2147483647;";
  const shadow = host.attachShadow({ mode: "open" });
  shadow.innerHTML = `
    <style>
      :host { all: initial; }
      .box { font: 13px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background:#0f1720; color:#e8eef5;
             border:1px solid #2a3a4c; border-radius:12px; box-shadow:0 8px 28px rgba(0,0,0,.35); width:250px; overflow:hidden; }
      .head { display:flex; align-items:center; justify-content:space-between; padding:10px 12px; background:#14202d; cursor:pointer; }
      .head b { font-size:13px; letter-spacing:.2px; }
      .dot { width:8px; height:8px; border-radius:50%; background:#f5b301; display:inline-block; margin-right:8px; }
      .body { padding:10px 12px 12px; display:grid; gap:8px; }
      .min .body { display:none; }
      button { all:unset; box-sizing:border-box; width:100%; text-align:center; padding:8px 10px; border-radius:8px; cursor:pointer;
               background:#1d2b3a; border:1px solid #2f4357; color:#e8eef5; font-weight:600; font-size:12.5px; }
      button:hover { background:#25384b; }
      button:disabled { opacity:.45; cursor:not-allowed; }
      button.primary { background:#f5b301; border-color:#f5b301; color:#111; }
      button.primary:hover { background:#ffc21a; }
      .msg { font-size:12px; color:#a9bacb; min-height:16px; }
      .msg.ok { color:#7fe0a5; } .msg.err { color:#ff9b8f; }
      .hint { font-size:11px; color:#7f93a8; }
      .tog { font-size:16px; color:#a9bacb; }
      .opt { display:flex; align-items:center; gap:6px; font-size:12px; color:#a9bacb; margin-top:-2px; cursor:pointer; }
      .opt input { margin:0; accent-color:#f5b301; }
      button.stop { background:#b42318; border-color:#b42318; color:#fff; }
    </style>
    <div class="box" id="box">
      <div class="head" id="head"><span><span class="dot"></span><b>Copiloto de Leads</b></span><span class="tog" id="tog">–</span></div>
      <div class="body">
        <button class="primary" id="bAll">Ler TODOS os comentários</button>
        <label class="opt"><input type="checkbox" id="optReplies" checked> incluir respostas</label>
        <button id="bComments">Capturar só os visíveis</button>
        <button id="bLikes">Ler curtidas / reposts (lista aberta)</button>
        <button id="bProfile">Capturar / enriquecer perfil</button>
        <button id="bPanel">Abrir painel de leads</button>
        <div class="msg" id="msg"></div>
        <div class="hint">Abra o post com os comentários visíveis e clique em “Ler TODOS”. Ele rola só a lista de comentários, em ritmo humano, e para sozinho no fim. Duplicados são ignorados.</div>
      </div>
    </div>`;
  document.documentElement.appendChild(host);

  const $ = (id) => shadow.getElementById(id);
  const box = $("box");
  try { if (localStorage.getItem("copiloto_min") === "1") { box.classList.add("min"); $("tog").textContent = "+"; } } catch (e) { /* ignore */ }
  $("head").addEventListener("click", () => {
    box.classList.toggle("min");
    const min = box.classList.contains("min");
    $("tog").textContent = min ? "+" : "–";
    try { localStorage.setItem("copiloto_min", min ? "1" : "0"); } catch (e) { /* ignore */ }
  });

  function say(text, kind) {
    const m = $("msg");
    m.textContent = text;
    m.className = "msg " + (kind || "");
  }

  function send(msg) {
    return new Promise((resolve) => {
      try {
        chrome.runtime.sendMessage(msg, (res) => {
          if (chrome.runtime.lastError) resolve({ ok: false, error: "Extensão recarregada — atualize a página (F5)." });
          else resolve(res || { ok: false, error: "Sem resposta" });
        });
      } catch (e) {
        resolve({ ok: false, error: "Extensão recarregada — atualize a página (F5)." });
      }
    });
  }

  function setReadingUI(on, mode) {
    const id = mode === "list" ? "bLikes" : "bAll";
    const b = $(id);
    b.textContent = on ? "Parar leitura" : (mode === "list" ? "Ler curtidas / reposts (lista aberta)" : "Ler TODOS os comentários");
    if (id === "bAll") b.classList.toggle("primary", !on);
    b.classList.toggle("stop", on);
    ["bAll", "bComments", "bLikes", "bProfile"].filter((x) => x !== id).forEach((x) => ($(x).disabled = on));
  }

  $("bAll").addEventListener("click", () => {
    if (reading) { stopRequested = true; say("Parando… salvando o que já foi lido."); return; }
    readAll({ mode: "comments", replies: $("optReplies").checked });
  });

  $("bComments").addEventListener("click", async () => {
    const { post, items } = captureComments();
    if (!post.isPost) { say("Abra um post ou reel para capturar comentários.", "err"); return; }
    if (!items.length) { say("Nenhum comentário visível encontrado. Abra os comentários e tente de novo.", "err"); return; }
    const res = await send({ type: "saveCaptures", post, items });
    if (res.ok) say(`${items.length} lidos · ${res.novos} novos · ${res.atualizados} atualizados${res.bloqueados ? ` · ${res.bloqueados} na lista “não contatar”` : ""}`, "ok");
    else say(res.error, "err");
  });

  $("bLikes").addEventListener("click", () => {
    if (reading) { stopRequested = true; say("Parando… salvando o que já foi lido."); return; }
    readAll({ mode: "list" });
  });

  $("bProfile").addEventListener("click", async () => {
    const r = captureProfile();
    if (r.erro) { say(r.erro, "err"); return; }
    const res = await send({ type: "saveProfile", profile: r.profile });
    const extra = res.contatos ? ` Contato: ${res.contatos}.` : " Nenhum e-mail/telefone público na bio.";
    if (res.ok) say((res.novo ? `@${r.profile.username} adicionado.` : `@${r.profile.username} enriquecido.`) + extra, "ok");
    else say(res.error, "err");
  });

  $("bPanel").addEventListener("click", () => send({ type: "openDashboard" }));
})();
