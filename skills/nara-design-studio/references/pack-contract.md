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
| **T0** | Prose spec only — no runtime pack directory at all | High | Degradation path when no pack can be built or pointed at |
| **T1** | Token CSS (`tokens/*.css`) + a manifest + a few specimen "cards" | Medium | The **neutral starter pack** bundled with `nara-design-studio` |
| **T2** | + a `_ds_bundle.js` exposing the design system's components, **adapted** to run standalone | Visual: none. **API: whatever the adaptation changed** — see below | An external pack, hand-made or built by `nara-design-pack-builder` |
| **T3** | + `data.js` (navigation tree / enums) + shared kit helpers (`kitHelpersPath`) | Same as T2 | A mature external pack (e.g. a product's own design-system pack) |

The tier is a spectrum of **anti-drift**, not a quality judgment: T1 is enough to demo the studio's interview →
candidates → comment → handoff loop and to do generic, token-driven design with zero product code. T2/T3 mount
the design system's own components, so what gets designed looks like what implementers build with. As an
example, a product with a mature internal design system (real components + navigation data + shared layout
helpers) is a natural **T3** pack; a brand-new or public-facing pack usually starts life at **T1** or **T2**.

**What T2/T3 does NOT eliminate.** A pack's components are *adapted* copies, not the ones an implementer
imports: `nara-design-pack-builder`'s adapt guide requires stripping store/router/context couplings into plain
props, converting CSS-in-JS to token styles, and replacing i18n hooks with resolved strings. Each of those is a
prop-shape divergence by construction, and a prop that no longer exists is accepted **silently** by React — the
screen just renders the wrong thing, with no type error, lint error or failing test. The pack's styling language
may also differ from the target repo's (token custom properties here, utility classes there), so design values
cannot be pasted either.

So visual drift is what T2/T3 removes; **API drift is what it relocates** — from the mockup into the handoff.
The contract closes it in two places, both mechanical rather than prose:

- `components[].real` in the manifest (§3.3) records every divergence at the moment it is made, and the studio
  writes the rows for the components a design actually rendered into its exported `Spec.md`.
- The **layout contract** (§6) states the structure implementation must reproduce, and `check-layout.py` diffs
  it against the implemented page.

T0 is not a directory contract — it means "no pack, prose-only spec" and is out of scope for this document
beyond noting it exists as the bottom of the ladder.

**A `DESIGN.md` is not T0.** A DESIGN.md (Stitch format, see `nara-design-md`) carries a complete token surface
in its frontmatter — a color role set, a typography scale, spacing, radii, and per-component style specs — which
is strictly more than a hand-written T1 pack usually ships. Convert it rather than reading it as prose:

```
python3 assets/runtime/designmd_to_pack.py --design <path/to/DESIGN.md> --out <packDir> [--namespace <Global>]
```

The transform is mechanical and makes no design judgments. It lands at **T1** for a DESIGN.md with no
`components:` block, and at **T2** when there is one — each entry becomes a standalone JSX component in the
generated `_ds_bundle.js`. Two properties the converter guarantees, both worth knowing when reading its output:

- **Authored vs derived is never blended.** The engine's chrome needs tokens a DESIGN.md does not define
  (`--ds-primary-hover`, `--ds-surface`, the ink ramp, `--ds-radius-200`, `--ds-shadow-popover`). Those are
  emitted into a separate, commented block in `tokens/tokens.css` and reported on stdout, so an authored value
  is always distinguishable from an inferred one. A chrome token with no source role at all is reported as
  `MISSING` and the converter exits non-zero.
- **No literal survives into a component.** A spec's literal geometry (`padding: 12px 24px`) becomes a
  component-scoped token (`--ds-comp-button-primary-padding`) that the generated JSX references via `var()`,
  so the pack itself satisfies the same adherence rules its output is held to (§3.5).

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
| `components` | array | pack-authoring / `nara-design-pack-builder`, Spec.md export | Component descriptors available for T2/T3 generation. The per-entry shape is owned by `nara-design-pack-builder`'s manifest schema, except for the `real` block the engine reads — see §3.3. A T1 pack ships this as an empty array. |
| `globalCssPaths` | array of strings | screen generation | CSS files, relative to the pack root, that every generated screen must link (typically the token stylesheet(s); T2/T3 packs may add more). |
| `tokens` | array of `{ name, value, kind, definedIn }` | interview / handoff | The design tokens the pack exposes (color, spacing, radius, …) and which stylesheet defines each — used to enumerate what's available when nothing else exists as a real component. |
| `cards` | array of `{ path, group, name }` | studio's specimen browser | Guideline / specimen HTML pages (foundations, component demos) the studio can show. Each card file also self-declares the same metadata in a leading `<!-- @dsCard group="..." name="..." subtitle="..." viewport="WxH" -->` comment, so a card is browsable standalone even without the manifest entry. |
| `startingPoints` | array (optional) | interview stage | Pack-provided example screens/templates used as jump-off points when interviewing for a new design. Not required — omit or leave empty for packs that don't curate any. |
| `adherenceConfig` | string (optional) | emit-time gate | Path, relative to the pack root, to this pack's adherence rule file — see §3.5. Omit to use the gate's built-in defaults. |

**Token vocabulary:** the engine's chrome (`studio.js` + `studio.css`) consumes design tokens under a single,
generic **`--ds-*`** prefix (e.g. `--ds-ink`, `--ds-primary`, `--ds-canvas`, `--ds-radius-200`) — the bundled
starter pack's `tokens/tokens.css` is the authoritative reference for the full set the chrome depends on. A pack
**SHOULD** name its own custom properties `--ds-*` directly so the chrome renders with zero extra wiring. A pack
that ships tokens under a different prefix (for example an `--acme-*` design system kept as-is) instead ships or
loads a small **adapter stylesheet** that maps its prefix onto `--ds-*` — one `:root { --ds-x: var(--acme-x); }`
line per chrome-used token. The adapter lives with the pack (not with the engine); list it in the pack's
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

### 3.3 `components[].real` — the pack → real prop map

Each entry in `components[]` may carry a `real` block naming what an implementer actually imports and every way
the adapted copy diverges from it. `nara-design-pack-builder` writes it during adaptation — the one moment both
sides are in view; reverse-engineering it later means re-reading the source design system from scratch.

```jsonc
{
  "name": "UserBadge",                       // the property on window.<namespace>
  "adaptedPath": "components/data/UserBadge.jsx",
  "status": "adapted",
  "real": {
    "import": "UserBadge",                   // null when there is no counterpart at all
    "from": "@/components/common/UserBadge", // package or path an implementer imports from
    "propMap": { "showAvatar": "isProfileImageVisible" },   // renamed props only
    "drop": ["size"],                        // props with NO counterpart — never carry them over
    "notes": "loginName and department feed the tooltip; omitting them ships an empty one."
  }
}
```

| Field | Meaning |
|---|---|
| `import` | The real component's name. `null` = no counterpart; `notes` must then say what to compose instead. |
| `from` | Where to import it from — the real package or path, never this pack's own path. |
| `propMap` | Renamed props only, `adaptedProp → realProp`. Props that survived adaptation unchanged are omitted. |
| `drop` | Props the adapted copy invented (or kept from a stripped coupling) that the real component does not have. These are the dangerous ones: React accepts an unknown prop silently. |
| `notes` | The non-mechanical part — children vs. slot props, enum value differences, "takes no props at all", required companion fields. |

Omit `real` only when the pack genuinely cannot name a counterpart. An absent block is not "no divergence": the
studio prints an explicit warning into the exported spec when a rendered component has no `real` entry, because
"unknown" and "identical" must not read the same to an implementer.

### 3.4 How a generated screen consumes the manifest

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

`components[].real` (§3.3) is deliberately **not** copied into `STUDIO_CONFIG`: the runtime fetches
`/_pack/_ds_manifest.json` directly and emits rows only for the components that candidate actually rendered.
Copying it per screen would let a screen's mapping rot while the pack's stayed correct.

### 3.5 `adherenceConfig` — the emit-time gate

The baseline rule "tokens only — no hardcoded brand values" (`SKILL.md` §5) cannot hold as prose: by the time
anyone reads output containing `padding: 16px`, the rule has already been broken. It is enforced mechanically
instead, before a generated screen is written:

```
python3 assets/runtime/check_adherence.py <file.html> [...] --pack <packDir>
```

Two rules ship on by default and need no pack cooperation — **raw hex colors** and **raw px values** outside a
small allowlist (a `1px` hairline is not a spacing decision). Exit code `1` means violations; fix them and
re-emit. Declarations inside a `:root { … }` block are always exempt, because `SKILL.md` §5 explicitly tells a
portable single-file export to inline the pack's token block, and those declarations *are* the tokens.

A pack tightens or relaxes the rules by shipping a JSON config and naming it in `adherenceConfig`:

```jsonc
{
  "forbidRawHex": true,
  "forbidRawPx": true,
  "allowedRawPx": ["0px", "1px"],
  "ignorePatterns": ["data-studio-label"],   // regexes; a matching line is skipped
  "allowTokens": ["--ds-primary", "…"]       // informational: what this pack actually defines
}
```

Declaring `adherenceConfig` and then not shipping the file is a hard error, not a silent pass — a gate that
quietly disables itself is worse than no gate. A pack that ships richer rules in another format (an ESLint or
oxlint config, say, with per-component prop allowlists) keeps that file for its own repo tooling; this field is
for the subset the studio can enforce on generated HTML without any extra toolchain.

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

Which pack a project uses is **not** part of this contract file — it is a per-project decision, recorded in
that project's `.claude/overrides/nara-design-studio.md` and asked for exactly once (`SKILL.md` §2). A project
never inherits a pack from another project: the user's `defaultPackPath` (see `settings.local.md.example`) and
any pack under `~/.claude/design-packs/` are offered as the pre-selected answer to that question, never applied
on their own. A design produced against the bundled neutral starter pack is always explicitly T1 — choosing it
is an answer, never a silent default.

---

## 6. The layout contract — what implementation must reproduce

Pixel fidelity is not the parity bar for a handoff; **layout** is: which sections exist, in what order, a
table's columns in order, a form's fields in order, and which side each action sits on. Those are design
decisions. Exact spacing and shade are not — they follow from the tokens.

`assets/runtime/layout-contract.js` reads exactly that off a live DOM and returns normalized JSON. It is the
**one** extraction, deliberately run on both sides:

| Side | How | Produces |
|---|---|---|
| Design | The studio loads it (`/_studio/layout-contract.js`); every exported `Spec.md` opens with the contract, and **Export → Layout contract (JSON)** downloads it | `<name>-<candidate>.layout.json` |
| Implementation | Paste the same file into the implemented page's console (or evaluate it via a browser MCP), then `copy(JSON.stringify(window.LAYOUT_CONTRACT.extract(), null, 2))` | `impl.layout.json` |

```
python3 assets/runtime/check-layout.py design.layout.json impl.layout.json
```

Exit `0` = match, `1` = drift, `2` = bad input. It reports missing / extra / reordered **sections**, reordered
or missing **table columns**, **field** order, and any action that moved to a different side. Section names
differ across the two sides (a design labels its regions, an app does not), so sections are aligned by content
overlap — column names, field labels, button copy — never by name.

Two consequences for whoever generates a screen:

- **Label every region an implementer must reproduce** with `data-studio-label`. The contract is built from
  those; an unlabeled region silently drops out of the handoff, which reads as "not part of the design".
- The extractor auto-detects the content root (`.ds-page` in studio output, `<main>` in a typical app) and
  ignores what is not layout: exact spacing/color, and option labels inside a radio/checkbox group (a `<label>`
  wrapping its own input is an option, not a field).

Tests: `python3 -m pytest assets/runtime/test_check_layout.py`
