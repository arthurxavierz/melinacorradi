/* Dra. Melina Corradi · Achilles Media */
(function () {
  "use strict";
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var hasIO = "IntersectionObserver" in window;
  var mobile = function () { return window.innerWidth < 860; };
  var play = function (v) { var p = v.play(); if (p && p.catch) p.catch(function () {}); };

  /* ---------- Cabeçalho, progresso e paralaxe ---------- */
  var header = $(".site-header"), bar = $(".progress-bar"), wa = $(".wa-float"), last = 0;
  var heroMove = $(".arch");
  function onScroll() {
    var y = window.scrollY, h = doc.scrollHeight - window.innerHeight;
    header.classList.toggle("is-solid", y > 40);
    var hide = y > 600 && y > last + 4 && !document.body.classList.contains("menu-open");
    if (hide) header.classList.add("is-hidden"); else if (y < last - 4 || y < 600) header.classList.remove("is-hidden");
    last = y;
    if (bar) bar.style.setProperty("--p", h > 0 ? (y / h).toFixed(4) : 0);
    if (wa) wa.classList.toggle("show", y > window.innerHeight * .6 || document.body.getAttribute("data-page") !== "index");
    if (!reduce && heroMove && y < window.innerHeight * 1.3) heroMove.style.setProperty("--hy", (y * 0.06).toFixed(1) + "px");
    fill();
    sweep();
  }
  var ticking = false;
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; onScroll(); }); } }, { passive: true });

  /* ---------- Menu tela cheia ---------- */
  var toggle = $(".menu-toggle"), overlay = $(".overlay");
  function setMenu(open) {
    overlay.setAttribute("data-open", open ? "true" : "false");
    overlay.setAttribute("aria-hidden", open ? "false" : "true");
    if (open) overlay.removeAttribute("inert"); else overlay.setAttribute("inert", "");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("menu-open", open);
    toggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
  }
  if (toggle && overlay) {
    toggle.addEventListener("click", function () { setMenu(overlay.getAttribute("data-open") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    $$("a", overlay).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
  }

  /* ---------- Vídeos de fundo: versão certa para a tela ---------- */
  var save = navigator.connection && navigator.connection.saveData;
  $$("video[data-desktop]").forEach(function (v) {
    var m = mobile() && v.getAttribute("data-mobile");
    if (m && v.getAttribute("data-poster-m")) v.poster = v.getAttribute("data-poster-m");
    if (reduce || save) return;
    if (mobile() && !m && v.closest(".hero-reels")) return; /* colunas extras não aparecem no celular */
    v.src = m ? v.getAttribute("data-mobile") : v.getAttribute("data-desktop");
    play(v);
  });

  /* prévias que só carregam perto da tela e pausam quando saem dela */
  if (!reduce && !save) {
    var vio = hasIO ? new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target, card = v.closest(".reel");
        if (en.isIntersecting) {
          if (!v.getAttribute("src")) v.src = v.getAttribute("data-src");
          play(v);
          v.addEventListener("playing", function () { if (card) card.classList.add("playing"); }, { once: true });
        } else if (v.getAttribute("src")) v.pause();
      });
    }, { rootMargin: "120px 200px" }) : null;
    $$("video[data-src]").forEach(function (v) { if (vio) vio.observe(v); });
  }

  /* ---------- Títulos que sobem palavra a palavra ---------- */
  $$("[data-split]").forEach(function (el) {
    var wi = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(" ")); return; }
            var w = document.createElement("span"), s = document.createElement("span");
            w.className = "w"; s.textContent = p; s.style.setProperty("--wi", wi++);
            w.appendChild(s); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
  });

  /* ---------- Revelação no scroll (com varredura para páginas abertas já roladas) ---------- */
  var revs = $$("[data-reveal], [data-mask], [data-split], .step");
  function show(el) { el.classList.add("in"); }
  var rio = hasIO ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { show(en.target); rio.unobserve(en.target); } });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }) : null;
  revs.forEach(function (el) { if (rio) rio.observe(el); else show(el); });
  function sweep() {
    var vh = window.innerHeight;
    revs.forEach(function (el) { if (!el.classList.contains("in") && el.getBoundingClientRect().top < vh * 0.95) show(el); });
  }
  setTimeout(sweep, 400);

  /* ---------- Manifesto que se preenche com a leitura ---------- */
  var fillEl = $("[data-fill]"), fillWords = [];
  if (fillEl) {
    var wrapWords = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(" ")); return; }
            var s = document.createElement("span"); s.textContent = p; s.style.transition = "opacity .3s"; fillWords.push(s); frag.appendChild(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) wrapWords(n);
      });
    };
    wrapWords(fillEl);
  }
  function fill() {
    if (!fillEl || reduce) return;
    var r = fillEl.getBoundingClientRect(), vh = window.innerHeight;
    var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
    var n = Math.round(p * fillWords.length);
    fillWords.forEach(function (w, k) { w.style.opacity = k < n ? 1 : 0.18; });
  }

  /* ---------- Contadores ---------- */
  var cio = hasIO ? new IntersectionObserver(function (es) {
    es.forEach(function (en) {
      if (!en.isIntersecting) return;
      var el = en.target, to = +el.getAttribute("data-count"), t0 = null;
      cio.unobserve(el);
      if (reduce) { el.textContent = to; return; }
      var step = function (t) {
        if (!t0) t0 = t;
        var p = Math.min(1, (t - t0) / 1600), e = 1 - Math.pow(1 - p, 4);
        el.textContent = Math.round(e * to);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 }) : null;
  $$("[data-count]").forEach(function (el) { if (cio) cio.observe(el); else el.textContent = el.getAttribute("data-count"); });

  /* ---------- Antes e depois ---------- */
  $$("[data-compare]").forEach(function (c) {
    var r = $("input", c);
    var set = function (v) { c.style.setProperty("--pos", v + "%"); };
    r.addEventListener("input", function () { c.classList.remove("hint"); set(r.value); });
    if (hasIO && !reduce) {
      var once = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return; once.disconnect();
        c.classList.add("hint"); set(22);
        setTimeout(function () { set(78); }, 900);
        setTimeout(function () { set(50); r.value = 50; }, 1900);
        setTimeout(function () { c.classList.remove("hint"); }, 2900);
      }, { threshold: .5 });
      once.observe(c);
    }
  });

  /* ---------- Vitrine de reels: setas e arrastar ---------- */
  $$("[data-rail]").forEach(function (rail) {
    var sec = rail.closest("section");
    var by = function (d) { var c = rail.querySelector(".reel"); rail.scrollBy({ left: d * (c ? c.offsetWidth + 16 : 300) * 2, behavior: "smooth" }); };
    var pv = $("[data-rail-prev]", sec), nx = $("[data-rail-next]", sec);
    if (pv) pv.addEventListener("click", function () { by(-1); });
    if (nx) nx.addEventListener("click", function () { by(1); });
    var down = false, sx = 0, sl = 0, moved = false;
    rail.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") return; down = true; moved = false; sx = e.clientX; sl = rail.scrollLeft; });
    window.addEventListener("pointermove", function (e) { if (!down) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) { moved = true; rail.classList.add("drag"); } rail.scrollLeft = sl - dx; });
    window.addEventListener("pointerup", function () { down = false; rail.classList.remove("drag"); });
    rail.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });

  /* ---------- Modal de vídeo ---------- */
  var vm = $("#vmodal"), vmv = vm && $("video", vm), lastFocus = null;
  function openVideo(el) {
    if (!vm) return;
    lastFocus = el;
    vmv.src = el.getAttribute("data-full");
    $(".vm-title", vm).textContent = el.getAttribute("data-title") || "";
    $(".vm-cap", vm).textContent = el.getAttribute("data-cap") || "";
    $(".vm-cat", vm).textContent = el.getAttribute("data-cat") || el.getAttribute("data-catname") || "";
    var ig = $(".vm-ig", vm); if (ig && el.getAttribute("data-ig")) ig.href = el.getAttribute("data-ig");
    vm.setAttribute("aria-hidden", "false"); vm.removeAttribute("inert");
    document.body.style.overflow = "hidden";
    play(vmv);
    $(".vmodal-close", vm).focus();
  }
  function closeVideo() {
    if (!vm || vm.getAttribute("aria-hidden") === "true") return;
    vmv.pause(); vmv.removeAttribute("src"); vmv.load();
    vm.setAttribute("aria-hidden", "true"); vm.setAttribute("inert", "");
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  if (vm) {
    $(".vmodal-close", vm).addEventListener("click", closeVideo);
    vm.addEventListener("click", function (e) { if (e.target === vm) closeVideo(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeVideo(); });
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-full]");
    if (el) { e.preventDefault(); openVideo(el); }
  });

  /* ---------- Lightbox de fotos ---------- */
  var lb = $(".lightbox");
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-img]");
    if (!el || !lb) return;
    $("img", lb).src = el.getAttribute("data-img");
    $("img", lb).alt = el.getAttribute("data-title") || "";
    $("p", lb).textContent = el.getAttribute("data-title") || "";
    if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
  });
  if (lb) {
    $(".lb-close", lb).addEventListener("click", function () { lb.close(); });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
  }

  /* ---------- Filtro da galeria ---------- */
  var mosaic = $("[data-mosaic]");
  if (mosaic) {
    var fbtns = $$(".filters button");
    fbtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-f");
        fbtns.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        $$(".tile", mosaic).forEach(function (t) { t.hidden = f !== "todas" && t.getAttribute("data-cat") !== f; });
      });
    });
  }

  /* ---------- Formulário de agendamento → WhatsApp ---------- */
  var form = $("[data-wa-form]");
  if (form) {
    var prev = $("[data-wa-preview]");
    var val = function (n) { var el = form.elements[n]; return el ? String(el.value || "").trim() : ""; };
    var checked = function (n) { return $$('input[name="' + n + '"]:checked', form).map(function (i) { return i.value; }); };
    var fmtDate = function (s) {
      if (!s) return "";
      var p = s.split("-"); var d = new Date(+p[0], +p[1] - 1, +p[2]);
      var dias = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"];
      return p[2] + "/" + p[1] + "/" + p[0] + " (" + dias[d.getDay()] + ")";
    };
    var msg = function () {
      var L = ["Olá, Dra. Melina! Vim pelo site e gostaria de agendar uma avaliação.", ""];
      if (val("nome")) L.push("*Nome:* " + val("nome"));
      if (val("idade")) L.push("*Idade:* " + val("idade") + " anos");
      var sv = checked("tratamento"); if (sv.length) L.push("*Tratamento:* " + sv.join(", "));
      var dt = fmtDate(val("data"));
      var ag = [dt, val("hora") ? "às " + val("hora") : "", checked("periodo")[0] ? "período: " + checked("periodo")[0].toLowerCase() : ""].filter(Boolean).join(", ");
      if (ag) L.push("*Sugestão de agenda:* " + ag);
      if (checked("paciente")[0]) L.push("*Paciente:* " + checked("paciente")[0].toLowerCase());
      if (val("obs")) L.push("*Observações:* " + val("obs"));
      return L.join("\n");
    };
    var render = function () {
      if (!prev) return;
      var m = msg();
      if (m.split("\n").length <= 2) { prev.innerHTML = "<em>Sua mensagem aparece aqui enquanto você preenche…</em>"; return; }
      prev.textContent = "";
      m.split("\n").forEach(function (line, k) {
        if (k) prev.appendChild(document.createTextNode("\n"));
        line.split(/(\*[^*]+\*)/).forEach(function (part) {
          if (/^\*[^*]+\*$/.test(part)) { var b = document.createElement("b"); b.textContent = part.slice(1, -1); prev.appendChild(b); }
          else if (part) prev.appendChild(document.createTextNode(part));
        });
      });
      var now = new Date(); prev.setAttribute("data-time", String(now.getHours()).padStart(2, "0") + ":" + String(now.getMinutes()).padStart(2, "0"));
    };
    /* tratamento vindo da página de tratamentos (?tratamento=Implantes dentários) */
    var q = new URLSearchParams(location.search).get("tratamento");
    if (q) {
      var map = { "Clareamento dental": "Clareamento", "Implantes dentários": "Implante", "Próteses e coroas": "Prótese ou coroa", "Ortodontia": "Aparelho ortodôntico", "Limpeza e prevenção": "Limpeza", "Restaurações": "Restauração", "Cirurgias e siso": "Siso ou extração", "Harmonização facial": "Harmonização facial" };
      var target = map[q] || q;
      $$('input[name="tratamento"]', form).forEach(function (i) { if (i.value === target) i.checked = true; });
    }
    var dateIn = form.elements.data;
    if (dateIn) { var t = new Date(); dateIn.min = t.getFullYear() + "-" + String(t.getMonth() + 1).padStart(2, "0") + "-" + String(t.getDate()).padStart(2, "0"); }
    form.addEventListener("input", function (e) { render(); var f = e.target.closest("[data-field]"); if (f) f.classList.remove("invalid"); });
    form.addEventListener("change", render);
    render();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = [];
      if (!val("nome")) bad.push("nome");
      var idade = +val("idade"); if (!idade || idade < 1 || idade > 120) bad.push("idade");
      if (!checked("tratamento").length) bad.push("tratamento");
      if (!val("data")) bad.push("data");
      $$("[data-field]", form).forEach(function (f) { f.classList.toggle("invalid", bad.indexOf(f.getAttribute("data-field")) > -1); });
      if (bad.length) {
        var first = $('[data-field="' + bad[0] + '"]', form);
        first.scrollIntoView({ behavior: "smooth", block: "center" });
        var inp = $("input", first); if (inp) setTimeout(function () { inp.focus({ preventScroll: true }); }, 350);
        return;
      }
      window.open("https://wa.me/" + form.getAttribute("data-wa") + "?text=" + encodeURIComponent(msg()), "_blank", "noopener");
    });
  }

  /* ---------- Rodapé ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
  $$("[data-top]").forEach(function (b) { b.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); }); });

  onScroll();
})();
