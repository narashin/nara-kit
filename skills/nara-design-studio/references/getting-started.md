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

Just invoke the skill — `/nara-design-studio` or say *"design a screen"*. With no pack configured, it uses the **bundled neutral starter pack** (`assets/starter-pack/`, token-only) so you can prototype layouts immediately. Everything renders from generic `--ds-*` design tokens.

To view a generated screen in the browser:

```bash
python3 assets/runtime/serve.py --pack assets/starter-pack --out <yourOutputDir>
# open http://localhost:8917/<your-file>.html
```

The server exposes three mounts so the runtime, the pack, and your output can live in different folders: `/_studio/*` (runtime), `/_pack/*` (pack), `/*` (output).

## Connecting your own design system (full fidelity)

The starter pack is layout-only (tier T1). To render with your product's **real components** (tier T2+, zero drift), give the engine a pack. On first run with no pack it offers three options:

1. **Build a pack from your codebase** — runs `/nara-design-pack-builder`, a guided React-first protocol that extracts your tokens + components + a manifest into a pack, then sets `packPath`.
2. **Point at an existing pack** — set `packPath` in `references/settings.local.md` (copy `settings.local.md.example`; this file is gitignored, never committed).
3. **Use the neutral starter pack** — the T1 default above.

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

## Reference

- `pack-contract.md` — fidelity tiers (T0–T3), required files per tier, every manifest field the engine reads, the serve topology.
- `settings.local.md.example` — the `packPath` template.
- `../../nara-design-pack-builder/SKILL.md` — extract a pack from your design system.
