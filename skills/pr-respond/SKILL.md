---
name: pr-respond
description: PR 리뷰 코멘트 대응 워크플로우. PR에 달린 리뷰를 fetch하고, 각 코멘트를 기술적으로 검증한 뒤 수용/반박/보류를 결정하여 대응한다. 수용 시 사이드이펙트 분석과 설계 고려를 거친 후 구현한다. Use when (1) PR에 리뷰가 달렸을 때, (2) "리뷰 대응", "PR 리뷰", "리뷰 코멘트", "뭐라고 할까", "어떻게 답하지", "review comment", "respond to review", "handle review feedback", (3) PR URL이나 번호와 함께 리뷰 관련 질문, (4) "리뷰어가 ~라고 했는데", "이 코멘트 어떻게 처리하지". Supports --dry-run (분석만), --status (미응답 목록).
---

# pr-respond — PR 리뷰 코멘트 대응

PR에 달린 리뷰 코멘트를 체계적으로 분석하고 대응한다.
각 코멘트를 기술적으로 검증한 뒤, 수용 또는 반박을 결정하고 실행한다.

**핵심 원칙**: `receiving-code-review` superpowers 원칙 준수 — 검증 없는 수용 금지, performative agreement 금지, 기술적 정확성 우선.

## 입력

`$ARGUMENTS` 파싱:

| 인자 | 동작 |
|------|------|
| (없음) | 현재 브랜치의 PR 자동 탐지 |
| `<PR번호>` | 해당 PR 번호로 직접 지정 |
| `<PR_URL>` | URL에서 PR 번호 추출 |
| `--dry-run` | 분석 + 응답 초안만. 코드 수정/reply 없음 |
| `--status` | 미응답 리뷰 코멘트 목록만 출력 |

## 전제조건

- `gh` CLI 인증 완료 상태
- PR이 존재하고 리뷰 코멘트가 1건 이상

## 실행

### Phase 1: 수집

1. **PR 정보 fetch**:
   ```bash
   # PR 자동 탐지 (현재 브랜치) 또는 지정된 번호 사용
   gh pr view [번호] --json number,url,headRefName,baseRefName,author

   # owner/repo 추출
   gh repo view --json owner,name
   ```

2. **리뷰 코멘트 fetch** (context-mode ctx_batch_execute 사용 — 응답 크기 대비, concurrency: 3):
   ```bash
   # 인라인 리뷰 코멘트
   GH_HOST={hostname} gh api repos/{owner}/{repo}/pulls/{number}/comments

   # PR-level 리뷰 (approve/request_changes/comment + body)
   GH_HOST={hostname} gh api repos/{owner}/{repo}/pulls/{number}/reviews

   # Issue comments (일반 댓글 — 인라인 리뷰가 아닌 코멘트 포함)
   GH_HOST={hostname} gh api repos/{owner}/{repo}/issues/{number}/comments
   ```
   **GHE 사용 시**: `GH_HOST={hostname}` env var 설정. `--hostname` 플래그 없음.

3. **Bot 필터링**: 다음 bot 코멘트는 무시:
   - `code-aimigo[bot]` — AI 코드리뷰 bot. LGTM/요약은 참고용이지만 대응 불필요
   - `github-actions[bot]` — CI/CD bot
   - `snyk[bot]`, `dependabot[bot]` 등 security/dependency bot
   - 판단 기준: `user.type === "Bot"` 또는 login에 `[bot]` 포함

4. **미응답 코멘트만 필터**: 이미 reply가 달린 코멘트는 제외.
   - 인라인 코멘트: `in_reply_to_id`가 없는 루트 코멘트 중, 자신의 reply가 없는 것만 대상
   - Issue comments: 자신의 reply comment가 없는 것만 대상

`--status` 모드면 여기서 목록 출력 후 종료.

### Phase 2: 분류

각 코멘트를 아래 기준으로 분류:

| 카테고리 | 설명 | 대응 방식 |
|----------|------|-----------|
| `blocking` | 보안, 버그, 크리티컬 이슈 | 반드시 검증 → 수용 또는 기술적 반박 |
| `suggestion` | 코드 개선 제안 | 검증 → 판단 |
| `question` | 의도/설계 질문 | 설명 reply |
| `nitpick` | 스타일, 네이밍, 포맷 | 간단 수용 또는 설명 |
| `praise` | 긍정 피드백 | 스킵 (reply 불필요) |

### Phase 3: 평가 (코멘트별)

**READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND** 패턴 적용:

1. **UNDERSTAND**: 리뷰어 의도 파악
   - 불명확하면 → 질문 reply를 먼저 작성 (구현하지 않음)
   - 여러 코멘트가 연관되면 → 전체 파악 후 판단 (부분 수용 금지)

