# test-implement — Pre-execution Gate

골든 샘플 읽은 직후, 첫 테스트 코드 작성 전 plan 출력 + 승인.

## 절차

1. Implementation Plan 출력:
   - 도메인 순서 표 (High → Medium → Low, dependency-first 반영)
   - 각 도메인별 예상 테스트 파일 경로
   - 사용할 mock/fixture/assertion 패턴 (golden sample 인용)
   - 예상 신규 파일 수 vs 기존 파일 수정 수
2. AskUserQuestion: "이 순서/패턴대로 진행할까요?"
3. 승인 후에만 코드 작성 진행.

## Skip 조건

- 사용자가 `--auto` / "go" / "approved" 명시
- 시나리오 1개 도메인 + 신규 파일 1개 → 1줄 요약 후 진행 가능
