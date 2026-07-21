---
name: nara-design-studio
description: >-
  Design and prototype product screens on ANY design system via a pluggable pack: interview → Studio candidates → element-comment refine loop → implementer handoff (HTML + Spec.md). Renders with the pack's REAL components (anti-drift), not hand-drawn chrome.
  USE FOR: "design a screen", "UI mockup", "wireframe this list", "prototype the flow", "design studio", "studio candidates".
  DO NOT USE FOR: backend/API work, writing specs/RFCs (use nara-rfc), publishing to Confluence (use nara-publish-spec), non-visual tasks.
---

This skill is a **pack-agnostic design-studio engine** — it ships no design system of its own. Every product-specific detail (tokens, real components, navigation data, brand rules) comes from a **pack**, resolved via the bootstrap gate below before anything is built. Read `references/pack-contract.md` once at the start of a session to know what a pack provides and how it's consumed; pull in the resolved pack's own docs (its manifest, its `pack.md` if it ships one) as needed.

Default output is **Studio Mode**: a locally-served page with 2–5 candidate directions the user compares, comments on, and exports — a planning/prototyping aid, not a one-shot static file (unless the user explicitly asks for production code).

---

## 1. How this skill runs

`design a <screen>` → load this skill → **resolve the pack (bootstrap gate, §2)** → **INTERVIEW until unambiguous (§4)** → restate the spec, get a go → **BUILD to baseline (§3) at the chosen fidelity (§6)** → **ITERATE by voice (§7)**. Never skip the interview, never build while blockers remain open, and never build before the pack is resolved.

For **design / options / explore** requests, default to **Studio Mode** (§3): brief → 2–5 candidates (usually 3) → pick → free refine. A plain "just one screen" request still resolves the pack and runs the interview — it just builds a single candidate.

## 2. Bootstrap gate — resolve the pack before building

This is an **explicit choice, never a silent fallback**. Every build first resolves which pack it renders against:

```
packPath set in references/settings.local.md (gitignored — copy from settings.local.md.example)?
 ├─ YES → load that pack, proceed. The user never sees this gate again.
 └─ NO  → ask the user, one of three options:
      (a) Build a pack from your design-system codebase
          → invoke the [nara-design-pack-builder](../nara-design-pack-builder/SKILL.md) skill. It writes a pack and sets packPath in `references/settings.local.md`, then hand back to this skill to resume the interview.
      (b) Point at an existing pack
          → ask for its path, write `packPath: <path>` into references/settings.local.md.
      (c) Use the bundled neutral starter pack (assets/starter-pack/, tier T1)
          → token-only, generic design; proceed with no product components.
```

Whichever option is chosen, tell the user which tier they're now building against (see `references/pack-contract.md` §1 for T0–T3) — a starter-pack design is always visibly T1, never presented as if it were the real product.

## 3. Studio Mode — the default for "design / explore / show me options"

