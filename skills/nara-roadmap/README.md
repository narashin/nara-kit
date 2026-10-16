# nara-roadmap: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Turn an unclear situation into a reviewable, constraint-aware roadmap (direction, priorities, milestones with completion evidence) through frontier-round interviews, including nontechnical initiatives with no repository. Conversation by default; saved only on request.

## 호출

- Claude Code: `/nara-roadmap [주제 또는 맥락]`
- Codex: `$nara-roadmap ...`

인자 없이 불러도 된다. 대화에 맥락이 있으면 그것으로 시작하고, 없으면 무엇을 다룰지부터 묻는다.

## 언제 쓰나

- **USE FOR:** "로드맵 짜줘", "마일스톤 정리", "뭐부터 할지 우선순위", "roadmap", "이거 어떻게 추진할지", "기획 방향 잡아줘", 기획 흐름 맨 앞에서 방향이 아직 없을 때.
- **DO NOT USE FOR:** 코드 작업 단위 분할 (→ nara-plan), 이미 있는 계획 찔러보기 (→ nara-grill), 외부 선행 사례 비교 (→ nara-research), AC 초안 (→ nara-ac-draft).

## 왜 있나

기획 흐름의 기존 스킬은 모두 방향이 정해진 뒤에 일한다. `nara-ac-draft`는 의도 한 줄을 요구사항으로, `nara-grill`은 이미 있는 계획을 검증으로, `nara-plan`은 고른 범위를 코드 작업 단위로 바꾼다. "이걸 어떻게 추진할지"가 아직 없는 단계, 특히 repo가 없는 비기술 과제는 맡는 스킬이 없었다. 이 스킬은 그 단계를 인터뷰로 풀어 마일스톤 단위의 제안으로 만든다. 날짜·담당자·역량은 지어내지 않고, 조사나 중단도 정당한 결론으로 둔다.

## 산출물

기본은 대화다. 저장을 요청하면 `docs/plan/roadmap-<slug>.md` 한 파일을 쓴다. 섹션은 목표와 결정 제약, 권고 방향, 마일스톤, 반복 운영, 열린 가정과 결정, 다음 행동이다. 골격과 예시는 [references/roadmap-format.md](references/roadmap-format.md).

## 설계 메모

출발점은 MTGVim/tiger-kit의 `tk-roadmap`(`5e35b6a`, MIT)이고, 그쪽은 phuryn/pm-skills(`8607e3b077817f89bf4a9b623246219734ac3be0`)의 결과 중심 로드맵·선택지 비교·우선순위와 mattpocock/skills wayfinder(`c55ee46073ed923f86ce59a5eb3b6d895095d1b7`)의 미정 범위와 제외 범위 구분을 가져왔다. 인터뷰 관점, 제약 3분류, 범위 상태 3종, 조사 마일스톤, 반복 운영 분리를 가져왔고 본문은 새로 썼다.

가져오지 않은 것: `.tigerkit/` 산출물 경로와 Git 제외 점검, 이모지 헤더 결과 요약, 출력 표기 규칙, 구분선으로 여는 질문 블록, skill-feedback 포인터. 저장 경로는 nara-kit 관례에 맞춰 `docs/plan/roadmap-<slug>.md`로 바꿨다. 질문 형식은 `nara-grill`의 frontier 라운드를 그대로 쓴다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
