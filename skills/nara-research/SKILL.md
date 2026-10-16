---
name: nara-research
description: >-
  Compare external prior art for one pending decision, or distill a source skill/workflow/repo into a keep/adapt/omit proposal, with every source pinned to a revision and the result saved as one markdown report.
  USE FOR: "선행 사례 조사", "다른 데선 어떻게 하나", "이 repo에서 뭘 가져올까", "스킬 증류", "research", "prior art", 외부 도구·접근법 비교, 남의 스킬·워크플로에서 흡수할 것 찾기.
  DO NOT USE FOR: 이미 가진 설계를 찔러보기 (→ nara-grill), 기획서 수치 검증 (→ nara-claim-audit), 결정 기록 (→ nara-adr), 스킬 생성·수정 (→ nara-skill-forge), 이 코드베이스 동작 질문 (코드를 직접 읽는다).
---

# research: 결정 하나를 위한 외부 근거 조사

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

입력은 둘 중 하나다. **선행 사례 비교**는 내려야 할 결정과 후보 접근법을 받아 외부 증거로 비교한다. **증류**는 남의 스킬·워크플로·repo를 받아 nara-kit이 가져올 것과 버릴 것을 가른다. 산출물은 `docs/research/YYMMDD-<slug>.md` 한 장이고, 내용은 제안이다. 적용은 사람이 정하고, 스킬 수정은 `nara-skill-forge`가 한다.

이 스킬은 상태 파일을 만들지 않는다. 한 번 호출이 리포트 하나다. 이어서 조사하려면 기존 리포트를 입력으로 받아 갱신 절을 덧붙인다.

## Core Rules

1. **결정에서 출발한다**: 조사는 하나의 downstream 결정을 위해 한다. 결정이 없으면 묻고 시작하지 않는다. 사용자의 현재안이나 가장 단순한 안을 baseline으로 보존한다. baseline을 최적화만 하는 조사는 비교가 아니다.
2. **출처는 revision을 고정한다**: repo는 커밋 SHA, 문서는 버전이나 날짜, 웹 페이지는 접근일. 고정 못 한 출처는 영수증에 수로 드러낸다.
3. **링크가 살아있는 것과 주장을 뒷받침하는 것은 다른 검사다**: 결정에 걸리는 주장은 그 구절이나 결과를 직접 읽고 리포트에 인용한다. 2차 출처는 닿을 수 있으면 1차로 거슬러 간다. 못 읽은 주장은 `[UNVERIFIED: requires <source>]`로 두고 지우지 않는다.
4. **관찰·주장·추론을 섞지 않는다**: 출력 계약의 provenance 라벨(Evidence / Interpretation / Decision / Suggestion)을 쓴다. 인기, 인용 횟수, 같은 말의 반복은 증거가 아니다. 재현하지 않은 효능은 "재현 안 함"으로 적는다.
5. **유력안에 반례로 도전한다**: 실패 사례와 한계를 찾아 해소되면 근거를, 남으면 불일치를 그대로 기록한다. 과거에 받아들인 주장이 뒤집히면 삭제 대신 정정 이유를 남긴다.
6. **권고는 최소 충분안 + 확신도 + 뒤집을 증거**: 증거가 결정을 못 가르면 가장 작은 빠진 입력이나 관찰 가능한 성공·실패 기준이 있는 bounded spike를 제안한다. 제안이지 실행 권한이 아니다.
7. **증류는 제안이지 수정이 아니다**: `keep | adapt | omit` 표를 만들고 형태(reference 추가 / 기존 스킬 개선 / 독립 스킬 / no-op)를 판정한다. 내부 워크플로가 있다는 이유만으로 새 스킬을 제안하지 않는다. 절차는 [distillation](references/distillation.md).
8. **외부 검색에 사내 것을 보내지 않는다**: 코드, 로그, 식별자, 사내 워크플로 본문은 일반화해서 묻는다. 리포트가 공개 repo에 들어가면 placeholder만 쓴다.
9. **효율·안전·호환은 짝 증거 없이 주장하지 않는다**: "더 빠르다", "더 안전하다"는 비교 대상과 측정이 같이 있을 때만 쓴다.

## 인자 ($ARGUMENTS)

