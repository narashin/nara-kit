# Attack Protocol

3개 lane을 병렬 subagent로 동시 실행. 각 lane은 read-only. 결과는 main 세션이
수합해 verdict를 확정한다 — lane의 자기보고를 그대로 믿지 않고, 인용된
코드 위치를 스팟체크한 뒤 append한다.

스코프 복원: manifest가 없으면 리포트 본문의 파일 목록으로, 그것도 없으면
finding들의 location으로 파일 목록을 복원 — 복원 방식과 한계(스코프 밖 파일
누락 가능)를 append 섹션에 기록한다.

## Lane 1: refuter

입력: confirmed + unadjudicated finding 전부(원 confidence는 전달하되 anchoring
주의 명시) + 코드. unadjudicated의 verdict는 원 리포트 승격이 아니라 검증 참고.

finding마다:
1. failure_path를 실제 코드에서 한 단계씩 재추적 — 끊기는 지점이 있으면 격추.
2. counterevidence 수색: 기존 guard, validation layer, caller의 방어, 테스트.
   원 리뷰의 `counterevidence_checked`에 없는 곳을 우선 수색.
3. preconditions가 실제로 도달 가능한지 검증 (dead branch, 불가능한 상태 조합).

Non-runtime finding(중복 util·rename leftover·dead code 등 관측 사실 기반 —
nara-code-review의 observability 루브릭): failure_path 재추적 대신 주장된 사실
자체를 repo에서 재검증(grep/read). 사실이 성립하면 upheld.

판정: `upheld`(반박 실패, 근거 유지) / `refuted`(failure_path 불성립 — 근거 인용
필수) / `weakened`(성립하나 severity/evidence가 과대 — 조정안 제시).
기본값 없음 — 판단 불가면 `upheld (refutation inconclusive)`로 명시.
경계 규칙: failure_path는 불성립하나 같은 지점에 실제 결함이 존재하면
`refuted` + missed-found로 재정식화(두 항목을 상호 링크). `weakened`는
path가 성립하는 경우에만. 재정식화 항목에도 missed-found 채택 게이트를 동일
적용 — 미달이면 노트로 강등. trailing status의 `N missed-found`는 게이트
통과 채택분만 센다(노트 제외).

## Lane 2: blind hunter

입력: 리뷰 스코프의 diff + 파일 컨텍스트. **원 리포트는 절대 전달하지 않는다.**

- 일반 리뷰 수행 (behavior/contracts/resilience/tests 관점 자유).
  diff를 복원할 수 없으면 스코프 파일 전체를 대상으로 하고 그 한계를 기록.
- 반환된 finding을 main 세션이 리포트와 fingerprint 대조:
  - 리포트에 없음 → `missed-found` 후보 (스팟체크 후 채택). 채택에도 원 리포트의
    게이트(evidence ≥ E2 AND confidence ≥ threshold)를 적용 — 미달은 노트로만.
  - 리포트의 rejected/open-question과 일치 → 원 처리의 재평가 재료
    (해당 섹션이 리포트에 없으면 이 대조는 생략을 명시).
- lane 프롬프트에 리포트 내용이 한 줄이라도 들어가면 결과 전체 무효 — 재실행.

## Lane 3: rigor auditor

입력: 리포트 전문 + git 접근.

- evidence level 라벨 vs 실제 적힌 근거의 정합 (E2 주장인데 결정적 경로 없음 등).
  단 non-runtime finding(suggestion·구조·중복)은 observability 루브릭(E3=repo
  검증된 사실, E2=diff에서 도출) 기준 — 실행경로 부재 자체는 위반이 아님.
- `verified` 주장 vs proof: 리포트가 가리키는 hunk가 실제 diff에 존재하는가,
  validation 결과가 인용돼 있는가
- E0/E1·needs-context가 finding 목록에 섞여 있지 않은가
- trailing status 존재 + 본문과 모순 없음 (예: mismatch인데 applied 보고).
  정상 값 인지: fix 0건 런의 `fix-ledger: match`+`0 verified, 0 unverified,
  0 mismatched`, empty-scope/--fix=none의 `n/a`, `manual-only` 수렴 라벨은
  위반이 아니라 규정된 값이다 (code-review report/verification 참조).
- suppressed-by-project-exception의 exception이 실제 override에 존재·미만료인가

산출: 위반 목록 (위치 + 무엇이 왜 위반인지). 스타일 지적 금지 — 무결성만.
