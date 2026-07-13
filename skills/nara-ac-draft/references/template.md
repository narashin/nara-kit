# 출력 템플릿

산출물: `docs/requirements.md`. 형식은 `prep` 산출물과 동일 구조 — downstream `gap` / `test-discover`가 동일하게 소비.

## Frontmatter

```yaml
---
sources: [internal-draft]
generated_by: nara-ac-draft
intent: "<verbatim 한 줄 의도>"
fetched_at: <ISO date>
confirmed_at: <ISO date when user confirms — initial run에는 omit>
---
```

`sources: [internal-draft]`로 외부 SoT 부재를 downstream에 명시.

## 본문 구조

```markdown
# Requirements: <feature name>

## Source
- Intent (verbatim): "<한 줄 의도>"
- Domain hints: <scanned terms or [NOT FOUND]>
- Related modules: <auto-scan 결과 or [NOT FOUND]>

## User Stories
- **US-1**: As <actor>, I want <capability>, so that <benefit>.
- **US-2**: ...

## Functional Requirements
- **FR-1**: <US verbatim 재기술. 의역/재구성 금지>
- **FR-2**: ...

## Acceptance Criteria

### AC-1 (US-1, Happy)
Given <precondition>
When <action>
Then <observable outcome>

### AC-2 (US-1, Edge)
Given ...
When ...
Then ...

### AC-3 (US-2, Sad)
Given ...
When ...
Then ...

## Open Questions
- [blocking] <진행 전 사용자 확정 필요한 항목>

## Unknown / Needs Confirmation
- [ ] <axis>: <choices or open question>
- [ ] <UNVERIFIED 마크 항목 요약>

## Agreed Exceptions
(없음)

## Out of Scope
- <inferred-but-deferred items>
```

## 섹션별 규약

| 섹션 | 필수 | 비울 수 있음 | 비고 |
|------|------|------|------|
| Source | ✅ | ❌ | Intent verbatim |
| User Stories | ✅ | ❌ (≥1) | "so that" 절 의무 |
| Functional Requirements | ✅ | ❌ (US와 1:1) | prep 규약 — 의역 금지 |
| Acceptance Criteria | ✅ | ❌ (≥1) | Gherkin 단일 형식 |
| Open Questions | ✅ | ✅ (헤더만 + "없음") | blocking만 |
| Unknown / Needs Confirmation | ✅ | ❌ | never empty — intents zero-ambiguity 아님 |
| Agreed Exceptions | ✅ | ✅ (헤더만 + "없음") | gap false-positive 방지 |
| Out of Scope | ✅ | ✅ (헤더만 + "없음") | scope creep 차단 |

## AC-ID 명명

- 형식: `AC-<순번>` (예: `AC-1`, `AC-2`, `AC-15`)
- 1부터 순차, gap 허용 (삭제된 ID는 `[DEPRECATED]`)
- Story와 Category는 괄호 안 메타: `### AC-3 (US-2, Edge)`
- ID 재실행 안정성: 같은 intent 재호출 시 기존 ID 유지

## Gherkin 작성 규약

- Given: precondition (상태/시간/사용자 속성)
- When: actor 액션 (1개 동사)
- Then: observable outcome (검증 가능한 결과)
- And/But 허용 — but 한 AC에 3줄 초과 금지 (복잡하면 AC 분리)
- Scenario Outline / Examples 표 v0에서는 미사용 — 단일 시나리오만
