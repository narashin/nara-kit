/*
 * Layout contract extractor — the ONE structural reading used on both sides of the handoff.
 * Generic: no design-system or product specifics.
 *
 * WHY
 * The parity bar for a design is not pixels; it is layout: which sections exist, in what order, a
 * table's columns in order, a form's fields in order, and which side each action sits on. This file
 * reads exactly that off a live DOM and emits normalized JSON, so the same code can be run against
 *   (a) a studio candidate     →  the DESIGN contract (studio.js calls it at Export time), and
 *   (b) the implemented page   →  the IMPL contract (paste into the console / a browser MCP),
 * and `check-layout.py` can diff the two mechanically instead of anyone eyeballing screenshots.
 *
 * USAGE
 *   window.LAYOUT_CONTRACT.extract()                       // auto-detects the content root
 *   window.LAYOUT_CONTRACT.extract(document.querySelector("main"))
 *   copy(JSON.stringify(window.LAYOUT_CONTRACT.extract(), null, 2))   // DevTools console
 *
 * The extractor is deliberately dumb: it reports what is rendered, never what was intended. Anything
 * it cannot see (a region with no label, heading, table, field or button) shows up as `content only`,
 * which is itself the signal to label that region in the design.
 */
(function () {
  "use strict";

  var VERSION = 1;

  function textOf(el) { return (el.textContent || "").trim().replace(/\s+/g, " "); }
  function shortText(el, max) { var t = textOf(el); max = max || 40; return t.length > max ? t.slice(0, max - 1) + "…" : t; }
  function visible(el) { var r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; }

  /* Which third of its container an element sits in — the "primary CTA is top-right" kind of fact.
     Thirds (not exact px) on purpose: that is the decision an implementation must preserve. */
  function alignIn(el, container) {
    if (!container) return null;
    var er = el.getBoundingClientRect(), cr = container.getBoundingClientRect();
    if (!cr.width) return null;
    var center = (er.left + er.right) / 2 - cr.left, third = cr.width / 3;
    return center < third ? "left" : center > third * 2 ? "right" : "center";
  }

  /* Pagination pages are chrome, not actions — otherwise every contract lists "1, 2, 3" as buttons. */
  function isPaginationBtn(b) {
    if (b.closest && b.closest("[class*='pagination']")) return true;
    if (/^\d+$/.test(textOf(b))) return true;
    var al = b.getAttribute("aria-label") || "";
    return /^(previous|next|first|last)$/i.test(al);
  }

  /* Content root: the studio's page wrapper, else the app's <main>, else the body. */
  function defaultRoot(scope) {
    var s = scope || document;
    return s.querySelector(".ds-page") || s.querySelector("main") || s.querySelector("[role='main']") ||
           s.querySelector("[id^='mnt-']") || (s.body || s);
  }

  /* Sections. Studio outputs mark them with data-studio-label; the real app has no such markers, so we
     fall back to the content root's own block children (descending through a lone wrapper). */
  function sectionsOf(root) {
    var labeled = Array.prototype.filter.call(root.querySelectorAll("[data-studio-label]"), function (el) {
      return !el.classList.contains("studio-interactions") && visible(el);
    });
    var leaves = labeled.filter(function (el) {
      return !labeled.some(function (o) { return o !== el && el.contains(o); });
    });
    if (leaves.length) return leaves;
    var kids = Array.prototype.filter.call(root.children, function (el) { return el.nodeType === 1 && visible(el); });
    var guard = 0;
    while (kids.length === 1 && guard++ < 4) {
      var next = Array.prototype.filter.call(kids[0].children, function (el) { return el.nodeType === 1 && visible(el); });
      if (!next.length) break;
      kids = next;
    }
    return kids;
  }

  function sectionName(el, index) {
    if (el.getAttribute("data-studio-label")) return el.getAttribute("data-studio-label");
    var h = el.querySelector("h1, h2, h3");
    if (h) return shortText(h, 32);
    return "section " + (index + 1);
  }

  function extractSection(el, index) {
    var title = el.querySelector("h1, h2, h3");
    var tabs = Array.prototype.map.call(el.querySelectorAll('[role="tab"], [class*="tabs"] > button, [class*="tab-list"] > button'), function (t) { return shortText(t, 24); });

    var tables = [];
    Array.prototype.forEach.call(el.querySelectorAll("table"), function (tb) {
      var cols = Array.prototype.map.call(tb.querySelectorAll("th"), function (t) { return textOf(t) || "—"; });
      if (cols.length) tables.push({ columns: cols });
    });

    /* Field labels only. A label that wraps its own radio/checkbox is an OPTION inside a field
       ("Major", "Minor", …), not a field — listing those turns a 4-field panel into a 30-item list and
       makes every option-copy tweak read as layout drift. */
    var fields = tables.length ? [] : Array.prototype.filter.call(el.querySelectorAll("label"), function (l) {
      return !l.querySelector("input[type='radio'], input[type='checkbox']");
    }).map(function (l) { return shortText(l, 24); });
    var rows = Array.prototype.map.call(el.querySelectorAll("dt"), function (t) { return shortText(t, 24); });

    var actions = [];
    Array.prototype.forEach.call(el.querySelectorAll("button, a[role='button']"), function (b) {
      if (actions.length >= 8 || isPaginationBtn(b)) return;
      var t = shortText(b, 28);
      if (!t) return;
      actions.push({ text: t, align: alignIn(b, el) });
    });
    /* A labeled control IS the action — measure it against its container, not itself. */
    if (!actions.length && /^(BUTTON|A|SPAN)$/.test(el.tagName)) {
      var t0 = shortText(el, 28);
      if (t0) actions.push({ text: t0, align: alignIn(el, el.parentElement) });
    }

    return {
      index: index + 1,
      name: sectionName(el, index),
      title: title ? shortText(title, 48) : null,
      tabs: tabs,
      tables: tables,
      fields: fields,
      rows: rows,
      actions: actions,
    };
  }

  /**
   * @param {Element} [root]  content container; auto-detected when omitted
   * @param {{label?: string}} [opts]
   * @returns {{version:number,label:string,url:string,sections:Array}}
   */
  function extract(root, opts) {
    opts = opts || {};
    var r = root || defaultRoot();
    if (!r) return { version: VERSION, label: opts.label || "", url: location.href, sections: [] };
    return {
      version: VERSION,
      label: opts.label || document.title || "",
      url: location.href,
      sections: sectionsOf(r).map(extractSection),
    };
  }

  /* Markdown rendering of a contract — what lands at the top of an exported Spec.md. */
  function toMarkdownLines(contract) {
    return (contract.sections || []).map(function (s) {
      var parts = [];
      if (s.title) parts.push('title "' + s.title + '"');
      if (s.tabs.length) parts.push("tabs: " + s.tabs.join(" · "));
      s.tables.forEach(function (t, ti) {
        parts.push((s.tables.length > 1 ? "table " + (ti + 1) + " columns" : "columns") + " (in order): " + t.columns.join(" · "));
      });
      if (s.fields.length) parts.push("fields (in order): " + s.fields.join(" · "));
      if (s.rows.length) parts.push("rows (in order): " + s.rows.join(" · "));
      if (s.actions.length) {
        parts.push("actions: " + s.actions.map(function (a) { return "`" + a.text + "`" + (a.align ? " (" + a.align + ")" : ""); }).join(", "));
      }
      return s.index + ". **" + s.name + "** — " + (parts.length ? parts.join("; ") : "_content only_");
    });
  }

  window.LAYOUT_CONTRACT = { version: VERSION, extract: extract, toMarkdownLines: toMarkdownLines };
})();
