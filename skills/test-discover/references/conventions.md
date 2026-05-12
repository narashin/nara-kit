# Test Scenario Conventions & Output Format

## Mandatory Fields Per Scenario

- `#### [{ID}] {behavior-based title}` -- title reads like a spec
- `**진입경로**:` -- exact entry path (URL, menu, API endpoint, or `Module.method (file:line)`)
- `**실행역할**:` -- Create | Read | Update | Delete | N/A
- `**실행독립**:` -- 가능 | 불가 (serial: {preceding ID})
- `**선행 생성**:` -- only when dependent on another scenario's output
- `**데이터 힌트**:` -- data token format `{PREFIX}-{YYYYMMDD-HHmm}`

## Step Conventions

- Steps numbered from 0
- Action steps: plain text
- Verification steps: prefixed with `-> 확인:` (Korean) or `-> Verify:` (English)
- Wait times explicit for E2E: `0.5초 대기`, `1초 대기`, `3초 대기`
- Pre-action state checked before action, post-action state checked after

## Structural Conventions

- Group scenarios by CRUD operation (use "N/A" group for non-CRUD like validation, init, logging)
- Serial dependencies declared with `serial:` in 실행독립 field
- Independent scenarios can run in any order
- ID format: `[{SCOPE}-{FEATURE}-{NNN}]` (e.g., `[E2E-PEM-001]`, `[API-ORD-001]`)

## Output File

Write to: `docs/test-scenarios/scenarios-detailed.md`

Create directory if it does not exist. If scenario files exist elsewhere, treat as prior art for gap analysis but do NOT merge/overwrite. Always write to canonical path.

## Template

```markdown
# {Project} {Feature} 테스트 시나리오

- Project: {name}
- Feature: {feature}
- Version: V1
- Scenario Coverage Ratio: {S3/S2} (S3 {n} / S2 {m})

## 공통 사전조건

- 실행 URL: {url or [UNVERIFIED]}
- 계정: {account or [UNVERIFIED]}
- 기본 실행 persona: {role}
- 실패 조건: {global failure conditions}

## 시나리오 의존 체인

### Serial 블록
- [{ID}] title -> [{ID}] title -> ...

### 독립 실행 가능
- [{ID}], [{ID}], ...

## 시나리오 제목 인덱스

- [{ID}] title
...

## 시나리오

### Create

#### [{ID}] {behavior-based title}

**진입경로**: ...
**실행역할**: Create
**실행독립**: 가능
**데이터 힌트**: `{PREFIX}-{YYYYMMDD-HHmm}`

0. ...
1. ...
2. -> 확인: ...

### Read
...
### Update
...
### Delete
...
```

## Language Support

- Default: Korean
- `lang=en`: switch all labels to English (`-> Verify:`, `Entry path`, `Execution role`, `Independent execution`, `Preceding creation`, `Data hint`, `Common Preconditions`)
- Code identifiers, URLs, technical terms remain in original form
