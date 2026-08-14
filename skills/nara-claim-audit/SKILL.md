---
name: nara-claim-audit
description: >-
  Run a deterministic script that compares numeric claims in a local spec markdown against CSV snapshots, then classify each claim.
  USE FOR: "수치 맞나 확인해줘", "기획서 숫자 검증", "데이터랑 문서 대조", "claim audit", "게시 전 수치 점검".
  DO NOT USE FOR: 요구사항 vs 코드 갭 (→ nara-gap), 브라우저 AC 판정 (→ nara-browser-verify), Confluence 게시 (→ nara-publish-spec).
---

# claim-audit — 기획문서 수치 감사

로컬 기획 md의 **수치 주장**을 CSV 스냅샷과 대조한다. 사람이 셀 수 없는 양(문서 20개 규모)을 전제로 하므로 **측정은 스크립트가 소유**하고 LLM은 오케스트레이션만 한다.

문제는 "몰라서 비워둔 수치"가 아니라 **자신 있게 틀린 수치**다. `[UNVERIFIED]`는 쓰는 사람이 자각할 때만 붙으므로 이 실패를 못 잡는다.

## Core Rules

1. **측정은 `assets/audit.py`가 한다** — LLM이 마커를 해석하지 않는다. 같은 입력 → 같은 출력이어야 자동 교체가 안전해진다.
2. **추측 금지** — 문법 밖은 `syntax_error`, 없는 컬럼·파일·필터 결과 0행은 `mapping_failure`, 마커 앞 숫자가 둘 이상이면 `ambiguous`. **0으로도, 근처 숫자로도 대체하지 않는다.**
3. **마커 없는 수치는 건드리지 않는다** — 날짜·목차 번호·순번, 코드블록 안 예시 전부 제외.
4. **CSV 기준 한정** — 결론은 "이 CSV 스냅샷 기준"이며 mtime을 함께 보고한다. 라이브 DB·게시본과의 동기화는 검증하지 않는다.
5. **로컬 md만** — Confluence write 없음. 게시는 `nara-publish-spec`, 개정 이력은 `nara-spec-revision` 소유.
6. **교체는 건별 승인 없이** — 수백 건 전제. 대신 교체 전 **스냅샷**을 남기고 **살균 게이트**가 오염된 CSV를 막는다. 기본 실행(`--apply` 없음)은 읽기 전용.

## 마커 문법

```
활성 사용자 10명 <!-- src: users.csv | count rows where status=active -->
```

허용 집계 `count rows` / `distinct <col>` / `sum|avg|max|min <col>`, 필터 `where <col> <op> <값>`(AND만, `= != < > <= >=`), 단위 환산 `/ <수>` `* <수>`. 자연어·JOIN·서브쿼리·`or`는 거부. 상세: [marker-syntax](references/marker-syntax.md).

의도적으로 다른 값이면 같은 줄에 `<!-- intentional: <사유> -->`를 덧붙인다 — 판정이 `intentional`로 빠지고 교체 대상에서 제외된다.

## 실행

```bash
# 감사만 (읽기 전용)
python3 <skill>/assets/audit.py --doc <spec>.md --data <csv-dir> [--json]

# 불일치 자동 교체 (스냅샷 + 살균 게이트)
python3 <skill>/assets/audit.py --doc <spec>.md --data <csv-dir> --apply [--dry-run]
```

exit `0` = 차단 요소 없음, `1` = 미해결(`mapping_failure`/`syntax_error`) 또는 보류 존재, `2` = 스냅샷 경로가 tracked라 진행 거부.

**살균 게이트** — 교체 전에 다음을 `held`로 빼고 쓰지 않는다: 데이터 행 0건 CSV(→ `mapping_failure`), 실측이 문서값의 1/10 이하로 붕괴, 10배 이상 폭증. 10 미만 소수(2→3)는 비율 검사 면제 — 작은 수는 정상 변동이 비율상 커 보인다.

**스냅샷** — `--snapshot-dir`(기본 `.claims-audit/runs`)이 `git check-ignore`를 통과해야 한다. 실패 시 `→ ESCALATE` 후 **진행 거부**. receipt에 복구 명령이 실린다.

1. **문서·데이터 경로 확정** — `--data`가 없으면 CSV 위치를 묻는다. 추측해서 훑지 않는다.
2. **스크립트 실행** — 출력을 그대로 근거로 쓴다. LLM이 값을 다시 계산하지 않는다.
3. **해석** — `mismatch`는 문서가 틀렸을 수도, CSV가 낡았을 수도 있다. 둘 다 제시하고 단정하지 않는다.
4. **보고** — receipt에 판정별 건수와 CSV mtime.

