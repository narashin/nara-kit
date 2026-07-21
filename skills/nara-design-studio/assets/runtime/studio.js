/*
 * design-studio runtime (plain Claude Code, vanilla DOM — no build/React).
 * Reads window.STUDIO_CONFIG + .studio-candidate[data-id] slots, renders the
 * top bar (candidate switcher, fidelity badge, comment mode, interaction mode,
 * Send to Agent, export) and owns all interaction state. Colors via CSS custom
 * properties (design tokens) only.
 *
 * Config shape:
 *   window.STUDIO_CONFIG = {
 *     title, brief,
 *     pack: { name, namespace, sourceRepo, sourcePackages, kitHelpersPath, reuseRule },
 *     candidates: [{ id, label, note, interactions: [{ target, action }] }],
 *     fidelity: "wireframe" | "styled"
 *   }
 *
 * studio.js owns ONLY the studio chrome (candidate switcher, fidelity badge, comment mode,
 * Send-to-Agent) and candidate show/hide + comment pins. It does NOT render the app shell.
 * Each candidate mounts a <Shell> built from the REAL DS bundle (window[pack.namespace], per the pack config):
 * DS.Header + DS.LeftNav fed the pack's nav data (data.js), so the header/left-nav are the
 * actual product components, never a token recreation. See studio-template.html and the
 * template's own "T2+ REAL PACK MOUNT" guidance block for the pattern.
 */
