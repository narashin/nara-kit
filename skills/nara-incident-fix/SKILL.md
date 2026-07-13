---
name: nara-incident-fix
description: >-
  Implement a TDD fix (Red-Green-Refactor) based on docs/incident-report.md analysis.
  USE FOR: "incident-fix", "장애 수정", "버그 고쳐", "fix the incident", "incident 수정 구현".
  DO NOT USE FOR: incident analysis (use /nara-incident), general bug investigation, code review.
---

# incident-fix — 장애 리포트 기반 수정 구현

`docs/incident-report.md`를 SoT로 삼아 TDD 방식으로 수정을 구현한다.

## 전제조건

`docs/incident-report.md` 존재 필수. 없으면 `/nara-incident` 먼저 실행 안내 후 중단.

## Pre-execution gate (필수)

incident-report.md 읽은 직후, **Phase 1 시작 전**:

1. **Fix Plan 요약 출력**:
   - Proposed Fix 핵심 (1-2줄)
   - 영향 파일 목록 (Proposed Fix + Similar Patterns)
   - 작성 예정 실패 테스트 시나리오 한 줄 요약
   - Side Effects 검증 대상 경로
2. **AskUserQuestion**: "이 방향으로 Red-Green-Refactor 진행할까요?"
3. 승인 전 테스트 작성/코드 수정 **금지**

**Skip 조건**:
- 사용자가 `--auto` / "go" / "approved" 명시
- Proposed Fix가 단일 파일 + 단일 라인 변경 + Similar Patterns 비어있음 → 1줄 요약 후 진행 가능

## 실행 (3-Phase TDD)

### Phase 1: RED — 실패 테스트 작성
- incident-report.md의 Proposed Fix + Test Gap 섹션 읽기
- 현재 실패하는 테스트 작성 (재현 조건 기반)
- 테스트 실행 → 실패 확인

### Phase 2: GREEN — 최소 수정 구현
- Proposed Fix 섹션 기준으로 최소한의 코드 수정
- 테스트 통과 확인
- Similar Patterns 섹션 항목도 동시 수정

### Phase 3: Side Effects 검증
- incident-report.md의 Side Effects 섹션 확인
- 영향 경로별 기존 테스트 실행
- 신규 회귀 없음 확인

## Examples

```bash
# Phase 1: 실패 테스트 실행
npx jest --testPathPattern="order-cancel" --no-coverage

# Phase 2: 수정 후 통과 확인
npx jest --testPathPattern="order-cancel" --no-coverage

# Phase 3: 전체 회귀 검증
npx jest --no-coverage
```

## Error Handling

- report 없음 → `/nara-incident` 안내 후 중단
- Phase 1 테스트 이미 통과 → 재현 조건 재검토
- Phase 2 기존 테스트 깨짐 → Proposed Fix 범위 재확인
- Phase 3 회귀 → Side Effects 기반 원인 분석 후 보고

## 규칙

- incident-report.md 수정 금지 — 읽기 전용 SoT. 분석이 틀렸으면 `/nara-incident` 재실행.
- 범위 밖 수정 금지. Proposed Fix + Similar Patterns 범위만.
- Phase별 완료 후 검증 통과 확인 필수.
