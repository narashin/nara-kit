# nara-ask-repo: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Answer one concrete question about a repository's behavior — this repo, another local checkout, or a remote GitHub repo pinned to a commit — read-only, with path:line evidence beside every claim: where a value comes from, whether something exists, what a change would affect, who owns a behavior.

## 호출

- Claude Code: `/nara-ask-repo`
- Codex: `$nara-ask-repo`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "이 값 어디서 와", "이거 실제로 쓰여?", "이거 바꾸면 어디 영향", "이 동작 누구 책임이야", "다른 repo에서 이거 어떻게 해", "저 저장소 보고 판단해줘", "ask-repo", repo 동작 질문, 다른 저장소 코드 확인.
- **DO NOT USE FOR:** 독자용 설명 문서·발표 자료 (→ nara-explain), 외부 선행 사례 비교·남의 스킬 증류 (→ nara-research), 구현 (→ nara-implement), 리뷰 (→ nara-code-review), 일반 지식 질문, 화면 실물 확인 (→ nara-browser-verify).

## 이웃 스킬과의 차이

nara-ask-repo는 질문 하나에 근거로 답한다. 독자를 위한 설명 문서는 nara-explain, 다른 곳의 선행 사례 비교나 스킬 증류는 nara-research가 맡는다.

## 설계 메모

출발점은 MTGVim/tiger-kit `tk-ask-repo`(`5e633e3`, MIT)다. 검색 출발점 고정, 선언은 모양만 증명한다는 원칙, 못 찾음과 없음의 구분(넷 중 하나로 판정), 영향 범위 셋 분류, 소비자 쪽부터 보는 책임 판정, 답 먼저 쓰는 형식을 가져왔다. 원본은 명시 호출 전용이지만 읽기만 하는 스킬이라 자연어 호출을 열어 두었다. 다른 로컬 checkout이나 원격 GitHub 저장소를 커밋 SHA로 고정해 읽는 부분은 nara-kit에서 새로 붙였다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