(function () {
  "use strict";

  function h(tag, attrs, children) {
    var e = document.createElement(tag);
    attrs = attrs || {};
    Object.keys(attrs).forEach(function (k) {
      if (k === "class") e.className = attrs[k];
      else if (k === "html") e.innerHTML = attrs[k];
      else if (k.indexOf("on") === 0 && typeof attrs[k] === "function") e.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c != null) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function icons() { if (window.lucide) window.lucide.createIcons(); }

  var cfg, root, stage, bar, noteLayer;
  var state = { activeId: null, pickedId: null, wireframe: false, commentMode: false, comments: [], seq: 0,
                interactionMode: false, specOverride: {} };

  function candidateEls() { return Array.prototype.slice.call(stage.querySelectorAll(".studio-candidate")); }
  function confOf(id) { return (cfg.candidates || []).find(function (x) { return x.id === id; }) || null; }
  function labelOf(id) { var c = confOf(id); return c ? c.label : id; }
  function noteOf(id) { var c = confOf(id); return c ? (c.note || "") : ""; }

  /* ---- candidate switcher + fidelity ---- */
  function setActive(id) {
    state.activeId = id;
    candidateEls().forEach(function (el) { el.classList.toggle("is-active", el.getAttribute("data-id") === id); });
    Array.prototype.forEach.call(bar.querySelectorAll(".studio-tab"), function (t) { t.classList.toggle("is-active", t.getAttribute("data-id") === id); });
    var strip = root.querySelector(".studio-note-strip");
    if (strip) strip.textContent = noteOf(id);
    clearNoteEditor();
    renderPins();
    /* interaction hotspots need the (React-mounted) target elements; retry to catch async mount. */
    renderHotspots();
    setTimeout(renderHotspots, 250);
    icons();
  }
  function pick(id) {
    state.pickedId = id;
    Array.prototype.forEach.call(bar.querySelectorAll(".studio-tab"), function (t) { t.classList.toggle("is-picked", t.getAttribute("data-id") === state.pickedId); });
  }
  /* Fidelity is a build-time choice (config.fidelity), applied once — not a live toggle. */
  function setFidelity(wire) {
    state.wireframe = wire;
    document.body.classList.toggle("wireframe", wire);
  }

  /* ---- comment mode ---- */
  var hoverEl = null;
  function clearHover() { if (hoverEl) { hoverEl.classList.remove("studio-hover"); hoverEl = null; } }
  function onStageHover(ev) {
    if (!state.commentMode && !state.interactionMode) return;
    var active = stage.querySelector(".studio-candidate.is-active");
    var t = active && active.contains(ev.target) && ev.target !== active ? ev.target : null;
    /* Interaction mode targets labeled COMPONENTS only — snap the highlight to the nearest
       [data-studio-label] so it's clear you're picking a component, not a raw DOM node/selector.
       Comment mode is unchanged (any element is fair game for a note). */
    if (t && state.interactionMode) {
      t = t.closest ? t.closest("[data-studio-label]") : null;
      if (t && !active.contains(t)) t = null;
    }
    if (t === hoverEl) return;
    clearHover();
    if (t) { hoverEl = t; t.classList.add("studio-hover"); }
  }
  function setCommentMode(on) {
    if (on && state.interactionMode) setInteractionMode(false);   // the two modes are mutually exclusive
    state.commentMode = on;
    document.body.classList.toggle("comment-mode", on);
    var b = bar.querySelector('[data-role="comment"]');
    if (b) b.classList.toggle("is-active", on);
    clearNoteEditor();
    if (!on) clearHover();
    if (on) flash("Hover to preview the target, click an element to leave a note, then 'Send to Agent'.");
  }
  /* Interaction mode — author the behavior spec in-browser (add/edit/delete), auto-saved to the sidecar. */
  function setInteractionMode(on) {
    if (on && state.commentMode) setCommentMode(false);
    state.interactionMode = on;
    document.body.classList.toggle("spec-mode", on);
    var b = bar.querySelector('[data-role="spec"]');
    if (b) b.classList.toggle("is-active", on);
    clearNoteEditor();
    if (!on) clearHover();
    renderLegends();   // toggle the "editing" hint in the legend header
    if (on) flash("Interaction mode: click an element to set / edit what it does. Saved automatically. Click a labeled element again to edit or delete.");
  }
  function hintFor(el) {
    var labelled = el.closest ? el.closest("[data-studio-label]") : null;
    if (labelled) return labelled.getAttribute("data-studio-label");
    var txt = (el.textContent || "").trim().replace(/\s+/g, " ");
    if (txt) return txt.length > 40 ? txt.slice(0, 40) + "…" : txt;
    return el.tagName.toLowerCase() + (el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : "");
  }
  /* A precise CSS selector scoped to the candidate — so Claude can target the exact element. */
  function selectorFor(el) {
    var root = el.closest ? el.closest(".studio-candidate") : null;
    if (!root) return el.tagName ? el.tagName.toLowerCase() : "";
    var base = '[data-id="' + root.getAttribute("data-id") + '"]';
    if (el === root) return base;
    var parts = [], cur = el;
    while (cur && cur !== root) {
      if (cur.getAttribute && cur.getAttribute("data-studio-label")) { parts.unshift('[data-studio-label="' + cur.getAttribute("data-studio-label") + '"]'); break; }
      if (cur.id) { parts.unshift("#" + cur.id); break; }
      var sel = cur.tagName.toLowerCase(), p = cur.parentElement;
      if (p) {
        var same = Array.prototype.filter.call(p.children, function (c) { return c.tagName === cur.tagName; });
        if (same.length > 1) sel += ":nth-of-type(" + (Array.prototype.indexOf.call(p.children, cur) + 1) + ")";
      }
      parts.unshift(sel);
      cur = cur.parentElement;
    }
    return base + " " + parts.join(" > ");
  }
  function clearNoteEditor() { if (noteLayer) { var open = noteLayer.querySelector(".studio-note[data-editing]"); if (open) open.remove(); } }

  function onStageClick(ev) {
    if (!state.commentMode && !state.interactionMode) return;
    var active = stage.querySelector(".studio-candidate.is-active");
    if (!active || !active.contains(ev.target)) return;
    ev.preventDefault(); ev.stopPropagation();
    clearNoteEditor();
    var srect = stage.getBoundingClientRect();
    var x = ev.clientX - srect.left + stage.scrollLeft;
    var y = ev.clientY - srect.top + stage.scrollTop;
    if (state.interactionMode) { openSpecEditor(ev.target, x, y); return; }
    /* Anchor the pin to the target element as a ratio of its box, so it survives window
       resize / reflow (px-only coords drift off-target). x/y are kept as a fallback. */
    var tgt = ev.target;
    var trect = tgt.getBoundingClientRect();
    var rx = trect.width ? (ev.clientX - trect.left) / trect.width : 0.5;
    var ry = trect.height ? (ev.clientY - trect.top) / trect.height : 0.5;
    var hint = hintFor(ev.target);
    var selector = selectorFor(ev.target);
    var editor = h("div", { class: "studio-note", "data-editing": "1", style: "left:" + x + "px;top:" + y + "px" }, [
      h("div", { class: "target" }, ["[" + labelOf(state.activeId) + "] " + hint]),
      h("textarea", { rows: "3", placeholder: "What should change here?" }),
    ]);
    var ta = editor.querySelector("textarea");
    var row = h("div", { class: "row" }, [
      h("button", { class: "studio-btn", onClick: function () { editor.remove(); } }, ["Cancel"]),
      h("button", { class: "studio-btn is-active", onClick: function () {
        var note = ta.value.trim(); if (!note) { editor.remove(); return; }
        state.seq += 1;
        state.comments.push({ n: state.seq, candidateId: state.activeId, candidateLabel: labelOf(state.activeId), selector: selector, hint: hint, note: note, x: x, y: y, rx: rx, ry: ry });
        editor.remove(); renderPins(); updateCount();
      } }, ["Add"]),
    ]);
    editor.appendChild(row);
    noteLayer.appendChild(editor);
    ta.focus();
  }
  /* Live pin position from the target element's current box (resize/reflow-safe); falls back to
     the stored click coords when the element can't be found. */
  function pinPos(c) {
    var el = c.selector ? stage.querySelector(c.selector) : null;
    if (el) {
      var er = el.getBoundingClientRect(), sr = stage.getBoundingClientRect();
      if (er.width || er.height) {
        return {
          x: er.left - sr.left + stage.scrollLeft + (c.rx != null ? c.rx : 0.5) * er.width,
          y: er.top - sr.top + stage.scrollTop + (c.ry != null ? c.ry : 0.5) * er.height,
        };
      }
    }
    return { x: c.x, y: c.y };
  }
  function renderPins() {
    noteLayer.querySelectorAll(".studio-pin").forEach(function (p) { p.remove(); });
    state.comments.filter(function (c) { return c.candidateId === state.activeId; }).forEach(function (c) {
      var pos = pinPos(c);
      noteLayer.appendChild(h("div", { class: "studio-pin", title: c.hint + " — " + c.note, style: "left:" + pos.x + "px;top:" + pos.y + "px" }, [String(c.n)]));
    });
  }

  /* ---- interaction spec: a numbered legend (part of the page, so it lands in screenshots) +
     hotspot badges anchored to each target element ([data-studio-label="…"]).
     Source per candidate = the sidecar override (state.specOverride[id], authored in-browser via
     Interaction mode and persisted to <name>.interactions.json) if present, else the config
     defaults (candidates[i].interactions). Interaction mode lets the user add / edit / delete these
     live, seeding from the config defaults on first change. ---- */
  function interactionsOf(id) {
    if (state.specOverride && state.specOverride[id]) return state.specOverride[id];
    var c = confOf(id);
    return (c && c.interactions) || [];
  }
  /* Get a mutable working list for a candidate, seeded (copied) from config defaults on first edit. */
  function workingSpec(id) {
    if (!state.specOverride[id]) {
      state.specOverride[id] = interactionsOf(id).map(function (x) { return { target: x.target, action: x.action }; });
    }
    return state.specOverride[id];
  }
  function upsertSpec(target, action) {
    var list = workingSpec(state.activeId);
    var e = list.filter(function (it) { return it.target === target; })[0];
    if (e) e.action = action; else list.push({ target: target, action: action });
    afterSpecChange();
  }
  function removeSpec(target) {
    var list = workingSpec(state.activeId);
    for (var i = 0; i < list.length; i++) { if (list[i].target === target) { list.splice(i, 1); break; } }
    afterSpecChange();
  }
  function afterSpecChange() { renderLegends(); renderHotspots(); icons(); persistSpec(); }

  function renderLegends() {
    candidateEls().forEach(function (cand) {
      var old = cand.querySelector(".studio-interactions");
      if (old) old.remove();
      var list = interactionsOf(cand.getAttribute("data-id"));
      if (!list || !list.length) return;
      var items = list.map(function (it, i) {
        return h("li", {}, [
          h("span", { class: "studio-int-n" }, [String(i + 1)]),
          h("span", { class: "studio-int-tgt" }, [it.target || ""]),
          h("span", { class: "studio-int-arrow" }, ["→"]),
          h("span", { class: "studio-int-act" }, [it.action || ""]),
        ]);
      });
      cand.appendChild(h("div", { class: "studio-interactions", "data-studio-label": "interactions" }, [
        h("div", { class: "studio-int-h" }, ["Interactions", state.interactionMode ? h("span", { class: "studio-int-editing" }, ["editing — click an element"]) : null]),
        h("ol", { class: "studio-int-list" }, items),
      ]));
    });
  }
  function renderHotspots() {
    noteLayer.querySelectorAll(".studio-hotspot").forEach(function (b) { b.remove(); });
    var cand = stage.querySelector(".studio-candidate.is-active");
    if (!cand) return;
    var list = interactionsOf(cand.getAttribute("data-id"));
    if (!list || !list.length) return;
    var sr = stage.getBoundingClientRect();
    list.forEach(function (it, i) {
      if (!it.target) return;
      var el;
      try { el = cand.querySelector('[data-studio-label="' + it.target + '"]'); } catch (e) { el = null; }
      if (!el) return;
      var er = el.getBoundingClientRect();
      if (!er.width && !er.height) return;
      var x = er.right - sr.left + stage.scrollLeft - 5;
      var y = er.top - sr.top + stage.scrollTop + 5;
      noteLayer.appendChild(h("div", { class: "studio-hotspot", title: it.action || "", style: "left:" + x + "px;top:" + y + "px" }, [String(i + 1)]));
    });
  }

  /* per-output sidecar url: /path/<name>.html -> /path/<name>.interactions.json */
  function sidecarUrl() { return location.pathname.replace(/\.html?$/, ".interactions.json"); }
  function loadSpecOverride() {
    return fetch(sidecarUrl(), { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && typeof j === "object") state.specOverride = j; })
      .catch(function () { /* no sidecar yet — config defaults stand */ });
  }
  /* Persist the whole override map to the sidecar via serve.py; clipboard/preview fallback if no server. */
  function persistSpec() {
    var body = JSON.stringify({ file: sidecarUrl(), interactions: state.specOverride });
    fetch("/__interactions", { method: "POST", headers: { "Content-Type": "application/json" }, body: body })
      .then(function (r) { if (!r.ok) throw new Error("no server"); flash("Interaction spec saved"); })
      .catch(function () {
        var name = sidecarUrl().split("/").pop();
        showResult("No capture server — save this as " + name, "Create that file next to the HTML (or run serve.py) so the spec sticks on reload.", JSON.stringify(state.specOverride, null, 2));
      });
  }
  /* Interaction-mode editor: click an element to set/edit/delete what it does. */
  function openSpecEditor(el, x, y) {
    /* Interactions attach to labeled components only — never a raw DOM selector (misleading, and
       hotspots anchor by data-studio-label). If the click isn't inside a labeled element, guide out. */
    var labelled = el.closest ? el.closest("[data-studio-label]") : null;
    if (!labelled) { flash("Interactions attach to labeled components only — click a highlighted element."); return; }
    clearNoteEditor();
    var target = labelled.getAttribute("data-studio-label");
    var existing = interactionsOf(state.activeId).filter(function (it) { return it.target === target; })[0];
    var editor = h("div", { class: "studio-note", "data-editing": "1", "data-spec": "1", style: "left:" + x + "px;top:" + y + "px" }, [
      h("div", { class: "target" }, ["[interaction] " + target]),
      h("textarea", { rows: "3", placeholder: "What happens when this is used? (e.g. opens the WFPF item / opens a modal / navigates to …)" }),
    ]);
    var ta = editor.querySelector("textarea");
    if (existing) ta.value = existing.action;
    var buttons = [];
    if (existing) buttons.push(h("button", { class: "studio-btn", onClick: function () { removeSpec(target); editor.remove(); } }, ["Delete"]));
    buttons.push(h("button", { class: "studio-btn", onClick: function () { editor.remove(); } }, ["Cancel"]));
    buttons.push(h("button", { class: "studio-btn is-active", onClick: function () {
      var action = ta.value.trim(); if (!action) { editor.remove(); return; }
      upsertSpec(target, action); editor.remove();
    } }, [existing ? "Save" : "Add"]));
    editor.appendChild(h("div", { class: "row" }, buttons));
    noteLayer.appendChild(editor);
    ta.focus();
  }
  function updateCount() {
    var badge = bar.querySelector(".studio-count");
    if (badge) badge.textContent = String(state.comments.length);
    if (badge) badge.style.display = state.comments.length ? "inline-flex" : "none";
  }
  function commentsText() {
    return state.comments.map(function (c) { return "[" + c.candidateLabel + "] [" + c.hint + "]  " + c.note + "   (" + c.selector + ")"; }).join("\n");
  }
  /* Primary path: POST comments to the capture server (serve.py) → the agent reads out/comments.jsonl.
     Fallback (plain http.server / file://): copy to clipboard so the user can paste into chat. */
  function sendToAgent() {
    if (!state.comments.length) {
      flash("No comments yet. Turn on 'Comment', click any element to leave a note, then send.");
      return;
    }
    var text = commentsText(), n = state.comments.length;
    var payload = JSON.stringify({ url: location.href, comments: state.comments });
    fetch("/__comments", { method: "POST", headers: { "Content-Type": "application/json" }, body: payload })
      .then(function (r) { if (!r.ok) throw new Error("no capture"); state.comments = []; renderPins(); updateCount();
        showResult("Sent " + n + " comment" + (n > 1 ? "s" : "") + " to the agent", "Captured to out/comments.jsonl. If the agent doesn't pick it up automatically, just say “apply my comments” in the chat.", text); })
      .catch(function () {
        var done = function () { showResult("Copied " + n + " comment" + (n > 1 ? "s" : "") + " to clipboard", "No capture server running — paste into the chat and the agent will apply them.", text); };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
        else { fallbackCopy(text); done(); }
      });
  }
  function showResult(title, hint, text) {
    var existing = document.querySelector(".studio-copied"); if (existing) existing.remove();
    var box = h("div", { class: "studio-copied" }, [
      h("div", { class: "studio-copied-head" }, [
        h("strong", {}, [title]),
        h("button", { class: "studio-btn", onClick: function () { box.remove(); } }, ["Close"]),
      ]),
      h("p", { class: "studio-copied-hint" }, [hint]),
      h("pre", {}, [text]),
    ]);
    document.body.appendChild(box);
  }
  function fallbackCopy(text) {
    var ta = h("textarea", { style: "position:fixed;opacity:0" }); ta.value = text; document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) { /* clipboard unavailable */ }
    ta.remove();
  }
  function flash(msg) {
    var f = h("div", { style: "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:200;background:var(--studio-ink);color:#fff;font-size:13px;padding:8px 14px;border-radius:var(--studio-radius)" }, [msg]);
    document.body.appendChild(f); setTimeout(function () { f.remove(); }, 2400);
  }

  /* ---- export (handoff) ----
     PDF = window.print() (dep-free, universal; print CSS stacks all candidates, hides chrome).
     Spec.md = a structured handoff that POINTS AT the real code (this HTML built from real DS
     components + the pack's source repo) so implementers reuse, not recreate — the md is an index, not a
     standalone that can drift. PNG is intentionally not a button (needs agent/playwright; PDF +
     OS screenshot cover it). */
  function exportPDF() { window.print(); }
  /* Trigger a real browser download (→ the user's Downloads folder). */
  function downloadFile(name, content, mime) {
    var blob = new Blob([content], { type: mime || "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = h("a", { href: url, download: name });
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  /* PNG can't be produced from browser JS reliably, so request a capture of the CURRENT candidate
     (one at a time) and let an agent with a browser MCP fulfill it — same watch-loop as comments
     (serve.py logs it to out/capture-requests.jsonl; watch-captures.sh wakes the agent). No server
     → show the recipe to run manually. */
  function exportPNG() {
    var id = state.activeId, label = labelOf(id);
    var recipe = "Capture the current candidate (“" + label + "”, data-id=" + id + ") of " + location.href + " as a full-page PNG.";
    var body = JSON.stringify({ url: location.href, candidateId: id, candidateLabel: label });
    /* PNG is NOT an instant browser download (JS can't rasterize the DOM reliably) — it's an
       agent-fulfilled capture. Always show a persistent box so the click never looks like a no-op. */
    fetch("/__capture", { method: "POST", headers: { "Content-Type": "application/json" }, body: body })
      .then(function (r) { if (!r.ok) throw new Error("no server"); showResult(
        "PNG requested for “" + label + "” — an agent captures it",
        "PNG can't be made in the browser, so this logged a request for this one candidate. An agent running watch-captures.sh with a browser MCP saves it to your Downloads folder now (<name>-" + id + ".png). Not watching? Just tell your agent “capture this candidate”. No browser-MCP agent at all → use PDF or an OS screenshot (⌘⇧4).",
        recipe); })
      .catch(function () { showResult(
        "PNG needs an agent with a browser MCP",
        "No capture server. Tell your agent the line below to shoot the current candidate, or use PDF from this menu / an OS screenshot (⌘⇧4).",
        recipe); });
  }

  /* ---- rendered-component introspection (React fiber) for the Spec.md handoff ----
     Reads the REAL component names + key props off the live React tree that the pack
     mounted, so the handoff doc carries a structural map without opening the HTML.
     Pack-agnostic: works for any React-rendered pack; degrades to null for a
     token-only pack (namespace "") or when React isn't present. */
  function reactRootFiber(container) {
    if (!container) return null;
    var ck = Object.keys(container).find(function (x) { return x.indexOf("__reactContainer$") === 0; });
    if (ck && container[ck] && container[ck].current) return container[ck].current;
    var child = container.firstElementChild;                       // fallback: climb from a child fiber to the root
    var fk = child && Object.keys(child).find(function (x) { return x.indexOf("__reactFiber$") === 0 || x.indexOf("__reactInternalInstance$") === 0; });
    var f = fk ? child[fk] : null;
    while (f && f.return) f = f.return;
    return f;
  }
  function fiberCompName(type) {
    if (!type || typeof type === "string") return null;           // null / host component (div, span…) → skip
    if (typeof type === "function") return type.displayName || type.name || null;
    if (typeof type === "object") {                               // memo / forwardRef wrappers
      if (type.displayName) return type.displayName;
      if (type.render) return type.render.displayName || type.render.name || null;
      if (type.type) return fiberCompName(type.type);
    }
    return null;
  }
  function fiberKeyProps(props) {
    if (!props) return "";
    var out = [];
    Object.keys(props).forEach(function (k) {
      if (out.length >= 4) return;                                 // cap: a handoff wants signal, not every prop
      if (k === "children" || k === "className" || k === "style" || k === "key" || k === "ref") return;
      var v = props[k], t = typeof v;
      if (t === "string") out.push(k + '="' + (v.length <= 32 ? v : v.slice(0, 29) + "…") + '"');
      else if (t === "number" || t === "boolean") out.push(k + "=" + v);
      /* skip functions / objects / arrays — too noisy for a handoff */
    });
    return out.join(" ");
  }
  function walkFiber(fiber, depth, acc, budget) {
    while (fiber) {                                                // siblings via loop, children via recursion; fiber trees are acyclic
      if (budget.n >= budget.max) { budget.truncated = true; return; }
      var name = fiberCompName(fiber.type), nextDepth = depth;
      if (name) {                                                  // host nodes descend without emitting/indenting
        budget.n++;
        var props = fiberKeyProps(fiber.memoizedProps);
        acc.push(new Array(depth + 1).join("  ") + "- " + name + (props ? "  " + props : ""));
        nextDepth = depth + 1;
      }
      if (fiber.child) walkFiber(fiber.child, nextDepth, acc, budget);
      fiber = fiber.sibling;
    }
  }
  function componentTreeFor(id) {
    var mount = document.getElementById("mnt-" + id);
    if (!mount) {
      var sec = candidateEls().find(function (el) { return el.getAttribute("data-id") === id; });
      mount = sec ? (sec.querySelector("[id^='mnt-']") || sec) : null;
    }
    var rootFiber = reactRootFiber(mount);
    if (!rootFiber) return null;
    var acc = [], budget = { n: 0, max: 120, truncated: false };
    walkFiber(rootFiber.child || rootFiber, 0, acc, budget);
    if (!acc.length) return null;
    if (budget.truncated) acc.push("  … (tree truncated at " + budget.max + " components)");
    return acc.join("\n");
  }

  function generateSpecMarkdown() {
    var L = [];
    L.push("# " + (cfg.title || (cfg.pack && cfg.pack.name ? cfg.pack.name + " screen" : "Design") ) + " — Interaction & Implementation Spec");
    L.push("");
    if (cfg.brief) { L.push("_" + cfg.brief + "_"); L.push(""); }
    L.push("## How to use this spec (implementer)");
    L.push("");
    L.push("This is an **index** — pair it with the exported image and the real components:");
    L.push("");
    L.push("1. **Visual reference = the exported PNG / PDF** (from this design's Export → PNG/PDF, handed off alongside this file). It opens anywhere and shows the screen plus the Interactions legend — no repo needed.");
    L.push("2. **Behavior = the Interactions list below** (element → result): what each button/link/row does, which modal opens, where it navigates.");
    var pk = cfg.pack || {};
    var repo = pk.sourceRepo || "the design system source";
    var pkgs = (pk.sourcePackages && pk.sourcePackages.length) ? " (" + pk.sourcePackages.join(", ") + ")" : "";
    if (pk.sourceRepo) {
      L.push("3. **Implement by REUSING the design system's real components** — do NOT recreate from tokens. " + (pk.reuseRule || "Reuse the DS components; do not recreate.") + " Real source of truth: **" + repo + "**" + pkgs + ". The **Component tree** under each direction names the real components to map to your imports.");
    } else {
      L.push("3. **Implement by REUSING the design system's real components** — do NOT recreate from tokens. ⚠️ **Pack metadata missing**: this pack's manifest has no `pack.sourceRepo` / `sourcePackages` / `reuseRule`, so the real import source can't be named here — populate the pack manifest's `pack.*` block (see the nara-design-pack-builder skill) for a correct source-of-truth line. Meanwhile, map from the **Component tree** under each direction (real rendered component names) to your design system's imports.");
    }
    L.push("4. **Live prototype:** serve this design with the nara-design-studio runtime (`serve.py --pack <packDir> --out <outDir>`) and open this file — the live, interactive render with the real DS components. Finalized handoffs live under the output dir's `handoff/`.");
    /* Emphasize the chosen direction: emit the Selected candidate first, mark the rest as alternatives. */
    var pickedId = state.pickedId;
    var ordered = candidateEls();
    if (pickedId) {
      ordered = ordered.slice().sort(function (a, b) {
        return (b.getAttribute("data-id") === pickedId ? 1 : 0) - (a.getAttribute("data-id") === pickedId ? 1 : 0);
      });
      L.push(""); L.push("> **Selected direction: " + labelOf(pickedId) + "** — the other candidate(s) below are alternatives considered, kept for context.");
    } else {
      L.push(""); L.push("> _No candidate selected in the studio — all directions below are still open. Use a tab's **Select** to mark the chosen one before final handoff._");
    }
    ordered.forEach(function (cand) {
      var id = cand.getAttribute("data-id");
      var tag = pickedId ? (id === pickedId ? "  _(selected)_" : "  _(alternative)_") : "";
      L.push(""); L.push("## " + labelOf(id) + tag);
      var note = noteOf(id); if (note) { L.push(""); L.push(note); }
      L.push(""); L.push("### Interactions (element → result)");
      var list = interactionsOf(id);
      if (list && list.length) list.forEach(function (it, i) { L.push((i + 1) + ". **" + it.target + "** → " + it.action); });
      else L.push("_none specified_");
      var labels = [];
      cand.querySelectorAll("[data-studio-label]").forEach(function (el) { var l = el.getAttribute("data-studio-label"); if (l && labels.indexOf(l) < 0) labels.push(l); });
      L.push(""); L.push("### Labeled regions"); L.push(labels.length ? labels.map(function (l) { return "`" + l + "`"; }).join(", ") : "_none_");
      var tree = componentTreeFor(id);
      L.push(""); L.push("### Component tree (as rendered)");
      if (tree) {
        L.push("Real component names + key props read from the live React render — map these to your design system's imports.");
        L.push(""); L.push("```"); L.push(tree); L.push("```");
      } else {
        L.push("_Token-built (no mounted components) or React unavailable — see the HTML source for structure._");
      }
    });
    L.push(""); L.push("## Components");
    var ns = pk.namespace ? "`window." + pk.namespace + "`" : "the DS bundle";
    var kit = pk.kitHelpersPath ? " plus the `KIT` helpers in `" + pk.kitHelpersPath + "`" : "";
    L.push("Composed from " + ns + kit + ". Read the JSX in the source file for the exact components + props, and reuse them. Genuinely-new UI (token-built) is the only thing to implement from scratch.");
    return L.join("\n");
  }
  function exportSpec() {
    var md = generateSpecMarkdown();
    var url = location.pathname.replace(/\.html?$/, ".spec.md");
    var name = url.split("/").pop();
    downloadFile(name, md, "text/markdown;charset=utf-8");   // → the browser's Downloads folder
    /* best-effort: also drop a copy next to the HTML for the agent/repo (ignored if no server) */
    fetch("/__spec", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ file: url, markdown: md }) }).catch(function () {});
    flash("Downloaded " + name + " — hand it off together with the HTML source (real DS components).");
  }
  function toggleExportMenu(anchor) {
    var open = document.querySelector(".studio-export");
    if (open) { open.remove(); return; }
    var menu = h("div", { class: "studio-export" }, [
      h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportSpec(); } }, [h("i", { "data-lucide": "file-text" }), "Spec.md — implementer handoff"]),
      h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportPNG(); } }, [h("i", { "data-lucide": "image" }), "PNG per candidate — needs a browser-MCP agent"]),
      h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportPDF(); } }, [h("i", { "data-lucide": "printer" }), "PDF — print / Save as PDF (all candidates)"]),
      h("div", { class: "studio-export-note" }, ["Implementer handoff = the HTML source (real DS components) + Spec.md. PDF/PNG are for stakeholders / records."]),
    ]);
    var r = anchor.getBoundingClientRect();
    menu.style.top = (r.bottom + 5) + "px";
    menu.style.right = Math.max(8, window.innerWidth - r.right) + "px";
    document.body.appendChild(menu);
    icons();
    setTimeout(function () {
      document.addEventListener("click", function closeM() { menu.remove(); document.removeEventListener("click", closeM); }, { once: true });
    }, 0);
  }

  /* ---- top bar ---- */
  function buildBar() {
    var tabs = h("div", { class: "studio-tabs" }, (cfg.candidates || []).map(function (c) {
      return h("button", { class: "studio-tab", "data-id": c.id, title: c.note || "", onClick: function () { setActive(c.id); } }, [c.label]);
    }));
    var pickBtn = h("button", { class: "studio-btn", onClick: function () { pick(state.activeId); flash("Selected " + labelOf(state.activeId)); } }, ["Select"]);
    /* Fidelity is fixed at build time (config.fidelity) — shown as a static badge, not a toggle. */
    var fidBadge = h("span", { class: "studio-fidelity", title: "Fidelity was chosen when this was built. Ask Claude to re-generate at the other fidelity." }, [cfg.fidelity === "wireframe" ? "Wireframe" : "Styled"]);
    var specBtn = h("button", { class: "studio-btn", "data-role": "spec", title: "Interaction mode: click an element to set / edit what it does (element → result). Auto-saved to a sidecar next to this file.", onClick: function () { setInteractionMode(!state.interactionMode); } }, [
      h("i", { "data-lucide": "mouse-pointer-click" }), "Interaction",
    ]);
    var commentBtn = h("button", { class: "studio-btn", "data-role": "comment", title: "Comment mode: hover to preview a target, click to leave a note for Claude", onClick: function () { setCommentMode(!state.commentMode); } }, [
      h("i", { "data-lucide": "message-square-plus" }), "Comment",
    ]);
    var count = h("span", { class: "studio-count", style: "display:none" }, ["0"]);
    var sendBtn = h("button", { class: "studio-btn", title: "Send your element comments to your coding agent (via the local server); falls back to clipboard", onClick: sendToAgent }, [h("i", { "data-lucide": "send" }), "Send to Agent", count]);
    var exportBtn = h("button", { class: "studio-btn", "data-role": "export", title: "Export for sharing / handoff — Spec.md (implementer) or PDF (stakeholders)", onClick: function (ev) { ev.stopPropagation(); toggleExportMenu(exportBtn); } }, [h("i", { "data-lucide": "download" }), "Export"]);
    bar = h("div", { class: "studio-bar" }, [tabs, pickBtn, h("div", { class: "spacer" }), fidBadge, specBtn, commentBtn, sendBtn, exportBtn]);
    root.insertBefore(bar, root.firstChild);
  }

  function init() {
    cfg = window.STUDIO_CONFIG || { candidates: [] };
    root = document.querySelector(".studio-root") || document.body;
    stage = root.querySelector(".studio-stage");
    if (!stage) { stage = h("div", { class: "studio-stage" }); while (root.firstChild) stage.appendChild(root.firstChild); root.appendChild(stage); }
    noteLayer = h("div", { class: "studio-note-layer" });
    stage.appendChild(noteLayer);
    if (!candidateEls().length) return;
    if (!stage.querySelector(".studio-note-strip")) stage.insertBefore(h("div", { class: "studio-note-strip" }, [""]), stage.firstChild);

    buildBar();
    renderLegends();
    stage.addEventListener("click", onStageClick, true);
    stage.addEventListener("mousemove", onStageHover);
    /* Reposition pins + interaction hotspots from their live targets when the layout reflows. */
    window.addEventListener("resize", function () { renderPins(); renderHotspots(); });

    var first = (cfg.candidates && cfg.candidates[0] && cfg.candidates[0].id) || candidateEls()[0].getAttribute("data-id");
    setActive(first);
    setFidelity((cfg.fidelity || "styled") === "wireframe");
    updateCount();
    icons();
    /* Load the persisted interaction sidecar (if any), then (re)render legends + hotspots. Also
       retry once for React/Babel-mounted candidate content that lands after init. */
    loadSpecOverride().then(function () { renderLegends(); renderHotspots(); icons(); });
    setTimeout(renderHotspots, 400);
  }

  window.NaraStudio = { init: init };
})();
