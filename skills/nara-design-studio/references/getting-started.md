# Getting started — nara-design-studio

Human-facing quick start. (The agent-facing protocol is in `../SKILL.md`; this page is for a person setting the skill up.)

## What it is

A design/prototyping studio that renders screens with a **design system pack** you plug in. You describe a screen, it interviews you until the spec is unambiguous, then builds **2–5 layout candidates** you compare, comment on, and refine — and hands off to implementers as HTML (built from the pack's real components) + a `Spec.md`.

The key idea: chrome that already exists in your product is **reused from the pack's real components**, never hand-redrawn — so the prototype can't drift from the shipped UI.

## How it works (flow)

```
describe a screen → interview (until spec is clear) → resolve a pack (see below)
  → build candidates → compare / Select → Comment + Interaction refine loop
  → export (Spec.md / PDF / PNG) or open a live handoff
```

The runtime lives in `assets/runtime/` (a small `serve.py` dev server + `studio.js`/`studio.css` + an HTML template). The design system lives in a separate **pack** the engine points at.

## Quick start (zero setup)

Just invoke the skill — `/nara-design-studio` or say *"design a screen"*. It asks once which design system this project builds on; pick **"start a new design system"** and it uses the **bundled neutral starter pack** (`assets/starter-pack/`, token-only) so you can prototype layouts immediately. Everything renders from generic `--ds-*` design tokens.

To view a generated screen in the browser:

```bash
python3 assets/runtime/serve.py --pack assets/starter-pack --out <yourOutputDir>
# open http://localhost:8917/<your-file>.html
```

The server exposes three mounts so the runtime, the pack, and your output can live in different folders: `/_studio/*` (runtime), `/_pack/*` (pack), `/*` (output).

## Connecting your own design system (full fidelity)

The starter pack is layout-only (tier T1). To render with your product's **real components** (tier T2+, zero drift), give the engine a pack.

**Which design system a project uses is asked once, per project, and never inherited.** A brand-new repo does not silently pick up whatever pack your last project used — that is how an unrelated design language ends up in a new product.

| Source | Role |
|--------|------|
| `.claude/overrides/nara-design-studio.md` → `pack:` / `packPath:` | **the decision.** Present → used, no question. Absent → you get asked, and your answer is written here. |
| `references/settings.local.md` → `defaultPackPath` | your usual pack — pre-selected in that question |
| `~/.claude/design-packs/<name>/` (any dir with a `_ds_manifest.json`) | packs a team or an internal distribution dropped in — also offered |

The question's other options:

1. **Build a pack from a design system you already have** — runs `/nara-design-pack-builder`. The source can be a local component codebase, an **installed npm package** (a design system that ships a UMD/dist build often needs no per-component adaptation), a Storybook, or a published CSS/token bundle.
2. **Convert a DESIGN.md** — if you have one (see `/nara-design-md`), it already carries a full color/typography/spacing/radius set plus per-component style specs, which is *more* than the starter pack ships:
   ```bash
   python3 assets/runtime/designmd_to_pack.py --design DESIGN.md --out ../my-pack
   ```
   The transform is mechanical. It lands at **T2** when the file has a `components:` block (each entry becomes a real mountable component) and **T1** when it doesn't. Every token the engine needs that DESIGN.md doesn't define is emitted into a separate `derived` block and printed, so you can always see what was inferred.
3. **Point at an existing pack** — give its path.
4. **Start a new design system** — the neutral starter pack (T1), then the greenfield path in `greenfield.md`.

A pack must expose its tokens as `--ds-*` (the engine's vocabulary). A pack that keeps a different prefix (e.g. `--acme-*`) ships a tiny **adapter stylesheet** mapping its prefix onto `--ds-*` — one `:root { --ds-x: var(--acme-x); }` line per chrome-used token — and lists it in the pack's `globalCssPaths`. The adapter lives **with the pack**, not with this engine. See `pack-contract.md` for the full manifest + tier contract.

## The refine loop

- **Comment mode** — hover an element, click to leave a note, hit **Send to Agent**. `serve.py` captures notes to `<out>/comments.jsonl`; run `assets/runtime/watch-comments.sh <outDir>` in the background and the agent applies them and re-emits automatically.
- **Interaction mode** — click an element to declare what it does (element → result); saved to a sidecar and shown as an on-page legend.
- **Export** — `Spec.md` (implementer handoff), `PDF` (print dialog), or `PNG` (an agent running `watch-captures.sh <outDir>` with a browser MCP fulfills the capture).

## Handoff

Save a finalized design under `<outDir>/handoff/`, then anyone can reopen the live prototype:

```bash
bash assets/runtime/open-design.sh <ID-or-fragment> <outDir> [packDir] [port]
```

## The adherence gate

"Use tokens, never hardcoded values" is checked, not trusted. Before output is served, the agent runs:

```bash
python3 assets/runtime/check_adherence.py <file.html> --pack <packDir>
```

It fails on raw hex colors and raw px values (a `1px` hairline is allowed; a `24px` margin is not), printing each with its line number. Token declarations inside an inlined `:root { … }` block are exempt. A pack can tighten or relax the rules by shipping a config and naming it in its manifest's `adherenceConfig` — see `pack-contract.md` §3.5.

## The layout check

Pixel fidelity is not what implementation has to reproduce — **layout** is: section order, table columns in order, field order, and which side each action sits on. Every exported `Spec.md` opens with that as a numbered list, and it is verifiable rather than advisory:

```bash
# design side — in the studio: Export → "Layout contract (JSON)"
# impl side   — paste assets/runtime/layout-contract.js into the implemented page's console, then:
#   copy(JSON.stringify(window.LAYOUT_CONTRACT.extract(), null, 2))
python3 assets/runtime/check-layout.py design.layout.json impl.layout.json
```

One extractor, run on both sides, so the comparison is mechanical instead of two people looking at screenshots. Exit `1` lists what moved. Label every region you expect an implementer to reproduce with `data-studio-label` — the contract is built from those, so an unlabeled region drops out silently. See `pack-contract.md` §6.

## Reference

- `pack-contract.md` — fidelity tiers (T0–T3) and what T2/T3 does *not* eliminate, required files per tier, every manifest field the engine reads (including `components[].real`, the pack → real prop map), the adherence config, the serve topology, and the layout contract.
- `settings.local.md.example` — the `defaultPackPath` template (pack resolution source 2).
- `../assets/runtime/designmd_to_pack.py` — DESIGN.md → pack converter.
- `../assets/runtime/check_adherence.py` — the emit-time hardcoded-value gate.
- `../assets/runtime/layout-contract.js` + `check-layout.py` — the layout-parity pair: one extractor run on both the design and the implemented page, then diffed.
- `../../nara-design-pack-builder/SKILL.md` — extract a pack from your design system.
