---
name: wiki-inject
description: >-
  Inject a note into personal LLM wiki (Obsidian). Routes by project + content type (source / meeting / concept).
  USE FOR: "wiki에 추가", "위키에 박아", "회의록 위키에", "/wiki-inject".
  DO NOT USE FOR: editing existing notes, Confluence (use publish-spec), session learnings (use reflect).
---

# wiki-inject — LLM Wiki Note 주입

## Vault Layout

```
~/Library/Mobile Documents/iCloud~md~obsidian/Documents/narashin/1_wiki/llm-wiki/
├── tech-notes/          # 외부 학습·연구 (영상, 블로그, 논문, 책)
│   ├── purpose.md
│   ├── schema.md
│   ├── raw/sources/     # 모든 raw 원천 (이 스킬이 다루는 층)
│   ├── raw/assets/      # 이미지·바이너리
│   └── wiki/...         # LLM-wiki 도구 ingest 자동 생성
├── org-common/         # 회사 전사·공통 (전사 회의, 릴리스 프로세스, 인프라 공통)
├── APP/               # APP 프로젝트
├── svc/               # svc 프로젝트
└── <new-project>/       # 신규 도메인 발견 시 사용자가 bootstrap
```

iCloud 동기화. **Karpathy LLM-wiki 컨벤션** ([gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)) 따름:

- **`raw/`** = immutable 원천 자료. 사용자가 drop. LLM 읽기만, 수정 X.
- **`wiki/*`** = **LLM-wiki 도구가 ingest로 자동 생성** (concepts, synthesis, entities, comparisons, queries, sources card). **수동 작성 X**.
- **`schema.md`, `purpose.md`** = 프로젝트 설정. 사용자가 직접 작성.

