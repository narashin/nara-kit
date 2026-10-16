# gh outputs for the template-repo fixture (GitHub not reachable in this run)

Repo: `acme-sre/order-service` on github.com. The branch is pushed.

## gh pr list --head feature/PROJ-77-export-csv --json number

```json
[]
```

## gh pr list --state merged --limit 5 --json number,title

```json
[
  {"number":71,"title":"fix(auth): refresh the session token once on 401 (PROJ-41)"},
  {"number":69,"title":"feat(report): add monthly totals to order report (PROJ-63)"},
  {"number":66,"title":"chore(ci): pin python to 3.12 (PROJ-60)"},
  {"number":64,"title":"docs(readme): document local setup (PROJ-58)"},
  {"number":62,"title":"refactor(report): extract row builder (PROJ-55)"}
]
```
