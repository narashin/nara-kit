# nara-claim-audit — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Audit numeric claims in a local spec markdown against CSV data snapshots, reporting each claim as match, mismatch, mapping failure, or syntax error.

## 호출

- Claude Code: `/nara-claim-audit`
- Codex: `$nara-claim-audit`
- 직접 실행: `python3 skills/nara-claim-audit/assets/audit.py --doc <spec>.md --data <csv-dir>`

## 언제 쓰나

- **USE FOR:** "수치 맞나 확인해줘", "기획서 숫자 검증", "데이터랑 문서 대조", "claim audit", "스펙 수치 감사", 게시 전 수치 점검.
- **DO NOT USE FOR:** 요구사항 vs 코드 갭 (→ nara-gap), 브라우저 AC 판정 (→ nara-browser-verify), Confluence 게시 (→ nara-publish-spec), 게시본 개정 이력 (→ nara-spec-revision).

## 왜 있나

기획은 데이터를 근거로 하는데, 그 수치가 실제와 다른 채로 문서가 완성되면 뒤에 쌓인 결정이 전부 흔들린다. `[UNVERIFIED]` 표시는 **쓰는 사람이 추측 중임을 자각할 때만** 붙으므로 "확신을 갖고 틀리게 쓴 값"은 못 잡는다. 이 스킬은 그걸 잡는다.

## 쓰는 법

1. 문서의 수치 옆에 출처 마커를 한 번 단다:
   ```
   활성 사용자 10명 <!-- src: users.csv | count rows where status=active -->
   ```
2. CSV가 있는 디렉터리를 지정해 감사를 돌린다.
3. `mismatch`가 나오면 문서가 틀렸거나 CSV가 낡은 것 — 둘 다 확인한다.

문법 전체는 [references/marker-syntax.md](references/marker-syntax.md).

## 설계 메모

측정은 `assets/audit.py`(Python 표준 라이브러리만)가 소유한다. LLM이 마커를 해석하면 같은 문서에서 매번 다른 값이 나올 수 있고, 그러면 자동 교체가 위험해진다. 테스트는 `assets/test_audit.py` — `python3 -m unittest test_audit`.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
