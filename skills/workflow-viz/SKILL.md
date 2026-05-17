---
name: workflow-viz
description: >-
  Generate a single self-contained HTML page that visualizes packages, components, and the
  information flow between them for selectable actions, driven by one workflow.json document.
  USE FOR: "workflow viz", "워크플로우 시각화", "패키지 흐름도", "flow map", "다이어그램 만들어", "패키지 간 흐름 문서화".
  DO NOT USE FOR: architecture decision records (use /adr), code-level sequence diagrams,
  generic README generation.
---

# Workflow Viz

Produce a single-file interactive HTML viewer that documents every package and component in an app, with clickable actions (e.g. `Invite new user`, `todesktop build`) that highlight the cross-package flow and annotate how data is passed at each hop.

The viewer is driven entirely by a `workflow.json` document. Both files ship as a unit: the JSON is the source of truth, the HTML is the renderer.

## Output

Two files written to `docs/workflow-viz/` (or a path the user names):

- `workflow.json` — schema in [references/json-schema.md](references/json-schema.md).
- `workflow.html` — self-contained viewer based on [assets/template.html](assets/template.html). No network, no build step, opens directly in any browser.

## Step 1 — Confirm intent

Before scanning the codebase, ask one short check-in to lock scope. Phrase it in the user's language. Example:

> "패키지 간 워크플로우 뷰어 만들겠습니다. 출력 경로 `docs/workflow-viz/` 맞나요? 그리고 우선 다룰 액션이 따로 있나요, 아니면 코드베이스에서 발견되는 모든 사용자/운영자 트리거를 자동으로 뽑아낼까요? 이게 말이 되나요? 질문 있나요?"

Capture two things:
1. Output path.
2. Action seed list — user-given vs. auto-discovered.

If the repo has no recognizable manifest at all (no `package.json`, `pnpm-workspace.yaml`, `Cargo.toml`, `go.mod`, etc.), stop and ask the user to point at the root packages — do not guess.

## Step 2 — Discover packages

Identify every package or component that can be a node. Priority order:

1. **Workspace manifests** — parse `package.json` workspaces, `pnpm-workspace.yaml`, `turbo.json`, `lerna.json`, `Cargo.toml [workspace]`, `go.work`. These are authoritative.
2. **Top-level service directories** — `apps/*`, `packages/*`, `services/*`, `crates/*` when no workspace file exists.
3. **External services** — third parties the code calls (`stripe`, `postmark`, `s3`, `auth0`, etc.). Add to `group: "external"` only if at least one action passes data to them.

For each package collect: stable `id` (kebab-case), display `name` (the manifest `name` field, or the directory), `group` (frontend / desktop / backend / data / infra / external), and a one-line `description` read from the package README or manifest.

Drop packages that no action touches. The viewer is for flows, not inventory.

## Step 3 — Discover actions

An action is a user-visible or operator-triggered flow that crosses package boundaries. Find them via these entry points:

- **CLI scripts** — `package.json` scripts that ship behavior (`build`, `release`, `migrate`), not dev-loops (`dev`, `lint`).
- **HTTP routes & RPC handlers** — API entry points named after intent.
- **UI buttons and form submits** — search frontend for handlers like `onSubmit`, `onClick` calling network code.
- **Scheduled jobs and queue consumers** — cron, BullMQ, SQS, etc.
- **External webhooks** — handlers for inbound events.
- **Build/release pipelines** — `todesktop build`, GitHub Action workflows, `release` scripts.

Bias toward actions that span at least two packages. Single-package actions add noise. Cap the initial set at 8–12 actions; document the rest in a `TODO` block at the top of the JSON for later expansion.

## Step 4 — Trace each action's steps

For each action, walk the call graph in execution order. Use `grep` and file reads — do not guess.

For every hop record:
- `from` and `to` package `id`.
- `via` — the actual mechanism, not the verb (`POST /api/invites`, `IPC: invite:send`, `pub→sub: user.invited`, `import + function call`).
- `data` — payload field names, not types (`email, role, workspaceId`).
- `trigger` — only when asynchronous (`webhook`, `cron`, `user submits form`).
- `notes` — invariants, auth, retries, failure modes worth knowing. One or two sentences max.

Where `[UNVERIFIED]` material is unavoidable (e.g. the call into an external service is not in the local repo), label it in `notes`.

## Step 5 — Author workflow.json

Write the document following [references/json-schema.md](references/json-schema.md). Validate before rendering:

- Every step's `from` and `to` resolves to a package `id` listed in `packages`.
- Steps within an action are ordered temporally.
- No package appears in `packages` without participating in at least one step.

## Step 6 — Render workflow.html

Copy [assets/template.html](assets/template.html) to the output path. Perform two text substitutions:

1. Replace `__WORKFLOW_TITLE__` (two occurrences) with the JSON `title`.
2. Replace the literal sequence `/* __WORKFLOW_JSON__ */ {"title":"Workflow Map","packages":[],"actions":[]}` with `/* __WORKFLOW_JSON__ */ ` followed by the stringified JSON.

The result is a single `.html` file. Open it directly — no server.

## Step 7 — Verify with the user

Report back with: total package count, action count, list of action labels, and the file paths. Close with:

> "이게 말이 되나요? 빠진 액션이나 잘못 표시된 흐름 있나요?"

Iterate on the JSON only — the HTML never needs hand editing.

## Rules

- Only state facts verifiable from code. Unverifiable hops or payloads carry `[UNVERIFIED: <reason>]` in `notes`.
- Group nodes by deployment boundary, not folder.
- Step granularity is package-level. Never model intra-package function calls.
- The viewer ships as one HTML file. Do not split CSS or JS into separate files.

## Resources

- [assets/template.html](assets/template.html) — single-file viewer template with `__WORKFLOW_TITLE__` and `__WORKFLOW_JSON__` substitution markers.
- [references/json-schema.md](references/json-schema.md) — full schema with field semantics, authoring rules, and a worked example.
