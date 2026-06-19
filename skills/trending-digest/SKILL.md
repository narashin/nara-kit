---
name: trending-digest
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
cron: "0 9 * * 1"       # 매주 월요일 09:00 로컬 시간
prompt: "/nara-kit:trending-digest --since weekly"
durable: true           # 세션 재시작 후에도 유지 (7일 후 자동 만료)
recurring: true
```

설정 명령어:
```
CronCreate(
  cron="0 9 * * 1",
  prompt="/nara-kit:trending-digest --since weekly",
  durable=true,
  recurring=true
)
```

> **주의:** CronCreate 크론잡은 7일 후 자동 만료됨. 매주 갱신 필요.
