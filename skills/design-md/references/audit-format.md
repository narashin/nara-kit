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
| Ambiguous | DESIGN.md value cannot be verified from source (incomplete Figma data, runtime-only value, non-hex) → tag `[UNVERIFIED]`, exclude from Score denominator |

## Report Template

```markdown
## Design Drift Report — {project name}

**Score**: {matched}/{total} ({percentage}%) — `Ambiguous` 항목은 분모(total)에서 제외

### Undocumented (in code, not in DESIGN.md)
- {file:line} — `{value}` not mapped to any DESIGN.md token

### Unused (in DESIGN.md, not in code)
- `{token}` ({hex}) — defined but not referenced

### Deviated (defined differently)
- {file:line} — expected `{DESIGN.md value}`, found `{actual value}`

### Ambiguous / Cannot Verify ([UNVERIFIED])
- {token | file:line} — cannot verify from source ({reason: incomplete Figma data | runtime-only | non-hex}); excluded from Score denominator

### Don't Violations
- {file:line} — violates: "{Don't rule text}"
```

> `Ambiguous` bucket 규칙: DESIGN.md 값을 소스에서 검증 불가한 항목(불완전 Figma 데이터, 런타임에서만 확인 가능한 값 등)은 `Undocumented`로 밀어넣지 말고 여기로 분리. matched/total 분모를 왜곡하지 않도록 Score 산출에서 제외한다.
