# prep — Gates 상세

## Trailing 출력 gate

모든 prep 응답 끝에 한 줄 출력:

```
[PREP] sources=N | raw_files=docs/sources/<id1>.raw.md,<id2>.raw.md | fetched=<ISO8601> | raw_lines=<sum> | req_lines=<count> | unverified=K/M | readiness=X/4
```

- `raw_lines`: 모든 raw 파일 라인 수 합
- `req_lines`: requirements.md 라인 수 (frontmatter 제외)
- `unverified`: `[UNVERIFIED]` 항목 / 전체 요구사항 항목
- 누락 시 prep 응답으로 인정 안 됨 (사용자 즉시 가시화)

## Stale 검증 (재실행 시)

`docs/requirements.md` 존재 시 frontmatter `sources[].fetched_at` 확인.

| 경과 | 행동 |
|------|------|
| ≤ 3일 + 새 SoT 인자 없음 | "최신 상태" 1줄 출력 후 종료 |
| > 3일 또는 새 SoT 인자 있음 | 재fetch 진행 |

기존 raw 파일 존재 시 hash 비교 → 동일하면 fetched_at만 갱신, 다르면 사용자에게 변경 사실 알리고 갱신.

## Readiness 판정

저장 후 requirements.md를 4개 기준 판정:

| 기준 | PASS | FAIL |
|------|------|------|
| Functional Requirements 항목 수 | ≥ 1 | 0 |
| `[UNVERIFIED]` 비율 | < 50% | ≥ 50% |
| Blocking Open Questions 수 | ≤ 3 | > 3 |
| Goal 섹션 | 비어있지 않음 | 비어있음 |

**Readiness = 4개 중 PASS 수**:
- 4/4 READY → "요구사항 충분. brainstorm → gap 진행 가능"
- 2-3/4 PARTIAL → "보완 후 진행 또는 `ac-draft`로 명확화 추천"
- 0-1/4 INSUFFICIENT → "`ac-draft` 필요. 보완 후 `/prep` 재실행"

## Raw 저장 규약

- fetched 원문은 `docs/sources/<id>.raw.md`에 그대로 저장
- 의역/요약/재정렬/번역 금지
- 메타데이터(URL, fetched_at) 한 줄만 frontmatter로 허용
- source-id 규칙: Jira = 티켓ID(소문자) / Confluence = page-id / Figma = file-key / 기타 = 슬러그