1. **Brief.** Take the design source from a planning doc — a local `.md` (auto-use `docs/requirements.md` if present), an external Jira/Confluence/Figma link (localize via MCP first, like nara-prep), or text pasted in chat. If none, run the interview (§4). Parse the brief to pre-fill the Readiness Rubric; interview only the gaps; never invent unstated requirements.
2. **Build.** Copy `assets/runtime/studio-template.html` — it already wires `/_studio/studio.css` + `/_studio/studio.js` (the engine chrome) and `/_pack/tokens/tokens.css` + `/_pack/_ds_bundle.js` (plus `/_pack/data.js` for a T3 pack); never hand-wire these paths yourself. Declare **2–5 layout-direction candidates** (default 3 — go up to 5 only when the directions stay genuinely distinct) as `<section class="studio-candidate" data-id="…"><div id="mnt-…"></div></section>` mounts, and a `window.STUDIO_CONFIG` object (`title`, `brief`, a `pack` block copied from the resolved pack's manifest `pack.*` fields plus its `namespace`, `candidates[]` each with an `interactions` list, and `fidelity`). **Render with the pack's REAL components, not hand-drawn chrome:** for a token-only pack (`namespace` is `""`, the bundled starter pack's case), author the candidate body straight from the pack's tokens — nothing to mount. For a T2+ pack, wrap the body in a `<Shell>` built from the pack's actual components read off `window[<namespace>]` (fed the pack's data via `window.STUDIO_PACK_DATA` for a T3 pack) — never hand-build a shell from tokens when the pack already has one. Add `data-studio-label="…"` to every commentable element. **Default `fidelity: "styled"`** (shown as a static badge) and don't ask; build `wireframe` only when the user explicitly requested a structure-only pass — never both in one build; to switch, regenerate. **Do NOT reinvent the studio chrome** — `assets/runtime/studio.js` + `studio.css` own the candidate switcher, fidelity badge, comment mode, Interaction mode, and Export menu.
3. **Serve.** `python3 assets/runtime/serve.py --pack <packPath> --out <outDir>` (add `--runtime <dir>` only when invoking from outside `assets/runtime/`; `--port` to override the default 8917). This resolves three mounts under one HTTP origin: `/_studio/*` → the engine chrome, `/_pack/*` → the resolved pack, `/*` → the generated output (candidate HTML, `out/`, `handoff/`). `file://` is not supported — a screen must be opened through this server for the mounts (and the studio's comment/interaction/spec/capture POSTs) to resolve.
4. **Refine (free, not fixed) — auto-loop.** The user `Select`s a candidate, hovers+clicks elements to attach comments (each captures a precise selector via `data-studio-label`), and hits **Send to Agent**. To make this hands-free: **right after emitting the studio, launch `assets/runtime/watch-comments.sh <outDir>` in the BACKGROUND** (`run_in_background: true`). It blocks until the next Send, then exits and wakes you with the new comment line(s) `{candidateLabel, selector, hint, note}` — **you apply them to the exact targeted fragment(s), re-emit the HTML, and re-launch the watcher**, all without the user typing "apply my comments." Repeat until they're happy. Save scratch work to `<outDir>/out/<name>.html`; a **finalized handoff → `<outDir>/handoff/<id>-<slug>-<YYYY-MM-DD>.html`**. To reopen a handed-off design later, run **`assets/runtime/open-design.sh <id-or-fragment> <outDir> [packDir] [port]`**.

**Pre-emit checklist (Studio Mode) — verify before you write the file:**
- [ ] The template's `/_studio/*` and `/_pack/*` references are untouched — no hand-wired absolute paths.
- [ ] Every candidate that reuses pack chrome mounts it from `window[<namespace>]` — nothing pre-existing is hand-drawn from tokens.
- [ ] Every actionable element has a `data-studio-label` and, where behavior matters, an `interactions` entry.
- [ ] Only genuinely-new UI is token-built; the output is served through `serve.py` (relative paths resolve).
- [ ] `fidelity` is set once, matches what was asked, and is never toggled live.

### Behavior spec (interactions) & export

- **Show what actions do — don't leave it implied.** Seed each candidate with `interactions: [{ target, action }]` in `STUDIO_CONFIG` (`target` = that element's `data-studio-label`). The runtime renders a numbered **"Interactions" legend** (part of the page) + a hotspot badge on each target. **Users can also author these in-browser** via **Interaction mode** (toolbar button): click an element → set/edit/delete what it does; it auto-saves to a `<name>.interactions.json` sidecar (written by `serve.py`) that the runtime merges over the config on load — edits stick across reloads with no agent step. Config `interactions` are the seed; the sidecar, once present, is authoritative for that candidate.
- **Export (toolbar → Export) — handoff by audience.** The **implementer handoff is the HTML source + `Spec.md`**, not an image: the output is built from the pack's real components, so the source *is* reference code, and `Spec.md` is a structured index — the pack's manifest `pack.*` fields as the source-of-truth line (a warning when unset), the **Selected** direction first (others marked alternatives), and a per-direction **Component tree** (real component names + key props read from the live React render, degrading to a note for token-only packs) that maps to your imports. **Export → Spec.md** saves the `.md` under `<outDir>` and offers it to the user. **Stakeholders / records get PDF or PNG:** **PDF** = Export → PDF opens the browser print dialog (print CSS stacks all candidates, hides the studio chrome, forces color to survive). **PNG** = Export → PNG posts a capture request for the **current candidate only** to `serve.py` (`<outDir>/capture-requests.jsonl`); an agent running `assets/runtime/watch-captures.sh <outDir>` in the background wakes and screenshots that candidate with a browser MCP, saving it to the user's Downloads. No server/MCP → PDF or an OS screenshot is the fallback. The interaction legend is in-page, so it lands in every export.

## 4. Interview protocol — interview until ambiguity is gone, not for N questions

Do **not** cap the interview at a fixed count. Ask in small batches (2–4 at a time), reflect answers back, and keep going until the **Readiness Rubric** below has **zero open blockers**. Then summarize the spec in 3–6 bullets and ask for a "go" before building.

Maintain a running **Open Questions** list. Every item is either (a) answered, or (b) explicitly deferred by the user ("you decide" / "assume X"). Build only when open **blocker** count = 0. This is the operational stand-in for "measuring" ambiguity — a checkable zero, not a fake confidence score.

### Readiness Rubric (the exit condition = the user's 3 criteria, made checkable)

**A. No confusion (clarity)** — for every region that will exist (header, nav, page title, and each content block), the *content* and its *purpose* are specified. No unapproved "TBD" placeholders. Real labels and representative data are known.

**B. No dead-ends (flow completeness)** — every actionable element (button, link, table row, tab, menu item) has a defined result: navigates where / opens what / does what. The screen's **entry point** and its **exit / back path** are defined. **Empty, loading, and error states** are each decided (designed or explicitly out of scope).

**C. Clear usage (usability)** — the **primary user** and their **primary task** are named; the **one main action** of the screen is identified; the **success state** ("done looks like…") is described.

If any A/B/C item is unknown, it is an open blocker — keep interviewing.

### Interview coverage (the axes every spec should resolve)

- **Screen type** — list / detail / form / dashboard / modal / flow (multi-step).
- **Fidelity** — **default to styled; do NOT ask.** The token layer makes styled essentially free, and the candidates already compare *layout directions*, so wireframe adds little here. Build wireframe only if the user explicitly asks for a grayscale structure-only pass. See §6.
- **Core data & states** — which fields/columns; which status values appear, and whether the pack already models them as a component (a Label/Chip/Badge) rather than needing new ones invented.
- **Primary actions & flow** — the main CTA; what each interactive element leads to; entry and back paths.
- **Empty / loading / error** — shown or skipped for this pass.
- **Options exploration** — one resolved design, or 2 side-by-side directions to compare?
- **Refine mechanism** — Studio Mode captures element comments (hover-preview + click) and sends them to Claude; there is no live tweaks panel. Fidelity is picked per pass, not toggled.
- **Audience & task** — who uses it, what they came to do, what success looks like.
- **Scope** — one screen or a small flow; keep each build to 1–2 screens.

## 5. Baseline constraints — always apply, every build (no need to be told)

- **FROZEN vs DESIGNED — the rule that stops chrome drift.** Anything that already exists as a real component in the resolved pack (an app shell, a table, a status label, an empty state, a pagination control — whatever the pack ships) is **reused verbatim, never invented or restyled**. You design **only genuinely-new UI** — the content this screen actually adds. The mechanism is **component reuse, not token recreation**: mount the pack's real components (`window[<namespace>]`) plus its `KIT` helpers (`pack.kitHelpersPath`, when the pack has one) and feed them the pack's own data. Token-only recreation is the trap — grabbing the pack's CSS variables and hand-drawing a header/table/pill that already exists as a component is precisely what lets a prototype drift from the real product; if a component exists in the pack, use it. When unsure whether an element already exists, assume it does and check the pack (its manifest `components` list, its bundle, its own docs) before authoring. Re-drawing a nav item, a column, a status pill, or an empty state that the pack already provides is a **bug**, not a design choice.
- **Tokens only — no hardcoded brand values.** Use the pack's own CSS custom properties (declared in the files listed under the manifest's `globalCssPaths`) for every color/spacing/radius/type value; never hardcode a hex or px that the pack already tokenizes. For a **portable single file** (saved outside this tree, shared standalone, or opened without `serve.py`), inline the pack's token `:root` block so relative `@import`s don't break.
- **Everything else — layout, spot color budget, card treatment, type scale, icon set, logo usage, status enums — is the resolved pack's own decision, not this engine's.** Read it from the pack's manifest and any docs it ships (its own `pack.md` / component docs); this engine imposes no brand-specific numbers of its own. `references/pack-contract.md` documents exactly which manifest fields carry this information.
- **Starting points = real IA by default.** If the pack declares `startingPoints` (example screens/templates) and the request matches one, read its real structure and adopt it — its nav shape, its real columns, its real status enums — instead of inventing labels, columns, or statuses. Deviate only where the user explicitly overrides, and surface the reference structure during the interview so they can confirm or change it.

