# workflow.json Schema

Single document drives the entire viewer. No build step — JSON is inlined into the HTML template, replacing the marker comment `/* __WORKFLOW_JSON__ */`.

## Top-level shape

```json
{
  "title": "string — app or repo name shown in header",
  "packages": [Package, ...],
  "actions": [Action, ...]
}
```

## Package

A package, service, or component — anything that can be a node.

| Field         | Required | Description |
|---------------|----------|-------------|
| `id`          | yes      | Stable identifier used by step `from`/`to`. Kebab-case. |
| `name`        | yes      | Human-readable label shown on the node. e.g. `@scope/web`. |
| `group`       | yes      | Column the node renders in. Use functional layers: `frontend`, `desktop`, `backend`, `data`, `infra`, `external`. Group order follows first-seen order in the JSON. |
| `description` | no       | One-line purpose, shown under the name. |

Group nodes by deployment boundary or layer — not by file system folder. Two packages that ship together in the same binary belong to one group.

## Action

A user-visible or operator-triggered flow. Examples: `Invite new user`, `todesktop build`, `Refresh OAuth token`, `Sync workspace`.

| Field     | Required | Description |
|-----------|----------|-------------|
| `id`      | yes      | Stable identifier. |
| `label`   | yes      | Action button text. |
| `summary` | no       | One-line description shown under the button and in the side panel header. |
| `steps`   | yes      | Ordered list of `Step`. |

### Step

One hop between two packages. Steps render as numbered arrows on the canvas and as numbered cards in the side panel.

| Field     | Required | Description |
|-----------|----------|-------------|
| `from`    | yes      | Package `id` initiating the call. |
| `to`      | yes      | Package `id` receiving the call. |
| `via`     | no       | Transport / mechanism. e.g. `POST /api/invites`, `IPC: invite:send`, `pub→sub: user.invited`, `import + function call`, `Worker postMessage`. |
| `data`    | no       | Payload shape or key fields passed. e.g. `email, role, workspaceId`. |
| `trigger` | no       | What causes this hop. e.g. `user submits form`, `webhook from Stripe`, `cron 0 * * * *`. Use when the step is not synchronous. |
| `notes`   | no       | Free-form annotation: invariants, retries, auth, side effects, failure modes. Keep one or two sentences. |

A step represents a directed information transfer. If the same package answers back, model it as a second step with reversed `from`/`to`.

## Authoring rules

1. **Cover every package that participates in at least one action.** Packages with no incoming or outgoing edges should be removed from `packages` unless they exist for context.
2. **Keep step granularity at the package boundary.** Do not model intra-package function calls.
3. **Annotate `via` with the actual mechanism**, not the verb. Prefer `HTTP POST /api/invites` over `sends invite`.
4. **Order steps temporally.** Step 1 happens first.
5. **Branches and loops:** if an action forks, model the dominant path. Document the branch in `notes`.
6. **External services** belong in `packages` under `group: "external"`.

## Example

```json
{
  "title": "Acme App",
  "packages": [
    { "id": "web", "name": "@acme/web", "group": "frontend", "description": "Next.js client" },
    { "id": "api", "name": "@acme/api", "group": "backend", "description": "Express API" },
    { "id": "db", "name": "postgres", "group": "data", "description": "Primary DB" },
    { "id": "mail", "name": "Postmark", "group": "external", "description": "Transactional email" }
  ],
  "actions": [
    {
      "id": "invite-user",
      "label": "Invite new user",
      "summary": "Admin invites a teammate by email.",
      "steps": [
        { "from": "web", "to": "api", "via": "POST /api/invites", "data": "email, role, workspaceId", "trigger": "admin submits invite form" },
        { "from": "api", "to": "db", "via": "INSERT invites", "data": "id, email, role, token, expiresAt", "notes": "token is 32-byte random, indexed unique." },
        { "from": "api", "to": "mail", "via": "POST /email", "data": "to, templateId=invite, vars{inviteUrl}" },
        { "from": "mail", "to": "web", "via": "user clicks link", "data": "GET /invite?token=...", "trigger": "email recipient opens link" }
      ]
    }
  ]
}
```

## Embedding into the template

Replace the literal text `/* __WORKFLOW_JSON__ */ {"title":"Workflow Map","packages":[],"actions":[]}` in `assets/template.html` with `/* __WORKFLOW_JSON__ */ <stringified JSON>`. Also replace `__WORKFLOW_TITLE__` (appears twice — `<title>` and header `<h1>`) with the actual title. The result is a single self-contained `.html` file with no network or build dependencies.
