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
- `--task TASK-ID` → 해당 backlog 태스크 AC 기준 scoped 갭 분석 (gap.md 미생성, transient)

## 생성 모드

전제: `docs/requirements.md` 존재 필수. 없으면 "/prep 먼저 실행" 안내 후 중단.

판정 룰은 [references/gap-rubric.md](references/gap-rubric.md) 기계 적용. LLM 자의 판단 금지.

1. requirements.md 읽기
2. **Verbatim pre-scan** (자동):
   - requirements.md에서 따옴표/백틱/코드블록 안 모든 텍스트 추출
   - 각 텍스트에 대해 `git grep -F` 실행 → 0건이면 rubric §1에 따라 **Missing 강제**
   - LLM 판단 거치지 않음
3. 각 요구사항별 코드베이스 구현 상태 확인 (Grep/Glob, 핵심 로직만)
4. rubric §3 Evidence 강제 룰 적용 → Implemented 주장 중 매핑 불가 항목 Partial 강등
5. Agreed Exceptions 반영 (갭에서 제외)
6. `[UNVERIFIED]` 항목 → Agreed Exceptions로 분류
7. rubric §4 Forced Doubt Sampling → Implemented 중 20% (최소 2개) `Needs Confirm` 표시
8. gap.md 생성. Follow template in [references/gap-template.md](references/gap-template.md).

### 점수 산출
```
Score = (Implemented + Partial*0.5) / (Total - Agreed Exceptions) * 100
```

## 검증 모드 (`--verify`)

기존 gap.md의 Missing/Partial 항목만 추출 → 코드 확인 → gap.md 업데이트 + 점수 재산출.
Verbatim pre-scan + Evidence 강등 + Doubt sampling 모두 동일 적용.

## 규칙

- Agreed Exceptions 항목은 갭으로 보고하지 않음
- 구현 여부 확인 불가 시 `Unknown (코드 접근 불가)` 표기
- 점수 80 미만: "구현 계속 필요" 명시. 80 이상: "리뷰 단계 진입 가능" 명시
- Evidence는 `파일경로:라인번호` 형식. 코드 내용 인라인 출력 금지
- 모든 판정은 [references/gap-rubric.md](references/gap-rubric.md) 기준 따름. "비슷하다" 식 자의 판단 금지
- Verbatim 항목(따옴표/백틱/코드블록 안 텍스트)은 의미 무관 exact match. grep 0건이면 Missing 강제
- Implemented 판정에 evidence 없으면 자동 Partial 강등

## 태스크 모드 (`--task TASK-ID`)

backlog 태스크 단위 scoped gap. `/backlog decompose` 내부에서 호출됨.

1. `backlog task list`에서 TASK-ID의 title, description, AC 읽기
2. task description 키워드로 관련 디렉토리/파일 scope 도출
3. scope 내에서만 Grep/Glob (최대 10파일, symbol-level 선호)
4. AC 항목 내 따옴표/백틱 텍스트 Verbatim pre-scan 적용 (scope 내 grep)
5. 각 AC 항목별 구현 상태 확인 + rubric §3 Evidence 강등 적용
6. 결과를 transient로 반환 (gap.md 미생성)
7. 점수 산출 공식 동일
