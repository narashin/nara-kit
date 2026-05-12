# Incident Analysis: 5-Step Procedure + Output Template

## 실행 (5단계 교차 검증)

### 1단계: 현상 파악 + 재현
- 장애 보고 내용 정리 (누가, 언제, 어떤 현상)
- 재현 조건 특정 (환경, 입력, 순서)
- 영향 범위 파악 (영향 유저 수, 기능 범위, 데이터 오염 여부)

### 2단계: 가설 수립 (최소 3개)
코드베이스 분석하여 원인 가설 3개 이상:
```
가설 A: {원인 설명}
- 근거: {코드 위치, 로그, 조건}
- 반증: {이 가설이 틀리다면 관찰돼야 할 것}
```

### 3단계: 증거 대조
각 가설별 증거/반증/확신도(높음/중간/낮음). 증거 없이 "높음" 판정 금지.

### 4단계: 수정 방향 + 사이드이펙트
- 수정 방향 (구체적 파일/함수 수준)
- 의존 경로 분석
- 사이드이펙트
- 유사 패턴 (코드베이스 다른 곳에도 같은 버그 있는지)

### 5단계: 반대 심문 (자기 반박) — 건너뛰기 금지
- "이 분석이 틀렸다면 어디서 틀렸을까?"
- "선택한 가설 외에 다른 원인은?"
- "수정 방향이 실제 원인을 해소하는가, 증상만 가리는가?"

## 산출물 (`docs/incident-report.md`)

```markdown
# Incident Report: {장애 제목}

- Ticket: {링크}
- Reported: {날짜}
- Severity: Critical | Major | Minor

## 1. Summary
## 2. Impact
## 3. Reproduction
## 4. Root Cause Analysis
### Hypothesis A: {가설명} ⭐ (유력)
### Hypothesis B: {가설명}
## 5. Proposed Fix
## 6. Side Effects
## 7. Similar Patterns
## 8. Test Gap
## 9. Prevention
## 10. Self-Review (반대 심문 결과)
```
