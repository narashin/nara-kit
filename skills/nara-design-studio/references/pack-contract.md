# The nara-design-studio pack contract

`nara-design-studio` is a **generic engine**: it ships no design-system components of its own. Everything
product-specific — tokens, real components, navigation data, brand rules — comes from a **pack**: a directory
that follows this contract. This document defines that contract so a pack author (human or agent, including
`nara-design-pack-builder`) knows exactly what a pack must contain and how the engine consumes it, without
needing to read the engine's source.

A pack can be as small as a token stylesheet or as complete as a full component bundle with app data. The
**fidelity tier** below tells you which.

---

## 1. Fidelity tiers

| Tier | Pack materials | Drift vs. the real product | Where it typically lives |
|------|-----------------|------------------------------|---------------------------|
| **T0** | `DESIGN.md` prose only — no runtime pack directory at all | High | Degradation path when no pack can be built or pointed at |
| **T1** | Token CSS (`tokens/*.css`) + a manifest + a few specimen "cards" | Medium | The **neutral starter pack** bundled with `nara-design-studio` |
| **T2** | + a real `_ds_bundle.js` exposing the design system's actual components | None (components are real) | An external pack, hand-made or built by `nara-design-pack-builder` |
| **T3** | + `data.js` (navigation tree / enums) + shared kit helpers (`kitHelpersPath`) | None | A mature external pack (e.g. a product's own design-system pack) |

The tier is a spectrum of **anti-drift**, not a quality judgment: T1 is enough to demo the studio's interview →
candidates → comment → handoff loop and to do generic, token-driven design with zero product code. T2/T3 mount
**real** components, so what gets designed is what implementers actually have to build with — no drift between
prototype and production. As an example, a product with a mature internal design system (real components +
navigation data + shared layout helpers) is a natural **T3** pack; a brand-new or public-facing pack usually
starts life at **T1** or **T2**.

T0 is not a directory contract — it means "no pack, prose-only spec" and is out of scope for this document
beyond noting it exists as the bottom of the ladder.

---

## 2. Required files per tier

| Tier | Required files (relative to the pack root) |
|------|----------------------------------------------|
| **T1** | `tokens/*.css` (one or more token stylesheets) + `_ds_manifest.json`. A stub `_ds_bundle.js` that exposes no components is optional — only needed so a template's `<script src="/_pack/_ds_bundle.js">` doesn't 404 when nothing else provides one. |
| **T2** | Everything in T1, **plus** a real `_ds_bundle.js` that exposes the pack's actual components on `window.<namespace>` (the window global named by the manifest's `namespace` field). |
| **T3** | Everything in T2, **plus** `data.js` (navigation tree / enums, exposed as the object the manifest calls out) **and** the kit helpers file pointed to by `manifest.pack.kitHelpersPath` (shared JSX that composes common layouts on top of the DS components). |

A pack directory is otherwise free-form beyond these required paths — `_ds_manifest.json` is the single source
of truth for where everything else lives (see §3 `globalCssPaths`, `cards`).

---

## 3. The manifest — `_ds_manifest.json`

Every pack ships one `_ds_manifest.json` at its root. It is the only file the engine (and any agent generating
a screen from a pack) needs to parse to understand what the pack offers.

### 3.1 Top-level fields

| Field | Type | Read by | Meaning |
|-------|------|---------|---------|
| `namespace` | string | template wiring | The `window` global the pack's `_ds_bundle.js` exposes (e.g. `"DS"`). Empty string (`""`) for a token-only pack with no bundle — the render guard then skips mounting any DS component and renders the token-built sample body as-is. |
| `source` | string (optional) | humans / docs | A free-text label for where this pack came from (e.g. `"starter"`). Not consumed by the runtime — documentation only. |
| `pack` | object | Spec.md export, bootstrap gate | Pack metadata block — see §3.2. |
| `components` | array | pack-authoring / `nara-design-pack-builder` | Component descriptors available for T2/T3 generation. The exact per-entry shape is owned by `nara-design-pack-builder`'s manifest schema; a T1 pack ships this as an empty array. |
| `globalCssPaths` | array of strings | screen generation | CSS files, relative to the pack root, that every generated screen must link (typically the token stylesheet(s); T2/T3 packs may add more). |
| `tokens` | array of `{ name, value, kind, definedIn }` | interview / handoff | The design tokens the pack exposes (color, spacing, radius, …) and which stylesheet defines each — used to enumerate what's available when nothing else exists as a real component. |
| `cards` | array of `{ path, group, name }` | studio's specimen browser | Guideline / specimen HTML pages (foundations, component demos) the studio can show. Each card file also self-declares the same metadata in a leading `<!-- @dsCard group="..." name="..." subtitle="..." viewport="WxH" -->` comment, so a card is browsable standalone even without the manifest entry. |
| `startingPoints` | array (optional) | interview stage | Pack-provided example screens/templates used as jump-off points when interviewing for a new design. Not required — omit or leave empty for packs that don't curate any. |

