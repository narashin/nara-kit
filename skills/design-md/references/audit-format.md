# Audit Output Format

## Collection

1. Parse DESIGN.md YAML frontmatter → defined tokens (colors, typography, spacing, rounded, components)
2. Parse Do's/Don'ts → design rules
3. Scan project code:
   - Tailwind class usage → color/spacing/radius tokens
   - Hardcoded hex/px values
   - Component style patterns

## Drift Categories

| Category | Check |
|----------|-------|
| Colors | Hardcoded hex in code that should use a DESIGN.md token |
| Colors | DESIGN.md token defined but unused in code |
| Typography | Font weight/size usage not matching DESIGN.md hierarchy |
| Components | Component style deviating from DESIGN.md spec |
| Spacing | Values outside defined spacing scale |
| Do's/Don'ts | Don't rules violated in code |

## Report Template

```markdown
## Design Drift Report — {project name}

**Score**: {matched}/{total} ({percentage}%)

### Undocumented (in code, not in DESIGN.md)
- {file:line} — `{value}` not mapped to any DESIGN.md token

### Unused (in DESIGN.md, not in code)
- `{token}` ({hex}) — defined but not referenced

### Deviated (defined differently)
- {file:line} — expected `{DESIGN.md value}`, found `{actual value}`

### Don't Violations
- {file:line} — violates: "{Don't rule text}"
```
