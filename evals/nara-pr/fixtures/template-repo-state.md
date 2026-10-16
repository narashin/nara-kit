# Repository state for the template-repo fixture (built by template-repo.sh)

Current branch: `feature/PROJ-77-export-csv`, upstream base `origin/main`.

## .github/pull_request_template.md (on main)

```markdown
<!-- Keep every heading. Delete nothing. Reviewers grep for these. -->
## What
<!-- One paragraph: what changes for the user. -->

## Why

## Test plan
<!-- How a reviewer can verify this without reading the code. -->

## Checklist
- [ ] Tests added or updated
- [ ] Docs updated (or not needed)
- [ ] No secrets in the diff
```

## CONTRIBUTING.md (on main)

```markdown
# Contributing

## Pull requests

PR titles follow Conventional Commits with the ticket at the end:

    type(scope): imperative subject (PROJ-123)

Example: `fix(auth): refresh the session token once on 401 (PROJ-41)`.
Use the PR template in `.github/`; do not remove its headings.
```

## git log origin/main..HEAD --oneline

```
4a927c8 PROJ-77 test: cover CSV header
fd70d56 PROJ-77 feat: add CSV export for order report
```

## git diff origin/main...HEAD

```diff
diff --git a/src/report.py b/src/report.py
index 5872f8a..0bd875f 100644
--- a/src/report.py
+++ b/src/report.py
@@ -1,2 +1,8 @@
 def rows(orders):
     return [(o.id, o.total) for o in orders]
+
+
+def to_csv(orders):
+    lines = ["id,total"]
+    lines += [f"{i},{t}" for i, t in rows(orders)]
+    return "\n".join(lines)
diff --git a/tests/test_report.py b/tests/test_report.py
new file mode 100644
index 0000000..8a7f38f
--- /dev/null
+++ b/tests/test_report.py
@@ -0,0 +1,4 @@
+from src.report import to_csv
+
+def test_to_csv_header():
+    assert to_csv([]).splitlines()[0] == "id,total"
```
