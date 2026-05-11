# incident-fix — 장애 리포트 기반 수정 구현

`docs/incident-report.md`를 SoT로 사용하여 장애를 수정한다.
superpowers verification 패턴을 따른다: 증거 없는 완료 선언 금지.

## 전제조건

- `docs/incident-report.md` 존재 필수. 없으면 → "`/incident` 먼저 실행" 안내 후 중단.
- 유력 가설(⭐)이 1개 이상 있어야 진행. 없으면 → "가설 확신도 부족. 추가 조사 필요" 안내 후 중단.

## 실행 (5 Phase, 각 Phase에 Gate)

<phases>

### Phase 0: 리포트 로드 + 작업 계획

1. `docs/incident-report.md` 읽기
2. 추출:
   - 유력 가설 (Hypothesis ⭐)
   - Proposed Fix (수정 대상 + 방향)
   - Side Effects 테이블
   - Test Gap (추가할 테스트)
   - Similar Patterns
3. 작업 항목을 TaskCreate로 등록

<gate>
- [ ] 리포트 로드 완료
- [ ] 유력 가설 확신도 "중간" 이상
- [ ] Proposed Fix 섹션에 구체적 파일/함수 명시됨
Gate 실패 시: "/incident 리포트 보완 필요" 안내 후 중단.
</gate>

### Phase 1: RED — 실패하는 테스트 작성

incident-report.md의 **Test Gap** 섹션 기반으로 테스트 작성.

1. 장애 현상을 재현하는 테스트 케이스 작성
2. 테스트 실행 → **반드시 실패 확인**
3. 실패 이유가 장애 현상과 일치하는지 확인

```
✅ 올바른 RED: 테스트 실행 → FAIL (expected: X, got: Y — 장애 현상과 일치)
❌ 잘못된 RED: 테스트 실행 → FAIL (compile error, import error — 장애와 무관한 실패)
❌ 잘못된 RED: 테스트 실행 → PASS (이미 통과하면 장애 재현 실패)
```

<gate>
- [ ] 테스트 실행 커맨드 실행 완료 (exit code 확인)
- [ ] 실패 출력에서 장애 현상과 일치하는 에러 메시지 확인
- [ ] 실패 이유가 올바른 이유인지 (컴파일 에러가 아닌 로직 에러) 확인
Gate 실패 시: 테스트 수정. 3회 실패 → Phase 0으로 돌아가 가설 재검토.
</gate>

### Phase 2: GREEN — 최소 수정 구현

incident-report.md의 **Proposed Fix** 기반으로 수정.

1. 유력 가설의 원인을 해소하는 **최소한의** 코드 변경
2. "while I'm here" 개선 금지 — 장애 수정만
3. 테스트 실행 → **반드시 통과 확인**
4. 기존 테스트 전체 실행 → **회귀 없음 확인**

```
✅ 올바른 GREEN: [테스트 커맨드] → 34/34 pass, 0 failures
❌ "통과한 것 같음", "에러 없어 보임" — 출력 확인 없는 주장 금지
```

<gate>
- [ ] 새 테스트 PASS (RED에서 FAIL이었던 것이 PASS)
- [ ] 기존 테스트 전체 PASS (회귀 없음)
- [ ] 변경 파일이 Proposed Fix 범위 안에 있음 (scope creep 방지)
Gate 실패 시: 수정 재시도. 3회 실패 → STOP. "가설이 틀렸을 가능성" 경고 + Phase 0 재검토.
</gate>

### Phase 3: Side Effects 검증

incident-report.md의 **Side Effects** 테이블 기반.

1. Side Effects 테이블의 각 "영향 경로"를 코드에서 추적
2. 각 경로에 대해:
   - 해당 경로의 기존 테스트 실행 → 통과 확인
   - 기존 테스트 없으면 → 간단한 검증 테스트 추가
3. 위험도 "높음" 경로는 수동 확인 필요 시 사용자에게 알림

