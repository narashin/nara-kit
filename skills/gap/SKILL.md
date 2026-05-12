---
name: gap
description: >-
  Analyze gap between docs/requirements.md and codebase, producing docs/gap.md with a score (0-100).
  USE FOR: "gap", "gap 분석", "구현 얼마나 됐어", "요구사항 대비 진행률", "--verify".
  DO NOT USE FOR: writing requirements (use /prep), code implementation, code review.
---

# gap — 요구사항 vs 구현 갭 분석

`docs/requirements.md`와 현재 코드베이스를 비교하여 갭을 분석한다.

## 모드 (`$ARGUMENTS`)

- (없음) → 전체 갭 분석 + gap.md 생성
- `--verify` → 기존 gap.md 기준 재검증 (경량)
- `--score` → gap.md에서 점수만 산출
- `--doc` → requirements.md 자체 완성도 체크

## 생성 모드

전제: `docs/requirements.md` 존재 필수. 없으면 "/prep 먼저 실행" 안내 후 중단.

1. requirements.md 읽기
2. 각 요구사항별 코드베이스 구현 상태 확인 (Grep/Glob, 핵심 로직만)
3. Agreed Exceptions 반영 (갭에서 제외)
4. `[UNVERIFIED]` 항목 → Agreed Exceptions로 분류
5. gap.md 생성. Follow template in [references/gap-template.md](references/gap-template.md).

### 점수 산출
```
Score = (Implemented + Partial*0.5) / (Total - Agreed Exceptions) * 100
```

## 검증 모드 (`--verify`)

기존 gap.md의 Missing/Partial 항목만 추출 → 코드 확인 → gap.md 업데이트 + 점수 재산출.

## 규칙

- Agreed Exceptions 항목은 갭으로 보고하지 않음
- 구현 여부 확인 불가 시 `Unknown (코드 접근 불가)` 표기
- 점수 80 미만: "구현 계속 필요" 명시. 80 이상: "리뷰 단계 진입 가능" 명시
- Evidence는 `파일경로:라인번호` 형식. 코드 내용 인라인 출력 금지
