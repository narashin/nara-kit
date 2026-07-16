---
name: nara-incident
description: >-
  Generate a structured incident analysis report with root cause hypotheses, evidence, and proposed fix.
  USE FOR: "incident", "/nara-incident TICKET", "장애 분석", "버그 원인 찾아", "root cause".
  DO NOT USE FOR: code modification (use /nara-incident-fix), general debugging, code review.
---

# incident — 장애 분석 리포트 생성

장애 보고를 받아 구조화된 분석 리포트를 생성한다. **코드 수정 금지. 리포트만 산출.**

## 입력

`$ARGUMENTS`에서 장애 소스 파싱:
- Jira URL/티켓 ID → `mcp__jira__jira_get_issue`
- Slack 메시지 URL → Slack MCP
- 텍스트 → 그대로 구조화

## 실행

5단계 교차 검증으로 분석. Load [references/incident-procedure.md](references/incident-procedure.md) for full procedure.

핵심 단계: 현상 파악 → 가설 3개+ 수립 → 증거 대조 → 수정 방향 + 사이드이펙트 → 반대 심문(자기 반박, 건너뛰기 금지).

## 산출물

`docs/incident-report.md` 생성. Follow template in [references/incident-procedure.md](references/incident-procedure.md).

## Feedback loop gate (재현 우선)

가설을 "유력"으로 올리기 전에 **재현 가능한 red-capable feedback loop**를 먼저 만든다. failing test, curl/HTTP 스크립트, CLI fixture, trace replay, 반복 재현 loop 등 무엇이든 (1) 실제 증상을 잡고 (2) 에이전트가 다시 실행할 수 있고 (3) 최소 한 번 실제 실행하며 (4) red/green 판정이 가능해야 한다. **재현 없이 가설을 원인으로 확정하거나 "유력"으로 표시하지 않는다.**

재현할 수 없으면 시도한 방법, 부족한 환경·artifact, 필요한 로그/HAR/fixture/trace/권한을 보고하고, 추측 patch나 가설을 확정 사실처럼 표현하지 않는다.

## 규칙

- 코드 수정 절대 금지 (분석·리포트만)
- 확인 불가한 것은 `[미확인: <이유>]` 표기
- 가설 "유력" 표시 하나만 — 재현 증거로 뒷받침될 때만
- Evidence는 `파일:라인` 형식
- 재현에 필요한 입력·환경·권한이 없으면 `Blocked`, 실행했으나 재현 증거를 못 얻으면 `Unverifiable`로 리포트 상태를 명시한다. 이 상태를 분석 완료로 보고하지 않는다.