`nara-research <결정 또는 질문> [--source <repo URL | 경로 | 스킬명>] [--update <기존 리포트>] [--no-file]`

`--source`가 있으면 증류 모드다. `--update`는 기존 리포트에 갱신 절을 덧붙인다. `--no-file`은 같은 내용을 채팅으로만 낸다.

## Procedure

1. **Scope**: 결정, 제약, 성공 기준, 제외 범위를 적는다. baseline을 확정한다. `docs/research/`에 같은 slug가 있으면 읽고 갱신 모드로 간다.
2. **재구성**: 제안된 구현과 독립적으로 문제를 다시 말한다. 확립된 용어와 인접 문제군을 찾는다. 대안은 baseline 포함 2~4개.
3. **수집**: 선행 사례 모드는 [evidence](references/evidence.md), 증류 모드는 [distillation](references/distillation.md)을 따른다. 가장 관련 있는 2~3개를 깊게 읽고, 구체적 공백을 메울 때만 넓힌다. 읽은 파일과 revision을 그때그때 적는다.
4. **비교**: 결정에 걸리는 축만 쓴다(가정, 정확도와 오탐, 비용, 구현 노력, 설명 가능성, 확장 조건). 모르는 칸은 비워 두고 unknown으로 센다.
5. **도전**: 유력안의 반례와 실패 보고를 찾는다.
6. **권고**: 최소 충분안, 확신도, 뒤집을 증거, 못 정했으면 빠진 입력이나 spike.
7. **리포트**: [report](references/report.md)의 골격으로 `docs/research/YYMMDD-<slug>.md`를 쓴다. 출처 색인에 모든 출처의 revision과 읽은 파일을 남긴다.
8. **자체 점검**: 결정에 걸리는 주장마다 인용이 있는지, 출처마다 revision이 있는지, 재현 안 한 효능이 사실처럼 적히지 않았는지 본다.

## Output (receipt)

```
조사 완료 (recorded only).
- 결정: 외부 선행사례 비교를 스킬로 둘지
- 권고: 얇은 독립 스킬 · 확신도 medium · 뒤집을 증거: 월 1회 미만 호출
- 출처 4 (SHA 고정 4) · 주장 9 (인용 8 / unverified 1)
- artifact: `docs/research/261009-research-skill.md`
- Next: 권고 수용 여부 결정. 수용이면 `/nara-skill-forge`로 적용
```

## Trailing status (필수)

```
research: <path> | chat-only | none (<사유>)
mode: prior-art | distill
sources: N (pinned p / unpinned u / unreadable r)
claims: N (cited c / unverified v)
verdict: <권고 한 줄> · confidence high | medium | low
distill: keep a / adapt b / omit c | n/a
```

`unpinned`와 `unverified`는 0이어도 적는다. `distill`은 증류 모드가 아니면 `n/a`.

## Error Handling (if-then)

| 트리거 | 대응 |
|---|---|
| 결정이 없는 열린 질문 | 어떤 결정을 위한 조사인지 묻고 중단 |
| `--source`가 비공개이거나 접근 불가 | 읽을 수 있는 범위만 증류하고 나머지는 `[UNVERIFIED: requires <source>]` |
| 출처 revision을 못 구함 | 그 출처를 `unpinned`로 세고 접근일을 적는다 |
| 사내 자료가 검색어에 들어가려 함 | 일반화한 질문으로 바꾼다. 못 바꾸면 그 검색은 건너뛴다 |
| 증거가 결정을 못 가름 | 권고 대신 빠진 입력 또는 spike 제안. `confidence low` |
| 증류 결과가 "가져올 것 없음" | 그것도 판정이다. omit 사유를 남기고 끝낸다 |
| 리포트 경로를 못 씀 | 채팅으로 같은 내용을 내고 `research: none (<사유>)` |

## References

- [evidence.md](references/evidence.md): 출처 고정, 주장과 출처 짝 검사, 비교 축, 반례 탐색
- [distillation.md](references/distillation.md): 남의 스킬·워크플로를 keep/adapt/omit으로 가르는 절차와 형태 판정 기준
- [report.md](references/report.md): `docs/research/<slug>.md` 골격과 출처 색인 형식
