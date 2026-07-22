# Attack Protocol

3개 lane을 Agent tool로 동시 실행. 각 lane은 read-only. 결과는 main 세션이
수합해 verdict를 확정한다 — lane의 자기보고를 그대로 믿지 않고, 인용된
코드 위치를 스팟체크한 뒤 append한다.

## Lane 1: refuter

입력: confirmed finding 목록(원 confidence는 전달하되 anchoring 주의 명시) + 코드.

finding마다:
1. failure_path를 실제 코드에서 한 단계씩 재추적 — 끊기는 지점이 있으면 격추.
2. counterevidence 수색: 기존 guard, validation layer, caller의 방어, 테스트.
   원 리뷰의 `counterevidence_checked`에 없는 곳을 우선 수색.
3. preconditions가 실제로 도달 가능한지 검증 (dead branch, 불가능한 상태 조합).

판정: `upheld`(반박 실패, 근거 유지) / `refuted`(failure_path 불성립 — 근거 인용
필수) / `weakened`(성립하나 severity/evidence가 과대 — 조정안 제시).
기본값 없음 — 판단 불가면 `upheld (refutation inconclusive)`로 명시.

## Lane 2: blind hunter

입력: 리뷰 스코프의 diff + 파일 컨텍스트. **원 리포트는 절대 전달하지 않는다.**

- 일반 리뷰 수행 (behavior/contracts/resilience/tests 관점 자유).
- 반환된 finding을 main 세션이 리포트와 fingerprint 대조:
  - 리포트에 없음 → `missed-found` 후보 (스팟체크 후 채택)
  - 리포트의 rejected/open-question과 일치 → 원 처리의 재평가 재료
- lane 프롬프트에 리포트 내용이 한 줄이라도 들어가면 결과 전체 무효 — 재실행.

## Lane 3: rigor auditor

입력: 리포트 전문 + git 접근.

- evidence level 라벨 vs 실제 적힌 근거의 정합 (E2 주장인데 결정적 경로 없음 등)
- `verified` 주장 vs proof: 리포트가 가리키는 hunk가 실제 diff에 존재하는가,
  validation 결과가 인용돼 있는가
- E0/E1·needs-context가 finding 목록에 섞여 있지 않은가
- trailing status 존재 + 본문과 모순 없음 (예: mismatch인데 applied 보고)
- suppressed-by-project-exception의 exception이 실제 override에 존재·미만료인가

산출: 위반 목록 (위치 + 무엇이 왜 위반인지). 스타일 지적 금지 — 무결성만.
