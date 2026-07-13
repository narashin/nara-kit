# templates — Bug / Feature 영어 본문

`jira_create_issue` 호출 시 `is_description_markdown=true` (그래야 `##` 헤더가 렌더링됨).

## 창작 금지 규율 (prep/incident 차용)

- 스레드에 없는 값(repro steps·environment·impact)은 **창작 금지** → `_not specified_` / `_TBD_` 표기
- Slack permalink + reporter handle + **원문 verbatim 인용**(한국어 보존)은 항상 포함 → 추적성. 번역 gist는 영어, 원문은 손실 없이 복원 가능
- Feature AC 추론 시 항상 `[proposed — needs confirmation]` 라벨 — 추측임을 명시

## Bug

```markdown
## Summary
<one-line, EN>

## Environment
- App / Version: <x | _not specified_>
- Platform: <x | _not specified_>

## Steps to Reproduce
1. ...
   (or: _Not provided in thread — follow-up needed_)

## Expected
<EN>

## Actual
<EN>

## Impact
<who / how many affected, blocking? | _not specified_>

## Source
- Slack: <permalink>
- Reporter: @handle (date)
- Original (verbatim): "원문 한국어 그대로"
```

## Feature

```markdown
## Summary
<one-line, EN>

## Background / Problem
<왜 필요 — user pain>

## Requested Change
<무엇을 요청>

## Acceptance Criteria
<conditional — 아래 규칙>

## Scope
- In: ...
- Out: ...

## Source
- Slack: <permalink>
- Reporter: @handle (date)
- Original (verbatim): "원문 그대로"

## Related
- relates to ABC-123   (관련 티켓 있을 때만)
```

### Acceptance Criteria — 조건부 draft

- 스레드에 근거 충분 → Given-When-Then 초안 생성, `[proposed — needs confirmation]` 라벨
- 근거 부족 → `_TBD — needs PO_`. 절대 창작하지 않음

priority는 Jira 기본값 유지 — 스킬이 건드리지 않음.