2. **VERIFY**: 코드베이스에서 실제 확인
   - 해당 파일:라인 읽기
   - 리뷰어가 지적한 문제가 실재하는지 확인
   - 관련 테스트 존재 여부 확인
   - 현재 구현의 이유/히스토리 확인 (git blame)

3. **EVALUATE**: 기술적 판단
   - 이 코드베이스에서 기술적으로 올바른가?
   - 기존 기능을 깨뜨리는가?
   - 현재 구현에 의도적 이유가 있는가?
   - YAGNI 해당하는가? (미사용 기능 추가 제안 → grep으로 실제 사용처 확인)

### Phase 4: 판단

```
IF 리뷰어 지적이 기술적으로 타당:
  → ACCEPT (Phase 5)

IF 리뷰어가 컨텍스트를 모르거나 기술적으로 부정확:
  → REBUT (Phase 6)

IF 판단 불확실 또는 아키텍처 방향 결정 필요:
  → HOLD — 유저에게 판단 위임 (분석 결과만 제시)
```

### Phase 5: 수용 경로 — 사이드이펙트 분석 후 구현

수용이라고 바로 구현하지 않는다. **반드시 사이드이펙트 분석 먼저.**

#### 5-1. 영향 범위 분석
- 변경 대상 함수/타입의 caller 추적 (Grep — 직접 호출, 타입 참조, re-export, 동적 import 각각)
- 관련 테스트 파일 확인
- API 계약 변경 여부

#### 5-2. 설계 고려
- 제안된 방식이 최선인가? 더 나은 대안은?
- 기존 코드베이스 패턴과 일관성 있는가?
- 제안 그대로 구현 vs 의도를 살린 다른 구현 — 근거 있는 선택

#### 5-3. 구현
- 변경 적용 (1건씩. 일괄 금지)
- `npx tsc --noEmit` (또는 프로젝트 타입체크)
- 관련 테스트 실행
- 리그레션 없음 확인

#### 5-4. Reply 작성

코멘트 스레드에 inline reply (`gh api repos/{owner}/{repo}/pulls/{number}/comments/{id}/replies -f body="..."`):

```
Fixed. [변경 내용 1줄 설명]
```

대안으로 구현한 경우:
```
Fixed differently — [대안 + 이유 1줄]. [변경 내용]
```

### Phase 6: 반박 경로 — 기술적 근거 제시

반박 사유 (하나 이상 해당 시):
- 기존 기능 깨뜨림
- 리뷰어가 전체 컨텍스트 모름
- YAGNI (grep 결과 미사용)
- 이 스택에서 기술적으로 부정확
- 레거시/호환성 이유 존재
- 유저의 아키텍처 결정과 충돌

Reply 형식:
```
[현재 구현 이유 1줄]. [기술적 근거 — 코드/테스트 참조].
[질문 또는 대안 제시 (있을 경우)]
```

### Phase 7: 정리

1. **변경사항 확인** (수용 건이 있을 때):
   - 변경 파일 목록 + diff 요약
   - **commit 메시지 제안** — 형식: `fix: <변경 내용 1줄>`. 자동 커밋 금지 — CLAUDE.md 규칙.
   - push 여부 유저에게 확인

2. **요약 출력**

## 출력 형식

```
## PR Review Response — PR #{number}

### 요약
- 총 코멘트: N건
- 수용 (구현 완료): N건
- 반박 (reply 완료): N건
- 질문 답변: N건
- 스킵 (praise): N건
- 판단 보류: N건 (유저 확인 필요)

### 수용 (구현 완료)
| # | 파일:라인 | 리뷰어 | 요약 | 대응 |
|---|-----------|--------|------|------|
| 1 | src/auth.ts:42 | @reviewer | null check 누락 | Fixed. early return 추가 |

### 반박
| # | 파일:라인 | 리뷰어 | 요약 | 반박 근거 |
|---|-----------|--------|------|-----------|
| 1 | src/api.ts:15 | @reviewer | 레거시 코드 제거 | backward compat 필요 (target: iOS 13+) |

### 판단 보류 (유저 확인 필요)
| # | 파일:라인 | 리뷰어 | 요약 | 쟁점 |
|---|-----------|--------|------|------|
| 1 | src/utils.ts:88 | @reviewer | 리팩터링 제안 | 아키텍처 방향 결정 필요 |

### 질문 답변
| # | 파일:라인 | 리뷰어 | 질문 | 답변 |
|---|-----------|--------|------|------|
| 1 | src/hooks.ts:20 | @reviewer | 왜 useMemo? | 렌더링 최적화 — 상위 컴포넌트 리렌더 빈도 높음 |
```

### --status 모드 출력

```
## PR #{number} — 미응답 리뷰 코멘트

| # | 카테고리 | 파일:라인 | 리뷰어 | 요약 |
|---|----------|-----------|--------|------|
| 1 | blocking | src/auth.ts:42 | @reviewer | null check 누락 |
| 2 | suggestion | src/api.ts:15 | @reviewer | 에러 핸들링 개선 |

총 N건 미응답
```

