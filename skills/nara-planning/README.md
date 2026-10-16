# nara-planning: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Own one feature's planning bundle (a folder under docs/product/: PRD, evidence ledger, decision log, conditional policy/flow/IA docs) and drive it by its coverage table. Each run picks the first open required item, does its own part, and offers the next skill (grill, ac-draft, claim-audit) to run in the same session on consent. Never invents interview results, numbers, policy, priorities, dates, or owners.

## 호출

- Claude Code: `/nara-planning [기능 한 줄 | slug] [근거 파일...]`
- Codex: `$nara-planning ...`

인자 없이 부르면 현재 브랜치의 기획 묶음을 이어 간다.

## 언제 쓰나

- **USE FOR:** "기획 시작", "기능 기획", "기획서 써줘", "요구사항 정의서", "스토리보드", "PRD 써줘", "기획 이어서", "인터뷰 정리", "근거 정리", "정책 정리", "권한·상태 전이 정리", "IA 정리", "KPI 정의", "planning".
- **DO NOT USE FOR:** 방향·마일스톤이 아직 없음 (→ nara-roadmap), 결정 하나만 찔러보기 (→ nara-grill), AC만 필요 (→ nara-ac-draft), 코드 작업 분할 (→ nara-plan), 기술 결정 문서 (→ nara-rfc, nara-adr), Confluence 게시 (→ nara-publish-spec).

## 왜 있나

기존 스킬은 질문(`nara-grill`)과 AC(`nara-ac-draft`)는 잘하지만, 목표·KPI·정책·권한·IA를 담을 파일이 없었고 grill이 확정한 결정을 읽는 곳도 없었다. 초보 기획자는 무엇을 빠뜨렸는지 모르는 것이 가장 큰 문제다. 이 스킬은 기능 하나의 기획 묶음을 소유하고, 커버리지 표로 빈 칸과 필요한 입력을 보여 주며, 다음 단계를 직접 이어 간다.

흐름을 이끌지만 워크플로 메타 스킬은 아니다. 폐기된 메타 스킬은 산출물 없이 호출 순서만 담았다. 이 스킬은 묶음 파일을 소유하고, 다른 스킬은 사용자 동의를 받고 같은 세션에서 실행한다.

## 산출물

`docs/product/<slug>/` 아래 `prd.md`(상태, 커버리지 표, 문제·대상·가치 제안·목표·범위·결정 로그), 근거가 있으면 `evidence.md`, 해당할 때만 `policy.md`·`flows.md`·`ia.md`. 개발 중인 기능의 AC는 `docs/requirements.md`, 나머지는 각 묶음의 `requirements.md`로 옮겨 둔다. 형식은 [references/bundle-format.md](references/bundle-format.md), 근거와 KPI는 [references/evidence.md](references/evidence.md).

## 설계 메모

pm-skills `01f0c62`(MIT)를 증류해 만들었다. 가져온 것은 인터뷰 원칙(The Mom Test), 인터뷰 요약에서 원문에 없는 칸은 비우는 규칙, 네 가지 위험 가정과 영향×위험 분류, 실험 전 성공 기준, KPI 정의표, 6요소 가치 제안, "모르면 가정 절로", 핵심 문서와 조건부 문서 구조다. 가져오지 않은 것: 고정 개수 생성(페르소나 3개 등), 스토리·테스트 시나리오 생성(ac-draft, test-discover가 담당), 전략 캔버스, 아이디어 대량 생성, 여러 스킬을 잇는 명령. 판정 전체는 조사 리포트(로컬 `docs/research/pm-skills-distillation.md`)에 있다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
