# Plan Approval (folded into the plan step)

Plan 단계의 일부. 별도 phase 아님. Written 임플리먼테이션 플랜 작성 직후, 첫 코드 변경 스킬(`subagent-driven-development`) 호출 전에 plan 승인을 받는다.

## 절차

1. **Plan 요약 출력**:
   - 대상 파일/도메인 (최대 10항목)
   - 변경 종류 (신규/수정/삭제)
   - TDD 적용 여부
   - 예상 검증 명령 (test/typecheck)
2. **AskUserQuestion**: "이 plan대로 진행할까요? (수정사항 있으면 알려주세요)"
3. 사용자 명시적 승인 후 execute 스킬 호출.

## Skip 조건 (gate 우회 허용)

- 사용자가 동일 세션에서 같은 plan 명시 승인 + plan 미변경
- 사용자가 "go" / "approved" / "그냥 가" / `--auto` 명시 → 다음 plan 변경 전까지만 skip
- scope = `small` (1-2 files, 단일 관심사) + 가역적(파일 신규 생성/주석 추가만) → 1줄 요약 + 진행 (출력은 의무)

비가역 작업(파일 삭제, 대량 수정, 외부 시스템 호출)은 scope 무관 gate 필수.

## Frontend — Component Pick gate

frontend 컴포넌트 신규 작성/수정 감지 시, 카탈로그 우회 직접 작성 차단.

5단계 절차 ([상세](component-pick-procedure.md)):

1. 카탈로그(`DESIGN.md` / `component-catalog.md` / 디자인 시스템 docs) 직접 매칭
2. Optional props로 해결 가능 여부
3. 코드베이스 grep (카탈로그 누락 가능성)
4. 발견 시 카탈로그 업데이트 후 사용
5. 모두 실패 시 STOP & AskUserQuestion 승인 후 신규 작성

Step 5는 `--auto`로 skip 불가 (신규 컴포넌트는 영구 영향).
