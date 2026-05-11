# reflect — 세션 학습 캡처

세션에서 내린 결정, 발견한 컨벤션, 주의사항을 구조화하여 프로젝트 지식으로 저장한다.
다음 세션에서 컨텍스트 복원 비용을 줄이는 것이 목적이다.

## 수집 (병렬 실행)

1. **세션 히스토리**: 이번 대화에서 내린 기술 결정 회고
2. **Git diff**: `git diff main...HEAD --stat` 또는 최근 커밋 목록
3. **gap.md 변화**: gap.md 있으면 점수 변화 확인
4. **발견된 패턴**: 세션 중 발견한 코드 컨벤션이나 프로젝트 특이사항

## 분류

수집 결과를 3가지로 분류:

### 1. Decisions (결정)
이번 세션에서 내린 기술적/설계적 결정.
- 예: "React Query 대신 SWR 채택 — 번들 사이즈 이유"
- 예: "API 에러 핸들링은 middleware에서 통합 처리"

### 2. Conventions (컨벤션)
발견하거나 확립한 코드 컨벤션.
- 예: "이 프로젝트에서 커스텀 훅은 `hooks/use*.ts` 패턴"
- 예: "API 타입은 `types/api/` 하위에 도메인별 분리"

### 3. Warnings (주의사항)
다음 세션에서 주의해야 할 함정이나 제약.
- 예: "payments 모듈 테스트는 VPN 필요"
- 예: "`legacy-auth` 모듈 건드리면 SSO 깨짐 — 마이그레이션 전까지 수정 금지"

## 예시

<example>
세션: React Query vs SWR 선택, hooks 네이밍 발견, legacy-auth 경고 발견

출력:
## Session Reflect — 2026-05-06

### Decisions
- React Query 채택: SWR 대비 캐시 무효화 전략이 approval flow 상태 변경 패턴에 적합

### Conventions
- 커스텀 훅: `hooks/use*.ts` 네이밍 패턴
- API 클라이언트: `lib/apiClient.ts` 중앙 집중 — 도메인별 분리 아님

### Warnings
- `legacy-auth` 모듈 수정 금지 — SSO 마이그레이션 전까지 건드리면 인증 깨짐

### Gap Status
- 이전: 40/100 → 현재: 65/100

### Next Session
- 결재 이력 조회 (FR-4) 구현
</example>

## 저장

분류 결과를 다음 위치에 저장:

1. **Auto-memory** (`~/.claude/projects/-Users-al02628725-Work/memory/`): 세션 간 지속되는 핵심 지식
   - Decisions/Warnings 중 다음 세션에도 유효한 것 → 해당 타입 파일에 Write/Edit
   - 타입 선택: `project_*.md` (프로젝트 진행 상황), `feedback_*.md` (행동 지침), `user_*.md` (사용자 선호)
   - MEMORY.md 인덱스도 업데이트
   - claude-mem은 hook이 대화를 자동 캡처 — 별도 저장 불필요
2. **docs/learnings.md** (선택적): 팀 공유가 필요한 학습 내용
   - 파일 이미 존재 시 append. 미존재 시 생성하지 않음 (사용자가 원하면 직접 생성).
3. **gap.md 업데이트**: Agreed Exceptions 변경 시 반영

## 출력 형식

```
## Session Reflect — {날짜}

### Decisions
- {결정 1}: {이유}
- {결정 2}: {이유}

### Conventions
- {컨벤션 1}
- {컨벤션 2}

### Warnings
- {주의사항 1}
- {주의사항 2}

### Gap Status
- 이전: {N}/100 → 현재: {M}/100 (gap.md 없으면 생략)

### Next Session
- {다음 세션에서 이어할 작업}
```

## 규칙

- 코드 변경 내역 나열 금지. `git log`로 볼 수 있는 건 생략.
- 결정의 **이유**를 반드시 포함. "왜"가 없는 결정은 기록 가치 없음.
- Conventions는 프로젝트 전반에 적용 가능한 것만. 일회성 패턴 제외.
- Warnings는 코드만 봐서는 알 수 없는 것만. 코드에 명시된 제약은 제외.
- 저장할 내용 없으면 "특이사항 없음" 출력 후 종료. 억지로 채우지 않음.