<gate>
- [ ] Side Effects 테이블의 모든 경로 검증 완료
- [ ] 위험도 "높음" 경로에 대해 테스트 또는 사용자 확인 완료
- [ ] 새로 추가한 검증 테스트 전체 PASS
</gate>

### Phase 4: Similar Patterns 수정

incident-report.md의 **Similar Patterns** 기반.

1. 유사 패턴이 있다면 동일한 RED → GREEN 사이클 적용
2. 유사 패턴 없으면 Skip (억지로 찾지 않음)
3. 각 유사 패턴 수정 후 테스트 실행

<gate>
- [ ] 유사 패턴 수정 각각에 대해 RED → GREEN 완료 (또는 Skip 근거 명시)
- [ ] 전체 테스트 스위트 PASS
</gate>

### Phase 5: 최종 검증 (Verification Before Completion)

superpowers verification-before-completion 패턴 적용.

| 주장 | 필요한 증거 | 불충분 |
|------|-----------|--------|
| 장애 수정됨 | Phase 1 RED 테스트가 GREEN | "코드 고쳤으니 될 것" |
| 회귀 없음 | 전체 테스트 PASS 출력 | "관련 없는 코드라 괜찮을 것" |
| 사이드이펙트 없음 | Phase 3 검증 완료 | "영향 없어 보임" |
| 빌드 성공 | 빌드 커맨드 exit 0 | 테스트만 통과 |

1. 전체 테스트 스위트 실행 (최종)
2. 린트/타입체크 실행 (프로젝트에 있으면)
3. 빌드 실행

<gate>
- [ ] 테스트: 전체 PASS (출력 확인)
- [ ] 린트: 0 errors (출력 확인)
- [ ] 빌드: exit 0 (출력 확인)
모든 gate 통과 시에만 "수정 완료" 선언.
</gate>

</phases>

## 예시

<example>
입력: `/incident-fix` (docs/incident-report.md 존재)

Phase 0: 리포트에서 추출
- 가설 A ⭐: cache key에 page 미포함 (확신도: 중간)
- Fix: useApprovalList.ts — queryKey에 page 파라미터 추가
- Test Gap: pagination 테스트 없음

Phase 1 RED:
```
// ApprovalList.test.tsx
test('page 2 요청 시 page=2 파라미터로 API 호출', () => {
  // ... mock setup
  expect(apiCall).toHaveBeenCalledWith('/api/approvals?page=2');
});
→ FAIL ✓ (page=1로 호출됨 — 장애 현상 일치)
```

Phase 2 GREEN:
```
// useApprovalList.ts — queryKey에 page 추가
queryKey: ['approvals', { page }]  // 기존: ['approvals']
→ 35/35 PASS ✓
```

Phase 3: Side Effects 검증
- 캐시 무효화 경로: 승인/반려 후 목록 갱신 → 테스트 PASS ✓
- SSR prefetch: 해당 없음 (CSR only)

Phase 5: 최종 검증
- 전체 테스트: 37/37 PASS
- eslint: 0 errors
- tsc: 0 errors
→ 수정 완료 ✓
</example>

## 완료 후

1. 수정 완료 선언 (증거 포함)
2. 다음 단계 안내:
   - `/reflect` — 세션 학습 캡처 (결정/컨벤션/주의사항)
   - `/gap --verify` — 기존 요구사항 갭 재확인 (해당 시)

## 규칙

- **증거 없는 완료 선언 절대 금지.** 모든 "완료" 주장에 커맨드 출력 필요.
- **3회 실패 → STOP.** 가설이 틀렸을 가능성 경고. Phase 0 재검토 또는 `/incident` 재실행.
- **범위 밖 수정 금지.** Proposed Fix + Similar Patterns 범위만. "여기도 고치면 좋겠다" 금지.
- **incident-report.md 수정 금지.** 읽기 전용 SoT. 분석이 틀렸으면 `/incident` 재실행.