**Token vocabulary:** the engine's chrome (`studio.js` + `studio.css`) consumes design tokens under a single,
generic **`--ds-*`** prefix (e.g. `--ds-ink`, `--ds-primary`, `--ds-canvas`, `--ds-radius-200`) — the bundled
starter pack's `tokens/tokens.css` is the authoritative reference for the full set the chrome depends on. A pack
**SHOULD** name its own custom properties `--ds-*` directly so the chrome renders with zero extra wiring. A pack
that ships tokens under a different prefix (for example, the external LYRIS pack's `--lyris-*` tokens, kept
as-is since that pack's repo is untouched) instead ships or loads a small **adapter stylesheet** that maps its
prefix onto `--ds-*` — one `:root { --ds-x: var(--lyris-x); }` line per chrome-used token. See
`assets/runtime/adapters/lyris-pack.css` for the reference example. List the adapter in the pack's
`globalCssPaths` (after the pack's own token file) so it loads on every generated screen.

### 3.2 The `pack.*` block

```jsonc
"pack": {
  "name": "Acme DS",
  "sourceRepo": "org/acme-design-system",
  "sourcePackages": ["@acme/ui-components", "components/layout"],
  "kitHelpersPath": "kit/_shared.jsx",
  "reuseRule": "Reuse Acme DS components; do not recreate from tokens.",
  "tier": "T3"
}
```

| Field | Meaning |
|-------|---------|
| `name` | Display name of the design system (e.g. `"Acme DS"`, or `"Starter"` for the bundled neutral pack). |
| `sourceRepo` | Human-readable pointer to the DS's real source repo. Printed as the "real source of truth" line in every exported `Spec.md`. Empty string for the neutral starter (it has no product repo). |
| `sourcePackages` | The real package/module names or paths an implementer should import from. Rendered as a parenthetical after `sourceRepo` in the exported spec. |
| `kitHelpersPath` | Relative path (inside the pack) to shared JSX helpers that compose common layouts on top of the DS's components. Empty if the pack ships none — typical for T1/T2; T3 packs usually have one. |
| `reuseRule` | One-line instruction, printed into every exported `Spec.md`, telling the implementer to reuse the DS's real components rather than recreate them from tokens. |
| `tier` | The pack's fidelity tier (`"T0"` \| `"T1"` \| `"T2"` \| `"T3"`, see §1). This is manifest-only metadata consumed by the pack-builder and the studio's bootstrap gate — it informs which capabilities to expect, it is not rendered into a generated screen. |

**Note on `namespace` placement:** `namespace` lives at the manifest's top level, **not** nested inside `pack`.
When an agent generates a screen from a pack, it copies `manifest.namespace` alongside the `pack.*` fields into
that screen's own embedded config object (see §4) purely as a per-screen convenience — don't be surprised that
the two shapes differ slightly between the source-of-truth manifest and a generated screen's config.

### 3.3 How a generated screen consumes the manifest

Each generated screen HTML embeds a small `STUDIO_CONFIG` object (read by the engine's runtime chrome,
`studio.js`) that carries a **subset** of the manifest, reshaped for that one screen:

```jsonc
window.STUDIO_CONFIG = {
  title: "...", brief: "...",
  pack: {
    name, namespace, sourceRepo, sourcePackages, kitHelpersPath, reuseRule
    // note: no "tier" here — tier is manifest/build-time metadata, not runtime config
  },
  candidates: [ /* per-direction id/label/note/interactions */ ],
  fidelity: "styled" // or "wireframe"
};
```

`studio.js` uses `cfg.pack.reuseRule`, `cfg.pack.sourceRepo`, `cfg.pack.sourcePackages`, `cfg.pack.namespace`,
and `cfg.pack.kitHelpersPath` verbatim when it builds the exported `Spec.md` handoff document, so a pack author
who fills these in accurately gets a correct, product-specific handoff spec for free — no template edits needed.

---

## 4. Serve topology

The engine runtime, the pack, and the generated output normally live in **three different directories** (the
runtime ships inside `nara-design-studio`, the pack is external, the output is per-project). One dev server
resolves all three under a single HTTP origin so a template's absolute paths work:

```
serve.py --pack <packDir> --out <outDir> [--runtime <dir>] [--port 8917]
```

| Mount | Serves | Backing directory |
|-------|--------|--------------------|
| `/_studio/*` | The engine's runtime chrome — `studio.js`, `studio.css` | `nara-design-studio`'s `assets/runtime/` (or `--runtime`) |
| `/_pack/*` | The design-system pack — bundle, tokens, data, manifest, kit helpers | `<packDir>` (the `--pack` argument) |
| `/*` | Generated output — candidate HTML, `out/`, finalized `handoff/` | `<outDir>` (the `--out` argument) |

`studio-template.html` references the runtime as `/_studio/studio.js` / `/_studio/studio.css`, and pack assets
as `/_pack/_ds_bundle.js`, `/_pack/tokens/tokens.css`, `/_pack/data.js`, `/_pack/<kitHelpersPath>` — filled in
from the manifest at generation time. Sidecars the studio writes at runtime (`comments.jsonl`,
`capture-requests.jsonl`, `*.interactions.json`, exported `*.spec.md`) are written under `<outDir>`, never under
the pack or runtime directories.

Each mount is traversal-guarded: a request path that would resolve outside its mounted root falls back to that
root instead of escaping it. `file://` is not supported — a screen must be opened through this server so the
three mounts (and the studio's comment/capture/spec POST endpoints) resolve.

---

## 5. Pointing the studio at a pack — `packPath`

Which pack a project uses is **not** part of this contract file — it's a per-project setting. See
`settings.local.md.example` in this same `references/` directory: it documents the `packPath` key that a
project's gitignored `settings.local.md` sets to point the studio at an external pack. Without a `packPath`
set, the studio falls back to its bundled neutral T1 starter pack (`assets/starter-pack/`) — a design produced
against the starter pack is always explicitly T1; the fallback is a visible choice, never a silent default.
