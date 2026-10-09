# nara-research — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Compare external prior art for one pending decision, or distill a source skill/workflow/repo into a keep/adapt/omit proposal, with every source pinned to a revision and the result saved as one markdown report.

## 호출

- Claude Code: `/nara-research <결정 또는 질문> [--source <repo URL | 경로 | 스킬명>] [--update <기존 리포트>] [--no-file]`
- Codex: `$nara-research ...`

## 언제 쓰나

- **USE FOR:** "선행 사례 조사", "다른 데선 어떻게 하나", "이 repo에서 뭘 가져올까", "스킬 증류", "research", "prior art", 외부 도구·접근법 비교, 남의 스킬·워크플로에서 흡수할 것 찾기.
- **DO NOT USE FOR:** 이미 가진 설계를 찔러보기 (→ nara-grill), 기획서 수치 검증 (→ nara-claim-audit), 결정 기록 (→ nara-adr), 스킬 생성·수정 (→ nara-skill-forge), 이 코드베이스 동작 질문 (코드를 직접 읽는다).

## 왜 있나

외부 repo나 남의 스킬을 보고 "뭘 가져올까"를 정하는 일이 반복됐는데, 매번 대화 안에서 끝나서 어느 revision을 읽었는지, 왜 안 가져왔는지가 남지 않았다. 이 스킬은 그 조사를 리포트 한 장으로 남긴다. 출처는 revision을 고정하고, 결정에 걸리는 주장은 구절을 인용하고, 재현 안 한 효능은 그렇다고 적는다.

산출물은 제안이다. 스킬을 고치는 것은 `nara-skill-forge`, 결정을 기록하는 것은 `nara-adr`이 한다.

## 산출물

`docs/research/YYMMDD-<slug>.md`. 골격은 [references/report.md](references/report.md). 같은 결정을 다시 조사하면 새 파일 대신 갱신 절을 덧붙인다.

## 설계 메모

출발점은 MTGVim/tiger-kit의 `tk-research`(`fd7a7a07f73b5b874e5d2cd335c6025d9da13c8e`)다. 증거 규율과 증류 절차, 출처 색인 형식을 가져왔고 본문은 새로 썼다. 그쪽의 영속 연구 상태(frontier 재생성, 체크포인트 ID, `--resume`, 외부 스케줄러 재개)와 실험 무결성 하네스, HTML 리포트는 가져오지 않았다. nara-kit에서 워크플로를 상태머신으로 포장한 스킬은 쓰이지 않았고, 조사 결과는 `docs/` markdown이 관례다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
