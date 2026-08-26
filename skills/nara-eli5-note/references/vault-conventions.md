# Obsidian vault 관례 (실측 2026-08-24)

vault `narashin` 한 개. 매번 조사하지 않기 위해 실측 결과를 고정해 둔 것.

**구조가 바뀌었을 수 있으므로, 노트를 넣기 전에 대상 폴더의 기존 노트 하나를 읽어 frontmatter 스키마를 확인한다.** 아래는 출발점이고 정본은 vault 자체다.

---

## 폴더 두 종류를 먼저 가른다

vault에는 성격이 다른 두 계열이 섞여 있고, **어느 쪽에 넣느냐로 frontmatter와 파일명이 갈린다.**

### 커리큘럼 — `2_personal/Study/*-core/`

순서가 있는 학습 과정. `00-*-index.md` + 번호 붙은 노트 + `_inbox.md` 구성.

```
2_personal/Study/
├── cs-core/     00-cs-index.md · 01-dns-… · B1-… · B6-…
├── git-core/    00-git-index.md · G1-… · _inbox.md
├── web-core/    00-web-index.md · W1-… · _inbox.md
└── sandy-core/  00-index.md · 02-… · _inbox.md
```

frontmatter에 학습 진행용 필드가 있다.

```yaml
created: 2026-08-14T13:10
updated: 2026-08-14T13:50
tags: [learning, web, frontend, curriculum, moc]
study_id: IDX-web
study_part: 색인
study_order: 0
study_requires: []
study_status: index
```

**여기에 넣는 경우** — 기존 커리큘럼의 다음 차시로 들어갈 때만. 그때는 index의 `## 목록`에 체크박스 한 줄을 추가하고 번호를 이어받는다. 주제가 그 커리큘럼의 축과 다르면 넣지 않는다(예: `web-core`는 "경계·계약·릴리스·실패 처리"이고 빌드 최적화는 그 축이 아니다).

### 주제 노트 — `2_personal/Study/<주제>/`

번호 없음, kebab-case 파일명, 진행 필드 없음. **실무에서 겪은 것을 정리한 노트가 여기 온다.**

```
2_personal/Study/
├── ai-agent/    tool-vs-harness.md · negative-vs-positive-instructions.md · …
├── react/       react-query-invalidation-scope.md · react-derived-state-frozen-flag.md
├── bundler/     vite-tree-shaking-bare-imports.md
└── planning/    User Scenario vs User Story vs AC.md
```

frontmatter가 단순하다.

```yaml
created: 2026-08-24T21:07
updated: 2026-08-24T21:07
tags:
  - bundler
  - vite
  - debugging
```

`planning/`처럼 **노트 한 개짜리 폴더가 정상이다.** 맞는 폴더가 없으면 새로 만드는 것이 이 vault의 관례다. 억지로 다른 폴더에 밀어넣지 않는다.

### 그 밖

- `2_personal/Study/_learning/` — `candidates.md`(세션에서 캐낸 발화 후보), `ledger.md`(원장). 직접 쓰지 않는다.
- `3_work/Projects/<프로젝트>/` — 업무 기록. 회의록·요구사항 청취 등.
- `3_work/Notes/` — 업무 메모.

학습 노트는 `2_personal`, 업무 산출물은 `3_work`. **개념 설명 노트는 항상 `2_personal/Study/` 아래다.**

---

## 톤

**해체(`~다`)를 쓴다.** ForgeHub repo 문서의 음슴체(`~함`)는 그 repo 규칙이고 vault에는 적용되지 않는다.

기존 노트에서 관찰된 것:

- **1인칭을 쓴다.** "내가 처음에 틀렸던 부분", "내가 짰던 키", "오늘 버그".
- **자기 오류를 숨기지 않고 절로 만든다.** 이게 노트의 가장 쓸모 있는 부분이다.
- **검증 근거를 앞에 밝힌다.** "공식 문서 + `query-core` 구현 + 레포 실측(installed 5.90.12)" 같은 한 줄.
- **[일반 지식] / [내 사례] / [미확인]** 표기를 쓰는 노트가 있다(`web-core` 계열). 주제 노트에서는 필수가 아니다.

---

## 노트 골격

기존 주제 노트(`react/react-query-invalidation-scope.md`)에서 뽑은 구조. 이걸 따른다.

```markdown
---
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
tags: [...]
---
# <개념> — <한 줄 결론>

> <어디서 잡은 것인지 한 줄>
> <무엇이 일어났는지. 숫자가 있으면 넣는다>
> <원인을 한 줄로. "X가 아니라 Y였다" 형태가 잘 먹는다>
> 검증: <무엇으로 확인했는지>

---

## TL;DR

- <불릿 4~6개. 이것만 읽어도 결론이 서게>

---

## 1. <개념을 한 문장으로>      ← eli5면 여기에 비유 그림
## 2. 증상
## 3. 원인
## 4. 왜 그렇게 되나            ← 그림이 가장 잘 붙는 자리
## 5. 처방                     ← 코드 + 결과 표
## 6. 안전하다는 근거           ← 실측. 추측이면 그렇다고 쓴다
## 7. 검증 방법                ← 재현 가능하게
## 8. 남은 리스크
## 9. 내가 틀렸던 것            ← 필수
---
## 다른 데도 쓰이는 감각        ← 이 사례를 넘어 남는 것

관련: [[…]]
```

절 개수는 주제에 맞춰 줄인다. **`내가 틀렸던 것`과 `TL;DR`은 빼지 않는다.**

---

## 링크

- 같은 폴더/커리큘럼 노트로 `[[파일명]]` 또는 `[[파일명|표시할 말]]`.
- 아직 없는 노트로 링크를 걸어도 된다 — 나중에 쓸 자리 표시가 된다.
- 커리큘럼에 넣었으면 그 index의 목록에 한 줄 추가. 주제 노트는 index가 없어 링크 의무가 없다.

## 시각

frontmatter `created`/`updated`는 **분 단위**다. 추측하지 않고 `date '+%Y-%m-%dT%H:%M'`로 얻는다.
