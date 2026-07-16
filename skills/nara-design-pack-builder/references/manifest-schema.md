# `_ds_manifest.json` — the target shape

This is the manifest `nara-design-pack-builder` writes at the end of Step 5 (`SKILL.md` §6). It is the same
contract `nara-design-studio` reads to consume a pack — see that skill's `references/pack-contract.md` for the
engine's side of this document (which fields the runtime actually loads, the fidelity tiers, and the
`/_studio` / `/_pack` / `/` serve topology). This file covers the same ground from the **builder's** side: what
to fill into each field while extracting a pack, and the `components[]` entry shape this skill owns (the
contract only says its exact per-entry shape is "owned by `nara-design-pack-builder`'s manifest schema" — this
is that schema).

**Token vocabulary — non-negotiable:** the engine's chrome consumes tokens under a single prefix, **`--ds-*`**
(`--ds-ink`, `--ds-primary`, `--ds-canvas`, `--ds-radius-200`, …). A pack built by this skill **SHOULD** emit its
own tokens directly under `--ds-*` — see `adapt-guide.md` §2 and `SKILL.md` Step 3. A pack that must keep the
source design system's own custom-property prefix (because adapted components' runtime styles reference it
directly, and renaming every reference isn't worth this pass) instead ships a small bridge adapter stylesheet
that maps its own prefix onto `--ds-*`, one `:root` line per chrome-used token, and lists that adapter file in
`globalCssPaths` right after the pack's own token file. The LYRIS pack is the reference example of this bridge
pattern — its custom properties keep their own prefix (its source repo is intentionally left untouched), and a
small adapter stylesheet maps them onto `--ds-*` for the engine. Do not reach for a bridge as the default path;
it exists for exactly that one case, not as a shortcut around renaming.

---

## 1. Top-level fields

| Field | Type | Fill it with |
|---|---|---|
| `namespace` | string | The `window` global your `_ds_bundle.js` exposes (e.g. `"DS"`, `"Acme"`). Every adapted component in `components[]` must actually exist at `window[namespace][component.name]` once the bundle loads — Step 7's mount check is what verifies this. |
| `source` | string (optional) | A free-text label for where this pack came from (e.g. `"acme-design-system"`). Documentation only — not read by the runtime. |
| `pack` | object | See §2. |
| `components` | array | One entry per component this skill enumerated in Step 2 and attempted in Step 4 — including flagged ones (§3). Never omit an attempted component; either it's `"adapted"` or it's `"flagged"` with a reason. |
| `globalCssPaths` | array of strings | Every CSS file (relative to the pack root) a generated screen must link — typically `["tokens/tokens.css"]`, plus a bridge adapter path if Step 3 needed one. |
| `tokens` | array | See §4 — the flat token list extracted in Step 3. |
| `cards` | array of `{ path, group, name }` | Any specimen/guideline HTML pages authored while building the pack (optional — a pure T2 component pack may ship none). |
| `startingPoints` | array (optional) | Example screens/templates worth offering as interview jump-off points. Usually empty for a freshly built pack; leave it out rather than fabricate entries. |

## 2. The `pack.*` block

```jsonc
"pack": {
  "name": "Acme DS",
  "sourceRepo": "org/acme-design-system",
  "sourcePackages": ["@acme/ui-components", "components/layout"],
  "kitHelpersPath": "kit/_shared.jsx",
  "reuseRule": "Reuse Acme DS components; do not recreate from tokens.",
  "tier": "T2"
}
```

| Field | Fill it with |
|---|---|
| `name` | The design system's own display name (what the user calls it, not this pack's internal directory name). |
| `sourceRepo` | Where the real source lives — printed verbatim into every `Spec.md` the studio exports, so implementers know where to go for the real thing. |
| `sourcePackages` | The actual package names / import paths an implementer would import from in the real product — not this pack's own paths. |
| `kitHelpersPath` | Relative path (inside the pack) to shared layout helpers, if Step 8 produced any. Leave `""` for a T2 pack that skipped Step 8. |
| `reuseRule` | One sentence, printed into every exported spec, telling implementers to reuse the real components rather than recreate them from tokens — this is the line that makes the studio's FROZEN-vs-DESIGNED rule concrete for this specific pack. |
| `tier` | `"T2"` once components + tokens are real and verified (Steps 1–7 done); `"T3"` only once Step 8's `data.js` + kit helpers are also real. Never mark a tier the pack doesn't actually back up — the studio's bootstrap gate surfaces this value to the user as a trust signal. |

## 3. `components[]` — entry shape (owned by this skill)

```jsonc
{
  "name": "Button",
  "group": "Actions",
  "sourcePath": "src/components/Button/Button.tsx",
  "adaptedPath": "components/actions/Button.jsx",
  "promptPath": "components/actions/Button.prompt.md",
  "typesPath": "components/actions/Button.d.ts",
  "status": "adapted",
  "note": ""
}
```

