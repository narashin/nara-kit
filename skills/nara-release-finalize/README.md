# nara-release-finalize — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Finalize a release after QA passes on the pre-release branch: open (or detect) the merge PR into the base branch with drafted release notes, then — once that PR is merged — tag the merge commit and push it (which triggers production deploy) behind an explicit confirmation gate. One command, re-run as-is; it auto-detects the stage from PR state. Approval and merge always stay human-only.

## 호출

- Claude Code: `/nara-release-finalize`
- Codex: `$nara-release-finalize`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "release finalize", "release-finalize", "pre-release main 머지", "머지 PR 열어", "release 태그", "release note 작성", "release@v 태그", "/nara-release-finalize 1.5.0".
- **DO NOT USE FOR:** QA 배포 준비 (→ release-prep), PR approve/merge 실행 자체 (사람이 GitHub에서 수행), 일반 feature PR 생성 (→ pr), 커밋 메시지 (→ commit).

## 설정

로컬 설정 파일(`*.local.md`)이 필요할 수 있음. 자세한 절차는 [SKILL.md](SKILL.md) 참고.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
