# nara-release-prep — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

One-shot release preparation: collect PRs merged into develop but not in the base branch, recreate the release branch, trigger the QA deploy workflow (workflow_dispatch), and append the release Fix Version to every referenced Jira ticket. Per-repo config with first-run bootstrap.

## 호출

- Claude Code: `/nara-release-prep`
- Codex: `$nara-release-prep`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "릴리즈 준비", "release prep", "release-prep", "fix version 추가", "pre-release 만들어", "QA 배포 준비", "/nara-release-prep 1.2.3".
- **DO NOT USE FOR:** PR 생성 (→ pr), 커밋 메시지 (→ commit), Jira 티켓 생성 (→ slack-to-jira), Jira 버전 생성 (team creates versions beforehand), production deploys.

## 설정

로컬 설정 파일(`*.local.md`)이 필요할 수 있음. 자세한 절차는 [SKILL.md](SKILL.md) 참고.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
