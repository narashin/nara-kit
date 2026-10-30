# gh outputs for the stack-repo fixture (GitHub not reachable in this run)

Repo: `acme-sre/web-ui` on the GitHub Enterprise Server host `git.example.com`. The branch is pushed. The repository has no PR template, no CONTRIBUTING.md, and no PR rules in AGENTS.md or CLAUDE.md.

## gh pr list --head <current branch> --json number

```json
[]
```

## gh pr list --state merged --limit 10 --json title

```json
[
  {"title":"PROJ-84 feat: Add coupon percent validation"},
  {"title":"PROJ-81 fix: Keep cart total after login"},
  {"title":"PROJ-79 refactor: Split report helpers"}
]
```

## gh extension list

(no output: no extensions installed)

## gh api --hostname git.example.com repos/acme-sre/web-ui/stacks?per_page=1

```text
HTTP/2.0 404 Not Found
{"message":"Not Found","documentation_url":"https://docs.github.com/enterprise-server@3.19/rest","status":"404"}
```

## gh api --hostname git.example.com repos/acme-sre/web-ui/pulls?per_page=1

```text
HTTP/2.0 200 OK
```