## 예시

<example>
상황: PR #142에 리뷰 코멘트 3건

코멘트 1: @senior-dev on src/auth.ts:42 — "validateToken에서 null check 빠져있음. token이 undefined일 때 crash 발생"
코멘트 2: @senior-dev on src/api.ts:15 — "이 레거시 헬퍼 제거하고 새 유틸로 교체하는 게 낫지 않나?"
코멘트 3: @senior-dev on src/hooks.ts:20 — "👍 깔끔하네요"

실행 결과:

## PR Review Response — PR #142

### 요약
- 총 코멘트: 3건
- 수용 (구현 완료): 1건
- 반박 (reply 완료): 1건
- 스킵 (praise): 1건

### 수용 (구현 완료)
| # | 파일:라인 | 리뷰어 | 요약 | 대응 |
|---|-----------|--------|------|------|
| 1 | src/auth.ts:42 | @senior-dev | null check 누락 | Fixed. early return 추가 + 단위테스트 보강 |

사이드이펙트 분석: validateToken caller 3곳 확인 (LoginForm, AuthGuard, TokenRefresh). null 반환 시 기존 호출부 모두 optional chaining 사용 중 → 리그레션 없음.

### 반박
| # | 파일:라인 | 리뷰어 | 요약 | 반박 근거 |
|---|-----------|--------|------|-----------|
| 1 | src/api.ts:15 | @senior-dev | 레거시 헬퍼 제거 | legacyHelper는 v2 API 미지원 클라이언트용. grep 결과 MobileClientAdapter에서 활발히 사용 중. 제거 시 하위호환 깨짐. |

Reply: "legacyHelper is actively used by MobileClientAdapter for v2 API fallback (src/adapters/MobileClientAdapter.ts:34). Removing it breaks backward compat for clients not yet migrated to v3."
</example>

<example>
상황: /pr-respond --dry-run

출력 (코드 수정/reply 없이 분석만):

## PR Review Response — PR #89 (dry-run)

### 요약
- 총 코멘트: 2건
- 수용 예정: 1건
- 판단 보류: 1건

### 수용 예정 (미구현 — dry-run)
| # | 파일:라인 | 리뷰어 | 요약 | 계획 |
|---|-----------|--------|------|------|
| 1 | src/utils.ts:55 | @reviewer | 에러 메시지 하드코딩 | 상수 추출 예정. 영향 범위: 이 파일만. 사이드이펙트 없음 |

### 판단 보류
| # | 파일:라인 | 리뷰어 | 요약 | 쟁점 |
|---|-----------|--------|------|------|
| 1 | src/store.ts:12 | @reviewer | Redux → Zustand 전환 제안 | 아키텍처 방향 결정 필요. 현재 Redux 패턴이 프로젝트 전반에 사용 중 |
</example>

<example>
상황: /pr-respond --status

출력:

## PR #142 — 미응답 리뷰 코멘트

| # | 카테고리 | 파일:라인 | 리뷰어 | 요약 |
|---|----------|-----------|--------|------|
| 1 | blocking | src/auth.ts:42 | @senior-dev | null check 누락 |
| 2 | suggestion | src/api.ts:15 | @senior-dev | 레거시 헬퍼 교체 제안 |

총 2건 미응답
</example>

## 규칙

1. **Performative agreement 금지**: "You're right!", "Great point!", "Thanks!" 사용 금지. 수정했으면 "Fixed." 또는 기술적 설명만.
2. **검증 없는 수용 금지**: 코드베이스에서 실제 확인 후 판단. 리뷰어 말만 믿고 구현하지 않음.
3. **사이드이펙트 분석 필수**: 수용 시 영향 범위 + 설계 고려 없이 바로 구현 금지.
4. **1건씩 구현**: 여러 코멘트 일괄 구현 금지. 각각 구현 → 검증 → 다음.
5. **판단 불확실 시 보류**: 무리하게 판단하지 않음. 유저에게 위임.
6. **자동 커밋 금지**: CLAUDE.md 규칙. commit 메시지 제안만.
7. **Reply는 코멘트 스레드에**: `gh api .../comments/{id}/replies` 사용. top-level PR comment 금지.
8. **context-mode 사용**: gh API 응답은 ctx_batch_execute로 수집하여 컨텍스트 윈도우 보호.
9. **연관 코멘트 파악**: 여러 코멘트가 같은 이슈를 가리키면 개별 대응 대신 통합 판단.
10. **반박 시 방어적 톤 금지**: 감정적/사과/감사 표현 없이 기술적 사실만.
11. **검증 불가 시 솔직히 표기**: 코드 접근 불가, 테스트 실행 불가, 또는 판단 근거 불충분 시 추측하지 않음. "검증 불가 — [이유]" 표기 후 HOLD 처리.

