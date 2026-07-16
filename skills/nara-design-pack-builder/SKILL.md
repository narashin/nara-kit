---
name: nara-design-pack-builder
description: >-
  Extract a nara-design-studio DS pack (tokens + standalone component bundle + manifest) from a React design-system codebase, via a guided, verify-as-you-go protocol. React-first; flags non-React sources as manual.
  USE FOR: "build a design studio pack", "extract a DS pack", "make my design system work with design-studio", "pack-builder".
  DO NOT USE FOR: designing screens (use nara-design-studio), non-React design systems (manual pack), backend work.
---

This skill turns a real design-system codebase into a pack `nara-design-studio` can render against — real
components, real tokens, a manifest — so screens designed against the pack are what implementers actually build
with, not a lookalike drawn from tokens. It is **not** a magic auto-extractor: it is a guided, per-component
protocol with a human confirming the judgment calls (which components, how each adapts, whether each one
actually mounts) at every step. Read `references/manifest-schema.md` once before Step 5 — it's the shape you're
building toward the whole time, not just an output format to fill in at the end.

**React-first.** The target runtime — `nara-design-studio`'s `studio-template.html` — mounts components
in-browser via Babel-transformed JSX and CDN React, nothing else. That's the only mount protocol this skill
knows how to produce a pack for.

---

## 1. How this runs

Invoked directly ("build a design studio pack from `<repo>`") or from `nara-design-studio`'s bootstrap gate
option (a). On completion it hands back to `nara-design-studio` with `packPath` already set, so the studio
resumes the interview against the freshly built pack.

## 2. Step 1 — Locate the source & confirm it's React

Ask (or infer from the repo) four things: the repo/path, the component directory, the token source (CSS custom
properties file, a Style Dictionary build output, or a JS/TS theme object), and the framework.

**Gate — STOP here if the source is not React.** Vue, Svelte, Web Components, Angular, or a plain CSS/HTML
component library all fail this gate. Do not attempt adaptation, do not approximate. Tell the user, verbatim in
spirit:

> `nara-design-pack-builder` currently supports React-only sources — it targets `nara-design-studio`'s in-browser
> Babel + CDN React runtime, and a different framework needs a mount protocol this skill doesn't produce. Build a
> pack by hand instead: author `tokens/*.css` + `_ds_manifest.json` directly per
> `references/manifest-schema.md` (a token-only T1 pack needs no component adaptation at all), or use the
> studio's bundled neutral starter pack (bootstrap gate option (c)) until a React port exists.

Why this is a hard stop rather than a "best effort": a pack that claims components it can't actually mount is
worse than no pack — it would make the studio's FROZEN-vs-DESIGNED reuse rule (`nara-design-studio`'s
`pack-contract.md`) point at something that silently doesn't work.

## 3. Step 2 — Enumerate components

Scan the component directory for candidates: PascalCase `.jsx`/`.tsx` files, an index/barrel export, a
`components/` or `ui/` folder structure. Present the candidate list to the user grouped by folder or category —
don't pre-filter based on a guess at relevance. The user confirms the set: trims internal-only or
irrelevant ones, adds anything the scan missed. **Never adapt a component the user hasn't confirmed** — this is
the first of several checkpoints where a human, not a heuristic, decides scope.

## 4. Step 3 — Extract tokens

Identify the token source (CSS custom properties, Style Dictionary output, or a JS/TS theme object) and re-emit
every token the confirmed component set actually uses into `tokens/tokens.css`.

**Default: emit directly under the engine's `--ds-*` vocabulary** (`--ds-ink`, `--ds-primary`,
`--ds-radius-200`, …) — see `references/manifest-schema.md` and `nara-design-studio`'s
`references/pack-contract.md` §3.1 for the exact names its chrome depends on. This needs no bridge and is the
path to prefer.

**Exception — keep the source's own prefix + ship a bridge adapter.** If the adapted components' runtime styles
reference the source's own custom-property names directly (e.g. inline `style={{ color: 'var(--acme-ink)' }}`)
and renaming every reference isn't worth doing this pass, keep the original prefix and add a small adapter
stylesheet — one `:root { --ds-x: var(--acme-x); }` line per chrome-used token — listed in `globalCssPaths`
right after the token file. `nara-design-studio/assets/runtime/adapters/lyris-pack.css` is the worked reference
example for this pattern (the LYRIS pack's own custom-property prefix, bridged rather than renamed, because its
source repo is intentionally left untouched).

Record every extracted token — name, value, kind (`color` / `spacing` / `radius` / `type` / `shadow` / …), and
which file defines it — you'll need this list verbatim for the manifest's `tokens[]` array in Step 5.

## 5. Step 4 — Adapt each component, one at a time (the judgment step)

For every confirmed component, in order, do all of the following before moving to the next one:

1. Apply `references/adapt-guide.md`'s rules — strip store/router/context coupling, replace build-time
   CSS-in-JS/CSS Modules with token-driven inline styles, keep the original prop names.
