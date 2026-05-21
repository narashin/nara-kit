# handoff.md 8섹션 스키마

> `/reflect` 실행 시 In Progress/Open Questions 있으면 `docs/handoff.md`에 이 스키마로 작성. 다음 세션 `/now`가 우선 참조하는 단기 인계 계약.

## 스키마

```markdown
# Handoff — <세션 요약 1줄>

## 1. 현재 목표
<다음 세션이 이어갈 목표 1~3줄>

## 2. 작성 시점 context
- branch: `<name>`
- HEAD: `<sha>`
- working tree: <clean | dirty (N files)>
- timestamp: <ISO 8601>

## 3. 산출물 상태
- requirements: `docs/requirements.md` <존재/없음>
- gap: `docs/gap.md` (score: <n>) <존재/없음>
- 기타: <필요 시>

## 4. 진행 중 작업 (In Progress)
- <작업 1>: 어디까지 했고 다음에 X 하려던 참
- <작업 2>: ...

## 5. 열린 질문 (Open Questions)
- Q1: <답 없이 남은 질문>
- Q2: ...

## 6. 다음 안전 조치
- <검증 필요 항목 1>
- <검증 필요 항목 2>

## 7. 하지 말 것
- <명시적 안티패턴 / 함정>

## 8. 먼저 읽을 핵심 파일
- `<path1>` — <이유>
- `<path2>` — <이유>
```

## 작성 규칙

- **현재 목표**: 이번 세션이 아니라 *다음 세션이 이어갈* 목표
- **context**: stale check 가능하도록 baseline SHA 필수
- **In Progress**: 코드/커밋만 봐서 복원 불가능한 사고 흐름만. "X 함수 시그니처 A vs B 고민 중, A로 가다가 호환성 문제 발견" 같은 흐름
- **Open Questions**: 이미 결정된 건 Decisions로 격상, 답 없는 것만
- **다음 안전 조치**: handoff-read 시 가장 먼저 검증할 항목
- **하지 말 것**: "X 함수 건드리지 마라 — 다른 모듈 의존" 같은 함정 명시
- **먼저 읽을 파일**: 다음 세션 `/now`가 우선 fetch할 파일 (1~5개)

## 삭제 시점

handoff.md는 단기 계약. 다음 세션에서 In Progress/Open Questions 해소되면 `/reflect`가 파일 삭제. 영속 정보는 Decisions/Conventions/Warnings로 격상하여 memory 저장.
