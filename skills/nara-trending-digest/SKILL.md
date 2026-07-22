---
name: nara-trending-digest
description: >-
  Crawl GitHub Trending (weekly), LLM-filter for AI/LLM and DX tools, post digest to Slack DM and save to Obsidian.
  USE FOR: "GitHub trending", "트렌딩 다이제스트", "trending-digest", "이번 주 트렌딩", "깃헙 트렌딩 정리".
  DO NOT USE FOR: searching specific repos (→ WebSearch), code review (→ code-review).
---

# trending-digest — GitHub Trending 주간 다이제스트

GitHub Trending 페이지를 크롤하여 AI/LLM·DX 관련 레포를 선별, Slack DM + Obsidian에 저장한다.

## 인자 (`$ARGUMENTS`)

```
trending-digest [--since <daily|weekly|monthly>] [--lang <language>] [--top <N>] [--dry-run]
```

| 인자 | 기본값 | 설명 |
|------|--------|------|
| `--since` | `weekly` | 기간 필터 |
| `--lang` | (없음) | 언어 필터 (예: `typescript`, `python`) |
| `--top` | `10` | 최종 선택 레포 수 |
| `--dry-run` | false | Slack/Obsidian 전송 없이 터미널 출력만 |

## 실행 흐름

### Step 1 — 크롤링

Playwright로 GitHub Trending 페이지 접근:

```
https://github.com/trending[/<lang>]?since=<since>
```

`mcp__playwright__browser_navigate` → `mcp__playwright__browser_snapshot` 으로 DOM 스냅샷 획득.

추출 필드 (레포별):
- `owner/name`
- `description`
- `language`
- `stars_total` (전체 스타)
- `stars_period` (이번 기간 스타)
- `url`

### Step 2 — LLM 필터링

각 레포를 아래 기준으로 0–5점 채점:

| 점수 | 기준 |
|------|------|
| +2 | AI/LLM 핵심 (모델, 추론, RAG, agent, MCP) |
| +1 | AI 주변부 (데이터, 임베딩, 파인튜닝 보조) |
| +2 | DX/툴링 핵심 (개발 생산성, CLI, IDE, 코드 품질) |
| +1 | DX 주변부 (런타임 최적화, 모니터링, 테스트 보조) |
| -1 | 주제 무관 (게임, 순수 데모, 마케팅) |

**컷오프:** 2점 미만 제외. 점수 내림차순 정렬 후 `--top N` 선택.

### Step 3 — 다이제스트 포맷

아래 마크다운 템플릿 사용:

```markdown
# GitHub Trending Digest — <YYYY-MM-DD> (주간)

## 🔖 선별 기준: AI/LLM + DX 툴링

<N>개 선별 / 전체 <total>개 크롤

---

### 1. [owner/name](<url>)
**언어:** <language> | **스타:** <stars_total> (+<stars_period>)
<description>
> 선택 이유: <한 줄 설명>

...
```

### Step 4 — Slack DM 전송

```
mcp__slack__get_me        → user_id 획득
mcp__slack__post_message  → channel=<user_id> (DM), text=다이제스트 전문
```

`--dry-run` 이면 스킵.

### Step 5 — Obsidian 저장

경로: `Inbox/github-trending-<YYYY>-W<WW>.md`

```
mcp__obsidian-mcp-tools__create_vault_file
  path: Inbox/github-trending-<YYYY>-W<WW>.md
  content: <다이제스트 마크다운>
```

파일 이미 존재하면 `append_to_vault_file` 로 이어쓰기.

`--dry-run` 이면 스킵.

## 오류 처리

| 상황 | 처리 |
|------|------|
| Playwright 페이지 로드 실패 | 3회 재시도 후 `❌ 크롤링 실패` 출력 |
| 크롤 결과 0개 | `❌ 레포 없음 — GitHub 페이지 구조 변경 확인 필요` |
| Slack 전송 실패 | Obsidian 저장 계속 진행, `→ ESCALATE: Slack 전송 실패` |
| Obsidian 저장 실패 | 다이제스트 터미널 출력 fallback |

## 크론 설정

Claude Code CronCreate로 주간 자동 실행 설정:

```
cron: "3 9 * * 1"       # 매주 월요일 09:03 로컬 (off-minute — jitter 만료경계 완화)
prompt: "/nara-trending-digest --since weekly"
durable: true           # 세션 재시작 후에도 유지 (7일 후 자동 만료 → Step 0 self-renew로 연장)
recurring: true
```

설정 명령어:
```
CronCreate(
  cron="3 9 * * 1",
  prompt="/nara-trending-digest --since weekly",
  durable=true,
  recurring=true
)
```

> **7일 만료 vs 주간 실행 = 자기모순.** CronCreate 크론잡은 7일 후 자동 만료되는데 스케줄은 주간(월요일)이라, 갱신 없으면 다음 발화 직전/직후 만료돼 스케줄이 죽을 수 있다.

### Step 0 — 크론 self-renew (헤드리스 실행 시 **가장 먼저**, crawl 전)

CronCreate는 dedup하지 않는다 — 호출마다 **새 job ID**를 만든다. 따라서 단순 재생성은 **중복 크론**을 낳는다(주간 DM 2번). 반드시 **삭제 후 재생성**:

```
CronList()                                  # 기존 trending-digest job 조회
CronDelete(<matching job id(s)>)            # prompt에 "nara-trending-digest" 포함된 기존 job 전부 삭제
CronCreate(cron="3 9 * * 1", prompt="/nara-trending-digest --since weekly", durable=true, recurring=true)
```

- **crawl보다 먼저, 어떤 결과에도 묶지 않고 실행** — self-renew는 digest 내용이 필요 없다. crawl/Slack/Obsidian이 실패해도 스케줄은 살아남아야 하므로 Step 1~5 성공에 **의존하지 않는다** (crawl 실패로 체인이 죽는 것 방지). 그래서 Step 4/5가 아니라 맨 앞 Step 0.
- **스코프 한계(솔직)**: LLM은 크론-트리거인지 수동 실행인지 확실히 구분 못 한다(프롬프트 동일). 판별 신호는 `--dry-run`(수동)뿐 — dry-run이면 self-renew 생략. dry-run 아닌 수동 실행은 self-renew를 돌려도 CronList→Delete→Create라 중복은 안 생기고 스케줄만 갱신됨(무해).
- **잔여 리스크(플랫폼)**: recurring job의 마지막(7일째) 발화가 jitter로 만료 경계를 넘겨 스킵되면 재생성 체인이 끊길 수 있다. off-minute cron(`3 9`)으로 완화하되 완전 제거는 불가 — 끊기면 수동 재설정.

## 실행 맥락 (fire-and-forget)

이 스킬은 **주간 크론 헤드리스 실행**이 기본. Slack DM(본인) + Obsidian(개인 vault) write는 인터랙티브 confirm 게이트 없이 실행된다 — 헤드리스라 확인할 사람이 없기 때문. 안전은 **side effect의 저위험·가역성**(본인 DM·개인 노트, 삭제 가능)으로 확보. 게시 전 확인이 필요하면 `--dry-run`으로 수동 실행해 터미널 출력만 검토한다.