2. Mount the adapted component standalone in `studio-template.html`, served through `nara-design-studio`'s
   `serve.py`.
3. Verify it actually renders and its interactive states work.
4. Fix anything broken **before** starting the next component.

**Never batch-adapt ahead of verification.** A rendering failure in component 3 is cheap to fix immediately;
the same failure discovered after adapting twelve components is not — you'd be debugging blind across a much
larger diff. This is the same "verify-as-you-go" discipline the design spec calls out by name.

Alongside each adapted component, emit its three companion files (see `adapt-guide.md` for the exact shape of
each): `<Name>.jsx` (the standalone version), `<Name>.d.ts` (typed props — no `any`), `<Name>.prompt.md` (a
short usage note: when to reach for it, its key props, one example).

## 6. Step 5 — Emit the manifest

Write `_ds_manifest.json` at the pack root per `references/manifest-schema.md`: `namespace`, `components[]`
(one entry per component adapted in Step 4, including any `status: "flagged"` entries — see §7 below),
`tokens[]` (from Step 3), `cards[]` (any specimen pages you authored along the way), `globalCssPaths[]` (the
token file, plus a bridge adapter if Step 3 needed one), and the `pack.*` block (`name`, `sourceRepo`,
`sourcePackages`, `kitHelpersPath`, `reuseRule`, `tier`). Set `tier` honestly: `"T2"` once components + tokens
are real; bump to `"T3"` only after Step 8 also ships `data.js` + kit helpers.

## 7. Step 6 — Bundle

Concatenate or build the adapted components into a single `_ds_bundle.js` that exposes every one of them on
`window.<namespace>` — the same namespace string the manifest declares. Target only what the engine's runtime
actually provides: in-browser Babel + CDN React. No bundler-specific runtime (no webpack/Vite module runtime, no
CSS Modules loader, no build-time CSS-in-JS extraction) — anything a component needed at build time had to be
resolved during adaptation in Step 4, not deferred to the bundle step.

## 8. Step 7 — Verify every mount

Re-serve the **whole pack** (not just the last component you touched) —
`serve.py --pack <thisPackDir> --out <scratchDir>` — and mount every bundled component at least once in
`studio-template.html`. Fix anything that fails before calling the pack done. A manifest that lists a component
which doesn't actually mount is a worse failure mode than not listing it at all — it would make the studio
promise something the pack can't deliver.

## 9. Step 8 — Optional T3: `data.js` + kit helpers

Skip this step entirely for a T2 pack — it is optional, not a checklist item. If the source DS has real
navigation/IA and shared layout helpers worth carrying over, extract: the nav tree / route enums / status enums
into `data.js` (exposed as the object the manifest's consumer expects), and any shared layout composition (a
`Shell`/`Page` wrapper composed from the pack's own components) into the file `manifest.pack.kitHelpersPath`
points at. Only set `tier: "T3"` once both of these are real.

## 10. Step 9 — Write the pack dir; point the studio at it

Land everything under one pack directory: `tokens/`, the per-component `.jsx`/`.d.ts`/`.prompt.md` triples from
Step 4 (kept alongside the bundle for maintainability, even though the runtime loads the compiled
`_ds_bundle.js`, not these files directly), `_ds_manifest.json`, `_ds_bundle.js`, and — for a T3 pack —
`data.js` plus the kit helpers file. Then set `packPath` in `nara-design-studio`'s
`references/settings.local.md` (copy it from `settings.local.md.example` if it doesn't exist yet) to this pack's
absolute path, and hand back to `nara-design-studio` to resume the interview against it.

## 11. Honesty note — read before you promise a clean extraction

Quality depends entirely on the shape of the source design system, not on this protocol. A component built
purely from tokens and props adapts cleanly. A component deeply wired into an app's store, router, or a runtime
CSS-in-JS theme provider may not adapt cleanly at all — and that is **surfaced, not silently dropped**. When a
component can't be adapted to a dependency-light standalone form within a reasonable pass, list it in the
manifest's `components[]` with `status: "flagged"` and a one-line reason (see `references/manifest-schema.md`
§ component entries), rather than omitting it and letting the pack quietly under-report what the source DS
actually has. The first real extraction against a given codebase is the true validation of this protocol for
that codebase — treat early passes as calibration, not as proof the next codebase will go as smoothly.

## 12. Reference index

- [references/adapt-guide.md](references/adapt-guide.md) — the concrete per-component adaptation rules
  (Step 4): what to strip, how to drive styling from tokens, what each component's `.d.ts` / `.prompt.md`
  companion looks like.
- [references/manifest-schema.md](references/manifest-schema.md) — the full `_ds_manifest.json` shape this
  builder targets, including the `components[]` entry schema (`status: "flagged"` and all) that this skill owns.
- `nara-design-studio/references/pack-contract.md` — the engine-side contract: fidelity tiers, required files
  per tier, and every manifest field the studio's runtime actually reads.
- `nara-design-studio/assets/runtime/adapters/lyris-pack.css` — a worked bridge-adapter example (Step 3).
