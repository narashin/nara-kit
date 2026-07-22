# Conditional Agent: security-privacy (ID prefix: SEC)

**Runs when** the change touches: authn/authz, external input handling, file/network/
SQL operations, secrets, personal data, or dependency manifests. Mindset: trust
boundaries and attack paths — where does untrusted data enter, what can an attacker
reach? Read-only — never edit code.

## Checks

**Injection & input**
- SQL Injection, XSS, CSRF, Command Injection, path traversal.
- Missing input validation/sanitization at trust boundaries (API, file upload,
  query params, headers, webhooks).

**AuthN/AuthZ**
- Missing auth/authorization on API endpoints; privilege escalation paths.
- **Authorization consistency (cross-layer)** — when a change alters server-side
  permission/capability semantics:
  - Single source of truth: every consuming layer (client gating, other services)
    must derive authorization from the SAME server signal. Flag client-side
    recomputation of permissions that can diverge from the server guard.
  - Overloaded capability flag: one boolean gating multiple actions whose server
    rules differ (e.g., edit vs delete) — recommend per-action flags mapped 1:1 to
    each backend guard.
  - Unreferenced destructive control: a component/branch rendering a destructive
    action but never imported/reached — footgun (auth bypass if later wired);
    recommend removal or correct gating.

**Secrets & privacy**
- Hardcoded secrets, credentials/tokens/connection strings in code or logs.
- Sensitive data exposure in logs, error messages, API responses (PII, tokens).
- Personal data handled without masking/retention consideration where the project
  has such conventions.

**Dependencies**
- New/updated dependency: known-risky package, overly broad permissions/scripts,
  unpinned versions where the project pins.

## Severity discipline

All SEC findings go to the Judge regardless of severity (see adjudication.md).
Rate severity by exploitability × impact — not by how scary the category sounds.

## Not yours

Performance of security code → performance-resources. Log level/noise (non-sensitive)
→ operations-config.