→ **이 스킬은 `raw/` 층 전담.** wiki/* 은 절대 직접 안 씀.

## Projects

| Project | Path | When |
|---------|------|------|
| `tech-notes` | `llm-wiki/tech-notes/` | 외부 학습 자료 (영상·블로그·논문·책·트윗) |
| `org-common` | `llm-wiki/org-common/` | 회사 전사·공통 (전사 회의, 릴리스 프로세스, 인프라 공통 결정) |
| `APP` | `llm-wiki/APP/` | APP 프로젝트 (회의록·결정·인프라·코드 컨셉) |
| `svc` | `llm-wiki/svc/` | svc 프로젝트 (회의록·결정·인프라·코드 컨셉) |
| `<other>` | `llm-wiki/<other>/` | 신규 도메인. 사용자가 직접 bootstrap (디렉토리 생성 + schema/purpose 복사) |

가용 프로젝트 항상 `ls llm-wiki/`로 동적 확인. 디렉토리 없으면 escalate.

### Cross-project 판단 가이드

자료가 여러 프로젝트에 걸칠 때:

| 상황 | 위치 |
|------|------|
| 한 프로젝트 전용 회의·결정 | 해당 프로젝트 |
| 전사·여러 프로젝트 공통 | `org-common` |
| 외부 학습 자료 (영상·블로그·논문) | `tech-notes` |
| 한 프로젝트에서 발견된 일반 기술 인사이트 | `tech-notes` (도메인 지식 승격) + 해당 프로젝트에서 backlink |
| 두 프로젝트 공통 적용되는 가이드 | `tech-notes` 또는 `org-common`, 양쪽에서 backlink |

## Content Types (모두 raw/sources/ 행)

| Type | Target Dir | When |
|------|------------|------|
| `source` | `<project>/raw/sources/` | 외부 자료 (영상·블로그·논문·책·트윗·토크·Confluence dump·Jira plan) |
| `meeting-summary` | `<project>/raw/sources/` | 회의록 요약본 (Summary + Key Points + Action Items) |
| `meeting-raw` | `<project>/raw/sources/` | 회의록 원문 (발언 포함) |

**⚠️ 중요: nashsu/llm_wiki 도구는 `raw/sources/`만 watch.** `raw/meetings/`에 박으면 ingest 안 됨 → wiki/* 페이지 생성 안 됨. 모든 raw 자료는 `raw/sources/`로 가야 함.

frontmatter `type` 필드로 source 종류 구분 (source / meeting-summary / meeting-raw).

**제거됨: `concept-draft`** — wiki/concepts/는 LLM-wiki ingest의 산출물층. 수동 주입 시 일관성 깨짐.

정제된 컨셉이 필요하면:
1. raw/sources/에 원천 자료 주입
2. LLM-wiki 도구가 자동 감지 → wiki/concepts·wiki/synthesis 자동 생성

## Routing Logic

```
질문 1: 어느 프로젝트?
  - 사용자 명시 (APP/svc/org-common/tech-notes/기타) → 그 프로젝트
  - 콘텐츠 안에 프로젝트 코드명·Jira 키 → 추론 후 사용자 확인
  - 영상 URL/블로그/논문/책 등 외부 학습 자료 → tech-notes
  - 전사·여러 팀 공통 (전사 회의, 릴리스 정책 등) → org-common
  - 모호 → 반드시 사용자에게 확인

질문 2: 어떤 타입?
  - "요약본", Summary/Key Points/Action Items 구조 → meeting-summary
  - 발언자별 토씨까지 → meeting-raw
  - URL + 외부 자료 (영상/블로그/논문/책/Confluence dump) → source

질문 3: 충돌 검사
  - 동일 파일명 존재? → 갱신 / 신규 결정
  - 유사 주제 존재? → backlink로 연결
```

**원칙: 회의록 ≠ org-common 자동.** 프로젝트별 회의(APP H1, svc 인프라 등)는 해당 프로젝트로. org-common은 **전사 공통**(릴리스 정책, 인프라 표준 등) 전용.

## Steps

1. **프로젝트 결정** — 키워드 추론 → 모호하면 사용자 확인.
2. **타입 결정** — 입력 형식 추론 → 모호하면 사용자 확인.
3. **경로 결정** — `<vault>/<project>/raw/sources/<filename>.md`. 모든 타입이 raw/sources/ 행.
4. **중복 체크** — `ls`로 동일/유사 파일명 확인.
5. **파일명 결정** — 타입별 규칙 따름 (아래 표).
6. **frontmatter + 본문 작성** — 타입별 템플릿 따름.
7. **Backlinks** — 기존 노트 1~3개 연결. 고립 금지.
8. **저장** — Write tool.
9. **수신증 출력** — 경로 + 백링크 + 다음 액션.

## 파일명 규칙

| Type | 규칙 | 예시 |
|------|------|------|
| `source` | `<domain>-<thesis>.md` (kebab-case, 50자 이내) | `claude-agent-sdk-bash-is-all-you-need.md` |
| `meeting-summary` | `YYYY-MM-DD-<topic>.md` | `2026-05-18-h1-priorities-and-release.md` |
| `meeting-raw` | `YYYY-MM-DD-<topic>-raw.md` | `2026-05-18-h1-priorities-raw.md` |

전부 영문 kebab-case. 한글 파일명 X (Obsidian backlink 충돌).

## 타입별 Frontmatter + 본문 템플릿

### Type: `source` (외부 자료)

```yaml
---
created: 2026-05-18T10:00       # ISO 8601 KST
updated: 2026-05-18T10:00
tags:
  - <domain>                     # ai-native, anthropic 등
  - <subtopic>
  - <type>                       # talk, article, paper, thread, book
source:
  - <URL>
---
```

본문:
```markdown
# <Title> — <한 줄 캐치>

> Source: <URL>
> <저자/화자, 날짜>
> <왜 이 노트>
> 관련: [[other-note]]

---

## TL;DR
- 핵심 명제 3~6개

---

## 1. <섹션>
...

---

## 나의 운영과 매핑 (선택)

| 자료 컨셉 | 나의 구현 |
|---|---|

---

## 액션 가설 (선택)
- 단기 / 중기 / 장기

---

## 관련 노트
- [[note-1]] — 한 줄
```

### Type: `meeting-summary` (회의록 요약)

```yaml
---
created: 2026-05-18T10:00
updated: 2026-05-18T10:00
date: 2026-05-18                 # 회의 일자
project: org-common
type: meeting-summary
tags:
  - meeting
  - <topic>                      # h1, release, infra 등
  - <quarter>                    # 2026-h1
participants:
  - <name1>
  - <name2>
related-tickets:                 # 선택
  - PROJ-123
---
```

본문 (입력된 Summary/Key Points/Action Items 구조 유지):
```markdown
# <YYYY-MM-DD> <회의 주제>

> 참석자: <names>
> 관련: [[other-meeting]], [[concept]]

---

## Summary
<요약 단락>

## Key Points
- <키포인트>

## Action Items
- [ ] <task> — <assignee> — <due>

## Decisions
- <결정 사항>

## Open Questions
- <후속 논의 필요>

---

## 관련 노트
- [[YYYY-MM-DD-prev-meeting]] — 이전 회의
- [[concept-note]] — 관련 컨셉
```

### Type: `meeting-raw` (회의록 원문)

```yaml
---
created: 2026-05-18T10:00
updated: 2026-05-18T10:00
date: 2026-05-18
project: org-common
type: meeting-raw
tags:
  - meeting
  - raw
  - <topic>
participants:
  - <name1>
summary-link: [[2026-05-18-<topic>]]   # 요약본 링크 (있으면)
---
```

본문:
```markdown
# <YYYY-MM-DD> <주제> — Raw Transcript

> 원문. 발언자별 토씨 포함.
> 요약: [[YYYY-MM-DD-<topic>]]

---

## Transcript

<speaker>: <발언>

<speaker>: <발언>

...
```

## Backlink 규칙

- 모든 신규 노트는 기존 노트 1~3개와 연결
- 회의록은 같은 시리즈 이전 회의 + 관련 컨셉 노트
- 외부 자료는 같은 도메인 자료 + 적용 컨셉
- 고립 노트 금지 — 정 없으면 `purpose.md` 또는 `wiki/index.md` 연결

각 프로젝트의 라이브 노트 목록은 `ls <project>/raw/sources/` 1회 호출로 확인.

## 중복 처리

```
동일 파일명
  → "갱신? 또는 차별점으로 새 이름?" 확인
유사 주제, 다른 각도
  → 신규 + backlink로 기존 연결
동일 회의 다른 버전 (요약 + 원문)
  → 둘 다 생성, 서로 cross-link
완전 동일 자료
  → 기존 갱신 (updated만 변경)
```

## Output Receipt

```
Outcome: wiki note injected | duplicate detected | escalate
Evidence: <project>/raw/<type>/<filename>.md (<bytes>)
Artifact Paths: <전체 경로>
Project: tech-notes | org-common | APP | svc | <other>
Type: source | meeting-summary | meeting-raw
Backlinks: [[note-1]], [[note-2]]
Next Action: <연관 노트 갱신 / 컨셉 승격 / 후속 회의록 / Jira 티켓>
```

## Error Handling

| 케이스 | 처리 |
|--------|------|
| 프로젝트 디렉토리 없음 | `ls llm-wiki/`로 가용 목록 보여주고 사용자에게 선택 요청 |
| 타입 추론 실패 | 사용자에게 3지선다 확인 |
| raw/sources/ 디렉토리 없음 | 자동 `mkdir -p` |
| iCloud 경로 접근 불가 | 동기화 상태 확인 안내 후 중단 |
| 영문 파일명 규칙 위반 | kebab-case 변환 후 확인 |
| 백링크 0개 | 강제로 1개 이상 제안. 정 없으면 `purpose.md` 연결 |
| 회의록 참석자 정보 없음 | frontmatter `participants: []` 빈 배열로 두고 사용자에게 사후 보완 안내 |

## Karpathy 3-Layer + nashsu/llm_wiki 도구

```
wiki/{concepts, synthesis, entities, comparisons, queries, sources}/
  ↑ nashsu/llm_wiki 도구가 ingest로 자동 생성 (수동 X)
raw/sources/   ← 이 스킬이 다루는 층 (도구가 watch하는 유일한 디렉토리)
raw/assets/    ← 이미지·바이너리
  ↑ 사용자가 자료 drop, immutable
schema.md / purpose.md   ← 프로젝트 설정. 사용자가 직접 작성. ingest 시 LLM이 매번 읽음
```

- **이 스킬 = raw/sources/ 주입 전담**. wiki/* 절대 손대지 않음
- 도구 = nashsu/llm_wiki 데스크탑 앱 (https://github.com/nashsu/llm_wiki)
- 검증됨 (2026-05-18): `raw/sources/`에 박힌 자료만 ingest 됨. `raw/meetings/` 등 다른 서브디렉토리는 무시
- 참고 노트: `tech-notes/raw/sources/karpathy-llm-wiki-design.md`

## 관련 스킬

- `reflect` — 개인 메모리 (Claude 메모리 시스템). raw/는 외부 자료/회의록.
- `publish-spec` — Confluence 팀 공유. wiki-inject는 개인 위키.
- `explain` — 산출물 층 생성. wiki-inject는 원천 층.
- `prep` — Jira/Confluence SoT 로컬화. 회의록은 raw 원천이지만 prep는 docs/requirements.md 행.

## 사용 예

```
"이 영상 위키에 박아 https://youtube.com/..."
  → project=tech-notes, type=source

"APP H1 회의록 정리한거 박아"
  → project=APP, type=meeting-summary

"svc 인프라 회의 원문 raw로"
  → project=svc, type=meeting-raw

"전사 릴리스 프로세스 회의록"
  → project=org-common, type=meeting-summary

"이거 위키 어디 박지?"
  → 키워드 분석 + 모호하면 사용자 확인
```
