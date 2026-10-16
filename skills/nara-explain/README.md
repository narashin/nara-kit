# nara-explain — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Generate shareable explanations of code, features, projects, or PRs tailored to a specific audience.

## 호출

- Claude Code: `/nara-explain`
- Codex: `$nara-explain`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "explain", "설명해줘", "explain to PM", "발표 자료", "온보딩 문서", "이 PR 뭐 바꿨는지 설명해줘", "이 커밋 설명", "diff 설명".
- PR·커밋·브랜치·작업 트리 설명은 **HTML 한 장**(`docs/explain/<대상>.html`)으로 나온다. 비교 기준(base/head SHA)을 먼저 고정하고 주장마다 `path:line`을 단다. 순서는 배경, 직관, 흐름, 꼭 볼 곳, 이해 확인. "md로"라고 하면 Markdown. 만든 파일은 `assets/check_explain.py`로 정적 검사한다.
- **DO NOT USE FOR:** learning-focused explanations (use explain-like-senior), code review, documentation generation.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