## Output (receipt)

```
수치 감사 완료 (recorded only).
- 문서: `<path>` · CSV: `<dir>` (mtime `<ISO>`)
- 판정: match N / mismatch N / mapping_failure N / syntax_error N / intentional N
- 결론은 CSV 스냅샷 기준 — 라이브 DB·게시본 동기화는 미검증
- artifact: `docs/claims-audit.md`
- next: mismatch는 `--apply`로 교체(T-2), mapping_failure는 마커 수정 필요
```

## Examples

문서:

```markdown
- 활성 사용자 10명 <!-- src: users.csv | count rows where status=active -->
- 코어 팀원 5명 <!-- src: users.csv | count rows where team=core -->
- 관리자 2명 <!-- src: users.csv | count rows where role=admin -->
```

출력:

```
| line | claimed | measured | verdict | detail |
| 7 | 10 | 10 | match |  |
| 8 | 5 | 3 | mismatch |  |
| 9 | 2 |  | mapping_failure | column 'role' not in users.csv (headers: id, name, status, team, score) |
summary: mapping_failure=1, match=1, mismatch=1
```

`role` 컬럼이 없다고 **0으로 세지 않는다** — 그렇게 하면 "관리자 0명"이라는 자신 있는 오답이 문서에 박힌다.

## Error Handling (if-then)

| 트리거 | 대응 |
|---|---|
| `--data` 미지정 | 질문 후 중단. CSV 디렉터리 추측 금지 |
| CSV 헤더 없음 | `mapping_failure` — 해당 주장만 격리, 다른 주장은 계속 |
| 마커 컬럼이 헤더에 없음 | `mapping_failure` + 실제 헤더 목록 표시 |
| 필터 결과 0행 (값 오타·대소문자) | `mapping_failure` (0으로 보고하지 않음) |
| 마커 앞 숫자 2개 이상 | `ambiguous` — 교체 금지, 마커 위치 이동 안내 |
| 숫자 컬럼에 비숫자 셀 (`"1,200"`) | `mapping_failure` — 문자열 비교로 몰래 과소집계하지 않음 |
| 문법 밖 표현 | `syntax_error` — 해석 시도 금지 |
| 마커가 하나도 없음 | 사실 카드 경로 안내 (T-3), 자동 판정 안 함 |
| 그 외 실패 | `❌ 실패:` 블록 |

## 마커 없는 기존 문서 (bootstrap)

```bash
python3 <skill>/assets/audit.py --doc <spec>.md --data <csv-dir> --bootstrap
```

노이즈(날짜·목차 번호·리스트 순번·§참조·코드블록·버전·경로)를 제거하고 남은 수치를 후보로 제시하며, 값이 일치하는 CSV 사실을 힌트로 붙인다. **제안일 뿐 판정이 아니다** — 매핑이 추론이라 이 경로에서는 교체하지 않는다. 사람이 마커를 달면 그다음부터 전자동.

실측(`spec-naranizer.md`): 숫자 토큰 71개 → 후보 22개. 남는 오탐은 데이터 주장이 아닌 **스펙 파라미터**(`1~2문장`, `3개월`)이며, 기계적으로는 구분되지 않는다. 후보 수는 항상 출력해 필터 조정 근거로 남긴다.

## 진입 지점

- **`nara-publish-spec` pre-flight** — 게시 전 자동 실행(`Execution Flow` 스텝 0). `<!-- src: -->` 마커가 하나도 없으면 skip하고 `--bootstrap`만 안내한다. 마커가 있으면: `mapping_failure`·`syntax_error`·`held` 잔존 시 **게시 거부**(그 값들은 실측으로 확인되지 않았다), 단순 `mismatch`는 교체 후 **통과**(수백 건에서 게시가 영영 막히면 안 된다). 우회는 `--skip-claim-audit` 명시 플래그로만 가능하며 우회 사실을 receipt에 남긴다.
- **`nara-grill` 사실 조사** — 대화에 수치 주장 + CSV가 있을 때만 읽기 전용 대조. 수치가 문서에 굳기 전에 잡는다.

## References

- [marker-syntax.md](references/marker-syntax.md) — mini-DSL 전체 문법·거부 사례·예외 마커
