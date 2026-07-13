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

## 규칙

- 코드 수정 절대 금지
- 확인 불가한 것은 `[미확인: <이유>]` 표기
- 가설 "유력" 표시 하나만
- Evidence는 `파일:라인` 형식
