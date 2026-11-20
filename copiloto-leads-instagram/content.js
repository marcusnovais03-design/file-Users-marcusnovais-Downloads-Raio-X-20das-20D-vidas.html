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

  // ---------- Captura da lista de curtidas (janela "Curtidas" aberta por você) ----------
  function captureLikes() {
    const root = activeRoot();
    const post = currentPostInfo();
    if (root === document.querySelector("main") || root === document.body) {
      return { post, items: [], erro: "Abra a janela de curtidas do post (clique em “curtidas”) antes de capturar." };
    }
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
      items.set(u, { username: u, fullName: lines[0] || "", text: "", tipo: "curtida" });
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
    const link = header ? [...header.querySelectorAll("a[href]")].map((a) => a.href).find((h) => !h.includes("instagram.com")) : null;

    return {
      profile: {
        username: u,
        fullName: fullName || bioLines[0] || "",
        bio: bioLines.join(" · ").slice(0, 800),
        followers, following, posts,
        externalLink: link || ""
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
      button.primary { background:#f5b301; border-color:#f5b301; color:#111; }
      button.primary:hover { background:#ffc21a; }
      .msg { font-size:12px; color:#a9bacb; min-height:16px; }
      .msg.ok { color:#7fe0a5; } .msg.err { color:#ff9b8f; }
      .hint { font-size:11px; color:#7f93a8; }
      .tog { font-size:16px; color:#a9bacb; }
    </style>
    <div class="box" id="box">
      <div class="head" id="head"><span><span class="dot"></span><b>Copiloto de Leads</b></span><span class="tog" id="tog">–</span></div>
      <div class="body">
        <button class="primary" id="bComments">Capturar comentários visíveis</button>
        <button id="bLikes">Capturar curtidas (janela aberta)</button>
        <button id="bProfile">Capturar / enriquecer perfil</button>
        <button id="bPanel">Abrir painel de leads</button>
        <div class="msg" id="msg"></div>
        <div class="hint">Role e abra “ver mais comentários” você mesmo; depois capture de novo. Duplicados são ignorados.</div>
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

  $("bComments").addEventListener("click", async () => {
    const { post, items } = captureComments();
    if (!post.isPost) { say("Abra um post ou reel para capturar comentários.", "err"); return; }
    if (!items.length) { say("Nenhum comentário visível encontrado. Abra os comentários e tente de novo.", "err"); return; }
    const res = await send({ type: "saveCaptures", post, items });
    if (res.ok) say(`${items.length} lidos · ${res.novos} novos · ${res.atualizados} atualizados${res.bloqueados ? ` · ${res.bloqueados} na lista “não contatar”` : ""}`, "ok");
    else say(res.error, "err");
  });

  $("bLikes").addEventListener("click", async () => {
    const { post, items, erro } = captureLikes();
    if (erro) { say(erro, "err"); return; }
    if (!items.length) { say("Nenhum perfil na janela. Role a lista e tente de novo.", "err"); return; }
    const res = await send({ type: "saveCaptures", post, items });
    if (res.ok) say(`${items.length} curtidas · ${res.novos} novos · ${res.atualizados} atualizados`, "ok");
    else say(res.error, "err");
  });

  $("bProfile").addEventListener("click", async () => {
    const r = captureProfile();
    if (r.erro) { say(r.erro, "err"); return; }
    const res = await send({ type: "saveProfile", profile: r.profile });
    if (res.ok) say(res.novo ? `@${r.profile.username} adicionado com dados do perfil.` : `@${r.profile.username} enriquecido.`, "ok");
    else say(res.error, "err");
  });

  $("bPanel").addEventListener("click", () => send({ type: "openDashboard" }));
})();