| Field | Meaning |
|---|---|
| `name` | Must match the property name on `window.<namespace>` (`adapt-guide.md` §3) — this is how a generated screen actually mounts the component. |
| `group` | A grouping label for browsing (e.g. `"Actions"`, `"Forms"`, `"Navigation"`, `"Data Display"`) — mirrors how `cards[]` groups specimens. Free-form, but keep it consistent across entries. |
| `sourcePath` | Where this component lives in the **original** DS repo — traceability back to source. Informational only; the runtime never resolves this path. |
| `adaptedPath` | Where the standalone `.jsx` lives **inside this pack** — kept for maintainability alongside the compiled `_ds_bundle.js`, which is what the runtime actually loads. |
| `promptPath` / `typesPath` | Pointers to the component's companion files (`adapt-guide.md` §5). |
| `status` | `"adapted"` — mounted and verified per Step 7. `"flagged"` — attempted but not cleanly adaptable (see `adapt-guide.md` §6); still listed, never silently dropped, per `SKILL.md` §11's honesty note. |
| `note` | Required when `status` is `"flagged"`: one line on why (e.g. `"reads 5 pieces of global app state to derive its own layout; no reasonable prop substitute this pass"`). Optional, usually empty, when `status` is `"adapted"`. |

A `"flagged"` component is not mounted by `_ds_bundle.js` and is not expected to appear at
`window[namespace][name]` — its entry exists purely so the manifest is honest about what the source DS has that
this pack doesn't yet cover, rather than making that gap invisible.

## 4. `tokens[]` — entry shape

```jsonc
{ "name": "--ds-primary", "value": "#2563eb", "kind": "color", "definedIn": "tokens/tokens.css" }
```

One entry per token extracted in Step 3. `kind` is a short free-form label (`color`, `spacing`, `radius`,
`type`, `shadow`, …) — used by the studio's interview/handoff stages to enumerate what's available. `definedIn`
is the file (relative to the pack root) that actually declares the custom property — usually
`tokens/tokens.css`, or the bridge adapter file for a token whose canonical value is bridged rather than
re-declared.

## 5. Worked example — a freshly built T2 pack

```jsonc
{
  "namespace": "Acme",
  "source": "acme-design-system",
  "pack": {
    "name": "Acme DS",
    "sourceRepo": "org/acme-design-system",
    "sourcePackages": ["@acme/ui-components"],
    "kitHelpersPath": "",
    "reuseRule": "Reuse Acme DS components; do not recreate from tokens.",
    "tier": "T2"
  },
  "components": [
    {
      "name": "Button",
      "group": "Actions",
      "sourcePath": "src/components/Button/Button.tsx",
      "adaptedPath": "components/actions/Button.jsx",
      "promptPath": "components/actions/Button.prompt.md",
      "typesPath": "components/actions/Button.d.ts",
      "status": "adapted",
      "note": ""
    },
    {
      "name": "DataGrid",
      "group": "Data Display",
      "sourcePath": "src/components/DataGrid/DataGrid.tsx",
      "adaptedPath": "components/data-display/DataGrid.jsx",
      "promptPath": "components/data-display/DataGrid.prompt.md",
      "typesPath": "components/data-display/DataGrid.d.ts",
      "status": "flagged",
      "note": "reads live virtualization state from an app-level scroll-sync store; no reasonable prop substitute this pass"
    }
  ],
  "globalCssPaths": ["tokens/tokens.css"],
  "tokens": [
    { "name": "--ds-primary", "value": "#2563eb", "kind": "color", "definedIn": "tokens/tokens.css" },
    { "name": "--ds-ink", "value": "#18181b", "kind": "color", "definedIn": "tokens/tokens.css" },
    { "name": "--ds-radius-200", "value": "6px", "kind": "radius", "definedIn": "tokens/tokens.css" }
  ],
  "cards": [
    { "path": "guidelines/actions.card.html", "group": "Actions", "name": "Button variants" }
  ]
}
```

## 6. Checklist before calling `SKILL.md` Step 5 done

- [ ] `namespace` matches exactly what `_ds_bundle.js` assigns to `window`.
- [ ] Every component enumerated in Step 2 has a `components[]` entry — `"adapted"` or `"flagged"`, never absent.
- [ ] Every `"adapted"` entry actually mounted in Step 7's full-pack re-serve.
- [ ] `globalCssPaths` lists the token file (and bridge adapter, if any) — nothing a generated screen needs is
      missing.
- [ ] `tier` matches what Steps 1–8 actually delivered, not what you hope to deliver next pass.
- [ ] `pack.reuseRule` and `pack.sourceRepo` are filled in — these flow verbatim into every `Spec.md` the studio
      exports for this pack.
