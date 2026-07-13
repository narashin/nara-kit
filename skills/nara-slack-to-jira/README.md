# slack-to-jira — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·셋업 방법 안내.

Slack 스레드 permalink를 던지면 내용을 읽고 Bug/Feature로 분류, 기존 티켓 중복검사 후 draft를 보여주고, 승인하면 Jira 티켓을 만든다. 티켓 본문은 영어.

## 호출

```
/nara-slack-to-jira <slack-permalink> [<slack-permalink> ...]
```

자연어도 됨:

```
"이 슬랙 스레드 티켓 만들어줘 https://....slack.com/archives/C.../p..."
```

링크 여러 개를 한 번에 던져도 된다 (배치).

## 동작 흐름

1. **parse** — 링크에서 채널 ID + 스레드 timestamp 자동 추출 (네가 채널 ID를 입력할 일 없음)
2. **route** — 채널 → Jira 프로젝트 매칭. **처음 보는 채널이면 "어느 프로젝트로?" 한 번만 질문** → 답을 저장, 다음부터 안 물음
3. **fetch** — 스레드 전체 읽음
4. **classify** — Bug / Feature 분류 (스레드에 `(1)`,`(2)` 같은 힌트 있으면 그게 우선)
5. **dedup** — 기존 티켓 검색. 완전 중복 / 관련 / 신규 판정
6. **draft** — 표로 보여줌: 어느 프로젝트 · class · 신규/중복 · 요약. 행별로 펼치면 전체 본문
7. **approve** — 네가 일괄 승인 (행 수정/드롭/분류 변경 가능). **승인 전엔 아무것도 안 만듦**
8. **execute** — 신규→티켓 생성 · 관련→생성 + `relates` 링크 · 중복→기존 티켓에 댓글

## 설정 (자동 성장)

`~/.claude/slack-to-jira.md` 에 프로젝트별 profile이 쌓인다. **직접 쓸 필요 없음** — 새 채널 첫 등장 시 스킬이 물어보고 자동 저장.

```yaml
profiles:
  - channels: [C0123456789]        # 자동 학습됨
    jira_project: ABC
    issue_types: { bug: Bug, feature: Story }
    default_labels: [from-slack]
    dedup_jql_base: "statusCategory != Done"
```

특정 repo에서만 다르게 라우팅하려면 그 repo의 `.claude/overrides/slack-to-jira.md`가 글로벌을 덮어쓴다.

## 전제조건

- **Slack MCP** + **Jira MCP** 연결
- Slack MCP가 링크의 **워크스페이스**에 연결돼 있어야 스레드가 읽힘. 워크스페이스 여러 개면 각각 연결 필요 (`get_team_ids`로 확인). 안 되면 해당 링크는 error 표시 후 나머지 계속

## 배포 (스킬 수정 후)

skills/ 변경은 main에 push 전까진 라이브 아님. commit → main push가 곧 배포 (origin + github 양쪽):

```bash
git push origin main && git push github main
```

소비하는 쪽에서는 최신 스킬 받기:

```
npx skills update
```

## 로컬 테스트 (배포 전)

eval 벤치마크:

```bash
copilot login              # 최초 1회 (copilot-sdk executor 인증)
waza run slack-to-jira
```

또는 Claude 세션에서 링크 하나 주고 "이걸로 slack-to-jira 돌려봐" → draft까지 dry run.
