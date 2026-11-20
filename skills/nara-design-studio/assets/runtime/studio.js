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

  var cfg, root, stage, bar, noteLayer, pickBtn, fidStyled, fidWire;
  var state = { activeId: null, pickedId: null, wireframe: false, commentMode: false, comments: [], seq: 0,
                interactionMode: false, specOverride: {}, figmaExport: null };

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
    syncPick();
    renderPins();
    /* interaction hotspots need the (React-mounted) target elements; retry to catch async mount. */
    renderHotspots();
    setTimeout(renderHotspots, 250);
    icons();
  }
  function pick(id) {
    state.pickedId = id;
    Array.prototype.forEach.call(bar.querySelectorAll(".studio-tab"), function (t) { t.classList.toggle("is-picked", t.getAttribute("data-id") === state.pickedId); });
    syncPick();
  }
  /* Which direction was chosen is what the Layout contract export reads, so the
     control that records it says what it records and shows whether it has been used.
     A button labelled "Select", with a tick on a tab as its only feedback, did not read
     as the decision it is. */
  function syncPick() {
    if (!pickBtn) return;
    var chosen = !!state.pickedId && state.pickedId === state.activeId;
    pickBtn.classList.toggle("is-active", chosen);
    pickBtn.textContent = chosen ? "Selected direction" : "Select this direction";
  }
  /* `config.fidelity` decides where a design opens; this switches between the two
     readings of it. The wireframe pass is a stylesheet over the same markup, so nothing
     about the design changes — see the button in `buildBar`. */
  function setFidelity(wire) {
    state.wireframe = wire;
    document.body.classList.toggle("wireframe", wire);
    if (fidStyled) {
      fidStyled.classList.toggle("is-on", !wire);
      fidStyled.setAttribute("aria-pressed", wire ? "false" : "true");
    }
    if (fidWire) {
      fidWire.classList.toggle("is-on", wire);
      fidWire.setAttribute("aria-pressed", wire ? "true" : "false");
    }
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

  /* The element an interaction points at, or null when no [data-studio-label] in the candidate matches. */
  function targetEl(cand, target) {
    if (!target) return null;
    try { return cand.querySelector('[data-studio-label="' + target + '"]'); } catch (e) { return null; }
  }

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
      var el = targetEl(cand, it.target);
      if (!el) return;
      var er = el.getBoundingClientRect();
      if (!er.width && !er.height) return;
      var x = er.right - sr.left + stage.scrollLeft - 5;
      var y = er.top - sr.top + stage.scrollTop + 5;
      /* The badge sits on the target's corner and takes the pointer only for its tooltip; a click on it goes to
         whatever is under the pointer (a row or button inside a labeled region), as if the badge were not there. */
      noteLayer.appendChild(h("div", { class: "studio-hotspot", title: it.action || "", onClick: function (ev) {
        var b = ev.currentTarget; b.style.pointerEvents = "none";
        var under = document.elementFromPoint(ev.clientX, ev.clientY);
        b.style.pointerEvents = "";
        if (under) under.click();
      }, style: "left:" + x + "px;top:" + y + "px" }, [String(i + 1)]));
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
  /* Does this page's host act on what the runtime sends it, or only store it?
   *
   * A host that drives the agent itself — the desktop app — declares
   * `window.STUDIO_HOST = { fulfills: true }` before this script runs: comments go
   * straight into a run, and a PNG request is photographed by the host and saved beside
   * the design. serve.py declares nothing, because there the agent is a separate CLI
   * session that still has to be told.
   *
   * A declaration rather than something read off each response, because one of the places
   * that needs the answer is a menu label, built the instant the menu opens. It has to be
   * right before the first click, not after it.
   *
   * What it decides: whether the user is handed a block of text to copy for work that is
   * already done, and whether a menu item asks them to go set up a tool they do not need. */
  function hostFulfills() {
    return !!(window.STUDIO_HOST && window.STUDIO_HOST.fulfills);
  }

  /* Does this host ship the tool a layout contract is for?
   *
   * The JSON is worth nothing on its own. It exists to be diffed against the same JSON
   * captured from the implemented page, which is `check-layout.py`'s whole job. A host that
   * does not ship that script declares `layoutCheck: false` and stops being offered an
   * export it has nothing to compare.
   *
   * Unset means yes, because serve.py sits in the same directory as the script. */
  function hostChecksLayout() {
    return !window.STUDIO_HOST || window.STUDIO_HOST.layoutCheck !== false;
  }

  /* Primary path: POST comments to the capture server (serve.py) → the agent reads out/comments.jsonl.
     Fallback (plain http.server / file://): copy to clipboard so the user can paste into chat. */
  function sendToAgent() {
    if (!state.comments.length) {
      flash("No comments yet. Turn on 'Comment', click any element to leave a note, then send.");
      return;
    }
    var text = commentsText(), n = state.comments.length;
    var label = n + " comment" + (n > 1 ? "s" : "");
    var payload = JSON.stringify({ url: location.href, comments: state.comments });
    fetch("/__comments", { method: "POST", headers: { "Content-Type": "application/json" }, body: payload })
      .then(function (r) { if (!r.ok) throw new Error("no capture"); state.comments = []; renderPins(); updateCount();
        if (hostFulfills()) { flash("Sent " + label + " — the agent is applying them"); return; }
        showResult("Sent " + label + " to the agent", "Captured to out/comments.jsonl. If the agent doesn't pick it up automatically, just say “apply my comments” in the chat.", text); })
      .catch(function () {
        var done = function () { showResult("Copied " + label + " to clipboard", "No capture server running — paste into the chat and the agent will apply them.", text); };
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
  /* Classed as well as styled so a host can address it — a screenshot of the design, for
     one, should not catch a toast that happens to still be on screen. */
  function flash(msg) {
    var f = h("div", { class: "studio-flash", style: "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:200;background:var(--studio-ink);color:#fff;font-size:13px;padding:8px 14px;border-radius:var(--studio-radius)" }, [msg]);
    document.body.appendChild(f); setTimeout(function () { f.remove(); }, 2400);
  }

  /* ---- export (handoff) ----
     PDF = window.print() (dep-free, universal; print CSS stacks all candidates, hides chrome).
     The implementer gets this HTML (built from the pack's real components) and the Layout contract
     JSON; there is no generated spec document to drift from either. PNG is intentionally not a button (needs agent/playwright; PDF +
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
  /* Figma export: offered only when the pack ships figma-export.json naming its own procedure.
     The engine holds no Figma ids or steps; it records which candidate to send, with the pack's
     procedure and metadata, and an agent running watch-captures.sh on figma-requests.jsonl builds
     the file from the pack's real library components. */
  function loadFigmaExport() {
    return fetch("/_pack/figma-export.json", { cache: "no-store" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && typeof j.procedure === "string" && j.procedure) state.figmaExport = j; })
      .catch(function () { /* no server, or the pack has no Figma export: the menu leaves it out */ });
  }
  function exportFigma() {
    var id = state.pickedId || state.activeId, label = labelOf(id), fx = state.figmaExport;
    var recipe = "Export candidate “" + label + "” (data-id=" + id + ") of " + location.href + " to Figma, following the pack's procedure: " + fx.procedure;
    /* procedure and pack are not sent: serve.py fills both from the pack itself. */
    var body = JSON.stringify({ url: location.href, candidateId: id, candidateLabel: label });
    fetch("/__figma", { method: "POST", headers: { "Content-Type": "application/json" }, body: body })
      .then(function (r) { if (!r.ok) throw new Error("no figma route");
        showResult(
          "Figma export requested for “" + label + "” — an agent builds it",
          "Logged to figma-requests.jsonl. An agent running watch-captures.sh <outDir> 600 figma-requests.jsonl wakes, asks you which Figma file to write to, then builds this screen from the pack's library components. Not watching? Tell your agent the line below.",
          recipe); })
      .catch(function () { showResult(
        "Figma export needs an agent with the Figma MCP",
        "The server did not take the request (no server, or this host has no Figma export). Tell your agent the line below.",
        recipe); });
  }
  function exportPNG() {
    var id = state.activeId, label = labelOf(id);
    var recipe = "Capture the current candidate (“" + label + "”, data-id=" + id + ") of " + location.href + " as a full-page PNG.";
    var body = JSON.stringify({ url: location.href, candidateId: id, candidateLabel: label });
    /* PNG is NOT an instant browser download (JS can't rasterize the DOM reliably) — it's an
       agent-fulfilled capture. Always show a persistent box so the click never looks like a no-op. */
    fetch("/__capture", { method: "POST", headers: { "Content-Type": "application/json" }, body: body })
      .then(function (r) { if (!r.ok) throw new Error("no server");
        /* The host takes the picture itself and says where it went. A recipe to hand an
           agent would be instructions for work that is already finished. */
        if (hostFulfills()) { flash("Capturing “" + label + "” — the host is saving it beside the design"); return; }
        showResult(
          "PNG requested for “" + label + "” — an agent captures it",
          "PNG can't be made in the browser, so this logged a request for this one candidate. An agent running watch-captures.sh with a browser MCP saves it to your Downloads folder now (<name>-" + id + ".png). Not watching? Just tell your agent “capture this candidate”. No browser-MCP agent at all → use PDF or an OS screenshot (⌘⇧4).",
          recipe); })
      .catch(function () { showResult(
        "PNG needs an agent with a browser MCP",
        "No capture server. Tell your agent the line below to shoot the current candidate, or use PDF from this menu / an OS screenshot (⌘⇧4).",
        recipe); });
  }

  /* ---- layout contract ----
     The part of a design that MUST survive implementation regardless of pixel fidelity: section order,
     table column order, field order, and which side each action sits on. The extraction lives in
     layout-contract.js — ONE reading, run on both the design and the implemented page, so
     `check-layout.py` can diff them. Duplicating it here would let the two sides disagree. */
  function contractOf(cand) {
    var api = window.LAYOUT_CONTRACT;
    if (!api) return null;
    var page = cand.querySelector(".ds-page") || cand.querySelector("[id^='mnt-']") || cand;
    return api.extract(page, { label: labelOf(cand.getAttribute("data-id")) });
  }

  /* The design side of the layout check. Pair it with a contract captured from the implemented page
     (layout-contract.js in that page's console) and diff with check-layout.py. */
  function exportLayoutContract() {
    if (!window.LAYOUT_CONTRACT) {
      showResult("layout-contract.js isn't loaded",
        "Add the script below to this output and reload — the extractor lives there so the design and the implementation are read the same way.",
        '<script src="/_studio/layout-contract.js"></script>');
      return;
    }
    var picked = state.pickedId || state.activeId;
    var cand = candidateEls().find(function (el) { return el.getAttribute("data-id") === picked; });
    var contract = contractOf(cand);
    if (!contract || !contract.sections.length) { flash("No sections found to contract — is the candidate rendered?"); return; }
    var name = location.pathname.split("/").pop().replace(/\.html?$/, "") + "-" + picked + ".layout.json";
    downloadFile(name, JSON.stringify(contract, null, 2), "application/json");
    flash("Downloaded " + name + " — diff it against the implemented page with check-layout.py.");
  }

  function toggleExportMenu(anchor) {
    var open = document.querySelector(".studio-export");
    if (open) { open.remove(); return; }
    var menu = h("div", { class: "studio-export" }, [
      hostChecksLayout()
        ? h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportLayoutContract(); } }, [h("i", { "data-lucide": "list-checks" }), "Layout contract (JSON) — for check-layout.py"])
        : null,
      /* The label states what will happen here, not in general. Telling someone they need
         a browser-MCP agent, in a host that photographs the page itself, sends them off to
         set up a tool to get something they already have. */
      h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportPNG(); } }, [h("i", { "data-lucide": "image" }),
        hostFulfills() ? "PNG per candidate — saved beside the design" : "PNG per candidate — needs a browser-MCP agent"]),
      state.figmaExport
        ? h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportFigma(); } }, [h("i", { "data-lucide": "figma" }), "Figma — editable design from the library (an agent builds it)"])
        : null,
      h("button", { class: "studio-export-item", onClick: function () { menu.remove(); exportPDF(); } }, [h("i", { "data-lucide": "printer" }), "PDF — print / Save as PDF (all candidates)"]),
      h("div", { class: "studio-export-note" }, ["Implementer handoff = " + (state.figmaExport ? "the Figma file, or " : "") + "the HTML source (real DS components)" + (hostChecksLayout() ? " + the Layout contract" : "") + ". PDF/PNG are for stakeholders / records."]),
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


  /* ---- first-run tour ----
   *
   * Six controls, and two of them ("Export", and the pick button) name a mechanism
   * rather than a reason. A list of instructions somewhere else does not fix that: the
   * work is connecting a name to the thing it sits on, which an arrow does and prose
   * does not.
   *
   * Shown once, skippable, and re-openable from the bar. A tour you dismissed by
   * accident and cannot get back is worse than no tour.
   *
   * Seen-state is a cookie, not localStorage. This page is served from an ephemeral
   * port, so its origin changes every run and localStorage goes with it; cookies are
   * scoped by host and ignore the port, so they survive.
   */
  var TOUR_COOKIE = "studio_tour_seen";
  var tourAt = -1;

  function tourSeen() {
    return document.cookie.split(";").some(function (c) {
      return c.trim().indexOf(TOUR_COOKIE + "=") === 0;
    });
  }
  function markTourSeen() {
    document.cookie = TOUR_COOKIE + "=1; Max-Age=31536000; Path=/; SameSite=Strict";
  }

  /* Copy for the tour, in the languages this runtime ships.
   *
   * Here rather than in a file the page fetches: an extra request would 404 for every
   * consumer that ships no translation, and the tour is fifteen strings. Chosen from
   * `navigator.language`, so a Korean machine gets Korean without anyone passing a flag,
   * and anything else falls back to English rather than to a half-translated mix. */
  var TOUR_COPY = {
    en: {
      skip: "Skip", next: "Next", done: "Got it", help: "How this page is meant to be used",
      steps: [
        ["Directions", "Each tab is a different take on the same screen. Switch between them to compare."],
        ["Choose one", "Records this take as the direction to build. Exports that hand off one direction read this one; the others are kept as alternatives."],
        ["Comment on anything", "Turn this on, then click any element to leave a note about it. Notes are pinned to the element, not to the page."],
        ["Say what it does", "Click an element to record what happens when it is used. Behaviour the picture cannot show."],
        ["Send the notes back", "Hands your notes to the agent, which revises the design from them. This is the loop: look, comment, send."],
        ["Hand it over", "This HTML, plus the Layout contract or Figma file where Export offers them, for whoever implements it. PDF or PNG for everyone who just needs to see it."],
      ],
    },
    ko: {
      skip: "건너뛰기", next: "다음", done: "알겠어요", help: "이 화면을 쓰는 방법",
      steps: [
        ["방향", "탭마다 같은 화면의 다른 방향입니다. 눌러서 비교하세요."],
        ["하나 고르기", "만들 방향으로 기록합니다. 방향 하나를 넘기는 내보내기는 이 방향을 쓰고, 나머지는 검토한 대안으로 남습니다."],
        ["어디든 코멘트", "켜고 아무 요소나 누르면 메모를 남깁니다. 메모는 페이지가 아니라 그 요소에 붙습니다."],
        ["동작 적기", "요소를 누르고 눌렀을 때 무엇이 일어나는지 적습니다. 그림이 보여줄 수 없는 것입니다."],
        ["메모 보내기", "메모를 에이전트에게 넘기면 그걸로 디자인을 고칩니다. 이게 반복입니다. 보고, 적고, 보내기."],
        ["넘기기", "구현할 사람에게는 이 HTML과, Export에 있으면 레이아웃 계약이나 Figma 파일. 보기만 하면 되는 사람에게는 PDF나 PNG."],
      ],
    },
  };

  function tourCopy() {
    var lang = (navigator.language || "en").toLowerCase();
    return TOUR_COPY[lang.split("-")[0]] || TOUR_COPY.en;
  }

  function tourSteps() {
    var copy = tourCopy().steps;
    var targets = [
      bar.querySelector(".studio-tabs"),
      pickBtn,
      bar.querySelector('[data-role="comment"]'),
      bar.querySelector('[data-role="spec"]'),
      bar.querySelector(".studio-count") && bar.querySelector(".studio-count").parentNode,
      bar.querySelector('[data-role="export"]'),
    ];
    return targets
      .map(function (el, i) { return { el: el, title: copy[i][0], body: copy[i][1] }; })
      .filter(function (s) { return !!s.el; });
  }

  function endTour() {
    var overlay = document.querySelector(".studio-tour");
    if (overlay) overlay.remove();
    tourAt = -1;
    markTourSeen();
  }

  function showTour(at) {
    var steps = tourSteps();
    if (!steps.length) return;
    if (at >= steps.length) { endTour(); return; }
    tourAt = at;

    var step = steps[at];
    var r = step.el.getBoundingClientRect();
    var old = document.querySelector(".studio-tour");
    if (old) old.remove();

    /* One element, positioned over the target, with a shadow big enough to cover the
       rest of the window. Cheaper and better supported than a clip-path cutout. */
    var hole = h("div", { class: "studio-tour-hole" });
    hole.style.top = (r.top - 4) + "px";
    hole.style.left = (r.left - 4) + "px";
    hole.style.width = (r.width + 8) + "px";
    hole.style.height = (r.height + 8) + "px";

    var copy = tourCopy();
    var next = h("button", { class: "studio-btn", onClick: function () { showTour(at + 1); } },
      [at === steps.length - 1 ? copy.done : copy.next]);
    var skip = h("button", { class: "studio-tour-skip", onClick: endTour }, [copy.skip]);
    var card = h("div", { class: "studio-tour-card" }, [
      h("div", { class: "studio-tour-step" }, [(at + 1) + " / " + steps.length]),
      h("div", { class: "studio-tour-title" }, [step.title]),
      h("div", { class: "studio-tour-body" }, [step.body]),
      h("div", { class: "studio-tour-row" }, [skip, next]),
    ]);

    var overlay = h("div", { class: "studio-tour" }, [hole, card]);
    document.body.appendChild(overlay);

    /* Measured after insertion: the card's width depends on its text. Kept on screen
       and pointing down at the control, which all of these sit above. */
    var cw = card.getBoundingClientRect().width;
    var left = Math.min(Math.max(8, r.left + r.width / 2 - cw / 2), window.innerWidth - cw - 8);
    card.style.top = (r.bottom + 14) + "px";
    card.style.left = left + "px";
    card.style.setProperty("--arrow", (r.left + r.width / 2 - left) + "px");
    next.focus();
  }

  /* ---- top bar ---- */
  function buildBar() {
    var tabs = h("div", { class: "studio-tabs" }, (cfg.candidates || []).map(function (c) {
      return h("button", { class: "studio-tab", "data-id": c.id, title: c.note || "", onClick: function () { setActive(c.id); } }, [c.label]);
    }));
    pickBtn = h("button", { class: "studio-btn", title: "Record this candidate as the direction to build. Exports that hand off one direction read it; the others are kept as alternatives.", onClick: function () { pick(state.activeId); flash("Selected " + labelOf(state.activeId)); } }, ["Select this direction"]);
    /* `config.fidelity` is where the design opens, not what it is allowed to be.
     *
     * This used to be a static badge, shown only for a wireframe, on the reasoning that
     * fidelity was fixed at build time. That reasoning does not survive looking at what
     * the wireframe pass does: it is a stylesheet over the same markup, the same sections
     * in the same order with the same interaction targets. Both readings of a design are
     * therefore equally true, and turning one off to see the other is a thing a reviewer
     * wants several times in a sitting — structure now, styling next.
     *
     * Both states are named, and one of them is filled. A single "Wireframe" button was
     * tried first and read as decoration: unpressed it gave no sign it could be pressed,
     * and pressed it left the reader to work out what pressing it again would give.
     */
    fidStyled = h("button", {
      class: "studio-seg-item", "data-role": "fidelity-styled",
      title: "The design as built, with the design system's styling.",
      onClick: function () { setFidelity(false); },
    }, ["Styled"]);
    fidWire = h("button", {
      class: "studio-seg-item", "data-role": "fidelity-wireframe",
      title: "Same structure, styling stripped. A stylesheet over this design, not a different one.",
      onClick: function () { setFidelity(true); },
    }, ["Wireframe"]);
    var fidSeg = h("div", { class: "studio-seg", role: "group", "aria-label": "Fidelity" }, [fidStyled, fidWire]);
    var specBtn = h("button", { class: "studio-btn", "data-role": "spec", title: "Interaction mode: click an element to set / edit what it does (element → result). Auto-saved to a sidecar next to this file.", onClick: function () { setInteractionMode(!state.interactionMode); } }, [
      h("i", { "data-lucide": "mouse-pointer-click" }), "Interaction",
    ]);
    var commentBtn = h("button", { class: "studio-btn", "data-role": "comment", title: "Comment mode: hover to preview a target, click to leave a note for Claude", onClick: function () { setCommentMode(!state.commentMode); } }, [
      h("i", { "data-lucide": "message-square-plus" }), "Comment",
    ]);
    var count = h("span", { class: "studio-count", style: "display:none" }, ["0"]);
    var sendBtn = h("button", { class: "studio-btn", title: "Send your element comments to your coding agent (via the local server); falls back to clipboard", onClick: sendToAgent }, [h("i", { "data-lucide": "send" }), "Send to Agent", count]);
    var exportBtn = h("button", { class: "studio-btn", "data-role": "export", title: "Export for sharing / handoff — what implementers get, and PDF / PNG for stakeholders", onClick: function (ev) { ev.stopPropagation(); toggleExportMenu(exportBtn); } }, [h("i", { "data-lucide": "download" }), "Export"]);
    var helpBtn = h("button", { class: "studio-btn", "data-role": "help", title: tourCopy().help, onClick: function (ev) { ev.stopPropagation(); showTour(0); } }, [h("i", { "data-lucide": "help-circle" })]);
    bar = h("div", { class: "studio-bar" }, [tabs, pickBtn, h("div", { class: "spacer" }), fidSeg, specBtn, commentBtn, sendBtn, exportBtn, helpBtn]);
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
    /* After icons(), so the controls have their final size to point at. */
    if (!tourSeen()) setTimeout(function () { showTour(0); }, 400);
    window.addEventListener("resize", function () { if (tourAt >= 0) showTour(tourAt); });
    document.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && tourAt >= 0) endTour(); });
    /* Load the persisted interaction sidecar (if any), then (re)render legends + hotspots. Also
       retry once for React/Babel-mounted candidate content that lands after init. */
    loadSpecOverride().then(function () { renderLegends(); renderHotspots(); icons(); });
    loadFigmaExport();
    setTimeout(renderHotspots, 400);
    /* Mounts can land after any fixed retry; re-anchor badges when candidate
       content changes. Observes candidates only: noteLayer (badges) sits outside them, so no loop. */
    var reanchor = 0;
    var mo = new MutationObserver(function () { clearTimeout(reanchor); reanchor = setTimeout(renderHotspots, 100); });
    candidateEls().forEach(function (cand) { mo.observe(cand, { childList: true, subtree: true }); });
  }

  window.NaraStudio = { init: init };
})();