## 6. Fidelity modes

- **Wireframe** — grayscale, no color/shadow; layout skeleton + information hierarchy only (gray bars for text/data, silhouette pills for status). Keep the real region layout and spacing. For fast structure agreement.
- **Styled** — full pack styling: real tokens, real components, real status colors, the pack's own surface/border/radius treatment. For look-and-feel and clickable prototypes.

**Default: styled — and don't ask about fidelity.** In a token-based pack, styled is essentially free and the layout-direction candidates already cover structural comparison, so wireframe is rarely worth it. Treat **wireframe as an explicit opt-in only** (user says "wireframe" / "low-fi" / "just structure"). When used, it's a build-time choice (`STUDIO_CONFIG.fidelity`, static badge) — build one fidelity per pass, never both; to switch, regenerate. The mechanism stays available; just don't offer it proactively.

## 7. Iteration

- **By voice** — apply only what's asked; leave all other layout/spacing/color/content untouched. ("add a Severity column, P1 in red" → change just that.)
- **No live tweaks** — Studio Mode deliberately has no tweaks panel (knobs proved low-value). Fidelity is a build-time choice shown as a badge, not a toggle. Any change (density, accent, columns, copy, "make it styled now") goes through element comments → Send to Agent → regenerate. Keeps the surface small and the output honest.
- **Options** — Studio Mode renders 2–5 layout-direction candidates (default 3) the user switches between and `Select`s; the element-comment → `Send to Agent` loop (precise selector per note, captured to `<outDir>/comments.jsonl`) feeds per-element edits back to you. (Outside Studio Mode, render directions side-by-side to compare or mix.)

## 8. Reference index

- `references/getting-started.md` — human-facing quick start: what it is, how it works, zero-setup starter-pack run, connecting a real design system, the refine loop, and handoff.
- `references/pack-contract.md` — the pack contract: fidelity tiers (T0–T3), required files per tier, every manifest field the engine reads, and the `/_studio` / `/_pack` / `/` serve topology.
- `references/settings.local.md.example` — template for the gitignored `settings.local.md` that sets `packPath` (copy it, fill in a path, or omit it to use the starter pack).
- `assets/runtime/` — the engine itself: `studio.js` + `studio.css` (the studio chrome — candidate switcher, comment mode, Interaction mode, Export), `serve.py` (the three-mount dev server), `studio-template.html` (the pack-neutral output skeleton), and `watch-comments.sh` / `watch-captures.sh` / `open-design.sh` (the auto-loop and reopen helpers).
- `assets/starter-pack/` — the bundled neutral T1 pack (tokens + manifest + a specimen card) used when the user picks bootstrap-gate option (c).
